# usb_watcher.py — Слежение за USB-накопителями (Linux + Windows)
import os, time, logging, threading, glob, re
log = logging.getLogger(__name__)

def get_removable_drives():
    drives = []
    try:
        import psutil
        for p in psutil.disk_partitions(all=False):
            mp = p.mountpoint; opts = (p.opts or "").lower(); fstype=(p.fstype or "").lower()
            if os.name=="nt":
                if "removable" in opts or "cdrom" in opts:
                    if os.path.exists(mp): drives.append(mp)
            else:
                if mp.startswith(("/media/","/run/media/","/mnt/")) or "removable" in opts:
                    if os.path.exists(mp): drives.append(mp)
                elif fstype in ("vfat","exfat","ntfs","fuseblk") and mp.startswith("/media"):
                    drives.append(mp)
        if drives: return list(dict.fromkeys(drives))
    except Exception as e: log.warning(f"psutil: {e}")
    if os.name!="nt":
        for pattern in ["/media/*/*","/media/*","/run/media/*/*","/run/media/*","/mnt/*"]:
            for p in glob.glob(pattern):
                if os.path.isdir(p) and os.path.ismount(p): drives.append(p)
                elif os.path.isdir(p) and os.path.exists(os.path.join(p,"SteamID.txt")): drives.append(p)
        user_media=f"/media/{os.getenv('USER','')}"
        if os.path.isdir(user_media):
            for d in os.listdir(user_media):
                full=os.path.join(user_media,d)
                if os.path.isdir(full): drives.append(full)
        return list(dict.fromkeys(drives))
    try:
        import ctypes
        bitmask=ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1<<i):
                letter=f"{chr(65+i)}:\\"
                if ctypes.windll.kernel32.GetDriveTypeW(ctypes.c_wchar_p(letter))==2: drives.append(letter)
    except: pass
    return list(dict.fromkeys(drives))

def parse_gameids(file_path: str):
    """Парсит SteamID.txt — поддерживает:
       123456,765678
       570, 730
       1245620, ELDEN RING
       271590
       # комментарий
       Всё через запятую/пробел/новую строку. Имя после запятой если не число — считается названием.
    """
    games=[]
    try:
        with open(file_path,"r",encoding="utf-8-sig") as f:
            for lineno, raw in enumerate(f,1):
                line=raw.strip()
                if not line or line.startswith("#"): continue
                # убираем комментарии после #
                if "#" in line: line=line.split("#",1)[0].strip()
                if not line: continue
                parts=[p.strip() for p in line.split(",")]
                i=0
                while i < len(parts):
                    part=parts[i]
                    if not part: i+=1; continue
                    # случай "1245620, ELDEN RING" — второй кусок это имя
                    if part.isdigit() and i+1 < len(parts) and parts[i+1] and not parts[i+1].isdigit() and not parts[i+1].split(None,1)[0].isdigit():
                        # следующий кусок — название (содержит буквы)
                        if any(c.isalpha() for c in parts[i+1]):
                            games.append((part, parts[i+1])); i+=2; continue
                    # обычный id или "123 Name"
                    sub=part.split(None,1)
                    appid=sub[0].strip()
                    name=sub[1].strip() if len(sub)>1 and any(c.isalpha() for c in sub[1]) else None
                    if not appid.isdigit():
                        nums=re.findall(r"\d+",part)
                        if nums:
                            for n in nums: games.append((n,None))
                        else: log.warning(f"Кривой AppID '{appid}' строка {lineno} — пропуск")
                        i+=1; continue
                    games.append((appid,name)); i+=1
    except Exception as e: log.error(f"Ошибка чтения {file_path}: {e}")
    # убрать дубликаты сохраняя порядок
    seen=set(); uniq=[]
    for a,n in games:
        if a not in seen: seen.add(a); uniq.append((a,n))
    return uniq

def find_gameids_on_removables():
    from config import GAMEIDS_FILENAME
    for drive in get_removable_drives():
        candidate=os.path.join(drive,GAMEIDS_FILENAME)
        if os.path.isfile(candidate):
            log.info(f"Найден {candidate}")
            return candidate, parse_gameids(candidate)
    if os.name!="nt":
        for pattern in ["/media/*/*/SteamID.txt","/media/*/SteamID.txt","/run/media/*/*/SteamID.txt","/mnt/*/SteamID.txt"]:
            for p in glob.glob(pattern):
                if os.path.isfile(p): return p, parse_gameids(p)
    return None, []

class USBWatcher(threading.Thread):
    def __init__(self,poll_interval=1.5,on_insert=None,on_remove=None):
        super().__init__(daemon=True)
        self.poll_interval=poll_interval; self.on_insert=on_insert; self.on_remove=on_remove
        self._stop=threading.Event(); self._last_file=None
    def stop(self): self._stop.set()
    def run(self):
        log.info("USBWatcher запущен")
        while not self._stop.is_set():
            try:
                path,games=find_gameids_on_removables()
                if path and path!=self._last_file and games:
                    self._last_file=path
                    log.info(f"Вставлена флешка {path} ({len(games)} игр)")
                    if self.on_insert: self.on_insert(path,games)
                elif not path and self._last_file:
                    if self.on_remove: self.on_remove(self._last_file)
                    self._last_file=None
                elif path and not games:
                    log.warning(f"Файл {path} пуст")
            except Exception as e: log.exception(f"USBWatcher: {e}")
            time.sleep(self.poll_interval)
