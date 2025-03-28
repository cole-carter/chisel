#!/usr/bin/env python3

import os
import shutil
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES
from datetime import datetime
import pandas as pd
from utils import get_client_directory

logger = logging.getLogger(__name__)

class FileImportDialog:
    def __init__(self, parent, client_name=None, on_complete=None):
        """
        Initialize file import dialog
        client_name: If provided, updates existing client. If None, files will be staged for new client
        on_complete: Callback function to run after successful file import
        """
        self.parent = parent
        self.client_name = client_name
        self.on_complete = on_complete
        self.staged_files = {'ahrefs': None, 'pickup': None}
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Import Files" if client_name else "Stage Files")
        self.dialog.tk.eval('package require tkdnd')
        
        # Center the dialog
        window_width = 600
        window_height = 400
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # File path variables
        self.ahrefs_file = tk.StringVar()
        self.pickup_file = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Client info (if updating existing client)
        if self.client_name:
            info_frame = ttk.LabelFrame(main_frame, text="Client Information", padding="10")
            info_frame.pack(fill=X, pady=(0, 20))
            ttk.Label(info_frame, text=f"Client: {self.client_name}").pack(anchor=W)
        
        # Files Frame
        files_frame = ttk.LabelFrame(main_frame, text="Drop Files", padding="10")
        files_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))
        
        # Ahrefs File Drop
        self.ahrefs_drop = ttk.Label(
            files_frame, 
            text="Drop Ahrefs Export File Here",
            relief="solid",
            padding=20
        )
        self.ahrefs_drop.pack(fill=X, pady=(0, 10))
        self.ahrefs_drop.drop_target_register(DND_FILES)
        self.ahrefs_drop.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, 'ahrefs'))
        
        self.ahrefs_label = ttk.Label(files_frame, textvariable=self.ahrefs_file)
        self.ahrefs_label.pack()
        
        # Pickup File Drop
        self.pickup_drop = ttk.Label(
            files_frame, 
            text="Drop Pickup Export File Here",
            relief="solid",
            padding=20
        )
        self.pickup_drop.pack(fill=X, pady=(20, 10))
        self.pickup_drop.drop_target_register(DND_FILES)
        self.pickup_drop.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, 'pickup'))
        
        self.pickup_label = ttk.Label(files_frame, textvariable=self.pickup_file)
        self.pickup_label.pack()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Button(
            btn_frame,
            text="Import" if self.client_name else "Stage Files",
            style="primary.TButton",
            command=self.process_files
        ).pack(side=RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy
        ).pack(side=RIGHT)
        
    def on_drop(self, event, file_type):
        """Handle file drop events"""
        file_path = event.data.strip('{}').strip('"')
        
        # Basic validation
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Invalid file path")
            return
        
        if not file_path.endswith('.csv'):
            messagebox.showerror("Error", "File must be a CSV")
            return
        
        try:
            # Validate file structure
            df = pd.read_csv(file_path)
            if file_type == 'ahrefs' and 'Referring page URL' not in df.columns:
                messagebox.showerror("Error", "Invalid Ahrefs file format")
                return
            if file_type == 'pickup' and 'URL' not in df.columns:
                messagebox.showerror("Error", "Invalid Pickup file format")
                return
            
            # Store file info
            self.staged_files[file_type] = {
                'path': file_path,
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
            }
            
            # Update UI
            if file_type == 'ahrefs':
                self.ahrefs_file.set(os.path.basename(file_path))
                self.ahrefs_drop.configure(foreground='green')
            else:
                self.pickup_file.set(os.path.basename(file_path))
                self.pickup_drop.configure(foreground='green')
                
        except Exception as e:
            messagebox.showerror("Error", f"Error validating file: {str(e)}")
            
    def process_files(self):
        """Process and store the files"""
        if not all(self.staged_files.values()):
            messagebox.showerror("Error", "Both files are required")
            return
            
        try:
            if self.client_name:
                # Move current files to reports directory with timestamp
                self._archive_current_files()
                
                # Import new files
                client_dir = os.path.join(get_client_directory(), self.client_name)
            else:
                # Just store staged files for later use
                if self.on_complete:
                    self.on_complete(self.staged_files)
                self.dialog.destroy()
                return
                
            # Copy new files
            for file_type, file_info in self.staged_files.items():
                timestamp = file_info['timestamp']
                src_path = file_info['path']
                filename = os.path.basename(src_path)
                dest_path = os.path.join(client_dir, filename)
                shutil.copy2(src_path, dest_path)
            
            messagebox.showinfo("Success", "Files imported successfully!")
            
            if self.on_complete:
                self.on_complete(self.staged_files)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing files: {str(e)}")
            
    def _archive_current_files(self):
        """Archive current client files to reports directory with timestamp"""
        if not self.client_name:
            return
            
        client_dir = os.path.join(get_client_directory(), self.client_name)
        reports_dir = os.path.join(client_dir, 'reports')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create archive directory
        archive_dir = os.path.join(reports_dir, timestamp)
        os.makedirs(archive_dir, exist_ok=True)
        
        # Move current files and reports
        for filename in os.listdir(client_dir):
            if filename.endswith('.csv') or filename == 'output':
                src_path = os.path.join(client_dir, filename)
                if os.path.isfile(src_path):
                    shutil.move(src_path, os.path.join(archive_dir, filename))
                else:
                    shutil.move(src_path, os.path.join(archive_dir, filename))
