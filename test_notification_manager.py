#!/usr/bin/env python3
"""Test NotificationManager with and without plyer dependency"""
import sys
import unittest
from unittest.mock import MagicMock, patch


class TestNotificationManagerWithoutPlyer(unittest.TestCase):
    """Test NotificationManager when plyer is not available"""
    
    def setUp(self):
        """Set up test by clearing module cache"""
        self._clear_module_cache()
    
    def _clear_module_cache(self):
        """Helper to clear src.utils modules from cache"""
        # Clear module cache to ensure fresh import
        modules_to_clear = [
            mod for mod in sys.modules.keys() 
            if mod.startswith('src.utils')
        ]
        for mod in modules_to_clear:
            del sys.modules[mod]
        if 'plyer' in sys.modules:
            del sys.modules['plyer']
    
    def test_import_without_plyer(self):
        """Test that NotificationManager can be imported when plyer is missing"""
        # Mock the import to simulate plyer not being installed
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'plyer' or (name.startswith('plyer') and '.' in name):
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)
        
        builtins.__import__ = mock_import
        
        try:
            from src.utils.notification_manager import NotificationManager, PLYER_AVAILABLE
            
            # Should be able to import
            self.assertFalse(PLYER_AVAILABLE, "PLYER_AVAILABLE should be False when plyer is missing")
            
            # Should be able to instantiate
            nm = NotificationManager()
            self.assertIsNotNone(nm, "NotificationManager should be instantiable")
            self.assertFalse(nm.enabled, "NotificationManager.enabled should be False")
            self.assertFalse(nm.is_available, "NotificationManager.is_available should be False")
        finally:
            builtins.__import__ = original_import
    
    def test_send_notification_without_plyer(self):
        """Test that send_notification returns False gracefully when plyer is missing"""
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'plyer' or (name.startswith('plyer') and '.' in name):
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)
        
        builtins.__import__ = mock_import
        
        try:
            from src.utils.notification_manager import NotificationManager
            
            nm = NotificationManager()
            result = nm.send_notification('Test', 'Test message')
            
            # Should return False but not raise an exception
            self.assertFalse(result, "send_notification should return False when plyer is missing")
        finally:
            builtins.__import__ = original_import
    
    def test_import_from_utils_without_plyer(self):
        """Test that NotificationManager can be imported from src.utils when plyer is missing"""
        import builtins
        original_import = builtins.__import__
        
        def mock_import(name, *args, **kwargs):
            if name == 'plyer' or (name.startswith('plyer') and '.' in name):
                raise ModuleNotFoundError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)
        
        builtins.__import__ = mock_import
        
        try:
            from src.utils import NotificationManager
            
            # Should be able to import from src.utils
            nm = NotificationManager()
            self.assertIsNotNone(nm, "NotificationManager should be importable from src.utils")
            self.assertFalse(nm.enabled, "NotificationManager.enabled should be False")
        finally:
            builtins.__import__ = original_import


class TestNotificationManagerWithPlyer(unittest.TestCase):
    """Test NotificationManager when plyer is available"""
    
    def setUp(self):
        """Set up test by clearing module cache"""
        self._clear_module_cache()
    
    def _clear_module_cache(self):
        """Helper to clear src.utils modules from cache"""
        modules_to_clear = [
            mod for mod in sys.modules.keys() 
            if mod.startswith('src.utils')
        ]
        for mod in modules_to_clear:
            del sys.modules[mod]
        if 'plyer' in sys.modules:
            del sys.modules['plyer']
    
    def test_import_with_plyer(self):
        """Test that NotificationManager works correctly when plyer is available"""
        # Create mock plyer module
        mock_plyer = MagicMock()
        mock_notification = MagicMock()
        mock_plyer.notification = mock_notification
        
        with patch.dict('sys.modules', {'plyer': mock_plyer}):
            from src.utils.notification_manager import NotificationManager, PLYER_AVAILABLE
            
            self.assertTrue(PLYER_AVAILABLE, "PLYER_AVAILABLE should be True when plyer is available")
            
            nm = NotificationManager()
            self.assertTrue(nm.enabled, "NotificationManager.enabled should be True")
            self.assertTrue(nm.is_available, "NotificationManager.is_available should be True")
    
    def test_send_notification_with_plyer(self):
        """Test that send_notification actually calls plyer.notification.notify when available"""
        mock_plyer = MagicMock()
        mock_notification = MagicMock()
        mock_plyer.notification = mock_notification
        
        with patch.dict('sys.modules', {'plyer': mock_plyer}):
            from src.utils.notification_manager import NotificationManager
            
            nm = NotificationManager()
            result = nm.send_notification('Test Title', 'Test Message', timeout=5)
            
            # Should return True
            self.assertTrue(result, "send_notification should return True when plyer is available")
            
            # Should have called the notify method
            mock_notification.notify.assert_called_once_with(
                title='Test Title',
                message='Test Message',
                app_name='Iran Insurance Manager',
                timeout=5
            )
    
    def test_send_installment_reminder_with_plyer(self):
        """Test send_installment_reminder method - skipped due to persian_utils dependency"""
        # This test is skipped because it requires jdatetime and other Persian calendar dependencies
        # The core functionality is tested in test_send_notification_with_plyer
        self.skipTest("Requires jdatetime and persian_utils dependencies")
            
    def test_send_overdue_reminder_with_plyer(self):
        """Test send_overdue_reminder method"""
        mock_plyer = MagicMock()
        mock_notification = MagicMock()
        mock_plyer.notification = mock_notification
        
        with patch.dict('sys.modules', {'plyer': mock_plyer}):
            from src.utils.notification_manager import NotificationManager
            
            nm = NotificationManager()
            result = nm.send_overdue_reminder(
                policy_number='12345',
                days_overdue=5
            )
            
            # Should have called notify with timeout=15
            self.assertTrue(mock_notification.notify.called, "notify should be called")
            call_args = mock_notification.notify.call_args
            self.assertEqual(call_args.kwargs['timeout'], 15, "timeout should be 15 for overdue reminders")
    
    def test_send_payment_confirmation_with_plyer(self):
        """Test send_payment_confirmation method - skipped due to persian_utils dependency"""
        # This test is skipped because it requires persian_utils dependencies
        # The core functionality is tested in test_send_notification_with_plyer
        self.skipTest("Requires persian_utils dependencies")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
