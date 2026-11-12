<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <strong>Deutsch</strong> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Convertidor NUP Symbol">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  Eine super einfache App für <b>macOS</b> und <b>Windows</b>, die den <b>Ordner</b> eines Nintendo Switch 2-Spieledumps in eine einzige <b><code>.nup</code></b>-Paketdatei umwandelt — mit nur wenigen Klicks. Kein Terminal nötig.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="Plattform">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="Lizenz">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="Neueste Version"></a>
</p>

## Download

| System | Download | Hinweise |
| --- | --- | --- |
| **Windows** 10/11 (64-Bit) | [Neueste Version](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | Entpacken und `ConvertidorNUP.exe` ausführen. Eine einzige eigenständige Datei, nichts zu installieren. SmartScreen warnt möglicherweise vor einer nicht signierten App: *Weitere Informationen → Trotzdem ausführen*. |
| **macOS** 13+ (Apple Silicon) | [Neueste Version](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | Ad-hoc-signiert (nicht notarisiert): Wenn macOS sie beim ersten Mal blockiert, klicken Sie mit der rechten Maustaste auf die App und wählen Sie **Öffnen**. |

Keine Kompilierung nötig — holen Sie sich die App auf der [Releases](https://github.com/AbadXDev/convertidor-nup/releases)-Seite und nutzen Sie sie.

## Screenshots

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP unter Windows">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP unter macOS">
</p>

<p align="center"><i>Windows · macOS — dieselbe App, derselbe Ablauf.</i></p>

## Was sie tut

1. **Ordner auswählen** (per Schaltfläche oder per Drag & Drop) — die App prüft das Layout des Dumps (`base/`, `updates/<version>/`, `dlc/`… oder ein flacher Ordner mit `exefs/` + `romfs/`), liest die **Titel-ID** direkt aus `main.npdm`, listet die gefundenen Pakete auf und zeigt die Gesamtgröße an.
2. Sie füllt den **Namen** und die **Version** des Spiels aus dem Ordnernamen vorab aus (z. B. `pokopia_v2-0-1` → „Pokopia“, „2.0.1“) — Sie können sie nach Wunsch bearbeiten.
3. **Umwandeln** — verfolgen Sie den Fortschrittsbalken beim Packen. Wenn sie fertig ist, wird die `.nup` standardmäßig tiefenprüft (SHA-256), damit Sie wissen, dass die Datei in Ordnung ist.

Die Ausgabedatei heißt `Name [TitleID].nup` und wird neben dem Quellordner gespeichert (Sie können ein anderes Ziel wählen).

## Voraussetzungen

- Windows 10/11 (64-Bit) oder macOS 13+ (Apple Silicon).
- Beim ersten Start installiert die App das Packwerkzeug, falls es noch nicht installiert ist, mit **einem Klick**: Sie lädt das Open-Source-Werkzeug [`nup`](https://github.com/a55uka/nup) von a55uka herunter und richtet es selbst ein. Sie braucht Internet und **Python 3.10 oder neuer** — und wenn Python fehlt, erkennt die App das und führt Sie Schritt für Schritt durch die Installation.

## Aus dem Quellcode bauen

- **macOS** (SwiftUI): `./build.sh` — kompiliert die App, erzeugt das Symbol, signiert sie ad hoc und installiert **Convertidor NUP.app** auf Ihrem Schreibtisch und in `/Applications`.
- **Windows** (C# / WinForms, .NET 8): siehe [`windows/`](windows/) — führen Sie `windows/build-windows.bat` unter Windows aus, oder veröffentlichen Sie mit `dotnet publish`.

## Mitwirkende & Lizenz

- App von **AbadXDev** — MIT-Lizenz (siehe `LICENSE`).
- Das Packen übernimmt das Kommandozeilenwerkzeug [`nup`](https://github.com/a55uka/nup) (MIT), das **nicht** in dieser App enthalten ist; es wird bei der ersten Verwendung heruntergeladen.
- Keine Verbindung zu Nintendo. Nur mit Dumps von Spielen verwenden, die Sie besitzen.
