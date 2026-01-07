from datetime import datetime
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
import os
from aiosmtpd.controller import Controller
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
            if msg.is_multipart():
                body = ''
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
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

class EmailServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Email Server")
        self.root.geometry("950x750")
        
        self.received_emails = []
        self.server_running = False
        self.smtp_controller = None
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.attachments = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Server tab
        server_frame = ttk.Frame(notebook)
        notebook.add(server_frame, text='Server')
        self.create_server_tab(server_frame)
        
        # Send Email tab
        send_frame = ttk.Frame(notebook)
        notebook.add(send_frame, text='Send Email')
        self.create_send_tab(send_frame)
        
        # Inbox tab
        inbox_frame = ttk.Frame(notebook)
        notebook.add(inbox_frame, text='Inbox')
        self.create_inbox_tab(inbox_frame)
        
    def create_server_tab(self, parent):
        # Server controls
        control_frame = ttk.LabelFrame(parent, text="Server Control", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(control_frame, text="Host:").grid(row=0, column=0, sticky='w', padx=5)
        self.host_entry = ttk.Entry(control_frame, width=20)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Port:").grid(row=0, column=2, sticky='w', padx=5)
        self.port_entry = ttk.Entry(control_frame, width=10)
        self.port_entry.insert(0, "1025")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        self.start_btn = ttk.Button(control_frame, text="Start Server", command=self.start_server)
        self.start_btn.grid(row=0, column=4, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Server", command=self.stop_server, state='disabled')
        self.stop_btn.grid(row=0, column=5, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=6, pady=5)
        
        # Server log
        log_frame = ttk.LabelFrame(parent, text="Server Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True)
        
    def create_send_tab(self, parent):
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        send_frame = ttk.Frame(canvas)
        
        send_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=send_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # SMTP Configuration
        config_frame = ttk.LabelFrame(send_frame, text="SMTP Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=10)
        
        # Mode selection
        mode_frame = ttk.Frame(config_frame)
        mode_frame.pack(fill='x', pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side='left', padx=5)
        self.smtp_mode = tk.StringVar(value="local")
        ttk.Radiobutton(mode_frame, text="Local (Testing)", variable=self.smtp_mode, 
                       value="local", command=self.toggle_smtp_config).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text="Direct Send (No Auth)", variable=self.smtp_mode, 
                       value="direct", command=self.toggle_smtp_config).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text="Gmail SMTP (Authenticated)", variable=self.smtp_mode, 
                       value="external", command=self.toggle_smtp_config).pack(side='left', padx=5)
        
        # External SMTP settings
        self.external_config_frame = ttk.Frame(config_frame)
        
        # SMTP Server
        smtp_server_frame = ttk.Frame(self.external_config_frame)
        smtp_server_frame.pack(fill='x', pady=2)
        ttk.Label(smtp_server_frame, text="SMTP Server:").pack(side='left', padx=5)
        self.smtp_server_entry = ttk.Entry(smtp_server_frame, width=25)
        self.smtp_server_entry.insert(0, "smtp.gmail.com")
        self.smtp_server_entry.pack(side='left', padx=5)
        
        ttk.Label(smtp_server_frame, text="Port:").pack(side='left', padx=5)
        self.smtp_port_entry = ttk.Entry(smtp_server_frame, width=8)
        self.smtp_port_entry.insert(0, "587")
        self.smtp_port_entry.pack(side='left', padx=5)
        
        # Authentication
        auth_frame = ttk.Frame(self.external_config_frame)
        auth_frame.pack(fill='x', pady=2)
        ttk.Label(auth_frame, text="Email:").pack(side='left', padx=5)
        self.smtp_email_entry = ttk.Entry(auth_frame, width=30)
        self.smtp_email_entry.pack(side='left', padx=5)
        
        ttk.Label(auth_frame, text="Password:").pack(side='left', padx=5)
        self.smtp_password_entry = ttk.Entry(auth_frame, width=25, show="*")
        self.smtp_password_entry.pack(side='left', padx=5)
        
        ttk.Button(auth_frame, text="Test Connection", 
                  command=self.test_smtp_connection).pack(side='left', padx=5)
        
        # Help text
        help_text = ttk.Label(self.external_config_frame, 
                             text="Gmail: Use App Password (not regular password). Enable 2FA at myaccount.google.com/apppasswords",
                             foreground="blue", wraplength=700, font=('TkDefaultFont', 8))
        help_text.pack(fill='x', pady=5)
        
        # Direct send warning
        self.direct_warning_frame = ttk.Frame(config_frame)
        warning_label = ttk.Label(self.direct_warning_frame,
                                 text="⚠️ Direct Send: Emails will likely go to spam or be rejected. No authentication required.",
                                 foreground="orange", wraplength=700, font=('TkDefaultFont', 9, 'bold'))
        warning_label.pack(fill='x', pady=5)
        
        # Email fields frame
        fields_frame = ttk.LabelFrame(send_frame, text="Email Details", padding=10)
        fields_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # From
        ttk.Label(fields_frame, text="From:").grid(row=0, column=0, sticky='w', pady=5)
        self.from_entry = ttk.Entry(fields_frame, width=60)
        self.from_entry.insert(0, "sender@example.com")
        self.from_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        # To
        ttk.Label(fields_frame, text="To:").grid(row=1, column=0, sticky='w', pady=5)
        self.to_entry = ttk.Entry(fields_frame, width=60)
        self.to_entry.insert(0, "recipient@example.com")
        self.to_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        
        # CC
        ttk.Label(fields_frame, text="CC:").grid(row=2, column=0, sticky='w', pady=5)
        self.cc_entry = ttk.Entry(fields_frame, width=60)
        self.cc_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        
        # BCC
        ttk.Label(fields_frame, text="BCC:").grid(row=3, column=0, sticky='w', pady=5)
        self.bcc_entry = ttk.Entry(fields_frame, width=60)
        self.bcc_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=5)
        
        # Subject
        ttk.Label(fields_frame, text="Subject:").grid(row=4, column=0, sticky='w', pady=5)
        self.subject_entry = ttk.Entry(fields_frame, width=60)
        self.subject_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=5)
        
        # Attachments
        attach_frame = ttk.LabelFrame(fields_frame, text="Attachments", padding=5)
        attach_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.attachment_listbox = tk.Listbox(attach_frame, height=3)
        self.attachment_listbox.pack(side='left', fill='both', expand=True)
        
        attach_btn_frame = ttk.Frame(attach_frame)
        attach_btn_frame.pack(side='right', fill='y', padx=(5, 0))
        
        ttk.Button(attach_btn_frame, text="Add File", 
                  command=self.add_attachment).pack(fill='x', pady=2)
        ttk.Button(attach_btn_frame, text="Remove", 
                  command=self.remove_attachment).pack(fill='x', pady=2)
        ttk.Button(attach_btn_frame, text="Clear All", 
                  command=self.clear_attachments).pack(fill='x', pady=2)
        
        # Message
        ttk.Label(fields_frame, text="Message:").grid(row=6, column=0, sticky='nw', pady=5)
        self.message_text = scrolledtext.ScrolledText(fields_frame, height=8, wrap=tk.WORD)
        self.message_text.grid(row=6, column=1, sticky='nsew', pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(fields_frame)
        button_frame.grid(row=7, column=1, sticky='e', pady=10)
        
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_send_form).pack(side='left', padx=5)
        self.send_btn = ttk.Button(button_frame, text="Send Email", 
                                   command=self.send_email)
        self.send_btn.pack(side='left', padx=5)
        
        fields_frame.columnconfigure(1, weight=1)
        fields_frame.rowconfigure(6, weight=1)
        
        # Initially hide external config
        self.toggle_smtp_config()
        
    def create_inbox_tab(self, parent):
        inbox_frame = ttk.Frame(parent, padding=10)
        inbox_frame.pack(fill='both', expand=True)
        
        # Email list with controls
        list_frame = ttk.LabelFrame(inbox_frame, text="Received Emails", padding=5)
        list_frame.pack(fill='both', expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill='x', pady=(0, 5))
        
        self.email_count_label = ttk.Label(toolbar, text="Emails: 0")
        self.email_count_label.pack(side='left', padx=5)
        
        ttk.Button(toolbar, text="Clear Inbox", command=self.clear_inbox).pack(side='right', padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_inbox).pack(side='right', padx=5)
        
        # Treeview for email list
        columns = ('Time', 'From', 'To', 'Subject')
        self.email_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=10)
        
        self.email_tree.heading('#0', text='#')
        self.email_tree.column('#0', width=40)
        self.email_tree.heading('Time', text='Time')
        self.email_tree.column('Time', width=150)
        self.email_tree.heading('From', text='From')
        self.email_tree.column('From', width=200)
        self.email_tree.heading('To', text='To')
        self.email_tree.column('To', width=200)
        self.email_tree.heading('Subject', text='Subject')
        self.email_tree.column('Subject', width=250)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.email_tree.yview)
        self.email_tree.configure(yscrollcommand=scrollbar.set)
        
        self.email_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.email_tree.bind('<<TreeviewSelect>>', self.on_email_select)
        
        # Email content
        content_frame = ttk.LabelFrame(inbox_frame, text="Email Content", padding=5)
        content_frame.pack(fill='both', expand=True, pady=10)
        
        self.content_text = scrolledtext.ScrolledText(content_frame, height=10, wrap=tk.WORD)
        self.content_text.pack(fill='both', expand=True)
        
    def log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def validate_email(self, email):
        """Validate email format"""
        return bool(self.email_pattern.match(email.strip()))
    
    def toggle_smtp_config(self):
        """Toggle SMTP configuration visibility"""
        if self.smtp_mode.get() == "external":
            self.external_config_frame.pack(fill='x', pady=5)
            self.direct_warning_frame.pack_forget()
        elif self.smtp_mode.get() == "direct":
            self.external_config_frame.pack_forget()
            self.direct_warning_frame.pack(fill='x', pady=5)
        else:
            self.external_config_frame.pack_forget()
            self.direct_warning_frame.pack_forget()
    
    def test_smtp_connection(self):
        """Test SMTP server connection"""
        server = self.smtp_server_entry.get().strip()
        port = self.smtp_port_entry.get().strip()
        email = self.smtp_email_entry.get().strip()
        password = self.smtp_password_entry.get()
        
        if not all([server, port, email, password]):
            messagebox.showerror("Error", "Please fill in all SMTP configuration fields")
            return
        
        try:
            port = int(port)
            self.log(f"Testing connection to {server}:{port}...")
            
            smtp = smtplib.SMTP(server, port, timeout=10)
            smtp.starttls()
            smtp.login(email, password)
            smtp.quit()
            
            messagebox.showinfo("Success", "SMTP connection successful!")
            self.log("SMTP connection test successful")
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Error", "Authentication failed. Check your email and password.\nFor Gmail, use an App Password.")
            self.log("SMTP authentication failed")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
            self.log(f"SMTP connection failed: {str(e)}")
        
    def start_server(self):
        host = self.host_entry.get().strip()
        
        try:
            port = int(self.port_entry.get())
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid port: {str(e)}")
            return
        
        self.log(f"Starting SMTP server on {host}:{port}...")
        
        try:
            # Start server in separate thread
            server_thread = threading.Thread(target=self.run_server, args=(host, port), daemon=True)
            server_thread.start()
            
            self.server_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.host_entry.config(state='disabled')
            self.port_entry.config(state='disabled')
            self.status_label.config(text=f"Status: Running on {host}:{port}", foreground="green")
            self.log("Server started successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            self.log(f"Error starting server: {str(e)}")
        
    def run_server(self, host, port):
        """Run SMTP server in background thread"""
        try:
            handler = EmailHandler(self)
            self.smtp_controller = Controller(handler, hostname=host, port=port)
            self.smtp_controller.start()
        except Exception as e:
            self.root.after(0, self.log, f"Server error: {str(e)}")
            self.root.after(0, messagebox.showerror, "Server Error", str(e))
            self.root.after(0, self.reset_server_ui)
        
    def stop_server(self):
        self.log("Stopping server...")
        try:
            if self.smtp_controller:
                self.smtp_controller.stop()
                self.smtp_controller = None
            self.log("Server stopped successfully")
        except Exception as e:
            self.log(f"Error stopping server: {str(e)}")
        finally:
            self.reset_server_ui()
    
    def reset_server_ui(self):
        """Reset server UI controls"""
        self.server_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.host_entry.config(state='normal')
        self.port_entry.config(state='normal')
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    def add_attachment(self):
        """Add file attachment"""
        files = filedialog.askopenfilenames(title="Select files to attach")
        for file_path in files:
            if file_path and file_path not in self.attachments:
                self.attachments.append(file_path)
                filename = os.path.basename(file_path)
                self.attachment_listbox.insert(tk.END, filename)
                self.log(f"Added attachment: {filename}")
    
    def remove_attachment(self):
        """Remove selected attachment"""
        selection = self.attachment_listbox.curselection()
        if selection:
            idx = selection[0]
            filename = self.attachment_listbox.get(idx)
            self.attachment_listbox.delete(idx)
            del self.attachments[idx]
            self.log(f"Removed attachment: {filename}")
    
    def clear_attachments(self):
        """Clear all attachments"""
        self.attachments.clear()
        self.attachment_listbox.delete(0, tk.END)
        if self.attachments:
            self.log("Cleared all attachments")
    
    def clear_send_form(self):
        """Clear the send email form"""
        self.from_entry.delete(0, tk.END)
        self.from_entry.insert(0, "sender@example.com")
        self.to_entry.delete(0, tk.END)
        self.to_entry.insert(0, "recipient@example.com")
        self.cc_entry.delete(0, tk.END)
        self.bcc_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.message_text.delete('1.0', tk.END)
        self.clear_attachments()
        self.log("Form cleared")
        
    def send_email(self):
        sender = self.from_entry.get().strip()
        recipient = self.to_entry.get().strip()
        cc = self.cc_entry.get().strip()
        bcc = self.bcc_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.message_text.get('1.0', tk.END).strip()
        
        # Validation
        if not sender or not recipient:
            messagebox.showerror("Error", "Please fill in From and To fields")
            return
        
        if not self.validate_email(sender):
            messagebox.showerror("Error", "Invalid sender email format")
            return
        
        # Validate all recipients
        recipients = [r.strip() for r in recipient.split(',')]
        for r in recipients:
            if not self.validate_email(r):
                messagebox.showerror("Error", f"Invalid recipient email format: {r}")
                return
        
        # Validate CC if provided
        cc_list = []
        if cc:
            cc_list = [c.strip() for c in cc.split(',')]
            for c in cc_list:
                if not self.validate_email(c):
                    messagebox.showerror("Error", f"Invalid CC email format: {c}")
                    return
        
        # Validate BCC if provided
        bcc_list = []
        if bcc:
            bcc_list = [b.strip() for b in bcc.split(',')]
            for b in bcc_list:
                if not self.validate_email(b):
                    messagebox.showerror("Error", f"Invalid BCC email format: {b}")
                    return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = recipient
            if cc:
                msg['Cc'] = cc
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            for file_path in self.attachments:
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 
                                      f'attachment; filename={os.path.basename(file_path)}')
                        msg.attach(part)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to attach {file_path}: {str(e)}")
                    return
            
            # Combine all recipients
            all_recipients = recipients + cc_list + bcc_list
            
            # Send based on mode
            if self.smtp_mode.get() == "local":
                # Local mode - use local server
                host = self.host_entry.get()
                port = int(self.port_entry.get())
                
                server = smtplib.SMTP(host, port, timeout=10)
                server.sendmail(sender, all_recipients, msg.as_string())
                server.quit()
                
                messagebox.showinfo("Success", "Email sent successfully to local server!")
                
            elif self.smtp_mode.get() == "direct":
                # Direct mode - send directly to recipient's mail server
                import dns.resolver
                
                sent_count = 0
                failed = []
                
                for recipient_email in all_recipients:
                    try:
                        # Extract domain from email
                        domain = recipient_email.split('@')[1]
                        
                        # Look up MX records
                        self.log(f"Looking up MX records for {domain}...")
                        mx_records = dns.resolver.resolve(domain, 'MX')
                        mx_host = str(mx_records[0].exchange).rstrip('.')
                        
                        self.log(f"Connecting to {mx_host}:25 for {recipient_email}...")
                        
                        # Connect to recipient's mail server
                        server = smtplib.SMTP(timeout=20)
                        server.set_debuglevel(1)  # Show debug info
                        
                        # Try to connect
                        try:
                            server.connect(mx_host, 25)
                        except Exception as conn_err:
                            # Try port 587 if 25 fails
                            self.log(f"Port 25 failed, trying port 587...")
                            server.connect(mx_host, 587)
                        
                        # Try EHLO with a proper hostname
                        server.ehlo('localhost.localdomain')
                        
                        # Try STARTTLS if available
                        if server.has_extn('STARTTLS'):
                            try:
                                server.starttls()
                                server.ehlo('localhost.localdomain')
                            except:
                                pass  # Continue without TLS
                        
                        # Send the email
                        server.sendmail(sender, [recipient_email], msg.as_string())
                        server.quit()
                        
                        sent_count += 1
                        self.log(f"✓ Sent to {recipient_email}")
                        
                    except smtplib.SMTPRecipientsRefused as e:
                        error_msg = f"Recipient refused (likely needs authentication)"
                        failed.append(f"{recipient_email}: {error_msg}")
                        self.log(f"✗ {recipient_email}: {error_msg}")
                    except smtplib.SMTPSenderRefused as e:
                        error_msg = f"Sender refused (server doesn't trust your address)"
                        failed.append(f"{recipient_email}: {error_msg}")
                        self.log(f"✗ {recipient_email}: {error_msg}")
                    except ConnectionRefusedError:
                        error_msg = "Connection refused (port 25 likely blocked by ISP)"
                        failed.append(f"{recipient_email}: {error_msg}")
                        self.log(f"✗ {recipient_email}: {error_msg}")
                    except Exception as e:
                        error_msg = str(e)
                        failed.append(f"{recipient_email}: {error_msg}")
                        self.log(f"✗ Failed to send to {recipient_email}: {error_msg}")
                
                if sent_count > 0:
                    msg_text = f"Sent to {sent_count} recipient(s)!\n\n"
                    msg_text += "Note: Email may be in spam folder or rejected by recipient's server."
                    if failed:
                        msg_text += f"\n\nFailed: {len(failed)}"
                    messagebox.showinfo("Partial Success" if failed else "Success", msg_text)
                else:
                    error_summary = "\n".join(failed[:3])
                    if "port 25" in error_summary.lower() or "connection refused" in error_summary.lower():
                        msg_text = "Direct sending failed!\n\n"
                        msg_text += "Common reasons:\n"
                        msg_text += "• Your ISP blocks port 25 (most do)\n"
                        msg_text += "• Mail servers require authentication\n"
                        msg_text += "• Your IP is not trusted\n\n"
                        msg_text += "Try using 'Gmail SMTP' mode instead."
                    else:
                        msg_text = f"Could not send to any recipients:\n\n{error_summary}"
                    messagebox.showerror("Failed", msg_text)
                    
            else:
                # External mode - use configured SMTP server
                smtp_server = self.smtp_server_entry.get().strip()
                smtp_port = int(self.smtp_port_entry.get())
                smtp_email = self.smtp_email_entry.get().strip()
                smtp_password = self.smtp_password_entry.get()
                
                if not all([smtp_server, smtp_email, smtp_password]):
                    messagebox.showerror("Error", "Please configure SMTP settings for external mode")
                    return
                
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.sendmail(sender, all_recipients, msg.as_string())
                server.quit()
                
                messagebox.showinfo("Success", f"Email sent successfully to {len(all_recipients)} recipient(s)!")
            
            self.log(f"Sent email to {recipient} - Subject: {subject}")
            if self.attachments:
                self.log(f"  with {len(self.attachments)} attachment(s)")
            
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Connection refused. Is the server running?")
            self.log("Error: Connection refused - server may not be running")
        except smtplib.SMTPAuthenticationError:
            messagebox.showerror("Error", "Authentication failed. Check your email and password.\nFor Gmail, use an App Password.")
            self.log("Error: SMTP authentication failed")
        except TimeoutError:
            messagebox.showerror("Error", "Connection timeout")
            self.log("Error: Connection timeout")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
            self.log(f"Error sending email: {str(e)}")
            
    def add_email_to_inbox(self, email_data):
        idx = len(self.received_emails)
        self.email_tree.insert('', 'end', text=str(idx), 
                              values=(email_data['time'], email_data['from'], 
                                     email_data['to'], email_data['subject']))
        self.update_email_count()
    
    def update_email_count(self):
        """Update email count label"""
        count = len(self.received_emails)
        self.email_count_label.config(text=f"Emails: {count}")
    
    def clear_inbox(self):
        """Clear all emails from inbox"""
        if not self.received_emails:
            messagebox.showinfo("Info", "Inbox is already empty")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all emails?"):
            self.received_emails.clear()
            for item in self.email_tree.get_children():
                self.email_tree.delete(item)
            self.content_text.delete('1.0', tk.END)
            self.update_email_count()
            self.log("Inbox cleared")
    
    def refresh_inbox(self):
        """Refresh inbox display"""
        for item in self.email_tree.get_children():
            self.email_tree.delete(item)
        
        for idx, email_data in enumerate(self.received_emails, 1):
            self.email_tree.insert('', 'end', text=str(idx), 
                                  values=(email_data['time'], email_data['from'], 
                                         email_data['to'], email_data['subject']))
        self.update_email_count()
        self.log("Inbox refreshed")
        
    def on_email_select(self, event):
        selection = self.email_tree.selection()
        if selection:
            item = self.email_tree.item(selection[0])
            idx = int(item['text']) - 1
            if 0 <= idx < len(self.received_emails):
                email_data = self.received_emails[idx]
                content = f"From: {email_data['from']}\n"
                content += f"To: {email_data['to']}\n"
                content += f"Subject: {email_data['subject']}\n"
                content += f"Time: {email_data['time']}\n"
                content += f"\n{email_data['body']}"
                
                self.content_text.delete('1.0', tk.END)
                self.content_text.insert('1.0', content)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailServerGUI(root)
    root.mainloop()
