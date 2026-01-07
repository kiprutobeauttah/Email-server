"""SMTP server management"""

import threading
from aiosmtpd.controller import Controller
from src.email_handler import EmailHandler


class ServerManager:
    """Manages the SMTP server lifecycle"""
    
    def __init__(self, gui):
        self.gui = gui
        self.smtp_controller = None
        self.server_running = False
    
    def start(self, host, port):
        """Start SMTP server in background thread"""
        try:
            handler = EmailHandler(self.gui)
            self.smtp_controller = Controller(handler, hostname=host, port=port)
            self.smtp_controller.start()
            self.server_running = True
            return True, "Server started successfully"
        except Exception as e:
            return False, str(e)
    
    def stop(self):
        """Stop SMTP server"""
        try:
            if self.smtp_controller:
                self.smtp_controller.stop()
                self.smtp_controller = None
            self.server_running = False
            return True, "Server stopped successfully"
        except Exception as e:
            return False, str(e)
    
    def is_running(self):
        """Check if server is running"""
        return self.server_running
