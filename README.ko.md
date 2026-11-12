<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <strong>한국어</strong> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Convertidor NUP 아이콘">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  Nintendo Switch 2 게임 덤프 <b>폴더</b>를 단 몇 번의 클릭으로 하나의 <b><code>.nup</code></b> 패키지 파일로 변환하는 <b>macOS</b> 및 <b>Windows</b>용 초간단 앱입니다. 터미널이 필요 없습니다.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="플랫폼">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="라이선스">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="최신 릴리스"></a>
</p>

## 다운로드

| 시스템 | 다운로드 | 참고 |
| --- | --- | --- |
| **Windows** 10/11(64비트) | [최신 릴리스](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | 압축을 풀고 `ConvertidorNUP.exe`를 실행하세요. 단일 자체 포함 파일로, 설치할 것이 없습니다. SmartScreen이 서명되지 않은 앱이라고 경고할 수 있습니다: *추가 정보 → 그래도 실행*. |
| **macOS** 13+(Apple Silicon) | [최신 릴리스](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | 임시 서명(공증 없음): 처음 실행할 때 macOS가 차단하면 앱을 마우스 오른쪽 버튼으로 클릭하고 **열기**를 선택하세요. |

컴파일할 필요 없습니다 — [Releases](https://github.com/AbadXDev/convertidor-nup/releases) 페이지에서 앱을 받아 바로 사용하세요.

## 스크린샷

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Windows에서의 Convertidor NUP">
  <img src="assets/mac.png" width="49%" alt="macOS에서의 Convertidor NUP">
</p>

<p align="center"><i>Windows · macOS — 같은 앱, 같은 흐름.</i></p>

## 기능

1. **폴더 선택**(버튼 또는 드래그 앤 드롭) — 앱이 덤프 레이아웃(`base/`, `updates/<version>/`, `dlc/`… 또는 `exefs/` + `romfs/`가 있는 플랫 폴더)을 검증하고, `main.npdm`에서 **타이틀 ID**를 바로 읽어, 찾은 패키지를 나열하고 전체 크기를 보여줍니다.
2. 폴더 이름에서 게임 **이름**과 **버전**을 자동으로 채웁니다(예: `pokopia_v2-0-1` → “Pokopia”, “2.0.1”) — 원하면 편집할 수 있습니다.
3. **변환** — 패키징하는 동안 진행률 막대를 지켜보세요. 완료되면 `.nup`이 기본적으로 정밀 검증(SHA-256)되므로 파일이 정상임을 알 수 있습니다.

출력 파일 이름은 `Name [TitleID].nup`이며 원본 폴더 옆에 저장됩니다(다른 위치를 선택할 수도 있습니다).

## 요구 사항

- Windows 10/11(64비트) 또는 macOS 13+(Apple Silicon).
- 처음 실행할 때 패키징 도구가 아직 설치되어 있지 않으면, 앱이 **한 번의 클릭**으로 설치합니다: a55uka의 오픈 소스 [`nup`](https://github.com/a55uka/nup) 도구를 다운로드해 스스로 설정합니다. 인터넷과 **Python 3.10 이상**이 필요합니다 — Python이 없으면 앱이 이를 감지해 설치 과정을 단계별로 안내합니다.

## 소스에서 빌드

- **macOS**(SwiftUI): `./build.sh` — 앱을 컴파일하고, 아이콘을 생성하고, 임시 서명한 뒤 **Convertidor NUP.app**을 바탕 화면과 `/Applications`에 설치합니다.
- **Windows**(C# / WinForms, .NET 8): [`windows/`](windows/) 참고 — Windows에서 `windows/build-windows.bat`를 실행하거나 `dotnet publish`로 게시하세요.

## 제작 및 라이선스

- 앱 제작: **AbadXDev** — MIT 라이선스(`LICENSE` 참고).
- 패키징은 명령줄 도구 [`nup`](https://github.com/a55uka/nup)(MIT)이 수행합니다. 이 도구는 이 앱에 **포함되어 있지 않으며**, 처음 사용할 때 다운로드됩니다.
- Nintendo와 관련이 없습니다. 본인이 소유한 게임의 덤프로만 사용하세요.
