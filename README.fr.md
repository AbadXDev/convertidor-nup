<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <strong>Français</strong> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Icône de Convertidor NUP">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  Une application ultra simple pour <b>macOS</b> et <b>Windows</b> qui convertit le <b>dossier</b> d'un dump de jeu Nintendo Switch 2 en un seul fichier de paquet <b><code>.nup</code></b> — en quelques clics seulement. Aucun terminal nécessaire.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="Plateforme">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="Licence">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="Dernière version"></a>
</p>

## Téléchargement

| Système | Téléchargement | Remarques |
| --- | --- | --- |
| **Windows** 10/11 (64 bits) | [Dernière version](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | Décompressez et lancez `ConvertidorNUP.exe`. Un seul fichier autonome, rien à installer. SmartScreen peut vous avertir qu'il s'agit d'une application non signée : *Plus d'infos → Exécuter quand même*. |
| **macOS** 13+ (Apple Silicon) | [Dernière version](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | Signée ad hoc (non notariée) : si macOS la bloque au premier lancement, faites un clic droit sur l'application et choisissez **Ouvrir**. |

Aucune compilation nécessaire — récupérez l'application sur la page des [Releases](https://github.com/AbadXDev/convertidor-nup/releases) et utilisez-la.

## Captures d'écran

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP sous Windows">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP sous macOS">
</p>

<p align="center"><i>Windows · macOS — la même application, le même fonctionnement.</i></p>

## Ce qu'elle fait

1. **Choisissez un dossier** (avec le bouton ou par glisser-déposer) — l'application vérifie la structure du dump (`base/`, `updates/<version>/`, `dlc/`… ou un dossier plat avec `exefs/` + `romfs/`), lit l'**ID de titre** directement depuis `main.npdm`, liste les paquets trouvés et affiche la taille totale.
2. Elle préremplit le **nom** et la **version** du jeu à partir du nom du dossier (par ex. `pokopia_v2-0-1` → « Pokopia », « 2.0.1 ») — vous pouvez les modifier si vous le souhaitez.
3. **Convertissez** — regardez la barre de progression pendant l'empaquetage. Une fois terminé, le `.nup` est vérifié en profondeur (SHA-256) par défaut, pour que vous soyez sûr que le fichier est bon.

Le fichier de sortie se nomme `Name [TitleID].nup` et est enregistré à côté du dossier source (vous pouvez choisir une autre destination).

## Configuration requise

- Windows 10/11 (64 bits) ou macOS 13+ (Apple Silicon).
- Au premier lancement, si l'outil d'empaquetage n'est pas encore installé, l'application l'installe en **un clic** : elle télécharge l'outil open source [`nup`](https://github.com/a55uka/nup) d'a55uka et le configure toute seule. Une connexion internet et **Python 3.10 ou plus récent** sont nécessaires — et si Python est absent, l'application le détecte et vous guide pas à pas pour l'installer.

## Compiler depuis le code source

- **macOS** (SwiftUI) : `./build.sh` — compile l'application, génère l'icône, la signe ad hoc et installe **Convertidor NUP.app** sur votre Bureau et dans `/Applications`.
- **Windows** (C# / WinForms, .NET 8) : voir [`windows/`](windows/) — lancez `windows/build-windows.bat` sous Windows, ou publiez avec `dotnet publish`.

## Crédits et licence

- Application réalisée par **AbadXDev** — Licence MIT (voir `LICENSE`).
- L'empaquetage est effectué par l'outil en ligne de commande [`nup`](https://github.com/a55uka/nup) (MIT), qui n'est **pas** inclus dans cette application ; il est téléchargé lors de la première utilisation.
- Aucune affiliation avec Nintendo. À utiliser uniquement avec des dumps de jeux que vous possédez.
