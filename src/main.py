#!/usr/bin/env python3

import os
import logging
from datetime import datetime
import pandas as pd
from urllib.parse import urlparse
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PATH_LENGTH = 10  # Optimal path length based on analysis

class URLProcessor:
    @staticmethod
    def clean_url(url, truncate=None):
        """Extract and clean domain from URL, optionally truncating path"""
        if url.startswith('//'):
            url = f"https:{url}"
        elif not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '').lower()
            path = parsed.path.rstrip('/').lower()
            if truncate is not None:
                path = path[:truncate]
            return f"{domain}{path}"
        except:
            logger.error(f"Error cleaning URL: {url}")
            return url.lower()

    def __init__(self):
        self.processor = URLProcessor.clean_url

    def clean_pickup_url(self, url):
        return self.processor(url, PATH_LENGTH)

    def clean_backlink_url(self, url):
        return self.processor(url)

def match_urls(ahrefs_df: pd.DataFrame, pickup_df: pd.DataFrame) -> pd.DataFrame:
    """Match backlinks against pickup URLs using optimized path length"""
    logger.info("Starting URL matching process...")
    
    # Create a copy of the dataframe for modifications
    df = ahrefs_df.copy()
    logger.info(f"Processing {len(df)} backlinks")
    
    # Clean and truncate pickup URLs
    story_title_col = 'Story Name' if 'Story Name' in pickup_df.columns else 'Title'
    pickup_urls = pickup_df[['URL', story_title_col]].copy()
    pickup_urls.rename(columns={story_title_col: 'story_title'}, inplace=True)
    
    # Initialize URL processor
    url_processor = URLProcessor()
    
    logger.info("Cleaning pickup URLs...")
    pickup_urls['clean_url'] = pickup_urls['URL'].apply(url_processor.clean_pickup_url)
    
    # Filter out pickup URLs that are just domains
    pickup_urls = pickup_urls[pickup_urls['clean_url'].str.contains('/')]
    logger.info(f"Using {len(pickup_urls)} pickup URLs with paths")
    
    logger.info("Cleaning backlink URLs...")
    df.loc[:, 'clean_url'] = df['Referring page URL'].apply(url_processor.clean_backlink_url)
    
    logger.info("Calculating link weights...")
    df.loc[:, 'link_weight'] = df['Domain rating'] ** 2 * 10
    
    # Initialize match columns
    df.loc[:, 'is_stacker_link'] = False
    df.loc[:, 'matched_story'] = ''
    
    # Create dictionary of pickup URLs for faster lookup
    pickup_dict = dict(zip(pickup_urls['clean_url'], pickup_urls['story_title']))
    
    # Find matches, requiring content after domain
    logger.info("Finding URL matches...")
    matches = 0
    urls_with_paths = df[df['clean_url'].str.contains('/')].index
    total_urls = len(urls_with_paths)
    
    try:
        batch_size = 1000
        for i in range(0, total_urls, batch_size):
            batch_indices = urls_with_paths[i:i+batch_size]
            if i % (batch_size * 10) == 0:
                logger.info(f"Processed {i}/{total_urls} URLs...")
            
            for idx in batch_indices:
                clean_url = df.loc[idx, 'clean_url']
                for pickup_url, story_title in pickup_dict.items():
                    if clean_url.startswith(pickup_url):
                        df.loc[idx, 'is_stacker_link'] = True
                        df.loc[idx, 'matched_story'] = story_title
                        matches += 1
                        break
    
        logger.info(f"Found {matches} matches")
    except Exception as e:
        logger.error(f"Error during URL matching: {str(e)}")
        raise
    
    # Keep only necessary columns in final output
    final_columns = [
        'Referring page URL',
        'Domain rating',
        'link_weight',
        'matched_story',
        'is_stacker_link'
    ]
    
    result = df[final_columns].copy()
    logger.info("URL matching complete")
    return result

def calculate_metrics(df: pd.DataFrame) -> dict:
    """Calculate metrics for matched links"""
    logger.info("Calculating metrics...")
    
    stacker_mask = df['is_stacker_link']
    stacker_links = df[stacker_mask].copy()
    non_stacker_links = df[~stacker_mask].copy()
    
    metrics = {
        'Total Links': len(df),
        'Stacker Links': len(stacker_links),
        'Non-Stacker Links': len(non_stacker_links),
        'Stacker Link Percentage': f"{(len(stacker_links) / len(df) * 100):.2f}%",
        'Average Stacker DR': f"{stacker_links['Domain rating'].mean():.2f}",
        'Average Non-Stacker DR': f"{non_stacker_links['Domain rating'].mean():.2f}",
        'Stacker Link Weight Gain': int(stacker_links['link_weight'].sum()),
        'Non-Stacker Link Weight Gain': int(non_stacker_links['link_weight'].sum()),
        'Total Stacker DR': f"{stacker_links['Domain rating'].sum():.2f}"
    }
    
    logger.info("Metrics calculation complete")
    return metrics