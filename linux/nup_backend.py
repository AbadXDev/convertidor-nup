"""Linux conversion logic. Importable without Tk or a graphical session."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import signal
import struct
import subprocess
import sys
import tempfile
import threading
import time
from typing import Callable
import urllib.request
import zipfile

# Pin the reference implementation so a moving branch cannot change installations.
NUP_REVISION = 'a4840f06c94ddeb414eea5b33c9704ffe995f11c'
NUP_ARCHIVE = f'https://codeload.github.com/a55uka/nup/zip/{NUP_REVISION}'
Log = Callable[[str], None]


class Cancelled(Exception):
    """The user cancelled this operation."""


@dataclass(frozen=True)
class DumpInfo:
    title_id: str
    packages: tuple[str, ...]
    total_bytes: int

    @property
    def valid(self) -> bool:
        return bool(self.packages)


def program_id(path: Path) -> str:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return ''
    # Match nup's ACI0 search, including NPDM header revisions with other offsets.
    offset = data.find(b'ACI0')
    if offset < 0 or offset + 0x18 > len(data):
        return ''
    value = struct.unpack_from('<Q', data, offset + 0x10)[0]
    return f'{value:016X}' if value else ''


def _files(root: Path, check_cancelled=lambda: None):
    check_cancelled()
    if root.is_symlink():
        raise ValueError(f'La carpeta contiene un enlace simbólico de directorio: {root}. '
                         'Selecciona la carpeta real o copia su contenido.')
    def onerror(error):
        raise error
    for directory, directories, names in os.walk(root, onerror=onerror):
        check_cancelled()
        for name in directories:
            if (Path(directory) / name).is_symlink():
                raise ValueError(f'La carpeta contiene un enlace simbólico de directorio: '
                                 f'{Path(directory) / name}. Selecciona la carpeta real o copia su contenido.')
        for name in names:
            check_cancelled()
            yield Path(directory) / name


def _has_files(root: Path, check_cancelled=lambda: None) -> bool:
    return root.is_dir() and any(path.name != '.listing' for path in _files(root, check_cancelled))


def analyze_dump(root: Path, *, check_cancelled=lambda: None) -> DumpInfo:
    check_cancelled()
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Elige una carpeta, no un archivo.')
    packages: list[str] = []
    candidates: list[Path] = []
    base, updates = root / 'base', root / 'updates'
    if base.is_dir() or updates.is_dir():
        if _has_files(base, check_cancelled):
            packages.append('Base')
            candidates.append(base)
        if updates.is_dir():
            for update in sorted((p for p in updates.iterdir()
                                  if re.fullmatch(r'[0-9]+', p.name) and p.is_dir()),
                                 key=lambda p: int(p.name)):
                if _has_files(update, check_cancelled):
                    packages.append(f'Update {update.name}')
                    candidates.append(update)
        dlc = root / 'dlc'
        if dlc.is_dir():
            for title in sorted(dlc.iterdir()):
                if title.is_dir() and re.fullmatch(r'[0-9a-fA-F]{16}', title.name):
                    for index in sorted(title.iterdir()):
                        if _has_files(index, check_cancelled):
                            packages.append(f'DLC {title.name.upper()} / {index.name}')
    elif (root / 'exefs').is_dir() or (root / 'romfs').is_dir():
        if _has_files(root, check_cancelled):
            packages.append('Base (carpeta plana)')
            candidates.append(root)
    title_id = ''
    for candidate in candidates:
        for relative in ('exefs/main.npdm', 'main.npdm'):
            title_id = program_id(candidate / relative)
            if title_id:
                break
        if title_id:
            break
    return DumpInfo(title_id, tuple(packages),
                    sum(p.stat().st_size for p in _files(root, check_cancelled)))


def clean_name_and_version(folder_name: str) -> tuple[str, str]:
    match = re.search(r'_v([0-9][0-9.-]*)$', folder_name)
    version = match[1].replace('-', '.') if match else ''
    raw = folder_name[:match.start()] if match else folder_name
    name = raw.replace('_', ' ').replace('-', ' ').strip()
    if name.islower() or ' ' in name:
        # Preserve existing uppercase words such as DOOM.
        name = ' '.join(word[:1].upper() + word[1:] if word.islower() else word
                        for word in name.split())
    return name, version


def _validate_destination(source: Path, destination: Path) -> None:
    if not destination.is_dir():
        raise ValueError('La carpeta de destino no existe.')
    if destination == source or source in destination.parents:
        raise ValueError('Elige un destino fuera de la carpeta del juego.')


def output_path(source: Path, destination: Path, name: str, title_id: str) -> Path:
    source, destination = source.resolve(), destination.resolve()
    _validate_destination(source, destination)
    clean = re.sub(r'[/\x00-\x1f:]', '-', name.strip())
    if not clean or clean in ('.', '..'):
        raise ValueError('Escribe un nombre para el juego.')
    suffix = f' [{title_id}]' if title_id else ''
    return destination / f'{clean}{suffix}.nup'


class ProcessRunner:
    """One cancellable job, possibly consisting of several sequential commands."""

    def __init__(self):
        self.cancelled = threading.Event()

    def check_cancelled(self) -> None:
        if self.cancelled.is_set():
            raise Cancelled()

    def cancel(self) -> None:
        self.cancelled.set()

    def run(self, args: list[str], *, env=None, cwd=None, log: Log = lambda _: None) -> None:
        self.check_cancelled()
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace',
                                   env=env, cwd=cwd, start_new_session=True)
        finished = threading.Event()

        def stop_process():
            while not finished.wait(0.05):
                if self.cancelled.is_set():
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        return
                    # The group can outlive its leader and keep our stdout pipe
                    # open. Check the whole group, even after the leader exits.
                    deadline = time.monotonic() + 2
                    while time.monotonic() < deadline:
                        try:
                            os.killpg(process.pid, 0)
                        except ProcessLookupError:
                            return
                        time.sleep(0.05)
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    return

        watcher = threading.Thread(target=stop_process, daemon=True)
        watcher.start()
        try:
            for line in process.stdout:
                line = line.rstrip('\r\n')
                if line:
                    log(line)
            code = process.wait()
            self.check_cancelled()
            if code:
                raise RuntimeError(f'El comando terminó con código {code}. Revisa el registro.')
        finally:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
            finished.set()
            watcher.join(timeout=3)
            process.stdout.close()


class NupTool:
    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            xdg = os.environ.get('XDG_DATA_HOME', '')
            data_dir = Path(xdg) if xdg and Path(xdg).is_absolute() else Path.home() / '.local/share'
            data_dir /= 'convertidor-nup'
        self.root = Path(data_dir) / f'nup-{NUP_REVISION}'
        self.python = self.root / 'venv/bin/python'
        self.modules = self.root / 'src'

    @property
    def command(self) -> list[str]:
        return [str(self.python), '-u', '-m', 'nup.cli']

    @property
    def environment(self) -> dict[str, str]:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.modules)
        env['PYTHONUNBUFFERED'] = '1'
        env.pop('PYTHONHOME', None)
        return env

    @property
    def ready(self) -> bool:
        return (self.root.joinpath('ready').is_file() and self.python.is_file()
                and self.modules.joinpath('nup/cli.py').is_file())

    def install(self, runner: ProcessRunner, log: Log) -> None:
        if self.ready:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        log('Descargando nup (versión fijada para esta aplicación)…')
        with tempfile.TemporaryDirectory(prefix='download-', dir=self.root) as work:
            archive = Path(work) / 'nup.zip'
            with urllib.request.urlopen(NUP_ARCHIVE, timeout=20) as response, archive.open('wb') as target:
                while chunk := response.read(256 * 1024):
                    runner.check_cancelled()
                    target.write(chunk)
            prefix = f'nup-{NUP_REVISION}/tools/nup/nup/'
            # Copy only Python package members; never extract arbitrary ZIP paths.
            with zipfile.ZipFile(archive) as source:
                if prefix + 'cli.py' not in source.namelist():
                    raise RuntimeError('La descarga no contiene la herramienta nup esperada.')
                for member in source.infolist():
                    runner.check_cancelled()
                    if member.filename.startswith(prefix) and not member.is_dir():
                        relative = Path(member.filename[len(prefix):])
                        if relative.is_absolute() or '..' in relative.parts:
                            raise RuntimeError('La descarga contiene una ruta inválida.')
                        target = self.modules / 'nup' / relative
                        target.parent.mkdir(parents=True, exist_ok=True)
                        content = source.read(member)
                        if relative == Path('pack.py'):
                            # This pinned revision declares Python >=3.10 but imports
                            # NotRequired from typing (introduced in Python 3.11).
                            content = content.replace(
                                b'from typing import IO, TYPE_CHECKING, TypedDict, NotRequired',
                                b'from typing import IO, TYPE_CHECKING, TypedDict\n'
                                b'try:\n    from typing import NotRequired\n'
                                b'except ImportError:\n    from typing_extensions import NotRequired')
                        elif relative == Path('format.py'):
                            # Enum containment accepted integer values only in 3.12+.
                            content = content.replace(b'if codec not in Codec:',
                                                      b'if codec not in tuple(Codec):')
                        target.write_bytes(content)
                (self.root / 'LICENSE.nup').write_bytes(source.read(f'nup-{NUP_REVISION}/LICENSE'))
        log('Creando un entorno privado de Python…')
        try:
            runner.run([sys.executable, '-m', 'venv', str(self.root / 'venv')], log=log)
        except RuntimeError as exc:
            raise RuntimeError('No se pudo crear el entorno. En Debian/Ubuntu instala python3-venv; '
                               'consulta linux/README.md y vuelve a intentar.') from exc
        log('Instalando zstandard en el entorno privado…')
        runner.run([str(self.python), '-m', 'pip', 'install', '--disable-pip-version-check',
                    'zstandard>=0.22', 'typing_extensions>=4.0; python_version < "3.11"'], log=log)
        runner.run(self.command + ['--help'], env=self.environment, log=log)
        runner.check_cancelled()
        (self.root / 'ready').write_text(NUP_REVISION + '\n')
        log('Herramienta nup lista.')

    def convert(self, source: Path, output: Path, name: str, version: str,
                verify: bool, runner: ProcessRunner, log: Log) -> None:
        source, output = source.resolve(strict=True), output.absolute()
        _validate_destination(source, output.parent.resolve())
        if os.path.lexists(output):
            raise FileExistsError(f'Ya existe {output.name}. Cambia el nombre o el destino.')
        if not self.ready:
            raise RuntimeError('Instala primero la herramienta nup.')
        runner.check_cancelled()
        # Recheck the source just before packing, including directory links
        # that may have changed since the GUI's initial scan.
        if not analyze_dump(source, check_cancelled=runner.check_cancelled).valid:
            raise ValueError('No se encontraron paquetes en esta carpeta.')
        # Same filesystem as output; final publication is exclusive and atomic.
        with tempfile.TemporaryDirectory(prefix='.convertidor-', dir=output.parent) as staging:
            temporary = Path(staging) / 'output.nup'
            args = self.command + ['pack', str(source), str(temporary), '--name', name]
            if version.strip():
                args += ['--display-version', version.strip()]
            runner.run(args, env=self.environment, log=log)
            if not temporary.is_file():
                raise RuntimeError('La herramienta no generó un archivo .nup.')
            runner.check_cancelled()
            if verify:
                log('Verificando el archivo (SHA-256)…')
                runner.run(self.command + ['verify', str(temporary)], env=self.environment, log=log)
            runner.check_cancelled()
            # os.rename would overwrite a file created since the initial check.
            os.link(temporary, output)
