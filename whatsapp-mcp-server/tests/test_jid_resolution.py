import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to sys.path to import whatsapp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import whatsapp

class TestJIDResolution(unittest.TestCase):
    
    @patch('sqlite3.connect')
    def test_resolve_jids(self, mock_connect):
        # Mock DB response
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Return two JIDs for the phone number
        mock_cursor.fetchall.return_value = [
            ("123456789@s.whatsapp.net",),
            ("123456789@lid",)
        ]
        
        # Call function
        jids = whatsapp.resolve_jids("123456789")
        
        # Assertions
        self.assertEqual(len(jids), 2)
        self.assertIn("123456789@s.whatsapp.net", jids)
        self.assertIn("123456789@lid", jids)
        mock_cursor.execute.assert_called_once()
        args, kwargs = mock_cursor.execute.call_args
        self.assertIn("%123456789%", args[1])

if __name__ == '__main__':
    unittest.main()
