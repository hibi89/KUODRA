"""Test GUI staging dispatch without opening a native Linux window.

Real GUI widget creation is tested in the Windows PyInstaller EXE CI step,
not merely by this mocked routing test.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
import unittest
from unittest.mock import patch

from desktop.entry import main


class GuiSmokeRoutingTests(unittest.TestCase):
    def test_gui_smoke_dispatches_without_official_source_or_file(self):
        value={
            'schema':'kuodra.windows-gui-smoke.v1',
            'status':'TK_WINDOW_RENDERED_NO_NETWORK',
            'window_width':930,'window_height':650,
            'required_control_count':11,
            'missing_controls':0,'user_data_loaded':False,
            'network_requests':0,'consumer_release_ready':False,
        }
        output=StringIO()
        with patch('kuodra.gui.main',return_value=value) as gui:
            with redirect_stdout(output):
                result=main(['--gui-smoke'])
        self.assertEqual(result,0)
        gui.assert_called_once_with(smoke_only=True)
        obj=json.loads(output.getvalue())
        self.assertEqual(obj['status'],'TK_WINDOW_RENDERED_NO_NETWORK')
        self.assertFalse(obj['consumer_release_ready'])


if __name__=='__main__':
    unittest.main()
