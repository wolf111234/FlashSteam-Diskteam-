# Diskteam

Простой лаунчер Steam-игр с флешки. Вставил флешку с `SteamID.txt` — чёрное окно 1100×500 с дискетами по центру. Выбор — запуск через `steam://rungameid`.

Simple Steam launcher from USB. Plug flash with `SteamID.txt` — 1100×500 black window with floppies centered. Select — launch via `steam://rungameid`.

---

## 🇷🇺 Русская инструкция

### Как работает
1. Висит в фоне, опрос флешек 1.5с
2. Ищет `SteamID.txt` в корне флешки
3. Парсит AppID → окно (1 игра — дискета, 2+ — сетка от середины)
4. `Enter`/клик → задвигание → `steam://rungameid/<id>`. Если Steam не найден — возврат.

### Формат SteamID.txt (UTF-8, корень флешки)
```
570,730
570
1245620, ELDEN RING
# комментарий
```
- Через запятую или с новой строки
- `AppID, Название` — название опционально (тянется из Store API)
- `#` — комментарий
- Где взять ID: `store.steampowered.com/app/570/` → `570`

### Установка Linux
```bash
git clone https://github.com/ТВОЙ_НИК/Diskteam.git
cd Diskteam
pip install -r requirements.txt  # pygame-ce psutil
python3 main.py                  # ждёт флешку
python3 main.py --test           # тест без флешки
```

### Установка Windows(BETA)
```bat
pip install -r requirements.txt
python main.py
pythonw main.py  :: без консоли
:: автозапуск: Win+R -> shell:startup -> ярлык на pythonw.exe + Diskteam\main.py
```

### Управление
`↑↓←→/WASD/стик` — выбор, `Enter/Space/A/клик` — запуск, `Esc/B` — выход, колёсико — листание

### Сборка
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name Diskteam main.py
# Linux: dist/Diskteam  Windows: dist/Diskteam.exe
```

### Структура
```
Diskteam/
├── main.py | menu.py | usb_watcher.py | steam_api.py | launcher.py | config.py
└── windows(Test)/  # копия для теста на Windows VM
```

---

## 🇬🇧 English Guide

### How it works
1. Runs in background, polls USB every 1.5s
2. Looks for `SteamID.txt` in flash root
3. Parses AppIDs → 1100×500 window centered (1 game — floppy, 2+ — grid)
4. `Enter`/click → slide down → `steam://rungameid/<id>`. If Steam not found — returns.

### SteamID.txt format (UTF-8, flash root)
```
570,730
570
1245620, ELDEN RING
# comment
```
- Comma-separated or one per line
- `AppID, Name` — name optional (fetched from Store API)
- `#` — comment
- Get AppID: `store.steampowered.com/app/570/` → `570`

### Setup Linux
```bash
git clone https://github.com/YOUR_NICK/Diskteam.git
cd Diskteam
pip install -r requirements.txt
python3 main.py         # wait for flash
python3 main.py --test  # demo without flash
```

### Setup Windows(BETA)
```bat
pip install -r requirements.txt
python main.py
pythonw main.py  :: no console
:: autostart: Win+R -> shell:startup -> shortcut to pythonw.exe + Diskteam\main.py
```

### Controls
`Arrows/WASD/stick` — navigate, `Enter/Space/A/click` — launch, `Esc/B` — exit, wheel — scroll

### Build
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name Diskteam main.py
```

### Requirements
Python 3.10+, Steam installed, `cache/` for covers/names.

Log: `diskteam.log`
