<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <strong>Русский</strong> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Значок Convertidor NUP">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  Супер простое приложение для <b>macOS</b> и <b>Windows</b>, которое преобразует <b>папку</b> дампа игры Nintendo Switch 2 в один файл пакета <b><code>.nup</code></b> — всего за пару щелчков. Терминал не нужен.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="Платформа">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="Лицензия">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="Последняя версия"></a>
</p>

## Скачать

| Система | Загрузка | Примечания |
| --- | --- | --- |
| **Windows** 10/11 (64-бит) | [Последняя версия](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | Распакуйте и запустите `ConvertidorNUP.exe`. Один автономный файл, устанавливать ничего не нужно. SmartScreen может предупредить о неподписанном приложении: *Подробнее → Выполнить в любом случае*. |
| **macOS** 13+ (Apple Silicon) | [Последняя версия](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | Подписано ad hoc (без нотаризации): если macOS заблокирует приложение при первом запуске, щёлкните по нему правой кнопкой мыши и выберите **Открыть**. |

Компилировать ничего не нужно — возьмите приложение на странице [Releases](https://github.com/AbadXDev/convertidor-nup/releases) и пользуйтесь.

## Снимки экрана

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP в Windows">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP в macOS">
</p>

<p align="center"><i>Windows · macOS — одно и то же приложение, один и тот же порядок действий.</i></p>

## Что оно делает

1. **Выберите папку** (кнопкой или перетаскиванием) — приложение проверяет структуру дампа (`base/`, `updates/<версия>/`, `dlc/`… или плоскую папку с `exefs/` + `romfs/`), считывает **ID заголовка** прямо из `main.npdm`, перечисляет найденные пакеты и показывает общий размер.
2. Оно само заполняет **название** и **версию** игры из имени папки (например, `pokopia_v2-0-1` → «Pokopia», «2.0.1») — при желании их можно изменить.
3. **Преобразуйте** — следите за полосой прогресса во время упаковки. По завершении `.nup` по умолчанию проходит глубокую проверку (SHA-256), чтобы вы были уверены, что файл в порядке.

Выходной файл называется `Name [TitleID].nup` и сохраняется рядом с исходной папкой (можно выбрать другое место).

## Требования

- Windows 10/11 (64-бит) или macOS 13+ (Apple Silicon).
- При первом запуске, если инструмент упаковки ещё не установлен, приложение установит его в **один щелчок**: оно скачает инструмент с открытым исходным кодом [`nup`](https://github.com/a55uka/nup) от a55uka и настроит его самостоятельно. Нужны интернет и **Python 3.10 или новее** — а если Python отсутствует, приложение обнаружит это и шаг за шагом проведёт вас через установку.

## Сборка из исходного кода

- **macOS** (SwiftUI): `./build.sh` — компилирует приложение, создаёт значок, подписывает его ad hoc и устанавливает **Convertidor NUP.app** на рабочий стол и в `/Applications`.
- **Windows** (C# / WinForms, .NET 8): см. [`windows/`](windows/) — выполните `windows/build-windows.bat` в Windows или опубликуйте с помощью `dotnet publish`.

## Авторы и лицензия

- Приложение создано **AbadXDev** — лицензия MIT (см. `LICENSE`).
- Упаковку выполняет инструмент командной строки [`nup`](https://github.com/a55uka/nup) (MIT), который **не** входит в состав этого приложения; он скачивается при первом использовании.
- Не связано с Nintendo. Используйте только с дампами игр, которыми вы владеете.
