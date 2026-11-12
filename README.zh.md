<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <strong>简体中文</strong> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Convertidor NUP 图标">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  一款适用于 <b>macOS</b> 和 <b>Windows</b> 的超简单应用，可将 Nintendo Switch 2 游戏转储<b>文件夹</b>转换为单个 <b><code>.nup</code></b> 包文件 — 只需点击几下即可。无需使用终端。
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="平台">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="许可证">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="最新版本"></a>
</p>

## 下载

| 系统 | 下载 | 说明 |
| --- | --- | --- |
| **Windows** 10/11（64 位） | [最新版本](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | 解压并运行 `ConvertidorNUP.exe`。单个自包含文件，无需安装。SmartScreen 可能会警告这是一个未签名的应用：选择*更多信息 → 仍要运行*。 |
| **macOS** 13+（Apple Silicon） | [最新版本](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | 临时签名（未公证）：如果首次运行时被 macOS 阻止，请右键点击该应用并选择**打开**。 |

无需编译 — 直接从 [Releases](https://github.com/AbadXDev/convertidor-nup/releases) 页面下载应用即可使用。

## 截图

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP 在 Windows 上">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP 在 macOS 上">
</p>

<p align="center"><i>Windows · macOS — 同一款应用，相同的流程。</i></p>

## 功能

1. **选择文件夹**（点击按钮或拖放）— 应用会验证转储的布局（`base/`、`updates/<版本>/`、`dlc/`……或带有 `exefs/` + `romfs/` 的扁平文件夹），直接从 `main.npdm` 读取**标题 ID**，列出找到的软件包并显示总大小。
2. 它会根据文件夹名称预填游戏**名称**和**版本**（例如 `pokopia_v2-0-1` → “Pokopia”、“2.0.1”）— 你可以自行编辑。
3. **转换** — 观看打包时的进度条。完成后，`.nup` 默认会进行深度验证（SHA-256），让你确信文件没有问题。

输出文件名为 `Name [TitleID].nup`，保存在源文件夹旁边（你也可以选择其他保存位置）。

## 系统要求

- Windows 10/11（64 位）或 macOS 13+（Apple Silicon）。
- 首次运行时，如果打包工具尚未安装，应用会**一键**安装它：下载 a55uka 的开源 [`nup`](https://github.com/a55uka/nup) 工具并自动完成配置。需要网络连接和 **Python 3.10 或更高版本** — 如果缺少 Python，应用会检测到并一步步引导你完成安装。

## 从源代码构建

- **macOS**（SwiftUI）：`./build.sh` — 编译应用、生成图标、进行临时签名，并将 **Convertidor NUP.app** 安装到你的桌面和 `/Applications`。
- **Windows**（C# / WinForms，.NET 8）：见 [`windows/`](windows/) — 在 Windows 上运行 `windows/build-windows.bat`，或使用 `dotnet publish` 发布。

## 制作与许可

- 应用由 **AbadXDev** 制作 — MIT 许可证（见 `LICENSE`）。
- 打包由 [`nup`](https://github.com/a55uka/nup) 命令行工具（MIT）完成，该工具**不**包含在此应用中：首次使用时会自动下载。
- 与任天堂无关。请仅与你自己拥有的游戏转储一起使用。
