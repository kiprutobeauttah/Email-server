"""Email handler for incoming SMTP messages"""

from datetime import datetime
from email import message_from_bytes


class EmailHandler:
    """Handler for incoming SMTP messages"""
    
    def __init__(self, gui):
        self.gui = gui
    
    async def handle_DATA(self, server, session, envelope):
        """Process incoming email"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Parse email
            msg = message_from_bytes(envelope.content)
            subject = msg.get('Subject', 'No Subject')
            
            # Get body
            body = self._extract_body(msg)
            
            # Store email
            email_data = {
                'time': timestamp,
                'from': envelope.mail_from,
                'to': ', '.join(envelope.rcpt_tos),
                'subject': subject,
                'body': body,
                'peer': session.peer
            }
            
            self.gui.received_emails.append(email_data)
            
            # Update GUI (thread-safe)
            self.gui.root.after(0, self.gui.add_email_to_inbox, email_data)
            self.gui.root.after(0, self.gui.log, 
                f"Received email from {envelope.mail_from} - Subject: {subject}")
            
            return '250 Message accepted for delivery'
        except Exception as e:
            self.gui.root.after(0, self.gui.log, f"Error processing email: {str(e)}")
            return '550 Error processing message'
    
    def _extract_body(self, msg):
        """Extract email body from message"""
        if msg.is_multipart():
            body = ''
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return body
