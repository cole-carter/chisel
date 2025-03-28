#!/usr/bin/env python3

import os
import logging
from datetime import datetime
import pandas as pd
import hashlib
from utils import get_project_root, get_client_directory

logger = logging.getLogger(__name__)

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_latest_report(client_dir):
    """Get the most recent report directory and file hashes"""
    reports_dir = os.path.join(client_dir, 'reports')
    if not os.path.exists(reports_dir):
        return None, None
        
    report_dirs = [d for d in os.listdir(reports_dir) 
                  if os.path.isdir(os.path.join(reports_dir, d))]
    
    if not report_dirs:
        return None, None
        
    latest_dir = max(report_dirs)
    latest_path = os.path.join(reports_dir, latest_dir)
    
    # Get file hashes from the latest report
    csv_files = [f for f in os.listdir(latest_path) if f.endswith('.csv')]
    file_hashes = {}
    for file in csv_files:
        file_path = os.path.join(latest_path, file)
        file_hashes[file] = calculate_file_hash(file_path)
        
    return latest_path, file_hashes

def files_match_latest(client_dir, current_files):
    """Check if current files match the latest report"""
    latest_path, latest_hashes = get_latest_report(client_dir)
    if not latest_hashes:
        return False
        
    current_hashes = {
        os.path.basename(file): calculate_file_hash(file)
        for file in current_files.values()
    }
    
    return current_hashes == latest_hashes

def read_csv(file_path):
    """Read CSV file"""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully read CSV file: {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        raise

def find_ahrefs_file(client_dir):
    """Find Ahrefs file using any supported naming pattern"""
    for file in os.listdir(client_dir):
        if file.endswith('Ahrefs.csv') or '-backlinks-subdomains_' in file:
            return os.path.join(client_dir, file)
    return None

def find_pickup_file(client_dir):
    """Find pickup export file"""
    for file in os.listdir(client_dir):
        if file.startswith('custom_pickup_export'):
            return os.path.join(client_dir, file)
    return None

def load_client_files(client_dir, client):
    """Load both Ahrefs and pickup files for a client"""
    client_path = os.path.join(client_dir, client)
    
    try:
        # Find files
        ahrefs_file = find_ahrefs_file(client_path)
        pickup_file = find_pickup_file(client_path)
        
        if not ahrefs_file or not pickup_file:
            logger.error(f"Missing required files for {client}")
            return None, None
        
        # Read files
        ahrefs_df = read_csv(ahrefs_file)
        pickup_df = read_csv(pickup_file)
        
        # Clean up Ahrefs dataframe to only keep necessary columns
        keep_columns = [
            'Referring page URL',
            'Domain rating',
            'Target URL'
        ]
        ahrefs_df = ahrefs_df[keep_columns]
        
        logger.info(f"Loaded {client}: {len(ahrefs_df)} backlinks, {len(pickup_df)} pickups")
        return ahrefs_df, pickup_df
        
    except Exception as e:
        logger.error(f"Error loading files for {client}: {str(e)}")
        return None, None
