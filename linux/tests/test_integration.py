"""Opt-in real nup installation and conversion; fixtures contain synthetic bytes only."""

import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nup_backend import NupTool, ProcessRunner, analyze_dump
from test_backend import write_npdm


@unittest.skipUnless(os.environ.get('NUP_INTEGRATION') == '1', 'Set NUP_INTEGRATION=1 (downloads nup and zstandard)')
class RealNupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory(prefix='real nup ñ ')
        cls.addClassCleanup(cls.work.cleanup)
        cls.root = Path(cls.work.name)
        cls.tool = NupTool(cls.root / 'data')
        cls.install_log = []
        try:
            cls.tool.install(ProcessRunner(), cls.install_log.append)
        except Exception as exc:
            raise RuntimeError('\n'.join(cls.install_log)) from exc

    def test_real_pack_verify_and_metadata(self):
        source = self.root / 'juego sintético $(sin shell)_v2-0-1'
        write_npdm(source / 'base/exefs/main.npdm')
        content = source / 'base/romfs/texto ñ.txt'
        content.parent.mkdir()
        content.write_text('Synthetic data for packaging tests.\n' * 100)
        write_npdm(source / 'updates/65536/exefs/main.npdm')
        addon = source / 'dlc/010012345678A001/0/romfs/data'
        addon.parent.mkdir(parents=True)
        addon.write_bytes(b'synthetic dlc')
        output = self.root / 'Juego ñ [0100123456789000].nup'
        log = []
        try:
            self.tool.convert(source, output, 'Juego ñ', '2.0.1', True, ProcessRunner(), log.append)
        except Exception as exc:
            self.fail(f'{exc}\n' + '\n'.join(log))
        self.assertTrue(output.is_file())
        self.assertTrue(any('verify: OK (deep)' in line for line in log), log)
        self.assertTrue(any(line.startswith('pack:') for line in log))
        info = []
        ProcessRunner().run(self.tool.command + ['info', str(output)],
                            env=self.tool.environment, log=info.append)
        text = '\n'.join(info)
        self.assertIn('0100123456789000', text)
        self.assertIn("'Juego ñ'", text)
        self.assertIn('display 2.0.1', text)
        self.assertIn('packages:  3', text)
        self.assertEqual(analyze_dump(source).title_id, '0100123456789000')

    def test_update_only_real_conversion(self):
        source = self.root / 'update only'
        write_npdm(source / 'updates/131072/exefs/main.npdm')
        output = self.root / 'update.nup'
        log = []
        try:
            self.tool.convert(source, output, 'Update', '', True, ProcessRunner(), log.append)
        except Exception as exc:
            self.fail(f'{exc}\n' + '\n'.join(log))
        info = []
        ProcessRunner().run(self.tool.command + ['info', str(output)],
                            env=self.tool.environment, log=info.append)
        self.assertTrue(any('[standalone]' in line for line in info), info)


if __name__ == '__main__':
    unittest.main()
