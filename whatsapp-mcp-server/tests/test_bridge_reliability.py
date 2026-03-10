import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import requests

# Add parent directory to sys.path to import whatsapp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import whatsapp

class TestBridgeReliability(unittest.TestCase):
    
    @patch('requests.get')
    def test_check_bridge_health_success(self, mock_get):
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "connected": True}
        mock_get.return_value = mock_response
        
        # Call function
        health = whatsapp.check_bridge_health()
        
        # Assertions
        self.assertTrue(health["success"])
        self.assertTrue(health["connected"])
        mock_get.assert_called_once_with(f"{whatsapp.WHATSAPP_API_BASE_URL}/health", timeout=2)

    @patch('requests.get')
    def test_check_bridge_health_failure(self, mock_get):
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection refused")
        
        # Call function
        health = whatsapp.check_bridge_health()
        
        # Assertions
        self.assertFalse(health["success"])
        self.assertIn("Connection refused", health["error"])

    @patch('whatsapp.check_bridge_health')
    def test_ensure_bridge_running_already_ok(self, mock_health):
        mock_health.return_value = {"success": True, "connected": True}
        
        # Should return True without doing anything
        result = whatsapp.ensure_bridge_running()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
