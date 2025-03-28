#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import shutil
import logging
from main import match_urls, calculate_metrics, URLProcessor
from file_handler import (
    load_client_files,
    find_ahrefs_file,
    find_pickup_file,
    files_match_latest,
    get_latest_report
)
from visualization import create_distribution_charts
from client_manager import NewClientDialog
from file_dialog import FileImportDialog
from tkinterdnd2 import TkinterDnD
from utils import get_client_directory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BacklinkAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Backlink Analyzer")
        
        # Initialize URL processor
        self.url_processor = URLProcessor()
        
        # Get screen dimensions and set size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Setup UI components
        self.setup_client_selection()
        self.setup_results_area()
        
        # Load clients
        self.load_available_clients()

    def setup_client_selection(self):
        """Setup the client selection dropdown and buttons"""
        # Client selection frame
        selection_frame = ttk.LabelFrame(self.main_frame, text="Client Selection", padding="10")
        selection_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        selection_frame.columnconfigure(0, weight=1)
        
        # Controls container
        controls = ttk.Frame(selection_frame)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)
        
        # Client dropdown
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(
            controls, 
            textvariable=self.client_var,
            state="readonly",
            width=40
        )
        self.client_dropdown.grid(row=0, column=0, padx=5)
        
        # Button container
        btn_frame = ttk.Frame(controls)
        btn_frame.grid(row=0, column=1, sticky="e")
        
        # New Client button
        self.new_client_btn = ttk.Button(
            btn_frame,
            text="New Client",
            command=self.create_new_client,
            style="secondary.TButton"
        )
        self.new_client_btn.pack(side=LEFT, padx=2)
        
        # Update Files button
        self.update_files_btn = ttk.Button(
            btn_frame,
            text="Update Files",
            command=self.update_client_files,
            style="secondary.TButton"
        )
        self.update_files_btn.pack(side=LEFT, padx=2)
        
        # Analyze button
        self.analyze_btn = ttk.Button(
            btn_frame,
            text="Analyze",
            command=self.analyze_client,
            style="primary.TButton"
        )
        self.analyze_btn.pack(side=LEFT, padx=2)

    def setup_results_area(self):
        """Setup the area for displaying analysis results"""
        # Results container using notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text='Summary')
        
        # Configure summary frame grid
        self.summary_frame.columnconfigure(0, weight=1)
        self.summary_frame.rowconfigure(1, weight=1)
        
        # Metrics panel
        self.metrics_frame = ttk.LabelFrame(self.summary_frame, text="Metrics", padding="10")
        self.metrics_frame.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        
        # Configure metrics grid
        for i in range(3):
            self.metrics_frame.columnconfigure(i, weight=1)
        
        # Charts panel
        self.charts_frame = ttk.Frame(self.summary_frame)
        self.charts_frame.grid(row=1, column=0, sticky="nsew")
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)
        
        # Create metrics grid
        self.metric_labels = {}
        metrics = [
            ('Stacker Links', 'Total number of Stacker links'),
            ('Non-Stacker Links', 'Total number of Non-Stacker links'),
            ('Average Stacker DR', 'Average DR for Stacker links'),
            ('Average Non-Stacker DR', 'Average DR for Non-Stacker links'),
            ('Stacker Link Weight Gain', 'Total link weight for Stacker links'),
            ('Non-Stacker Link Weight Gain', 'Total link weight for Non-Stacker links')
        ]
        
        for i, (name, desc) in enumerate(metrics):
            frame = ttk.Frame(self.metrics_frame)
            frame.grid(row=i//3, column=i%3, padx=5, pady=2, sticky="nsew")
            
            ttk.Label(frame, text=f"{name}:", font=("Helvetica", 10, "bold")).pack(anchor=W)
            ttk.Label(frame, text=desc, font=("Helvetica", 8)).pack(anchor=W)
            
            value_label = ttk.Label(frame, text="-", font=("Helvetica", 12))
            value_label.pack(anchor=W)
            self.metric_labels[name] = value_label

    def create_new_client(self):
        """Open the new client dialog"""
        dialog = NewClientDialog(self.root)
        self.root.wait_window(dialog.dialog)
        self.load_available_clients()
        
    def update_client_files(self):
        """Update files for existing client"""
        client = self.client_var.get()
        if not client:
            messagebox.showwarning("Warning", "Please select a client")
            return
            
        dialog = FileImportDialog(self.root, client, self.on_files_updated)
        self.root.wait_window(dialog.dialog)
        
    def on_files_updated(self, staged_files):
        """Handle file update completion"""
        self.analyze_client()

    def create_charts(self, df):
        """Create analysis charts"""
        # Clear previous charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Create distribution charts
        dist_fig = create_distribution_charts(df)
        dist_canvas = FigureCanvasTkAgg(dist_fig, master=self.charts_frame)
        dist_canvas.draw()
        canvas_widget = dist_canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        
        # Bind resize event
        self.root.bind('<Configure>', lambda e: self.on_window_resize())

    def on_window_resize(self):
        """Handle window resize events"""
        try:
            plt.close('all')
            for widget in self.charts_frame.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for child in widget.winfo_children():
                        for canvas in child.winfo_children():
                            if hasattr(canvas, 'draw'):
                                canvas.draw()
        except:
            pass

    def load_available_clients(self):
        """Load available clients into the dropdown"""
        try:
            client_dir = get_client_directory()
            
            clients = [d for d in os.listdir(client_dir) 
                      if os.path.isdir(os.path.join(client_dir, d))
                      and not d.startswith('.')]
            
            self.client_dropdown['values'] = sorted(clients)
            if clients:
                self.client_dropdown.set(clients[0])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load clients: {str(e)}")

    def analyze_client(self):
        """Run analysis for selected client and update GUI"""
        client = self.client_var.get()
        if not client:
            messagebox.showwarning("Warning", "Please select a client")
            return
            
        try:
            # Load and process data
            client_path = os.path.join(get_client_directory(), client)
            ahrefs_df, pickup_df = load_client_files(get_client_directory(), client)
            if ahrefs_df is None or pickup_df is None:
                raise Exception("Failed to load client files")
            
            # Check if files match latest report
            current_files = {
                'ahrefs': find_ahrefs_file(client_path),
                'pickup': find_pickup_file(client_path)
            }
            
            if files_match_latest(client_path, current_files):
                # Use latest report instead of reprocessing
                latest_path, _ = get_latest_report(client_path)
                matched_df = pd.read_csv(os.path.join(latest_path, 'backlinks_analysis.csv'))
                logger.info(f"Using existing report from {os.path.basename(latest_path)}")
            else:
                # Process new data
                logger.info("Processing new data...")
                matched_df = match_urls(ahrefs_df, pickup_df)
                logger.info("URL matching complete")
                metrics = calculate_metrics(matched_df)
                logger.info("Metrics calculation complete")
                
                # Create new report directory
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_dir = os.path.join(client_path, 'reports', timestamp)
                os.makedirs(report_dir, exist_ok=True)
                
                # Save processed CSV
                results_path = os.path.join(report_dir, 'backlinks_analysis.csv')
                matched_df.to_csv(results_path, index=False)
                
                # Save metrics
                metrics_path = os.path.join(report_dir, 'metrics.txt')
                with open(metrics_path, 'w') as f:
                    for metric, value in metrics.items():
                        f.write(f"{metric}: {value}\n")
                
                # Copy input files
                for file_type, file_path in current_files.items():
                    if file_path:
                        shutil.copy2(file_path, report_dir)
            
            # Update display
            metrics = calculate_metrics(matched_df)
            for name, label in self.metric_labels.items():
                label.config(text=str(metrics.get(name, "-")))
            
            # Create charts
            self.create_charts(matched_df)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            logger.error(f"Error analyzing {client}: {str(e)}")

def main():
    root = TkinterDnD.Tk()
    style = ttk.Style(theme='litera')
    app = BacklinkAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()