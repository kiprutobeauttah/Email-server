"""SMTP email sending functionality"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


class SMTPSender:
    """Handles sending emails via different methods"""
    
    @staticmethod
    def send_local(sender, recipients, msg, host, port):
        """Send email to local SMTP server"""
        server = smtplib.SMTP(host, port, timeout=10)
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        return True, "Email sent successfully to local server!"
    
    @staticmethod
    def send_direct(sender, recipients, msg, logger):
        """Send email directly to recipient's mail server"""
        import dns.resolver
        
        sent_count = 0
        failed = []
        
        for recipient_email in recipients:
            try:
                # Extract domain from email
                domain = recipient_email.split('@')[1]
                
                # Look up MX records
                logger(f"Looking up MX records for {domain}...")
                mx_records = dns.resolver.resolve(domain, 'MX')
                mx_host = str(mx_records[0].exchange).rstrip('.')
                
                logger(f"Connecting to {mx_host}:25 for {recipient_email}...")
                
                # Connect to recipient's mail server
                server = smtplib.SMTP(timeout=20)
                server.set_debuglevel(1)
                
                # Try to connect
                try:
                    server.connect(mx_host, 25)
                except Exception:
                    logger(f"Port 25 failed, trying port 587...")
                    server.connect(mx_host, 587)
                
                # Try EHLO with a proper hostname
                server.ehlo('localhost.localdomain')
                
                # Try STARTTLS if available
                if server.has_extn('STARTTLS'):
                    try:
                        server.starttls()
                        server.ehlo('localhost.localdomain')
                    except:
                        pass
                
                # Send the email
                server.sendmail(sender, [recipient_email], msg.as_string())
                server.quit()
                
                sent_count += 1
                logger(f"✓ Sent to {recipient_email}")
                
            except smtplib.SMTPRecipientsRefused:
                error_msg = "Recipient refused (likely needs authentication)"
                failed.append(f"{recipient_email}: {error_msg}")
                logger(f"✗ {recipient_email}: {error_msg}")
            except smtplib.SMTPSenderRefused:
                error_msg = "Sender refused (server doesn't trust your address)"
                failed.append(f"{recipient_email}: {error_msg}")
                logger(f"✗ {recipient_email}: {error_msg}")
            except ConnectionRefusedError:
                error_msg = "Connection refused (port 25 likely blocked by ISP)"
                failed.append(f"{recipient_email}: {error_msg}")
                logger(f"✗ {recipient_email}: {error_msg}")
            except Exception as e:
                error_msg = str(e)
                failed.append(f"{recipient_email}: {error_msg}")
                logger(f"✗ Failed to send to {recipient_email}: {error_msg}")
        
        return sent_count, failed
    
    @staticmethod
    def send_authenticated(sender, recipients, msg, smtp_server, smtp_port, smtp_email, smtp_password):
        """Send email via authenticated SMTP server (e.g., Gmail)"""
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        return True, f"Email sent successfully to {len(recipients)} recipient(s)!"
    
    @staticmethod
    def create_message(sender, recipient, cc, subject, body, attachments):
        """Create MIME message with attachments"""
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        if cc:
            msg['Cc'] = cc
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        for file_path in attachments:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 
                              f'attachment; filename={os.path.basename(file_path)}')
                msg.attach(part)
        
        return msg
