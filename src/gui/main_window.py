"""Main GUI window for Email Server"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading
import os
import smtplib

from src.gui.server_tab import ServerTab
from src.gui.send_tab import SendTab
from src.gui.inbox_tab import InboxTab
from src.server_manager import ServerManager
from src.validators import EmailValidator
from src.smtp_sender import SMTPSender


class EmailServerGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Python Email Server")
        self.root.geometry("950x750")
        
        self.received_emails = []
        self.attachments = []
        self.server_manager = ServerManager(self)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create main notebook with tabs"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        server_frame = ttk.Frame(notebook)
        send_frame = ttk.Frame(notebook)
        inbox_frame = ttk.Frame(notebook)
        
        notebook.add(server_frame, text='Server')
        notebook.add(send_frame, text='Send Email')
        notebook.add(inbox_frame, text='Inbox')
        
        # Initialize tab components
        ServerTab(server_frame, self)
        SendTab(send_frame, self)
        InboxTab(inbox_frame, self)
    
    # Server methods
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def start_server(self):
        """Start SMTP server"""
        host = self.host_entry.get().strip()
        valid, port = EmailValidator.validate_port(self.port_entry.get())
        
        if not valid:
            messagebox.showerror("Error", f"Invalid port: {port}")
            return
        
        self.log(f"Starting SMTP server on {host}:{port}...")
        
        def run_server():
            success, message = self.server_manager.start(host, port)
            if not success:
                self.root.after(0, messagebox.showerror, "Server Error", message)
                self.root.after(0, self.reset_server_ui)
            else:
                self.root.after(0, self.log, message)
        
        threading.Thread(target=run_server, daemon=True).start()
        
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.host_entry.config(state='disabled')
        self.port_entry.config(state='disabled')
        self.status_label.config(text=f"Status: Running on {host}:{port}", 
                                foreground="green")
    
    def stop_server(self):
        """Stop SMTP server"""
        self.log("Stopping server...")
        success, message = self.server_manager.stop()
        self.log(message)
        self.reset_server_ui()
    
    def reset_server_ui(self):
        """Reset server UI controls"""
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.host_entry.config(state='normal')
        self.port_entry.config(state='normal')
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    # Send email methods
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
        """Send email based on selected mode"""
        sender = self.from_entry.get().strip()
        recipient = self.to_entry.get().strip()
        cc = self.cc_entry.get().strip()
        bcc = self.bcc_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.message_text.get('1.0', tk.END).strip()
        
        # Validate inputs
        if not sender or not recipient:
            messagebox.showerror("Error", "Please fill in From and To fields")
            return
        
        if not EmailValidator.validate_email(sender):
            messagebox.showerror("Error", "Invalid sender email format")
            return
        
        # Validate recipients
        valid, recipients = EmailValidator.validate_email_list(recipient)
        if not valid:
            messagebox.showerror("Error", f"Invalid recipient: {recipients[0]}")
            return
        
        # Validate CC
        cc_list = []
        if cc:
            valid, cc_list = EmailValidator.validate_email_list(cc)
            if not valid:
                messagebox.showerror("Error", f"Invalid CC: {cc_list[0]}")
                return
        
        # Validate BCC
        bcc_list = []
        if bcc:
            valid, bcc_list = EmailValidator.validate_email_list(bcc)
            if not valid:
                messagebox.showerror("Error", f"Invalid BCC: {bcc_list[0]}")
                return
        
        try:
            # Create message
            msg = SMTPSender.create_message(sender, recipient, cc, subject, 
                                           body, self.attachments)
            
            all_recipients = recipients + cc_list + bcc_list
            
            # Send based on mode
            if self.smtp_mode.get() == "local":
                host = self.host_entry.get()
                port = int(self.port_entry.get())
                success, message = SMTPSender.send_local(sender, all_recipients, 
                                                        msg, host, port)
                messagebox.showinfo("Success", message)
                
            elif self.smtp_mode.get() == "direct":
                sent_count, failed = SMTPSender.send_direct(sender, all_recipients, 
                                                           msg, self.log)
                if sent_count > 0:
                    msg_text = f"Sent to {sent_count} recipient(s)!\n\n"
                    msg_text += "Note: Email may be in spam folder."
                    if failed:
                        msg_text += f"\n\nFailed: {len(failed)}"
                    messagebox.showinfo("Success", msg_text)
                else:
                    error_summary = "\n".join(failed[:3])
                    messagebox.showerror("Failed", f"Could not send:\n\n{error_summary}")
                    
            else:  # external
                smtp_server = self.smtp_server_entry.get().strip()
                smtp_port = int(self.smtp_port_entry.get())
                smtp_email = self.smtp_email_entry.get().strip()
                smtp_password = self.smtp_password_entry.get()
                
                if not all([smtp_server, smtp_email, smtp_password]):
                    messagebox.showerror("Error", "Please configure SMTP settings")
                    return
                
                success, message = SMTPSender.send_authenticated(
                    sender, all_recipients, msg, smtp_server, smtp_port, 
                    smtp_email, smtp_password)
                messagebox.showinfo("Success", message)
            
            self.log(f"Sent email to {recipient} - Subject: {subject}")
            if self.attachments:
                self.log(f"  with {len(self.attachments)} attachment(s)")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
            self.log(f"Error sending email: {str(e)}")
    
    # Inbox methods
    def add_email_to_inbox(self, email_data):
        """Add email to inbox list"""
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
        """Handle email selection"""
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
