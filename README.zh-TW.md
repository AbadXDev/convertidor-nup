<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <strong>繁體中文</strong>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Convertidor NUP 圖示">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  一款適用於 <b>macOS</b> 和 <b>Windows</b> 的超簡單應用程式，可將 Nintendo Switch 2 遊戲傾印<b>資料夾</b>轉換為單一 <b><code>.nup</code></b> 套件檔案 — 只需點擊幾下即可。無需使用終端機。
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="平台">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="授權">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="最新版本"></a>
</p>

## 下載

| 系統 | 下載 | 說明 |
| --- | --- | --- |
| **Windows** 10/11（64 位元） | [最新版本](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | 解壓縮並執行 `ConvertidorNUP.exe`。單一獨立檔案，無需安裝。SmartScreen 可能會警告這是一個未簽署的應用程式：選擇*更多資訊 → 仍要執行*。 |
| **macOS** 13+（Apple Silicon） | [最新版本](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | 臨時簽署（未公證）：如果首次執行時被 macOS 阻止，請右鍵點擊該應用程式並選擇**開啟**。 |

無需編譯 — 直接從 [Releases](https://github.com/AbadXDev/convertidor-nup/releases) 頁面下載應用程式即可使用。

## 截圖

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP 在 Windows 上">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP 在 macOS 上">
</p>

<p align="center"><i>Windows · macOS — 同一款應用程式，相同的流程。</i></p>

## 功能

1. **選擇資料夾**（點擊按鈕或拖放）— 應用程式會驗證傾印的版面配置（`base/`、`updates/<版本>/`、`dlc/`……或帶有 `exefs/` + `romfs/` 的扁平資料夾），直接從 `main.npdm` 讀取**標題 ID**，列出找到的套件並顯示總大小。
2. 它會根據資料夾名稱預填遊戲**名稱**和**版本**（例如 `pokopia_v2-0-1` → 「Pokopia」、「2.0.1」）— 您可以自行編輯。
3. **轉換** — 觀看打包時的進度列。完成後，`.nup` 預設會進行深度驗證（SHA-256），讓您確信檔案沒有問題。

輸出檔案名為 `Name [TitleID].nup`，儲存在來源資料夾旁邊（您也可以選擇其他儲存位置）。

## 系統需求

- Windows 10/11（64 位元）或 macOS 13+（Apple Silicon）。
- 首次執行時，如果打包工具尚未安裝，應用程式會**一鍵**安裝它：下載 a55uka 的開源 [`nup`](https://github.com/a55uka/nup) 工具並自動完成設定。需要網路連線和 **Python 3.10 或更高版本** — 如果缺少 Python，應用程式會偵測到並一步步引導您完成安裝。

## 從原始碼建置

- **macOS**（SwiftUI）：`./build.sh` — 編譯應用程式、產生圖示、進行臨時簽署，並將 **Convertidor NUP.app** 安裝到您的桌面和 `/Applications`。
- **Windows**（C# / WinForms，.NET 8）：見 [`windows/`](windows/) — 在 Windows 上執行 `windows/build-windows.bat`，或使用 `dotnet publish` 發佈。

## 製作與授權

- 應用程式由 **AbadXDev** 製作 — MIT 授權（見 `LICENSE`）。
- 打包由 [`nup`](https://github.com/a55uka/nup) 命令列工具（MIT）完成，該工具**不**包含在此應用程式中：首次使用時會自動下載。
- 與任天堂無關。請僅與您自己擁有的遊戲傾印一起使用。
