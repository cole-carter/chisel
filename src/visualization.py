#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Define our color scheme
COLORS = {
    'primary': '#2E1F5E',  # Dark purple
    'secondary': '#D4D0E3',  # Light purple
    'background': '#FFFFFF',  # White
    'grid': '#E5E5E5'  # Light gray
}


def create_distribution_charts(df: pd.DataFrame, figsize=None):
    """Create a figure with distribution charts for backlink analysis"""
    if figsize is None:
        figsize = (12, 8)

    fig = plt.figure(figsize=figsize, constrained_layout=True)
    fig.patch.set_facecolor(COLORS['background'])

    # Create GridSpec for better layout control
    gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

    # 1. Link Distribution Pie Chart
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(COLORS['background'])
    stacker_count = len(df[df['is_stacker_link']])
    non_stacker_count = len(df[~df['is_stacker_link']])

    wedges, texts, autotexts = ax1.pie(
        [stacker_count, non_stacker_count],
        labels=[f'Stacker Links\n{stacker_count:,d}',
                f'Non-Stacker Links\n{non_stacker_count:,d}'],
        autopct='%1.1f%%',
        colors=[COLORS['primary'], COLORS['secondary']],
        explode=(0.05, 0),  # Slightly explode Stacker slice
        shadow=True,
        labeldistance=1.2,  # Move labels further out
        pctdistance=0.85  # Move percentages out
    )
    plt.setp(autotexts, size=9, weight='bold')
    plt.setp(texts, size=10)
    ax1.set_title('Link Distribution', pad=20, weight='bold', size=12)

    # 2. Average DR Pie Chart
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(COLORS['background'])
    stacker_dr = df[df['is_stacker_link']]['Domain rating'].mean()
    non_stacker_dr = df[~df['is_stacker_link']]['Domain rating'].mean()

    wedges, texts, autotexts = ax2.pie(
        [stacker_dr, non_stacker_dr],
        labels=[f'Avg Stacker DR\n{stacker_dr:.1f}',
                f'Avg Non-Stacker DR\n{non_stacker_dr:.1f}'],
        autopct='%1.1f%%',
        colors=[COLORS['primary'], COLORS['secondary']],
        explode=(0.05, 0),
        shadow=True,
        labeldistance=1.2,
        pctdistance=0.85
    )
    plt.setp(autotexts, size=9, weight='bold')
    plt.setp(texts, size=10)
    ax2.set_title('DR Distribution', pad=20, weight='bold', size=12)

    # 3. Link Weight Distribution Pie Chart
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor(COLORS['background'])
    stacker_weight = df[df['is_stacker_link']]['link_weight'].sum()
    non_stacker_weight = df[~df['is_stacker_link']]['link_weight'].sum()

    wedges, texts, autotexts = ax3.pie(
        [stacker_weight, non_stacker_weight],
        labels=[f'Stacker Weight\n{stacker_weight:,.0f}',
                f'Non-Stacker Weight\n{non_stacker_weight:,.0f}'],
        autopct='%1.1f%%',
        colors=[COLORS['primary'], COLORS['secondary']],
        explode=(0.05, 0),
        shadow=True,
        labeldistance=1.2,
        pctdistance=0.85
    )
    plt.setp(autotexts, size=9, weight='bold')
    plt.setp(texts, size=10)
    ax3.set_title('Link Weight Distribution', pad=20, weight='bold', size=12)

    # 4. DR Bar Chart
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(COLORS['background'])

    # Calculate bin edges (10 bins from 0 to 100)
    bin_edges = np.linspace(0, 100, 11)

    # Plot histograms
    stacker_dr = df[df['is_stacker_link']]['Domain rating']
    non_stacker_dr = df[~df['is_stacker_link']]['Domain rating']

    # Plot with step 'post' style for cleaner look
    ax4.hist([non_stacker_dr, stacker_dr],  # Reversed order to put Stacker on top
             bins=bin_edges,
             label=['Non-Stacker Links', 'Stacker Links'],
             color=[COLORS['secondary'], COLORS['primary']],
             alpha=0.7,
             edgecolor='white',
             linewidth=1,
             stacked=True)

    # Add mean lines
    stacker_mean = stacker_dr.mean()
    non_stacker_mean = non_stacker_dr.mean()

    ax4.axvline(stacker_mean, color=COLORS['primary'], linestyle='--', linewidth=2,
                label=f'Stacker Mean: {stacker_mean:.1f}')
    ax4.axvline(non_stacker_mean, color=COLORS['secondary'], linestyle='--', linewidth=2,
                label=f'Non-Stacker Mean: {non_stacker_mean:.1f}')

    # Styling
    ax4.set_title('Domain Rating Distribution', pad=20, weight='bold', size=12)
    ax4.set_xlabel('Domain Rating', weight='bold')
    ax4.set_ylabel('Number of Links', weight='bold')
    ax4.grid(True, linestyle='--', alpha=0.3, color=COLORS['grid'])
    # Move legend to upper left to avoid overlapping with data
    ax4.legend(frameon=True, facecolor='white', framealpha=1, loc='upper left', fontsize='small')
    ax4.set_xlim(0, 100)

    return fig


def get_chart_styles():
    """Return consistent chart styling options"""
    return {
        'colors': COLORS,
        'figsize': {
            'distribution': (12, 8)
        }
    }