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
    @patch('whatsapp.mark_as_read') # Mock the internal call
    def test_listen_for_messages_batch(self, mock_mark_read, mock_connect):
        # Mock DB response
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Return two messages, both new
        # row: id, chat_jid, sender, content, timestamp, chat_name, media_type
        mock_cursor.fetchall.return_value = [
            ("msg1", "jid1", "sender1", "hi", "2026-01-01", "name", ""),
            ("msg2", "jid1", "sender1", "how are you", "2026-01-02", "name", "")
        ]
        
        # Mock load_agent_state to return no processed messages
        with patch('whatsapp.load_agent_state', return_value={"processed_ids": []}):
            # Call function with short timeout
            result = whatsapp.listen_for_messages(["jid1"], timeout_seconds=0.1)
            
            # Assertions for batch structure
            self.assertIsNotNone(result)
            self.assertEqual(result["batch_count"], 2)
            self.assertIn("jid1", result["chats"])
            self.assertEqual(len(result["chats"]["jid1"]), 2)
            self.assertEqual(result["chats"]["jid1"][0]["id"], "msg1")
            self.assertEqual(result["chats"]["jid1"][1]["id"], "msg2")
            
            # Verify automated read receipt
            # Should be called once for jid1 with both message IDs
            mock_mark_read.assert_called_with("jid1", ["msg1", "msg2"])

    @patch('requests.post')
    @patch('whatsapp.set_presence') # Mock the internal call
    def test_send_message_automated_typing(self, mock_set_presence, mock_post):
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # Call function
        whatsapp.send_message("recipient", "message")
        
        # Verify automated typing calls
        # 1. typing=True before send
        # 2. typing=False after send
        self.assertEqual(mock_set_presence.call_count, 2)
        mock_set_presence.assert_any_call("recipient", True, "text")
        mock_set_presence.assert_any_call("recipient", False, "text")

    @patch('requests.post')
    @patch('whatsapp.set_presence')
    def test_send_message_with_reply(self, mock_set_presence, mock_post):
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response
        
        # Call function with reply_to_id
        whatsapp.send_message("recipient", "message", reply_to_id="msg123")
        
        # Verify payload contains reply_to_id
        mock_post.assert_called_with(
            f"{whatsapp.WHATSAPP_API_BASE_URL}/send",
            json={"recipient": "recipient", "message": "message", "reply_to_id": "msg123"}
        )

if __name__ == '__main__':
    unittest.main()
