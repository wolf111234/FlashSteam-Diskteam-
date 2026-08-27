# steam_api.py — с кэшем: авы и названия сохраняются в cache/
import os, json, logging, urllib.request
from config import CACHE_DIR, HTTP_TIMEOUT
log=logging.getLogger(__name__)
def _ensure(): os.makedirs(CACHE_DIR, exist_ok=True)
def get_cached_name(app_id):
    p=os.path.join(CACHE_DIR,f"{app_id}.json")
    if os.path.exists(p):
        try: return json.load(open(p,encoding="utf-8")).get("name")
        except: pass
    return None
def get_cached_cover_path(app_id):
    p=os.path.join(CACHE_DIR,f"{app_id}.jpg")
    if os.path.exists(p) and os.path.getsize(p)>1024: return p
    return None
def fetch_name(app_id):
    _ensure()
    c=get_cached_name(app_id)
    if c: return c
    url=f"https://store.steampowered.com/api/appdetails?appids={app_id}&l=russian"
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Diskteam/1.0"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            d=json.loads(r.read().decode("utf-8"))
            e=d.get(str(app_id))
            if e and e.get("success") and e.get("data",{}).get("name"):
                name=e["data"]["name"]
                json.dump({"name":name}, open(os.path.join(CACHE_DIR,f"{app_id}.json"),"w",encoding="utf-8"), ensure_ascii=False)
                return name
    except Exception as e: log.warning(f"name {app_id}: {e}")
    fb=f"Game #{app_id}"
    try: json.dump({"name":fb}, open(os.path.join(CACHE_DIR,f"{app_id}.json"),"w",encoding="utf-8"), ensure_ascii=False)
    except: pass
    return fb
def fetch_cover(app_id):
    _ensure()
    c=get_cached_cover_path(app_id)
    if c: return c
    url=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
    dest=os.path.join(CACHE_DIR,f"{app_id}.jpg")
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"Diskteam/1.0"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            data=r.read()
            if len(data)<1024: raise ValueError("small")
            open(dest,"wb").write(data)
            return dest
    except Exception as e:
        log.warning(f"cover {app_id}: {e}")
        try: os.remove(dest)
        except: pass
    return None
