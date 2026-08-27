# Diskteam

Простой лаунчер Steam-игр с флешки. Вставил флешку с `SteamID.txt` — появилось чёрное окно 1100×500 с дискетами по центру. Выбрал — игра запустилась через `steam://rungameid`.

Без кэша, без лишнего — только дискеты с названиями.

## Как это работает
1. Программа висит в фоне и опрашивает флешки каждые 1.5с.
2. Ищет в корне флешки файл `SteamID.txt`.
3. Парсит AppID и показывает окно. 1 игра — одна дискета, 2+ — сетка.
4. `Enter`/`клик` — задвигание и `steam://rungameid/<id>`. Если Steam не найден — окно возвращается.

## Формат SteamID.txt
Файл в корне флешки, кодировка UTF-8. Поддерживается:
```
570,730
570
1245620, ELDEN RING
# комментарий, пустые строки игнорируются
```
- Через запятую в одну строку или каждый с новой строки
- `AppID, Название` — название опционально (если нет — тянется из Steam Store API)
- `#` в начале — комментарий
- Кривые ID пропускаются

Где взять AppID: открой игру в Steam → URL `store.steampowered.com/app/570/` → `570` это ID.

## Установка и запуск (Linux)
```bash
git clone https://github.com/ТВОЙ_НИК/Diskteam.git
cd Diskteam
pip install -r requirements.txt  # pygame-ce psutil
python3 main.py                  # ждёт флешку
python3 main.py --test           # тест без флешки (демо)
```

## Установка и запуск (Windows)
```bat
pip install -r requirements.txt
python main.py
:: без консоли:
pythonw main.py
:: автозапуск: Win+R -> shell:startup -> ярлык на pythonw.exe с аргументом diskteam\main.py
```

## Управление
- `↑↓←→` / `WASD` / стик — выбор
- `Enter` / `Space` / `A` / клик — запуск
- `Esc` / `B` — выход
- Колёсико — листание

## Сборка в один файл
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name Diskteam main.py
# Linux: dist/Diskteam
# Windows: dist/Diskteam.exe
```

## Структура проекта
```
Diskteam/
├── main.py        # фон + watcher
├── menu.py        # окно 1100x500, дискеты от середины
├── usb_watcher.py # поиск флешки, парсинг SteamID.txt
├── steam_api.py   # названия из Store API (без кэша)
├── launcher.py    # steam:// запуск
├── config.py      # настройки
└── requirements.txt
```

## Требования
- Python 3.10+
- Steam установлен и запущен
- Linux: композитор не нужен (чёрный фон), Wayland/X11

Лог: `diskteam.log` рядом с `main.py`.
