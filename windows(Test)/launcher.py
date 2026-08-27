# launcher.py — Запуск игр через steam:// (Linux + Windows)
import logging, webbrowser, os, subprocess, shutil
log = logging.getLogger(__name__)

def launch_game(app_id: str) -> tuple[bool, str]:
    url = f"steam://rungameid/{app_id}"
    try:
        if os.name == "nt":
            try: os.startfile(url)  # type: ignore
            except: webbrowser.open(url)
        else:
            # Linux: пробуем xdg-open, затем steam напрямую
            if shutil.which("xdg-open"):
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif shutil.which("steam"):
                subprocess.Popen(["steam", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                webbrowser.open(url)
            # проверим что steam вообще установлен
            if not shutil.which("steam") and not shutil.which("xdg-open"):
                return False, "Steam не найден (установи steam)"
        log.info(f"Запуск {url}")
        return True, "Запуск..."
    except Exception as e:
        log.exception(f"Ошибка запуска {app_id}: {e}")
        return False, f"Ошибка запуска: {e}"
