#!/usr/bin/env python3
"""
Python Email Server with GUI
Main entry point for the application
"""

import tkinter as tk
from src.gui import EmailServerGUI


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EmailServerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
