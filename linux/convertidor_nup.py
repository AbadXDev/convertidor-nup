#!/usr/bin/env python3
"""Convertidor NUP — Linux desktop interface, by AbadXDev and contributors."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import threading

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText
except ImportError:
    raise SystemExit('Falta Tkinter en este Python. Instala python3-tk (Debian/Ubuntu), '
                     'python3-tkinter (Fedora) o tk (Arch). Consulta linux/README.md. '
                     'Si usas Homebrew, prueba /usr/bin/python3 o instala su paquete python-tk.')

from nup_backend import (Cancelled, NupTool, ProcessRunner, analyze_dump,
                         clean_name_and_version, output_path)


class App(ttk.Frame):
    def __init__(self, root: tk.Tk, initial_folder: Path | None = None, *, tool=None):
        super().__init__(root, padding=20)
        self.root = root
        self.tool = tool if tool is not None else NupTool()
        self.source = None
        self.destination = None
        self.dump = None
        self.busy = False
        self.runner = None
        self.last_output = None
        self.closing = False
        self.events = queue.Queue()
        self.name = tk.StringVar()
        self.version = tk.StringVar()
        self.info = tk.StringVar()
        self.folder = tk.StringVar(value='Elige la carpeta que contiene base/, updates/ o exefs/ y romfs/.')
        self.output = tk.StringVar(value='Se guardará como: —')
        self.status = tk.StringVar(value='Elige la carpeta de un juego para empezar.')
        self.verify = tk.BooleanVar(value=True)
        root.title('Convertidor NUP')
        root.geometry('800x740')
        root.minsize(700, 640)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.pack(fill='both', expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(7, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        ttk.Label(header, text='Convertidor NUP', font=('TkDefaultFont', 21, 'bold')).pack(anchor='w')
        ttk.Label(header, text='Convierte una carpeta de juego de Switch 2 en un archivo .nup').pack(anchor='w')

        self.banner = ttk.LabelFrame(self, text='Herramienta de empaquetado', padding=10)
        self.banner.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        self.banner.columnconfigure(0, weight=1)
        ttk.Label(self.banner, text='Instala nup en tu usuario (requiere internet).').grid(row=0, column=0, sticky='w')
        self.install_button = ttk.Button(self.banner, text='Instalar (1 clic)', command=self.install_tool)
        self.install_button.grid(row=0, column=1, padx=(10, 0))

        source_frame = ttk.LabelFrame(self, text='1 · Elige la carpeta del juego', padding=12)
        source_frame.grid(row=2, column=0, sticky='ew', pady=(0, 12))
        source_frame.columnconfigure(1, weight=1)
        self.pick_button = ttk.Button(source_frame, text='Elegir carpeta…', command=self.pick_folder)
        self.pick_button.grid(row=0, column=0, sticky='nw', padx=(0, 12))
        ttk.Label(source_frame, textvariable=self.folder, wraplength=490).grid(row=0, column=1, sticky='w')
        ttk.Label(source_frame, textvariable=self.info, wraplength=690).grid(row=1, column=0, columnspan=2, sticky='w', pady=(10, 0))

        fields = ttk.Frame(self)
        fields.grid(row=3, column=0, sticky='ew')
        fields.columnconfigure(0, weight=3)
        fields.columnconfigure(1, weight=1)
        ttk.Label(fields, text='Nombre del juego').grid(row=0, column=0, sticky='w')
        ttk.Label(fields, text='Versión (opcional)').grid(row=0, column=1, sticky='w', padx=(15, 0))
        self.name_entry = ttk.Entry(fields, textvariable=self.name)
        self.name_entry.grid(row=1, column=0, sticky='ew', pady=5)
        self.version_entry = ttk.Entry(fields, textvariable=self.version, width=18)
        self.version_entry.grid(row=1, column=1, sticky='ew', padx=(15, 0), pady=5)

        destination = ttk.Frame(self)
        destination.grid(row=4, column=0, sticky='ew', pady=10)
        destination.columnconfigure(0, weight=1)
        ttk.Label(destination, textvariable=self.output, wraplength=530).grid(row=0, column=0, sticky='w')
        self.destination_button = ttk.Button(destination, text='Cambiar destino…', command=self.pick_destination)
        self.destination_button.grid(row=0, column=1, sticky='ne', padx=(10, 0))

        actions = ttk.Frame(self)
        actions.grid(row=5, column=0, sticky='ew')
        self.verify_check = ttk.Checkbutton(actions, text='Verificar al terminar (SHA-256, recomendado)', variable=self.verify)
        self.verify_check.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 12))
        self.convert_button = ttk.Button(actions, text='2 · Convertir a .nup', command=self.convert)
        self.convert_button.grid(row=1, column=0, sticky='w')
        self.cancel_button = ttk.Button(actions, text='Cancelar', command=self.cancel)
        self.cancel_button.grid(row=1, column=1, padx=10)
        self.open_button = ttk.Button(actions, text='Abrir carpeta', command=self.open_folder)
        self.open_button.grid(row=1, column=2)

        progress_frame = ttk.Frame(self)
        progress_frame.grid(row=6, column=0, sticky='ew', pady=12)
        self.progress = ttk.Progressbar(progress_frame, maximum=100)
        self.progress.pack(fill='x')
        ttk.Label(progress_frame, textvariable=self.status, wraplength=710).pack(anchor='w', pady=(7, 0))
        self.log_box = ScrolledText(self, height=8, wrap='word', state='disabled')
        self.log_box.grid(row=7, column=0, sticky='nsew')
        ttk.Label(self, text='By AbadXDev · Linux: contributors · Empaquetador nup: a55uka').grid(row=8, column=0, sticky='e', pady=(10, 0))

        self.controls = (self.pick_button, self.destination_button, self.name_entry,
                         self.version_entry, self.verify_check, self.install_button)
        self.name.trace_add('write', lambda *_: self.refresh())
        self.refresh()
        self._poll_id = root.after(40, self.poll)
        if initial_folder is not None:
            self.load_folder(initial_folder)

    def selected_output(self):
        if self.source is None or self.dump is None:
            return None
        return output_path(self.source, self.destination, self.name.get(), self.dump.title_id)

    def refresh(self):
        for control in self.controls:
            control.state(['disabled' if self.busy else '!disabled'])
        ready = self.tool.ready
        if ready:
            self.banner.grid_remove()
        else:
            self.banner.grid()
        self.cancel_button.state(['!disabled' if self.busy else 'disabled'])
        self.open_button.state(['!disabled' if self.last_output and not self.busy else 'disabled'])
        allowed = not self.busy and ready and self.dump is not None and self.dump.valid
        try:
            path = self.selected_output()
            self.output.set(f'Se guardará como: {path}' if path else 'Se guardará como: —')
            if path is None or os.path.lexists(path):
                allowed = False
                if path:
                    self.output.set(f'Ya existe: {path}. Cambia el nombre o el destino.')
        except (ValueError, OSError) as exc:
            self.output.set(str(exc))
            allowed = False
        self.convert_button.state(['!disabled' if allowed else 'disabled'])
        if self.source is None:
            self.destination_button.state(['disabled'])

    def append_log(self, line):
        self.log_box.configure(state='normal')
        self.log_box.insert('end', line + '\n')
        if int(self.log_box.index('end-1c').split('.')[0]) > 600:
            self.log_box.delete('1.0', '100.0')
        self.log_box.see('end')
        self.log_box.configure(state='disabled')
        match = re.search(r'pack:\s*(\d+)\s*/\s*(\d+)', line)
        if match and int(match[2]):
            self.progress.stop()
            self.progress.configure(mode='determinate', value=min(100, int(match[1]) * 100 / int(match[2])))
            self.status.set(f'Empaquetando… {match[1]} de {match[2]} archivos')
        elif line.startswith('Verificando'):
            self.status.set(line)
            self.progress.configure(mode='indeterminate')
            self.progress.start(15)

    def start_job(self, work, complete):
        if self.busy:
            return
        self.busy = True
        self.runner = ProcessRunner()
        runner = self.runner
        self.progress.configure(mode='indeterminate')
        self.progress.start(15)
        self.refresh()

        def worker():
            try:
                result = work(runner, lambda line: self.events.put(('log', line)))
                self.events.put(('done', (complete, result)))
            except Cancelled:
                self.events.put(('error', 'Cancelado. No se ha guardado ningún archivo final.'))
            except Exception as exc:
                self.events.put(('error', str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        for _ in range(200):
            try:
                kind, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == 'log':
                self.append_log(payload)
            else:
                self.busy = False
                self.runner = None
                self.progress.stop()
                self.progress.configure(mode='determinate', value=0)
                if kind == 'done':
                    complete, result = payload
                    complete(result)
                else:
                    self.status.set(payload)
                    self.append_log(payload)
                self.refresh()
                if self.closing:
                    self.root.destroy()
                    return
        self._poll_id = self.root.after(40, self.poll)

    def load_folder(self, folder):
        if self.busy:
            return
        self.source = Path(folder).resolve()
        self.destination = self.source.parent
        self.dump = None
        self.last_output = None
        self.folder.set(str(self.source))
        name, version = clean_name_and_version(self.source.name)
        self.name.set(name)
        self.version.set(version)
        self.info.set('Leyendo la carpeta…')
        self.status.set('Leyendo la carpeta…')

        def complete(info):
            self.dump = info
            packages = ' · '.join(info.packages)
            self.info.set(f'{packages}\nTítulo ID: {info.title_id or "no encontrado"} · {info.total_bytes / 1024**3:.2f} GiB')
            self.status.set('Carpeta válida. Instala nup si aún no está disponible.' if info.valid
                            else 'No se encontraron paquetes en esta carpeta.')
        self.start_job(lambda runner, log: analyze_dump(self.source, check_cancelled=runner.check_cancelled), complete)

    def pick_folder(self):
        folder = filedialog.askdirectory(parent=self.root, title='Elige la carpeta del juego', mustexist=True)
        if folder:
            self.load_folder(folder)

    def pick_destination(self):
        folder = filedialog.askdirectory(parent=self.root, title='Dónde guardar el .nup', mustexist=True)
        if folder:
            self.destination = Path(folder)
            self.refresh()

    def install_tool(self):
        self.status.set('Instalando la herramienta nup…')
        self.start_job(lambda runner, log: self.tool.install(runner, log),
                       lambda _: self.status.set('Herramienta nup lista. Ya puedes convertir.'))

    def convert(self):
        if self.busy or self.convert_button.instate(['disabled']):
            return
        try:
            output = self.selected_output()
        except (ValueError, OSError) as exc:
            self.status.set(str(exc))
            return
        source, name, version, verify = self.source, self.name.get(), self.version.get(), self.verify.get()
        self.last_output = None
        self.status.set('Empaquetando…')

        def complete(_):
            self.last_output = output
            self.progress.configure(value=100)
            self.status.set(f'Listo{" y verificado" if verify else ""}: {output.name}')
        self.start_job(lambda runner, log: self.tool.convert(source, output, name, version, verify, runner, log), complete)

    def cancel(self):
        if self.runner:
            self.runner.cancel()
            self.status.set('Cancelando…')

    def open_folder(self):
        if self.last_output and shutil.which('xdg-open'):
            try:
                subprocess.Popen(['xdg-open', str(self.last_output.parent)],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError as exc:
                self.status.set(str(exc))
        elif self.last_output:
            self.status.set(f'Abre esta carpeta: {self.last_output.parent}')

    def close(self):
        if self.busy:
            if messagebox.askyesno('Cerrar', '¿Cancelar la operación y cerrar la aplicación?', parent=self.root):
                self.closing = True
                self.cancel()
        else:
            self.root.destroy()

    def destroy(self):
        self.root.after_cancel(self._poll_id)
        if self.runner:
            self.runner.cancel()
        super().destroy()


def main():
    if sys.version_info < (3, 10):
        raise SystemExit('Se requiere Python 3.10 o posterior.')
    parser = argparse.ArgumentParser(description='Convertidor NUP para Linux')
    parser.add_argument('folder', nargs='?', type=Path, help='Carpeta del juego (opcional)')
    args = parser.parse_args()
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise SystemExit(f'No se pudo abrir la interfaz gráfica: {exc}. Ejecuta la app en una sesión de escritorio.')
    App(root, args.folder)
    root.mainloop()


if __name__ == '__main__':
    main()
