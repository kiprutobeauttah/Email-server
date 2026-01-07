"""Server tab UI components"""

import tkinter as tk
from tkinter import ttk, scrolledtext


class ServerTab:
    """Server control tab"""
    
    def __init__(self, parent, gui):
        self.gui = gui
        self.create_ui(parent)
    
    def create_ui(self, parent):
        """Create server tab UI"""
        # Server controls
        control_frame = ttk.LabelFrame(parent, text="Server Control", padding=10)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(control_frame, text="Host:").grid(row=0, column=0, sticky='w', padx=5)
        self.gui.host_entry = ttk.Entry(control_frame, width=20)
        self.gui.host_entry.insert(0, "localhost")
        self.gui.host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Port:").grid(row=0, column=2, sticky='w', padx=5)
        self.gui.port_entry = ttk.Entry(control_frame, width=10)
        self.gui.port_entry.insert(0, "1025")
        self.gui.port_entry.grid(row=0, column=3, padx=5)
        
        self.gui.start_btn = ttk.Button(control_frame, text="Start Server", 
                                        command=self.gui.start_server)
        self.gui.start_btn.grid(row=0, column=4, padx=5)
        
        self.gui.stop_btn = ttk.Button(control_frame, text="Stop Server", 
                                       command=self.gui.stop_server, state='disabled')
        self.gui.stop_btn.grid(row=0, column=5, padx=5)
        
        self.gui.status_label = ttk.Label(control_frame, text="Status: Stopped", 
                                          foreground="red")
        self.gui.status_label.grid(row=1, column=0, columnspan=6, pady=5)
        
        # Server log
        log_frame = ttk.LabelFrame(parent, text="Server Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.gui.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD)
        self.gui.log_text.pack(fill='both', expand=True)
