<p align="center">
  🌐 <strong>English</strong> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Convertidor NUP icon">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  A super simple app for <b>macOS</b> and <b>Windows</b> that converts a Nintendo Switch 2 game dump <b>folder</b> into a single <b><code>.nup</code></b> package file — in just a couple of clicks. No terminal needed.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="Latest release"></a>
</p>

## Download

| System | Download | Notes |
| --- | --- | --- |
| **Windows** 10/11 (64-bit) | [Latest release](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | Unzip and run `ConvertidorNUP.exe`. Single self-contained file, nothing to install. SmartScreen may warn about an unsigned app: *More info → Run anyway*. |
| **macOS** 13+ (Apple Silicon) | [Latest release](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | Ad-hoc signed (not notarized): if macOS blocks it the first time, right-click the app and choose **Open**. |

No compiling needed — grab the app from the [Releases](https://github.com/AbadXDev/convertidor-nup/releases) page and use it.

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

- Windows 10/11 (64-bit) or macOS 13+ (Apple Silicon).
- On first run, if the packing tool is not installed yet, the app installs it with **one click**: it downloads the open-source [`nup`](https://github.com/a55uka/nup) tool by a55uka and sets it up on its own. It needs internet and **Python 3.10 or later** — and if Python is missing, the app detects it and walks you through installing it, step by step.

## Build from source

- **macOS** (SwiftUI): `./build.sh` — compiles the app, generates the icon, signs it ad hoc and installs **Convertidor NUP.app** on your Desktop and in `/Applications`.
- **Windows** (C# / WinForms, .NET 8): see [`windows/`](windows/) — run `windows/build-windows.bat` on Windows, or publish with `dotnet publish`.

## Credits & license

- App by **AbadXDev** — MIT License (see `LICENSE`).
- Packing is done by the [`nup`](https://github.com/a55uka/nup) command-line tool (MIT), which is **not** bundled with this app; it's downloaded on first use.
- Not affiliated with Nintendo. Use it only with dumps of games you own.
