#!/usr/bin/env python3

import os
import shutil
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Source and destination paths
SRC_DIR = r"C:\Users\merman\Desktop\stacker-chisel-desktop\stacker-chisel\clients"
DEST_DIR = r"C:\Users\merman\Desktop\Stacker\DofollowBacklinks\clients"

def should_process_directory(name):
    """Filter out non-client directories"""
    skip_dirs = {'.ipynb_checkpoints', 'multi', 'testclient', 'test_results'}
    return os.path.isdir(os.path.join(SRC_DIR, name)) and name not in skip_dirs and not name.endswith('.ipynb')

def should_copy_file(filename):
    """Check if file should be copied"""
    if filename.startswith('.~lock.'):  # Skip lock files
        return False
    if 'Backlink Overlap Analysis' in filename and filename.endswith('Ahrefs.csv'):
        return True
    if filename.startswith('custom_pickup_export_'):
        return True
    return False

def main():
    # Get list of client directories
    client_dirs = [d for d in os.listdir(SRC_DIR) if should_process_directory(d)]
    logger.info(f"Found {len(client_dirs)} client directories to process")
    
    for client in client_dirs:
        src_client_dir = os.path.join(SRC_DIR, client)
        dest_client_dir = os.path.join(DEST_DIR, client)
        
        # Create client directory
        os.makedirs(dest_client_dir, exist_ok=True)
        
        # Find and copy relevant files
        files_copied = 0
        for file in os.listdir(src_client_dir):
            if should_copy_file(file):
                src_file = os.path.join(src_client_dir, file)
                dest_file = os.path.join(dest_client_dir, file)
                shutil.copy2(src_file, dest_file)
                files_copied += 1
                logger.info(f"Copied {file} to {dest_client_dir}")
        
        if files_copied == 0:
            logger.warning(f"No relevant files found for {client}")
        elif files_copied == 1:
            logger.warning(f"Only found one file for {client}, might be missing data")
        else:
            logger.info(f"Successfully copied {files_copied} files for {client}")

if __name__ == "__main__":
    main()