import os
from pathlib import Path
import sys
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import tkinter as tk
except ImportError:
    tk = None

import test_backend


@unittest.skipUnless(tk and os.environ.get('DISPLAY'), 'Tkinter and DISPLAY required (use Xvfb)')
class GuiTests(unittest.TestCase):
    def setUp(self):
        from convertidor_nup import App
        test_backend.ConversionTests.setUp(self)
        self.window = tk.Tk()
        self.window.withdraw()
        self.addCleanup(self.window.destroy)
        self.app = App(self.window, tool=self.tool)
        self.addCleanup(self.app.destroy)

    def wait_idle(self):
        deadline = time.monotonic() + 8
        while self.app.busy and time.monotonic() < deadline:
            self.window.update()
            time.sleep(0.01)
        self.window.update()
        self.assertFalse(self.app.busy, self.app.status.get())

    def load(self):
        self.app.load_folder(self.source)
        self.wait_idle()

    def test_load_convert_and_duplicate_protection(self):
        self.load()
        self.assertIn('0100123456789000', self.app.info.get())
        self.assertEqual(self.app.version.get(), '')
        self.assertTrue(self.app.convert_button.instate(['!disabled']))
        self.app.convert()
        self.assertTrue(self.app.pick_button.instate(['disabled']))
        self.wait_idle()
        self.assertIn('Listo', self.app.status.get())
        self.assertTrue(self.app.convert_button.instate(['disabled']))
        self.assertTrue((self.root / 'Source [0100123456789000].nup').exists())

    def test_worker_failure_restores_controls(self):
        self.load()
        self.app.name.set('fail')
        self.app.convert()
        self.wait_idle()
        self.assertIn('código 2', self.app.status.get())
        self.assertTrue(self.app.pick_button.instate(['!disabled']))
        self.assertTrue(self.app.convert_button.instate(['!disabled']))

    def test_cancel_restores_controls_without_output(self):
        self.load()
        self.app.name.set('slow')
        self.app.convert()
        self.app.cancel()
        self.wait_idle()
        self.assertIn('Cancelado', self.app.status.get())
        self.assertTrue(self.app.pick_button.instate(['!disabled']))
        self.assertFalse((self.root / 'slow [0100123456789000].nup').exists())

    def test_new_folder_resets_previous_version(self):
        self.load()
        self.app.version.set('9.9')
        self.app.load_folder(self.source)
        self.wait_idle()
        self.assertEqual(self.app.version.get(), '')

    def test_empty_folder_cannot_convert(self):
        empty = self.root / 'empty'
        empty.mkdir()
        self.app.load_folder(empty)
        self.wait_idle()
        self.assertTrue(self.app.convert_button.instate(['disabled']))
        self.assertIn('No se encontraron', self.app.status.get())


if __name__ == '__main__':
    unittest.main()
