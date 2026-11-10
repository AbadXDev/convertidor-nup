import os
from pathlib import Path
import signal
import struct
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nup_backend import (Cancelled, NupTool, ProcessRunner, analyze_dump,
                         clean_name_and_version, output_path, program_id)


def write_npdm(path, title_id=0x0100123456789000):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = bytearray(0xA0)
    struct.pack_into('<I', data, 0x70, 0x80)
    data[0x80:0x84] = b'ACI0'
    struct.pack_into('<Q', data, 0x90, title_id)
    path.write_bytes(data)


class DumpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='nup test ñ ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_npdm_bounds_and_little_endian(self):
        path = self.root / 'main.npdm'
        write_npdm(path)
        self.assertEqual(program_id(path), '0100123456789000')
        for data in (b'', b'ACI0', b'\0' * 0x70, b'\0' * 0x70 + b'\xff' * 8):
            path.write_bytes(data)
            self.assertEqual(program_id(path), '')

    def test_bundle_lists_numeric_updates_and_dlc(self):
        write_npdm(self.root / 'base/exefs/main.npdm')
        write_npdm(self.root / 'updates/10/exefs/main.npdm')
        write_npdm(self.root / 'updates/2/exefs/main.npdm')
        write_npdm(self.root / 'updates/not-a-version/exefs/main.npdm')
        dlc = self.root / 'dlc/010012345678A001/0/romfs/data'
        dlc.parent.mkdir(parents=True)
        dlc.write_bytes(b'dlc')
        info = analyze_dump(self.root)
        self.assertEqual(info.title_id, '0100123456789000')
        self.assertEqual(info.packages, ('Base', 'Update 2', 'Update 10', 'DLC 010012345678A001 / 0'))
        self.assertEqual(info.total_bytes, 4 * 0xA0 + 3)

    def test_flat_and_update_only_layout(self):
        write_npdm(self.root / 'exefs/main.npdm')
        self.assertEqual(analyze_dump(self.root).packages, ('Base (carpeta plana)',))
        (self.root / 'exefs/main.npdm').unlink()
        (self.root / 'exefs').rmdir()
        (self.root / 'base/exefs').mkdir(parents=True)
        write_npdm(self.root / 'updates/65536/exefs/main.npdm')
        self.assertEqual(analyze_dump(self.root).packages, ('Update 65536',))
        self.assertEqual(analyze_dump(self.root).title_id, '0100123456789000')

    def test_empty_dump_is_invalid(self):
        (self.root / 'base/exefs').mkdir(parents=True)
        (self.root / 'base/exefs/.listing').write_text('artifact')
        self.assertFalse(analyze_dump(self.root).valid)

    def test_linked_package_directory_is_rejected(self):
        actual = self.root / 'actual'
        write_npdm(actual / 'exefs/main.npdm')
        source = self.root / 'source'
        source.mkdir()
        (source / 'base').symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'simbólico'):
            analyze_dump(source)

    def test_scanning_honors_cancellation(self):
        write_npdm(self.root / 'base/exefs/main.npdm')
        checks = []
        def check():
            checks.append(True)
            if len(checks) == 3:
                raise Cancelled()
        with self.assertRaises(Cancelled):
            analyze_dump(self.root, check_cancelled=check)
        self.assertEqual(len(checks), 3)

    def test_name_version_and_filename_sanitizing(self):
        self.assertEqual(clean_name_and_version('pokopia_v2-0-1'), ('Pokopia', '2.0.1'))
        self.assertEqual(clean_name_and_version('DOOM_vNext'), ('DOOM vNext', ''))
        source = self.root / 'source'
        source.mkdir()
        path = output_path(source, self.root, ' Demo/Name: ñ ', '0100123456789000')
        self.assertEqual(path.name, 'Demo-Name- ñ [0100123456789000].nup')
        with self.assertRaises(ValueError):
            output_path(source, source, 'demo', '')
        with self.assertRaises(ValueError):
            output_path(source, self.root, '  ', '')

    def test_source_containment_checks_resolve_symlinks(self):
        source = self.root / 'source'
        source.mkdir()
        alias = self.root / 'alias'
        alias.symlink_to(source, target_is_directory=True)
        with self.assertRaises(ValueError):
            output_path(source, alias, 'demo', '')


class RunnerTests(unittest.TestCase):
    def test_arguments_and_carriage_return_progress(self):
        lines = []
        runner = ProcessRunner()
        runner.run([sys.executable, '-c', "import sys; print(sys.argv[1]); print('pack: 1/2\\rpack: 2/2', flush=True)",
                    'ñ $(touch NEVER) a b'], log=lines.append)
        self.assertEqual(lines, ['ñ $(touch NEVER) a b', 'pack: 1/2', 'pack: 2/2'])

    def test_cancel_stops_process(self):
        runner = ProcessRunner()
        started = threading.Event()
        outcomes = []

        def worker():
            try:
                runner.run([sys.executable, '-u', '-c', "import time; print('ready'); time.sleep(60)"],
                           log=lambda _: started.set())
            except Exception as exc:
                outcomes.append(exc)

        thread = threading.Thread(target=worker)
        thread.start()
        self.assertTrue(started.wait(5))
        runner.cancel()
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertIsInstance(outcomes[0], Cancelled)

    def test_cancel_before_launch(self):
        runner = ProcessRunner()
        runner.cancel()
        with self.assertRaises(Cancelled):
            runner.run([sys.executable, '-c', 'raise SystemExit(99)'])

    def test_cancel_kills_descendants_after_parent_exits(self):
        runner = ProcessRunner()
        ready = threading.Event()
        groups = []
        outcomes = []
        child = "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('child ready',flush=True); time.sleep(60)"
        parent = ("import os,subprocess,sys,time; print('group:' + str(os.getpid()),flush=True); "
                  f"subprocess.Popen([sys.executable,'-u','-c',{child!r}]); time.sleep(60)")
        def log(line):
            if line.startswith('group:'):
                groups.append(int(line.split(':')[1]))
            elif line == 'child ready':
                ready.set()
        def work():
            try:
                runner.run([sys.executable, '-u', '-c', parent], log=log)
            except Exception as exc:
                outcomes.append(exc)
        thread = threading.Thread(target=work, daemon=True)
        def cleanup():
            for group in groups:
                try:
                    os.killpg(group, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            thread.join(2)
        self.addCleanup(cleanup)
        thread.start()
        self.assertTrue(ready.wait(5))
        runner.cancel()
        thread.join(4)
        self.assertFalse(thread.is_alive(), 'Cancellation left a descendant holding stdout open')
        self.assertIsInstance(outcomes[0], Cancelled)


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='nup conversion ñ ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        write_npdm(self.source / 'exefs/main.npdm')
        self.out = self.root / 'result.nup'
        fake = self.root / 'fake nup.py'
        fake.write_text('''import pathlib, sys, time
if sys.argv[1] == 'pack':
    output = pathlib.Path(sys.argv[3])
    name = sys.argv[sys.argv.index('--name') + 1]
    output.write_text(name)
    print('pack: 1/1', flush=True)
    if name == 'fail': sys.exit(2)
    if name == 'slow': time.sleep(60)
else:
    if pathlib.Path(sys.argv[2]).read_text() == 'badverify': sys.exit(3)
    print('verify: OK')
''')

        class FakeTool(NupTool):
            @property
            def command(self):
                return [sys.executable, str(fake)]

            @property
            def ready(self):
                return True

        self.tool = FakeTool(self.root / 'data')

    def convert(self, name='demo', runner=None, log=lambda _: None):
        self.tool.convert(self.source, self.out, name, '1.0', True,
                          runner or ProcessRunner(), log)

    def test_success_publishes_only_after_verify(self):
        observations = []
        self.convert(log=lambda _: observations.append(self.out.exists()))
        self.assertTrue(observations)
        self.assertFalse(any(observations))
        self.assertEqual(self.out.read_text(), 'demo')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ['fake nup.py', 'result.nup', 'source'])

    def test_pack_or_verify_failure_leaves_no_output(self):
        for name in ('fail', 'badverify'):
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                self.convert(name)
            self.assertFalse(self.out.exists())
            self.assertFalse(list(self.root.glob('.convertidor-*')))

    def test_existing_output_is_preserved(self):
        self.out.write_text('original')
        with self.assertRaises(FileExistsError):
            self.convert()
        self.assertEqual(self.out.read_text(), 'original')

    def test_racing_output_is_preserved(self):
        def log(line):
            if line.startswith('pack:'):
                self.out.write_text('created by someone else')
        with self.assertRaises(FileExistsError):
            self.convert(log=log)
        self.assertEqual(self.out.read_text(), 'created by someone else')

    def test_cancel_cleans_partial_output(self):
        runner = ProcessRunner()
        def log(line):
            if line.startswith('pack:'):
                runner.cancel()
        with self.assertRaises(Cancelled):
            self.convert('slow', runner=runner, log=log)
        self.assertFalse(self.out.exists())
        self.assertFalse(list(self.root.glob('.convertidor-*')))

    def test_reject_output_inside_source(self):
        self.out = self.source / 'result.nup'
        with self.assertRaises(ValueError):
            self.convert()
        self.assertFalse(self.out.exists())

    def test_reject_output_inside_symlinked_package(self):
        actual = self.root / 'actual'
        write_npdm(actual / 'exefs/main.npdm')
        (self.source / 'base').symlink_to(actual, target_is_directory=True)
        self.out = actual / 'output.nup'
        with self.assertRaisesRegex(ValueError, 'simbólico'):
            self.convert()
        self.assertFalse(self.out.exists())


if __name__ == '__main__':
    unittest.main()
