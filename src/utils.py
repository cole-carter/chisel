#!/usr/bin/env python3

import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_project_root():
    """Get the project root directory from any file in the project"""
    current = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from src to get project root
    return os.path.dirname(current)

def get_client_directory():
    """Search possible locations for clients directory"""
    project_root = get_project_root()
    client_dir = os.path.join(project_root, 'clients')
    os.makedirs(client_dir, exist_ok=True)
    return client_dir

def find_client_directory():
    """For backward compatibility"""
    return get_client_directory()

def save_results(df, output_path):
    """Save DataFrame to CSV, creating directories if needed"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return True
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")
        return False