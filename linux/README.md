# Convertidor NUP — Linux

Interfaz gráfica en Python/Tkinter para el mismo empaquetador [nup](https://github.com/a55uka/nup) de las versiones de macOS y Windows. **By AbadXDev**, con soporte Linux de colaboradores.

Esta versión se ejecuta desde el código fuente: todavía no hay un binario Linux en Releases. Requiere una sesión de escritorio, **Python 3.10 o posterior**, Tkinter y soporte para entornos virtuales. No requiere Wine, .NET ni Swift.

## Requisitos

Instala los paquetes con el gestor de tu distribución, solo si faltan:

```sh
# Debian 12+ / Ubuntu 22.04+
sudo apt update
sudo apt install python3 python3-tk python3-venv ca-certificates

# Fedora (sistema tradicional, no Bazzite/Silverblue)
sudo dnf install python3 python3-tkinter python3-pip ca-certificates

# Arch Linux
sudo pacman -S python tk python-pip ca-certificates
```

Comprueba el Python que utilizarás con `python3 -m tkinter`: debe abrir una ventana de prueba. Si usas un Python de Homebrew sin Tkinter, prueba `/usr/bin/python3 -m tkinter` y ejecuta el lanzador con `PYTHON=/usr/bin/python3 ./linux/run.sh`.

## Ejecutar

Desde la raíz del repositorio:

```sh
./linux/run.sh
# Opcional: abrir directamente una carpeta
./linux/run.sh "/ruta/al/juego_v2-0-1"
```

También puedes ejecutar `python3 linux/convertidor_nup.py`. El lanzador acepta `PYTHON=/ruta/a/python3` para elegir intérprete.

1. Si falta la herramienta, pulsa **Instalar (1 clic)**. Se descarga una revisión fijada de nup y se crea un entorno virtual privado; necesita internet. La aplicación no ejecuta `sudo` ni instala paquetes en el Python del sistema.
2. Pulsa **Elegir carpeta…**. Se admiten `base/`, `updates/<versión decimal>/`, `dlc/<título ID de 16 hex>/<índice>/`, carpetas con solo actualizaciones y carpetas planas con `exefs/` o `romfs/`. La aplicación muestra los paquetes, el título ID leído de `main.npdm` y el tamaño total.
3. Revisa el nombre y la versión sugeridos. Elige un destino fuera de la carpeta de origen.
4. Pulsa **Convertir a .nup**. La verificación completa SHA-256 está activada por defecto. Puedes cancelar; la interfaz permanece disponible mientras trabaja.

El resultado se llama `Nombre [TítuloID].nup` (sin el ID si no se encuentra). No se sobrescriben archivos existentes, incluso si otro proceso crea el destino durante la conversión. Un archivo temporal se publica como resultado final solo después de completar los pasos seleccionados; errores y cancelaciones eliminan los temporales. El destino debe admitir enlaces duros (por ejemplo, ext4, Btrfs o XFS); en FAT/exFAT, utiliza primero un destino compatible y copia después el `.nup` terminado.

Esta primera versión usa el selector de carpetas; no incluye arrastrar y soltar ni paquetes AppImage/Flatpak. Los directorios enlazados simbólicamente dentro del origen se rechazan para evitar destinos que también formen parte de la entrada; selecciona la carpeta real o copia su contenido antes de convertir.

## Acceso directo opcional

Con el mismo Python que incluye Tkinter:

```sh
python3 linux/install_desktop.py
```

Copia la aplicación, su licencia y el icono a `${XDG_DATA_HOME:-~/.local/share}/convertidor-nup/` y añade `convertidor-nup.desktop` a `applications/`. Después puedes abrir **Convertidor NUP** desde el menú de aplicaciones y mover el repositorio. Repite el comando para actualizar la copia. No se configura ejecución automática al iniciar sesión.

Para quitar el acceso directo, elimina únicamente `applications/convertidor-nup.desktop` dentro de ese directorio de datos. Para desinstalar la app y su herramienta, elimina también su subcarpeta `convertidor-nup/`; los juegos y resultados guardados fuera de ella permanecen intactos.

## Bazzite / Fedora Atomic

Usa un contenedor Distrobox para disponer de Python con Tkinter sin modificar la imagen del sistema, siguiendo la [documentación de Bazzite](https://docs.bazzite.gg/Installing_and_Managing_Software/Distrobox/):

```sh
distrobox create --name nup-linux --image ubuntu:24.04
distrobox enter nup-linux
sudo apt update
sudo apt install python3 python3-tk python3-venv ca-certificates
# Dentro del contenedor, entra al repositorio (el directorio personal se comparte).
cd /ruta/a/convertidor-nup
/usr/bin/python3 linux/convertidor_nup.py
```

En usos posteriores ejecuta desde el host:

```sh
distrobox enter nup-linux -- /usr/bin/python3 /ruta/a/convertidor-nup/linux/convertidor_nup.py
```

Ejecuta la app y su herramienta siempre dentro del mismo contenedor. Para integrar aplicaciones de un contenedor en el menú del host, consulta [distrobox-export](https://distrobox.it/usage/distrobox-export/); un acceso directo generado dentro del contenedor necesita ese envoltorio para funcionar desde el host.

## Herramienta y compatibilidad

El instalador usa la revisión [`a4840f0`](https://github.com/a55uka/nup/commit/a4840f06c94ddeb414eea5b33c9704ffe995f11c) de nup. Descarga solo su código al primer uso, guarda su licencia MIT e instala `zstandard>=0.22` en el entorno privado. Para Python 3.10 añade `typing_extensions>=4.0` y un fallback de importación de `NotRequired` en la copia instalada de `pack.py`: esa revisión de nup declara Python 3.10 pero importa el símbolo desde `typing`, donde apareció en 3.11. Además, en la copia de `format.py` comprueba los valores del enum `Codec` mediante una tupla, compatible con Python anterior a 3.12. Son ajustes de compatibilidad del intérprete; conservan los códecs admitidos y el formato de empaquetado.

La instalación se guarda bajo `${XDG_DATA_HOME:-~/.local/share}/convertidor-nup/nup-<revisión>/`. Si falla la conexión, consulta el registro y pulsa **Instalar** otra vez. No se marca como lista hasta que el comando de nup arranca correctamente.

## Pruebas

Sin escritorio se ejecuta el backend y se omiten las pruebas de interfaz:

```sh
python3 -m unittest discover -s linux/tests -v
```

Para incluir la interfaz instala `xvfb`, `xauth` y `desktop-file-utils` y ejecuta:

```sh
xvfb-run -a python3 -m unittest discover -s linux/tests -v
# También instala nup y convierte/verifica archivos sintéticos; requiere internet.
NUP_INTEGRATION=1 xvfb-run -a python3 -m unittest discover -s linux/tests -v
```

Las pruebas no requieren juegos ni archivos protegidos. La CI cubre Python 3.10, 3.12 y 3.14. No se han validado todas las distribuciones ni los entornos Wayland/X11 existentes.

Licencia MIT. Sin afiliación con Nintendo; úsalo solo con dumps de tus propios juegos.
