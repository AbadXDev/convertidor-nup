<p align="center">
  🌐 <a href="README.md">English</a> · <a href="README.es.md">Español</a> · <a href="README.fr.md">Français</a> · <strong>Italiano</strong> · <a href="README.pt.md">Português</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.zh.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="assets/icon.png" width="128" alt="Icona di Convertidor NUP">
</p>

<h1 align="center">Convertidor NUP</h1>

<p align="center"><b>By AbadXDev</b></p>

<p align="center">
  Un'app semplicissima per <b>macOS</b> e <b>Windows</b> che converte la <b>cartella</b> di un dump di un gioco Nintendo Switch 2 in un unico file pacchetto <b><code>.nup</code></b> — con appena un paio di clic. Nessun terminale necessario.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-macOS%2013%2B%20%7C%20Windows%2010%2F11-blue" alt="Piattaforma">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="Licenza">
  <a href="https://github.com/AbadXDev/convertidor-nup/releases/latest"><img src="https://img.shields.io/github/v/release/AbadXDev/convertidor-nup" alt="Ultima versione"></a>
</p>

## Download

| Sistema | Download | Note |
| --- | --- | --- |
| **Windows** 10/11 (64 bit) | [Ultima versione](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Windows-….zip` | Estrai ed esegui `ConvertidorNUP.exe`. Un unico file autonomo, niente da installare. SmartScreen potrebbe avvisare che si tratta di un'app non firmata: *Ulteriori informazioni → Esegui comunque*. |
| **macOS** 13+ (Apple Silicon) | [Ultima versione](https://github.com/AbadXDev/convertidor-nup/releases/latest) → `Convertidor-NUP-Mac-….zip` | Firmata ad hoc (non autenticata): se macOS la blocca al primo avvio, fai clic destro sull'app e scegli **Apri**. |

Nessuna compilazione necessaria: scarica l'app dalla pagina delle [Releases](https://github.com/AbadXDev/convertidor-nup/releases) e usala.

## Schermate

<p align="center">
  <img src="assets/windows.jpg?v=2" width="49%" alt="Convertidor NUP su Windows">
  <img src="assets/mac.png" width="49%" alt="Convertidor NUP su macOS">
</p>

<p align="center"><i>Windows · macOS — la stessa app, lo stesso procedimento.</i></p>

## Cosa fa

1. **Scegli una cartella** (con il pulsante o trascinandola): l'app verifica la struttura del dump (`base/`, `updates/<versione>/`, `dlc/`… oppure una cartella piatta con `exefs/` + `romfs/`), legge l'**ID del titolo** direttamente da `main.npdm`, elenca i pacchetti trovati e mostra la dimensione totale.
2. Compila automaticamente il **nome** e la **versione** del gioco a partire dal nome della cartella (es. `pokopia_v2-0-1` → “Pokopia”, “2.0.1”): puoi modificarli se vuoi.
3. **Converti**: osserva la barra di avanzamento durante la creazione del pacchetto. Al termine, il `.nup` viene verificato in profondità (SHA-256) per impostazione predefinita, così sai che il file è buono.

Il file risultante si chiama `Name [TitleID].nup` e viene salvato accanto alla cartella di origine (puoi scegliere un'altra destinazione).

## Requisiti

- Windows 10/11 (64 bit) oppure macOS 13+ (Apple Silicon).
- Al primo avvio, se lo strumento di creazione dei pacchetti non è ancora installato, l'app lo installa con **un clic**: scarica lo strumento open source [`nup`](https://github.com/a55uka/nup) di a55uka e lo configura da sola. Servono una connessione internet e **Python 3.10 o versioni successive** — e se Python manca, l'app lo rileva e ti guida passo dopo passo nell'installazione.

## Compilare dal codice sorgente

- **macOS** (SwiftUI): `./build.sh` — compila l'app, genera l'icona, la firma ad hoc e installa **Convertidor NUP.app** sulla Scrivania e in `/Applications`.
- **Windows** (C# / WinForms, .NET 8): vedi [`windows/`](windows/) — esegui `windows/build-windows.bat` su Windows, oppure pubblica con `dotnet publish`.

## Crediti e licenza

- App realizzata da **AbadXDev** — Licenza MIT (vedi `LICENSE`).
- La creazione dei pacchetti è effettuata dallo strumento a riga di comando [`nup`](https://github.com/a55uka/nup) (MIT), che **non** è incluso in questa app: viene scaricato al primo utilizzo.
- Nessuna affiliazione con Nintendo. Usala solo con dump di giochi che possiedi.
