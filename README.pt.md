<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <a href="README.it.md">Italiano</a> · <strong>Português</strong> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Ícone do Convertidor NUP">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  Uma aplicação super simples para <b>macOS</b> e <b>Windows</b> que converte a <b>pasta</b> de um dump de jogo da Nintendo Switch 2 num único ficheiro de pacote <b><code>.nup</code></b> — com apenas alguns cliques. Sem necessidade de terminal.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="Plataforma">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="Licença">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="Versão mais recente"></a>
</p>

## Transferir

| Sistema | Transferência | Notas |
| --- | --- | --- |
| **Windows** 10/11 (64 bits) | [Versão mais recente](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | Extraia e execute `ConvertidorNUP.exe`. Um único ficheiro autónomo, nada para instalar. O SmartScreen pode avisar que é uma aplicação não assinada: *Mais informações → Executar mesmo assim*. |
| **macOS** 13+ (Apple Silicon) | [Versão mais recente](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | Assinatura ad hoc (sem notarização): se o macOS a bloquear na primeira vez, clique com o botão direito na aplicação e escolha **Abrir**. |

Não é preciso compilar nada — obtenha a aplicação na página de [Releases](https://github.com/AbadXDev/convertidor-nup/releases) e utilize-a.

## Capturas de ecrã

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP no Windows">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP no macOS">
</p>

<p align="center"><i>Windows · macOS — a mesma aplicação, o mesmo fluxo.</i></p>

## O que faz

1. **Escolha uma pasta** (com o botão ou arrastando-a) — a aplicação valida a estrutura do dump (`base/`, `updates/<versão>/`, `dlc/`… ou uma pasta plana com `exefs/` + `romfs/`), lê o **ID do título** diretamente do `main.npdm`, lista os pacotes encontrados e mostra o tamanho total.
2. Preenche automaticamente o **nome** e a **versão** do jogo a partir do nome da pasta (p. ex. `pokopia_v2-0-1` → “Pokopia”, “2.0.1”) — edite-os se quiser.
3. **Converta** — acompanhe a barra de progresso enquanto empacota. Quando termina, o `.nup` é verificado em profundidade (SHA-256) por predefinição, para saber que o ficheiro está bom.

O ficheiro resultante chama-se `Name [TitleID].nup` e é guardado ao lado da pasta de origem (pode escolher outro destino).

## Requisitos

- Windows 10/11 (64 bits) ou macOS 13+ (Apple Silicon).
- Na primeira execução, se a ferramenta de empacotamento ainda não estiver instalada, a aplicação instala-a com **um clique**: transfere a ferramenta de código aberto [`nup`](https://github.com/a55uka/nup) de a55uka e configura-a sozinha. Precisa de internet e do **Python 3.10 ou posterior** — e, se o Python estiver em falta, a aplicação deteta-o e guia-o passo a passo na instalação.

## Compilar a partir do código-fonte

- **macOS** (SwiftUI): `./build.sh` — compila a aplicação, gera o ícone, assina-a ad hoc e instala **Convertidor NUP.app** na sua Área de Trabalho e em `/Applications`.
- **Windows** (C# / WinForms, .NET 8): veja [`windows/`](windows/) — execute `windows/build-windows.bat` no Windows, ou publique com `dotnet publish`.

## Créditos e licença

- Aplicação de **AbadXDev** — Licença MIT (ver `LICENSE`).
- O empacotamento é feito pela ferramenta de linha de comandos [`nup`](https://github.com/a55uka/nup) (MIT), que **não** vem incluída nesta aplicação; é transferida na primeira utilização.
- Sem qualquer afiliação com a Nintendo. Utilize apenas com dumps de jogos que possui.
