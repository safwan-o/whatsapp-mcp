import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to sys.path to import whatsapp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import whatsapp

class TestWhatsAppTools(unittest.TestCase):
    
    @patch('requests.post')
    def test_mark_as_read_success(self, mock_post):
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "Messages marked as read"}
        mock_post.return_value = mock_response
        
        # Call function
        success, message = whatsapp.mark_as_read("123456789@s.whatsapp.net", ["msg1", "msg2"])
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(message, "Messages marked as read")
        mock_post.assert_called_once_with(
            f"{whatsapp.WHATSAPP_API_BASE_URL}/read",
            json={"chat_jid": "123456789@s.whatsapp.net", "message_ids": ["msg1", "msg2"]}
        )

    @patch('requests.post')
    def test_set_presence_success(self, mock_post):
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "Presence updated"}
        mock_post.return_value = mock_response
        
        # Call function
        success, message = whatsapp.set_presence("123456789@s.whatsapp.net", True, "audio")
        
        # Assertions
        self.assertTrue(success)
        self.assertEqual(message, "Presence updated")
        mock_post.assert_called_once_with(
            f"{whatsapp.WHATSAPP_API_BASE_URL}/presence",
            json={"chat_jid": "123456789@s.whatsapp.net", "is_typing": True, "media_type": "audio"}
        )

    @patch('sqlite3.connect')
    def test_listen_for_messages_backlog(self, mock_connect):
        # Mock DB response
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Return two messages, first is already processed
        # row: id, chat_jid, sender, content, timestamp, chat_name, media_type
        mock_cursor.fetchall.return_value = [
            ("old_msg", "jid", "sender", "hi", "2026-01-01", "name", ""),
            ("new_msg", "jid", "sender", "hello", "2026-01-02", "name", "")
        ]
        
        # Mock load_agent_state to return only the old message as processed
        with patch('whatsapp.load_agent_state', return_value={"processed_ids": ["old_msg"]}):
            # Call function with short timeout to avoid long loop
            result = whatsapp.listen_for_messages(["jid"], timeout_seconds=0.1)
            
            # Should return the new message
            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "new_msg")
            self.assertEqual(result["content"], "hello")

if __name__ == '__main__':
    unittest.main()
