#!/usr/bin/env python3
"""Install a per-user app copy and desktop shortcut; no root privileges needed."""

import os
from pathlib import Path
import shutil
import sys


def _desktop_value(value: str) -> str:
    return value.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')


def _exec_token(path: Path) -> str:
    value = str(path).replace('%', '%%')
    for character in ('\\', '"', '$', '`'):
        value = value.replace(character, '\\' + character)
    # The desktop format unescapes once before parsing Exec arguments.
    return '"' + _desktop_value(value) + '"'


def install(data_home: Path, applications_dir: Path, python: Path) -> Path:
    source = Path(__file__).resolve().parent
    target = data_home.resolve() / 'convertidor-nup'
    app = target / 'app'
    app.mkdir(parents=True, exist_ok=True)
    for name in ('convertidor_nup.py', 'nup_backend.py'):
        shutil.copy2(source / name, app / name)
    shutil.copy2(source.parent / 'assets/icon.png', target / 'icon.png')
    shutil.copy2(source.parent / 'LICENSE', target / 'LICENSE')
    applications_dir.mkdir(parents=True, exist_ok=True)
    entry = applications_dir / 'convertidor-nup.desktop'
    entry.write_text('[Desktop Entry]\nType=Application\nName=Convertidor NUP\n'
                     'Comment=Convierte carpetas de juegos a archivos NUP\n'
                     f'Exec={_exec_token(python.absolute())} {_exec_token(app / "convertidor_nup.py")}\n'
                     f'Icon={_desktop_value(str(target / "icon.png"))}\n'
                     'Terminal=false\nCategories=Utility;\nStartupNotify=true\n', encoding='utf-8')
    return entry


def main():
    if sys.version_info < (3, 10):
        raise SystemExit('Se requiere Python 3.10 o posterior.')
    try:
        import tkinter  # Validate the interpreter used by the shortcut.
    except ImportError:
        raise SystemExit('Falta Tkinter en este Python. Consulta linux/README.md.')
    value = os.environ.get('XDG_DATA_HOME', '')
    data = Path(value) if value and Path(value).is_absolute() else Path.home() / '.local/share'
    entry = install(data, data / 'applications', Path(sys.executable))
    print(f'Acceso directo instalado: {entry}')


if __name__ == '__main__':
    main()
