"""
Metric computation for A/B test analysis.

Calculates CTR, CVR, and related metrics by variant with lifts.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict


@dataclass
class MetricReport:
    """Container for computed metrics by variant."""
    metric_name: str
    control_n: int
    control_successes: int
    control_rate: float
    treatment_n: int
    treatment_successes: int
    treatment_rate: float
    absolute_lift: float
    relative_lift_pct: float
    
    def to_dict(self):
        return {
            'metric': self.metric_name,
            'control_n': self.control_n,
            'control_successes': self.control_successes,
            'control_rate': self.control_rate,
            'treatment_n': self.treatment_n,
            'treatment_successes': self.treatment_successes,
            'treatment_rate': self.treatment_rate,
            'absolute_lift': self.absolute_lift,
            'relative_lift_pct': self.relative_lift_pct
        }
    
    def __str__(self):
        return (
            f"\n{self.metric_name.upper()} Metrics:\n"
            f"  Control:   {self.control_rate:.4f} ({self.control_successes:,}/{self.control_n:,})\n"
            f"  Treatment: {self.treatment_rate:.4f} ({self.treatment_successes:,}/{self.treatment_n:,})\n"
            f"  Absolute Lift: {self.absolute_lift:+.4f} ({self.absolute_lift*100:+.2f}pp)\n"
            f"  Relative Lift: {self.relative_lift_pct:+.2f}%"
        )


class MetricComputer:
    """
    Computes experiment metrics (CTR, CVR) by variant.
    
    Handles:
    - Rate calculation with proper denominators
    - Absolute and relative lift computation
    - Segment-level breakdowns
    """
    
    def __init__(self, df: pd.DataFrame, eligible_only=True):
        """
        Initialize metric computer.
        
        Parameters
        ----------
        df : pd.DataFrame
            Experiment data
        eligible_only : bool
            Whether to filter to eligible users only (recommended)
        """
        self.df = df[df['eligible']] if eligible_only else df
        self.eligible_only = eligible_only
    
    def compute_ctr(self) -> MetricReport:
        """Compute Click-Through Rate (CTR) by variant."""
        return self._compute_binary_metric('CTR', 'clicked')
    
    def compute_cvr(self) -> MetricReport:
        """Compute Conversion Rate (CVR) by variant."""
        return self._compute_binary_metric('CVR', 'converted')
    
    def _compute_binary_metric(self, metric_name: str, outcome_col: str) -> MetricReport:
        """
        Generic computation for binary outcome metrics.
        
        Parameters
        ----------
        metric_name : str
            Name of metric (for reporting)
        outcome_col : str
            Column name containing binary outcome
        
        Returns
        -------
        MetricReport
            Computed metrics with lift
        """
        control = self.df[self.df['variant'] == 'control']
        treatment = self.df[self.df['variant'] == 'treatment']
        
        # Counts
        control_n = len(control)
        control_successes = control[outcome_col].sum()
        control_rate = control_successes / control_n if control_n > 0 else 0
        
        treatment_n = len(treatment)
        treatment_successes = treatment[outcome_col].sum()
        treatment_rate = treatment_successes / treatment_n if treatment_n > 0 else 0
        
        # Lifts
        absolute_lift = treatment_rate - control_rate
        relative_lift_pct = (absolute_lift / control_rate * 100) if control_rate > 0 else 0
        
        return MetricReport(
            metric_name=metric_name,
            control_n=control_n,
            control_successes=control_successes,
            control_rate=control_rate,
            treatment_n=treatment_n,
            treatment_successes=treatment_successes,
            treatment_rate=treatment_rate,
            absolute_lift=absolute_lift,
            relative_lift_pct=relative_lift_pct
        )
    
    def compute_segment_breakdown(self, metric_col: str, segment_col: str) -> pd.DataFrame:
        """
        Compute metric breakdown by segment.
        
        Parameters
        ----------
        metric_col : str
            Binary outcome column ('clicked' or 'converted')
        segment_col : str
            Segment column ('device_category', 'country', etc.)
        
        Returns
        -------
        pd.DataFrame
            Segment-level metrics with lifts
        """
        segments = self.df[segment_col].unique()
        results = []
        
        for segment in segments:
            segment_df = self.df[self.df[segment_col] == segment]
            
            control = segment_df[segment_df['variant'] == 'control']
            treatment = segment_df[segment_df['variant'] == 'treatment']
            
            control_n = len(control)
            control_rate = control[metric_col].mean() if control_n > 0 else 0
            
            treatment_n = len(treatment)
            treatment_rate = treatment[metric_col].mean() if treatment_n > 0 else 0
            
            lift = treatment_rate - control_rate
            rel_lift = (lift / control_rate * 100) if control_rate > 0 else 0
            
            results.append({
                'segment': segment,
                'control_n': control_n,
                'control_rate': control_rate,
                'treatment_n': treatment_n,
                'treatment_rate': treatment_rate,
                'absolute_lift': lift,
                'relative_lift_pct': rel_lift
            })
        
        return pd.DataFrame(results).sort_values('control_n', ascending=False)


def main():
    """CLI for computing metrics on saved dataset."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    data_path = 'data/experiment_users.parquet'
    print(f"Loading data from {data_path}...")
    df = pd.read_parquet(data_path)
    
    computer = MetricComputer(df, eligible_only=True)
    
    print("\n" + "="*70)
    print("METRIC COMPUTATION")
    print("="*70)
    
    ctr = computer.compute_ctr()
    print(ctr)
    
    cvr = computer.compute_cvr()
    print(cvr)
    
    print("\n" + "="*70)
    print("SEGMENT BREAKDOWN: CVR by Device")
    print("="*70)
    segment_breakdown = computer.compute_segment_breakdown('converted', 'device_category')
    print(segment_breakdown.to_string(index=False))


if __name__ == '__main__':
    main()
