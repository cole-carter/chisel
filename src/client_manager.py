#!/usr/bin/env python3

import os
import shutil
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from utils import get_client_directory
from file_dialog import FileImportDialog

logger = logging.getLogger(__name__)

class NewClientDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Client")
        
        # Center the dialog
        window_width = 400
        window_height = 200
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.client_name = tk.StringVar()
        self.staged_files = None
        self.parent = parent
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Client Name
        name_frame = ttk.LabelFrame(main_frame, text="Client Information", padding="10")
        name_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(name_frame, text="Client Name:").pack(anchor=W)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.client_name)
        self.name_entry.pack(fill=X, pady=(5, 0))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Next",
            style="primary.TButton",
            command=self.create_client
        ).pack(side=RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=RIGHT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.create_client())
        
        # Focus name entry
        self.name_entry.focus()
        
    def create_client(self):
        """Create new client directory"""
        client_name = self.client_name.get().strip()
        
        if not client_name:
            messagebox.showerror("Error", "Client name is required")
            return
            
        try:
            # Setup directory structure
            client_dir = os.path.join(get_client_directory(), client_name)
            
            if os.path.exists(client_dir):
                messagebox.showerror("Error", "Client already exists")
                return
            
            # Create directory structure
            os.makedirs(client_dir)
            os.makedirs(os.path.join(client_dir, 'output'), exist_ok=True)
            os.makedirs(os.path.join(client_dir, 'reports'), exist_ok=True)
            
            # Open file dialog
            self.dialog.destroy()
            FileImportDialog(
                self.parent,
                None,
                lambda files: self._finish_client_creation(client_name, files)
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating client: {str(e)}")
            
    def _finish_client_creation(self, client_name, staged_files):
        """Complete client creation with staged files"""
        try:
            client_dir = os.path.join(get_client_directory(), client_name)
            
            # Copy staged files
            for file_type, file_info in staged_files.items():
                src_path = file_info['path']
                filename = os.path.basename(src_path)
                dest_path = os.path.join(client_dir, filename)
                shutil.copy2(src_path, dest_path)
            
            logger.info(f"Created new client: {client_name}")
            messagebox.showinfo("Success", "Client created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error finalizing client: {str(e)}")
            # Cleanup on error
            shutil.rmtree(client_dir, ignore_errors=True)