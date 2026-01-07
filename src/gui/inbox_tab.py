"""Inbox tab UI components"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class InboxTab:
    """Inbox tab for viewing received emails"""
    
    def __init__(self, parent, gui):
        self.gui = gui
        self.create_ui(parent)
    
    def create_ui(self, parent):
        """Create inbox tab UI"""
        inbox_frame = ttk.Frame(parent, padding=10)
        inbox_frame.pack(fill='both', expand=True)
        
        # Email list with controls
        list_frame = ttk.LabelFrame(inbox_frame, text="Received Emails", padding=5)
        list_frame.pack(fill='both', expand=True)
        
        # Toolbar
        self._create_toolbar(list_frame)
        
        # Email list
        self._create_email_list(list_frame)
        
        # Email content viewer
        self._create_content_viewer(inbox_frame)
    
    def _create_toolbar(self, parent):
        """Create toolbar with controls"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill='x', pady=(0, 5))
        
        self.gui.email_count_label = ttk.Label(toolbar, text="Emails: 0")
        self.gui.email_count_label.pack(side='left', padx=5)
        
        ttk.Button(toolbar, text="Clear Inbox", 
                  command=self.gui.clear_inbox).pack(side='right', padx=5)
        ttk.Button(toolbar, text="Refresh", 
                  command=self.gui.refresh_inbox).pack(side='right', padx=5)
    
    def _create_email_list(self, parent):
        """Create email list treeview"""
        columns = ('Time', 'From', 'To', 'Subject')
        self.gui.email_tree = ttk.Treeview(parent, columns=columns, 
                                           show='tree headings', height=10)
        
        self.gui.email_tree.heading('#0', text='#')
        self.gui.email_tree.column('#0', width=40)
        self.gui.email_tree.heading('Time', text='Time')
        self.gui.email_tree.column('Time', width=150)
        self.gui.email_tree.heading('From', text='From')
        self.gui.email_tree.column('From', width=200)
        self.gui.email_tree.heading('To', text='To')
        self.gui.email_tree.column('To', width=200)
        self.gui.email_tree.heading('Subject', text='Subject')
        self.gui.email_tree.column('Subject', width=250)
        
        scrollbar = ttk.Scrollbar(parent, orient='vertical', 
                                 command=self.gui.email_tree.yview)
        self.gui.email_tree.configure(yscrollcommand=scrollbar.set)
        
        self.gui.email_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.gui.email_tree.bind('<<TreeviewSelect>>', self.gui.on_email_select)
    
    def _create_content_viewer(self, parent):
        """Create email content viewer"""
        content_frame = ttk.LabelFrame(parent, text="Email Content", padding=5)
        content_frame.pack(fill='both', expand=True, pady=10)
        
        self.gui.content_text = scrolledtext.ScrolledText(content_frame, 
                                                          height=10, wrap=tk.WORD)
        self.gui.content_text.pack(fill='both', expand=True)
