# main.py — Точка входа SteamFlash
import os, sys, logging, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import LOG_FILE, USB_POLL_INTERVAL
import usb_watcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("main")
menu_lock = threading.Lock()
menu_open = False

def on_insert(path, games):
    global menu_open
    with menu_lock:
        if menu_open: return
        menu_open = True
    log.info(f"Показываю меню для {path}")
    try:
        import menu
        menu.show_menu(games, flash_path=path)
    except Exception as e:
        log.exception(f"Ошибка меню: {e}")
    finally:
        with menu_lock: menu_open = False

def on_remove(path): log.info(f"Флешка {path} извлечена")

def main():
    log.info("=== SteamFlash запущен (Linux) ===" if os.name!="nt" else "=== SteamFlash запущен ===")
    # проверка зависимостей
    try: import pygame
    except ImportError: log.error("pygame не установлен: pip install pygame"); sys.exit(1)
    watcher = usb_watcher.USBWatcher(poll_interval=USB_POLL_INTERVAL, on_insert=on_insert, on_remove=on_remove)
    watcher.start()
    # для теста без флешки: если передать --test, сразу открыть меню с примером
    if "--test" in sys.argv:
        import menu
        import usb_watcher as uw
        _, g = uw.find_gameids_on_removables()
        demo = g if g else [("570",""), ("730","")]
        menu.show_menu(demo, flash_path=None)
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        log.info("Выход")
        # корректно завершить pygame если окно ещё открыто
        try:
            import pygame
            pygame.quit()
        except: pass
        sys.exit(0)

if __name__ == "__main__": main()
