<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <strong>日本語</strong> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Convertidor NUP のアイコン">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  Nintendo Switch 2 のゲームダンプの<b>フォルダ</b>を、わずか数クリックで単一の <b><code>.nup</code></b> パッケージファイルに変換する、<b>macOS</b> と <b>Windows</b> 向けの超シンプルなアプリです。ターミナルは不要です。
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="プラットフォーム">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="ライセンス">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="最新リリース"></a>
</p>

## ダウンロード

| システム | ダウンロード | 備考 |
| --- | --- | --- |
| **Windows** 10/11（64 ビット） | [最新リリース](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | 解凍して `ConvertidorNUP.exe` を実行します。単一の自己完結型ファイルで、インストールは不要です。SmartScreen が署名されていないアプリだと警告する場合があります：*詳細情報 → 実行*。 |
| **macOS** 13+（Apple Silicon） | [最新リリース](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | アドホック署名（公証なし）：初回起動時に macOS にブロックされた場合は、アプリを右クリックして **開く** を選択してください。 |

コンパイルは不要です — [Releases](https://github.com/AbadXDev/convertidor-nup/releases) ページからアプリを入手して、そのままお使いください。

## スクリーンショット

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Windows 上の Convertidor NUP">
  <img src="assets/mac.png" width="49%" alt="macOS 上の Convertidor NUP">
</p>

<p align="center"><i>Windows · macOS — 同じアプリ、同じ流れ。</i></p>

## できること

1. **フォルダを選ぶ**（ボタンまたはドラッグ＆ドロップ）— アプリがダンプのレイアウト（`base/`、`updates/<version>/`、`dlc/`…、または `exefs/` + `romfs/` のフラットなフォルダ）を検証し、`main.npdm` から**タイトル ID** を直接読み取り、見つかったパッケージを一覧表示して合計サイズを示します。
2. フォルダ名からゲームの**名前**と**バージョン**を自動入力します（例：`pokopia_v2-0-1` → 「Pokopia」、「2.0.1」）— 必要に応じて編集できます。
3. **変換** — パッキング中のプログレスバーを確認できます。完了すると、`.nup` はデフォルトで詳細検証（SHA-256）されるので、ファイルが正常であることが分かります。

出力ファイルの名前は `Name [TitleID].nup` で、元のフォルダの隣に保存されます（保存先は変更できます）。

## 動作環境

- Windows 10/11（64 ビット）または macOS 13+（Apple Silicon）。
- 初回起動時に、パッキングツールがまだインストールされていない場合、アプリが**ワンクリック**でインストールします：a55uka によるオープンソースの [`nup`](https://github.com/a55uka/nup) ツールをダウンロードし、自動でセットアップします。インターネット接続と **Python 3.10 以降** が必要です — Python が不足している場合、アプリがそれを検出し、インストール手順をステップごとに案内します。

## ソースからビルド

- **macOS**（SwiftUI）：`./build.sh` — アプリをコンパイルし、アイコンを生成し、アドホック署名して、**Convertidor NUP.app** をデスクトップと `/Applications` にインストールします。
- **Windows**（C# / WinForms、.NET 8）：[`windows/`](windows/) を参照 — Windows で `windows/build-windows.bat` を実行するか、`dotnet publish` で発行します。

## クレジットとライセンス

- アプリ制作：**AbadXDev** — MIT ライセンス（`LICENSE` を参照）。
- パッキングはコマンドラインツール [`nup`](https://github.com/a55uka/nup)（MIT）が行います。このツールは本アプリには**含まれておらず**、初回使用時にダウンロードされます。
- Nintendo とは関係ありません。ご自身が所有するゲームのダンプでのみご使用ください。
