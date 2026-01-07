"""Send email tab UI components"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class SendTab:
    """Send email tab"""
    
    def __init__(self, parent, gui):
        self.gui = gui
        self.create_ui(parent)
    
    def create_ui(self, parent):
        """Create send tab UI"""
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
        self._create_smtp_config(send_frame)
        
        # Email fields
        self._create_email_fields(send_frame)
    
    def _create_smtp_config(self, parent):
        """Create SMTP configuration section"""
        config_frame = ttk.LabelFrame(parent, text="SMTP Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=10)
        
        # Mode selection
        mode_frame = ttk.Frame(config_frame)
        mode_frame.pack(fill='x', pady=5)
        
        ttk.Label(mode_frame, text="Mode:").pack(side='left', padx=5)
        self.gui.smtp_mode = tk.StringVar(value="local")
        ttk.Radiobutton(mode_frame, text="Local (Testing)", 
                       variable=self.gui.smtp_mode, value="local", 
                       command=self.gui.toggle_smtp_config).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text="Direct Send (No Auth)", 
                       variable=self.gui.smtp_mode, value="direct", 
                       command=self.gui.toggle_smtp_config).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text="Gmail SMTP (Authenticated)", 
                       variable=self.gui.smtp_mode, value="external", 
                       command=self.gui.toggle_smtp_config).pack(side='left', padx=5)
        
        # External SMTP settings
        self.gui.external_config_frame = ttk.Frame(config_frame)
        self._create_external_config(self.gui.external_config_frame)
        
        # Direct send warning
        self.gui.direct_warning_frame = ttk.Frame(config_frame)
        warning_label = ttk.Label(self.gui.direct_warning_frame,
                                 text="⚠️ Direct Send: Emails will likely go to spam or be rejected. No authentication required.",
                                 foreground="orange", wraplength=700, 
                                 font=('TkDefaultFont', 9, 'bold'))
        warning_label.pack(fill='x', pady=5)
    
    def _create_external_config(self, parent):
        """Create external SMTP configuration"""
        # SMTP Server
        smtp_server_frame = ttk.Frame(parent)
        smtp_server_frame.pack(fill='x', pady=2)
        ttk.Label(smtp_server_frame, text="SMTP Server:").pack(side='left', padx=5)
        self.gui.smtp_server_entry = ttk.Entry(smtp_server_frame, width=25)
        self.gui.smtp_server_entry.insert(0, "smtp.gmail.com")
        self.gui.smtp_server_entry.pack(side='left', padx=5)
        
        ttk.Label(smtp_server_frame, text="Port:").pack(side='left', padx=5)
        self.gui.smtp_port_entry = ttk.Entry(smtp_server_frame, width=8)
        self.gui.smtp_port_entry.insert(0, "587")
        self.gui.smtp_port_entry.pack(side='left', padx=5)
        
        # Authentication
        auth_frame = ttk.Frame(parent)
        auth_frame.pack(fill='x', pady=2)
        ttk.Label(auth_frame, text="Email:").pack(side='left', padx=5)
        self.gui.smtp_email_entry = ttk.Entry(auth_frame, width=30)
        self.gui.smtp_email_entry.pack(side='left', padx=5)
        
        ttk.Label(auth_frame, text="Password:").pack(side='left', padx=5)
        self.gui.smtp_password_entry = ttk.Entry(auth_frame, width=25, show="*")
        self.gui.smtp_password_entry.pack(side='left', padx=5)
        
        ttk.Button(auth_frame, text="Test Connection", 
                  command=self.gui.test_smtp_connection).pack(side='left', padx=5)
        
        # Help text
        help_text = ttk.Label(parent, 
                             text="Gmail: Use App Password (not regular password). Enable 2FA at myaccount.google.com/apppasswords",
                             foreground="blue", wraplength=700, 
                             font=('TkDefaultFont', 8))
        help_text.pack(fill='x', pady=5)
    
    def _create_email_fields(self, parent):
        """Create email input fields"""
        fields_frame = ttk.LabelFrame(parent, text="Email Details", padding=10)
        fields_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # From
        ttk.Label(fields_frame, text="From:").grid(row=0, column=0, sticky='w', pady=5)
        self.gui.from_entry = ttk.Entry(fields_frame, width=60)
        self.gui.from_entry.insert(0, "sender@example.com")
        self.gui.from_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        # To
        ttk.Label(fields_frame, text="To:").grid(row=1, column=0, sticky='w', pady=5)
        self.gui.to_entry = ttk.Entry(fields_frame, width=60)
        self.gui.to_entry.insert(0, "recipient@example.com")
        self.gui.to_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=5)
        
        # CC
        ttk.Label(fields_frame, text="CC:").grid(row=2, column=0, sticky='w', pady=5)
        self.gui.cc_entry = ttk.Entry(fields_frame, width=60)
        self.gui.cc_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        
        # BCC
        ttk.Label(fields_frame, text="BCC:").grid(row=3, column=0, sticky='w', pady=5)
        self.gui.bcc_entry = ttk.Entry(fields_frame, width=60)
        self.gui.bcc_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=5)
        
        # Subject
        ttk.Label(fields_frame, text="Subject:").grid(row=4, column=0, sticky='w', pady=5)
        self.gui.subject_entry = ttk.Entry(fields_frame, width=60)
        self.gui.subject_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=5)
        
        # Attachments
        self._create_attachments_section(fields_frame)
        
        # Message
        ttk.Label(fields_frame, text="Message:").grid(row=6, column=0, sticky='nw', pady=5)
        self.gui.message_text = scrolledtext.ScrolledText(fields_frame, height=8, wrap=tk.WORD)
        self.gui.message_text.grid(row=6, column=1, sticky='nsew', pady=5, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(fields_frame)
        button_frame.grid(row=7, column=1, sticky='e', pady=10)
        
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.gui.clear_send_form).pack(side='left', padx=5)
        self.gui.send_btn = ttk.Button(button_frame, text="Send Email", 
                                       command=self.gui.send_email)
        self.gui.send_btn.pack(side='left', padx=5)
        
        fields_frame.columnconfigure(1, weight=1)
        fields_frame.rowconfigure(6, weight=1)
    
    def _create_attachments_section(self, parent):
        """Create attachments section"""
        attach_frame = ttk.LabelFrame(parent, text="Attachments", padding=5)
        attach_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.gui.attachment_listbox = tk.Listbox(attach_frame, height=3)
        self.gui.attachment_listbox.pack(side='left', fill='both', expand=True)
        
        attach_btn_frame = ttk.Frame(attach_frame)
        attach_btn_frame.pack(side='right', fill='y', padx=(5, 0))
        
        ttk.Button(attach_btn_frame, text="Add File", 
                  command=self.gui.add_attachment).pack(fill='x', pady=2)
        ttk.Button(attach_btn_frame, text="Remove", 
                  command=self.gui.remove_attachment).pack(fill='x', pady=2)
        ttk.Button(attach_btn_frame, text="Clear All", 
                  command=self.gui.clear_attachments).pack(fill='x', pady=2)
