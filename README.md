# Convertidor NUP

**By AbadXDev**

A super simple, native macOS app to convert a Nintendo Switch 2 game dump **folder** into a single **`.nup`** package file — in just a couple of clicks. No terminal needed.

![Platform](https://img.shields.io/badge/platform-macOS%2013%2B%20(Apple%20Silicon)-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Download

Grab the ready-to-use app from the [**Releases**](https://github.com/AbadXDev/convertidor-nup/releases) page — no compiling needed. The app is ad-hoc signed (not notarized): if macOS blocks it the first time, right-click the app and choose Open.

Descarga la app lista para usar desde la página de [**Releases**](https://github.com/AbadXDev/convertidor-nup/releases), sin compilar. Está firmada ad hoc (sin notarizar): si macOS la bloquea la primera vez, haz clic derecho sobre la app y elige Abrir.

## What it does

1. **Pick a folder** (button or drag & drop) — the app validates the dump layout (`base/`, `updates/<version>/`, `dlc/`… or a flat `exefs/` + `romfs/` folder), reads the **title ID** straight from `main.npdm`, lists the packages it found and shows the total size.
2. It pre-fills the game **name** and **version** from the folder name (e.g. `pokopia_v2-0-1` → “Pokopia”, “2.0.1”) — edit them if you want.
3. **Convert** — watch the progress bar while it packs. When it finishes, the `.nup` is deep-verified (SHA-256) by default, so you know the file is good.

The output is named `Name [TitleID].nup`, saved next to the source folder (you can choose another destination).

## Requirements

- macOS 13 or later, Apple Silicon
- On first run, if the packing tool is not installed yet, the app offers to install it with **one click** (it downloads the open-source [`nup`](https://github.com/a55uka/nup) tool by a55uka into `~/nup-tool` with a Python venv in `~/.venvs/nup`). Needs internet and Python 3.10+ (e.g. `brew install python@3.12`).

## Build from source

```bash
./build.sh
```

This compiles the SwiftUI app with `swiftc`, generates the icon, signs it ad hoc and installs **Convertidor NUP.app** on your Desktop and in `/Applications`.

## Credits & license

- App by **AbadXDev** — MIT License (see `LICENSE`).
- Packing is done by the [`nup`](https://github.com/a55uka/nup) command-line tool (MIT), which is **not** bundled with this app; it's downloaded on first use.
- Not affiliated with Nintendo. Use it only with dumps of games you own.

---

## En español

Una app nativa de macOS, súper fácil, para convertir la **carpeta** de un dump de juego de Switch 2 en un solo archivo **`.nup`**, con muy pocos clics y sin tocar la terminal.

1. **Elige la carpeta** (botón o arrastrándola): la app comprueba que sea un dump válido, lee el **título ID** del propio juego, te dice qué paquetes trae (base, updates, DLC) y cuánto ocupa.
2. Rellena sola el **nombre** y la **versión** desde el nombre de la carpeta; puedes corregirlos.
3. **Convierte**: barra de progreso en vivo y, al terminar, verificación completa (SHA-256) del archivo generado.

Requisitos: macOS 13 o superior (Apple Silicon). Si la herramienta de empaquetado no está instalada, la app la instala con 1 clic en el primer uso.

Compilar: `./build.sh` — genera e instala `Convertidor NUP.app` en el Escritorio y en `/Applications`.

Hecho por **AbadXDev** · Licencia MIT · Sin afiliación con Nintendo; úsalo solo con dumps de tus propios juegos.
