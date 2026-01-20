"""
Visualization script for A/B test analysis.
Creates the required 3 figures.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.metrics.compute import MetricComputer
from src.stats.inference import InferenceEngine
from src.utils.io import load_experiment_data, save_figure


def create_metric_comparison_table(ctr_metric, cvr_metric, ctr_inf, cvr_inf):
    """
    Create figure 1: Metric comparison table with lifts.
    """
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare table data
    data = [
        ['Metric', 'Control', 'Treatment', 'Absolute Lift', 'Relative Lift', '95% CI'],
        ['CTR', 
         f'{ctr_metric.control_rate:.2%}\n({ctr_metric.control_successes:,}/{ctr_metric.control_n:,})',
         f'{ctr_metric.treatment_rate:.2%}\n({ctr_metric.treatment_successes:,}/{ctr_metric.treatment_n:,})',
         f'{ctr_metric.absolute_lift:+.2%}',
         f'{ctr_metric.relative_lift_pct:+.1f}%',
         f'[{ctr_inf.ci_lower:+.2%}, {ctr_inf.ci_upper:+.2%}]'],
        ['CVR',
         f'{cvr_metric.control_rate:.2%}\n({cvr_metric.control_successes:,}/{cvr_metric.control_n:,})',
         f'{cvr_metric.treatment_rate:.2%}\n({cvr_metric.treatment_successes:,}/{cvr_metric.treatment_n:,})',
         f'{cvr_metric.absolute_lift:+.2%}',
         f'{cvr_metric.relative_lift_pct:+.1f}%',
         f'[{cvr_inf.ci_lower:+.2%}, {cvr_inf.ci_upper:+.2%}]']
    ]
    
    table = ax.table(cellText=data, cellLoc='center', loc='center',
                     colWidths=[0.12, 0.22, 0.22, 0.15, 0.12, 0.17])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header row
    for i in range(6):
        cell = table[(0, i)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, 3):
        for j in range(6):
            cell = table[(i, j)]
            cell.set_facecolor('#F2F2F2' if i % 2 == 0 else 'white')
            
            # Highlight lift columns if positive
            if j in [3, 4]:  # Lift columns
                if '+' in cell.get_text().get_text():
                    cell.set_facecolor('#D4EDDA')
                    cell.set_text_props(weight='bold', color='#155724')
    
    plt.title('A/B Test Results: Homepage Redesign V1', 
              fontsize=14, weight='bold', pad=20)
    
    return fig


def create_ci_plot(cvr_inf):
    """
    Create figure 2: Confidence interval plot for CVR lift.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data
    metrics = ['CVR Lift']
    point_estimate = cvr_inf.absolute_lift * 100  # Convert to pp
    ci_lower = cvr_inf.ci_lower * 100
    ci_upper = cvr_inf.ci_upper * 100
    error = [[point_estimate - ci_lower], [ci_upper - point_estimate]]
    
    # Plot
    ax.errorbar([0], [point_estimate], yerr=error, 
                fmt='o', markersize=12, capsize=10, capthick=2,
                color='#2E7D32', ecolor='#4CAF50', linewidth=2, 
                label='95% Confidence Interval')
    
    # Add horizontal line at zero
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='No Effect')
    
    # Annotations
    ax.text(0, point_estimate + (ci_upper - point_estimate) * 0.3, 
            f'{point_estimate:+.2f}pp\n({cvr_inf.relative_lift_pct:+.1f}%)',
            ha='center', va='bottom', fontsize=12, weight='bold')
    
    ax.text(0.05, ci_upper, f'Upper: {ci_upper:+.2f}pp', 
            ha='left', va='center', fontsize=9, style='italic')
    ax.text(0.05, ci_lower, f'Lower: {ci_lower:+.2f}pp', 
            ha='left', va='center', fontsize=9, style='italic')
    
    # Styling
    ax.set_xlim(-0.5, 0.5)
    ax.set_xticks([0])
    ax.set_xticklabels(['Conversion Rate'])
    ax.set_ylabel('Lift (percentage points)', fontsize=12)
    ax.set_title('Conversion Rate Lift with 95% Confidence Interval', 
                 fontsize=14, weight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle=':')
    ax.legend(loc='upper right', fontsize=10)
    
    # Color the area based on whether CI includes zero
    if ci_lower >= 0:
        ax.axhspan(ci_lower, ci_upper, alpha=0.1, color='green')
        conclusion = "CI does not include zero - Statistically significant improvement"
        color = '#2E7D32'
    else:
        ax.axhspan(ci_lower, ci_upper, alpha=0.1, color='gray')
        conclusion = "CI includes zero - Not statistically significant"
        color = '#757575'
    
    # Adjust layout first to make room for bottom text
    plt.tight_layout()
    
    # Add conclusion text below the plot with more space
    fig.text(0.5, 0.01, conclusion, ha='center', fontsize=10, 
             style='italic', weight='bold', color=color)
    
    # Add extra bottom margin to prevent overlap
    plt.subplots_adjust(bottom=0.15)
    
    return fig


def create_segment_lift_plot(df):
    """
    Create figure 3: Segment-level lift plot (CVR by device).
    """
    computer = MetricComputer(df, eligible_only=True)
    segment_breakdown = computer.compute_segment_breakdown('converted', 'device_category')
    segment_breakdown = segment_breakdown.sort_values('control_n', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_pos = np.arange(len(segment_breakdown))
    lifts = segment_breakdown['relative_lift_pct'].values
    segments = segment_breakdown['segment'].values
    
    # Color bars based on lift direction
    colors = ['#2E7D32' if lift > 0 else '#C62828' for lift in lifts]
    
    bars = ax.bar(x_pos, lifts, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, lift) in enumerate(zip(bars, lifts)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{lift:+.1f}%',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=11, weight='bold')
        
        # Add sample size below segment name
        n_control = segment_breakdown.iloc[i]['control_n']
        n_treatment = segment_breakdown.iloc[i]['treatment_n']
        ax.text(bar.get_x() + bar.get_width()/2., -max(abs(lifts)) * 0.15,
                f'n={n_control:,} | {n_treatment:,}',
                ha='center', va='top', fontsize=8, style='italic', color='gray')
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    # Styling
    ax.set_xticks(x_pos)
    ax.set_xticklabels([s.title() for s in segments], fontsize=11)
    ax.set_ylabel('Relative Lift in CVR (%)', fontsize=12)
    ax.set_title('Treatment Effect by Device Category', fontsize=14, weight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle=':')
    
    # Add note
    fig.text(0.5, 0.02, 
             'Note: Segment-level results are for diagnosis only. Treatment effect varies by device.',
             ha='center', fontsize=9, style='italic', color='#757575')
    
    plt.tight_layout()
    return fig


def main():
    """Generate all 3 required figures."""
    print("Loading experiment data...")
    df = load_experiment_data()
    
    print("Computing metrics...")
    computer = MetricComputer(df, eligible_only=True)
    ctr_metric = computer.compute_ctr()
    cvr_metric = computer.compute_cvr()
    
    print("Running statistical inference...")
    engine = InferenceEngine()
    ctr_inf = engine.analyze_metric(ctr_metric)
    cvr_inf = engine.analyze_metric(cvr_metric)
    
    print("\nGenerating visualizations...")
    
    # Figure 1: Metric comparison table
    print("  Creating Figure 1: Metric comparison table...")
    fig1 = create_metric_comparison_table(ctr_metric, cvr_metric, ctr_inf, cvr_inf)
    save_figure(fig1, 'metric_comparison.png')
    plt.close(fig1)
    
    # Figure 2: CI plot
    print("  Creating Figure 2: Confidence interval plot...")
    fig2 = create_ci_plot(cvr_inf)
    save_figure(fig2, 'cvr_confidence_interval.png')
    plt.close(fig2)
    
    # Figure 3: Segment lifts
    print("  Creating Figure 3: Segment lift plot...")
    fig3 = create_segment_lift_plot(df)
    save_figure(fig3, 'segment_lifts_by_device.png')
    plt.close(fig3)
    
    print("\n✓ All visualizations generated successfully!")


if __name__ == '__main__':
    main()
