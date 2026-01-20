"""
Utility functions for I/O and visualization.
"""

import pandas as pd
import os


def load_experiment_data(path='data/experiment_users.parquet'):
    """
    Load experiment dataset.
    
    Parameters
    ----------
    path : str
        Path to parquet file (relative to project root)
    
    Returns
    -------
    pd.DataFrame
        Experiment data
    """
    full_path = os.path.join(os.path.dirname(__file__), '../..', path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Data file not found: {full_path}")
    
    return pd.read_parquet(full_path)


def save_figure(fig, filename, output_dir='figures'):
    """
    Save matplotlib figure to output directory.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save
    filename : str
        Filename (without path)
    output_dir : str
        Output directory relative to project root
    
    Returns
    -------
    str
        Full path to saved figure
    """
    full_dir = os.path.join(os.path.dirname(__file__), '../..', output_dir)
    os.makedirs(full_dir, exist_ok=True)
    
    full_path = os.path.join(full_dir, filename)
    fig.savefig(full_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved figure: {output_dir}/{filename}")
    
    return full_path
