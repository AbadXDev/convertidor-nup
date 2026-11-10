from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from install_desktop import install


class DesktopTests(unittest.TestCase):
    def test_install_copies_app_and_produces_valid_shortcut(self):
        with tempfile.TemporaryDirectory(prefix='desktop ñ $ ` " ') as work:
            root = Path(work)
            entry = install(root / 'data', root / 'applications', Path(sys.executable))
            text = entry.read_text()
            self.assertTrue((root / 'data/convertidor-nup/app/convertidor_nup.py').is_file())
            self.assertTrue((root / 'data/convertidor-nup/app/nup_backend.py').is_file())
            self.assertTrue((root / 'data/convertidor-nup/icon.png').is_file())
            self.assertIn('Terminal=false', text)
            self.assertIn('Exec=', text)
            # Desktop Exec tokens protect reserved characters, including '%' expansion.
            self.assertIn('\\\\$', text)
            self.assertIn('\\\\`', text)
            if shutil.which('desktop-file-validate'):
                subprocess.run(['desktop-file-validate', str(entry)], check=True)


if __name__ == '__main__':
    unittest.main()
