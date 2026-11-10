<p align="center">
  <img src="assets/icon.png" width="128" alt="Convertidor NUP icon">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  A super simple app for <b>macOS</b>, <b>Windows</b> and <b>Linux</b> that converts a Nintendo Switch 2 game dump <b>folder</b> into a single <b><code>.nup</code></b> package file — in just a couple of clicks.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11%20%7C%20Linux-blue" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="Latest release"></a>
</p>

## Download

| System | Download | Notes |
| --- | --- | --- |
| **Windows** 10/11 (64-bit) | [Latest release](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | Unzip and run `ConvertidorNUP.exe`. Single self-contained file, nothing to install. SmartScreen may warn about an unsigned app: *More info → Run anyway*. |
| **macOS** 13+ (Apple Silicon) | [Latest release](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | Ad-hoc signed (not notarized): if macOS blocks it the first time, right-click the app and choose **Open**. |
| **Linux** (Python 3.10+) | [Source instructions](linux/README.md) | Run `./linux/run.sh` with Python, Tkinter and venv installed. Optional desktop shortcut. No Linux release binary yet. |

No compiling needed on Windows or macOS — grab the app from the [Releases](https://github.com/AbadXDev/convertidor-nup/releases) page and use it. Linux runs directly from source; see [`linux/`](linux/README.md).

## Screenshots

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP on Windows">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP on macOS">
</p>

<p align="center"><i>Windows · macOS — the same app, the same flow.</i></p>

## What it does

1. **Pick a folder** (button or drag & drop) — the app validates the dump layout (`base/`, `updates/<version>/`, `dlc/`… or a flat `exefs/` + `romfs/` folder), reads the **title ID** straight from `main.npdm`, lists the packages it found and shows the total size.
2. It pre-fills the game **name** and **version** from the folder name (e.g. `pokopia_v2-0-1` → “Pokopia”, “2.0.1”) — edit them if you want.
3. **Convert** — watch the progress bar while it packs. When it finishes, the `.nup` is deep-verified (SHA-256) by default, so you know the file is good.

The output is named `Name [TitleID].nup`, saved next to the source folder (you can choose another destination).

## Requirements

- Windows 10/11 (64-bit), macOS 13+ (Apple Silicon), or a Linux desktop with Python 3.10+, Tkinter and venv support. Linux installation instructions are described in [`linux/README.md`](linux/README.md).
- On first run, if the packing tool is not installed yet, the app installs it with **one click**: it downloads the open-source [`nup`](https://github.com/a55uka/nup) tool by a55uka and sets it up on its own. It needs internet and **Python 3.10 or later** — and if Python is missing, the app detects it and walks you through installing it, step by step.

## Build from source

- **macOS** (SwiftUI): `./build.sh` — compiles the app, generates the icon, signs it ad hoc and installs **Convertidor NUP.app** on your Desktop and in `/Applications`.
- **Windows** (C# / WinForms, .NET 8): see [`windows/`](windows/) — run `windows/build-windows.bat` on Windows, or publish with `dotnet publish`.
- **Linux** (Python / Tkinter): `./linux/run.sh` — no compilation required. See [`linux/README.md`](linux/README.md) for dependencies, the optional desktop shortcut and tests. Linux uses the folder picker rather than drag & drop.

## Credits & license

- App by **AbadXDev** — MIT License (see `LICENSE`).
- Packing is done by the [`nup`](https://github.com/a55uka/nup) command-line tool (MIT), which is **not** bundled with this app; it's downloaded on first use.
- Not affiliated with Nintendo. Use it only with dumps of games you own.

---

## En español

Una app súper fácil, para **macOS, Windows y Linux**, que convierte la **carpeta** de un dump de juego de Switch 2 en un solo archivo **`.nup`**, con muy pocos clics.

1. **Elige la carpeta** (botón o arrastrándola): la app comprueba que sea un dump válido, lee el **título ID** del propio juego, te dice qué paquetes trae (base, updates, DLC) y cuánto ocupa.
2. Rellena sola el **nombre** y la **versión** desde el nombre de la carpeta; puedes corregirlos.
3. **Convierte**: barra de progreso en vivo y, al terminar, verificación completa (SHA-256) del archivo generado.

Requisitos: Windows 10/11 (64 bits), macOS 13 o superior (Apple Silicon), o Linux con Python 3.10+, Tkinter y soporte para entornos virtuales. Si falta la herramienta de empaquetado, la app la instala con 1 clic en el primer uso (requiere internet). Para instalar los requisitos de Linux, consulta [la guía de Linux](linux/README.md).

Descarga: página de [Releases](https://github.com/AbadXDev/convertidor-nup/releases) (zip de Windows o de Mac, según tu sistema).

En Linux se ejecuta desde el código con `./linux/run.sh`; todavía no hay binario Linux en Releases. La interfaz permite elegir carpetas, editar nombre y versión, ver el progreso, cancelar y verificar el resultado. No incluye arrastrar y soltar.

Hecho por **AbadXDev** · Licencia MIT · Sin afiliación con Nintendo; úsalo solo con dumps de tus propios juegos.
