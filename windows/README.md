# Convertidor NUP — Windows

Versión para Windows del Convertidor NUP, con la misma interfaz y funciones que la de macOS. Escrita en C# (WinForms, .NET 8).

**By AbadXDev**

## Uso

Descarga `Convertidor-NUP-Windows-v1.1.zip` desde la página de [Releases](https://github.com/AbadXDev/convertidor-nup/releases), descomprímelo y ejecuta `ConvertidorNUP.exe`. No necesita instalación: es un único ejecutable autocontenido (no requiere tener .NET instalado).

1. **Elige la carpeta** del juego (botón o arrastrándola a la ventana). La app detecta si es un dump válido, lee el título ID y rellena nombre y versión.
2. **Convierte a .nup** y, si la casilla está marcada, el archivo se verifica (SHA-256) al terminar.

En el primer uso, si la herramienta de empaquetado no está instalada, la app ofrece instalarla con 1 clic (necesita internet, Git y Python 3 desde python.org).

> Nota: Windows puede mostrar el aviso de SmartScreen al ser un ejecutable sin firmar. Pulsa “Más información” → “Ejecutar de todas formas”.

## Compilar desde el código

Requiere el SDK de .NET 8:

```bat
build-windows.bat
```

o directamente:

```bat
dotnet publish ConvertidorNUP.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:EnableCompressionInSingleFile=true -o publish
```

El ejecutable queda en `publish\ConvertidorNUP.exe`.
