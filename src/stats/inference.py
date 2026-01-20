"""
Statistical inference for A/B test analysis.

Implements two-sample proportion tests with confidence intervals.
Focuses on effect sizes and uncertainty quantification.
"""

import numpy as np
from scipy import stats
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src import config
from src.metrics.compute import MetricReport


@dataclass
class InferenceReport:
    """Results from statistical inference on a metric."""
    metric_name: str
    control_rate: float
    treatment_rate: float
    absolute_lift: float
    relative_lift_pct: float
    ci_lower: float
    ci_upper: float
    p_value: float
    statistically_significant: bool
    confidence_level: float = 0.95
    
    def __str__(self):
        sig_marker = "✓" if self.statistically_significant else "✗"
        return (
            f"\n{self.metric_name.upper()} Inference:\n"
            f"  Control Rate:    {self.control_rate:.4f}\n"
            f"  Treatment Rate:  {self.treatment_rate:.4f}\n"
            f"  Absolute Lift:   {self.absolute_lift:+.4f} ({self.absolute_lift*100:+.2f}pp)\n"
            f"  Relative Lift:   {self.relative_lift_pct:+.2f}%\n"
            f"  95% CI:          [{self.ci_lower:+.4f}, {self.ci_upper:+.4f}]\n"
            f"  P-value:         {self.p_value:.4f}\n"
            f"  Significant:     {sig_marker} {self.statistically_significant} (α={1-self.confidence_level})"
        )
    
    def to_dict(self):
        return {
            'metric': self.metric_name,
            'control_rate': self.control_rate,
            'treatment_rate': self.treatment_rate,
            'absolute_lift': self.absolute_lift,
            'relative_lift_pct': self.relative_lift_pct,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
            'p_value': self.p_value,
            'statistically_significant': self.statistically_significant
        }


class InferenceEngine:
    """
    Statistical inference for binary outcome experiments.
    
    Implements:
    - Two-sample z-test for proportions
    - Confidence intervals for difference in proportions
    - Proper standard error calculation
    """
    
    def __init__(self, confidence_level=None):
        """
        Initialize inference engine.
        
        Parameters
        ----------
        confidence_level : float, optional
            Confidence level (default from config)
        """
        self.confidence_level = confidence_level or config.CONFIDENCE_LEVEL
        self.alpha = 1 - self.confidence_level
    
    def analyze_metric(self, metric_report: MetricReport) -> InferenceReport:
        """
        Perform statistical inference on a computed metric.
        
        Parameters
        ----------
        metric_report : MetricReport
            Precomputed metric from MetricComputer
        
        Returns
        -------
        InferenceReport
            Statistical inference results including CI and p-value
        """
        # Extract values
        n1 = metric_report.control_n
        x1 = metric_report.control_successes
        p1 = metric_report.control_rate
        
        n2 = metric_report.treatment_n
        x2 = metric_report.treatment_successes
        p2 = metric_report.treatment_rate
        
        # Compute confidence interval for difference in proportions
        ci_lower, ci_upper = self._proportion_diff_ci(p1, n1, p2, n2)
        
        # Compute p-value using two-sample z-test
        p_value = self._proportion_z_test(x1, n1, x2, n2)
        
        # Determine statistical significance
        significant = p_value < self.alpha
        
        return InferenceReport(
            metric_name=metric_report.metric_name,
            control_rate=p1,
            treatment_rate=p2,
            absolute_lift=metric_report.absolute_lift,
            relative_lift_pct=metric_report.relative_lift_pct,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            p_value=p_value,
            statistically_significant=significant,
            confidence_level=self.confidence_level
        )
    
    def _proportion_diff_ci(self, p1, n1, p2, n2):
        """
        Compute confidence interval for difference in proportions.
        
        Uses the standard error formula for independent proportions:
        SE = sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
        
        Parameters
        ----------
        p1, p2 : float
            Proportions for group 1 and 2
        n1, n2 : int
            Sample sizes for group 1 and 2
        
        Returns
        -------
        ci_lower, ci_upper : float
            Lower and upper bounds of confidence interval for (p2 - p1)
        """
        diff = p2 - p1
        
        # Standard error of difference
        se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        
        # Z-score for confidence level
        z = stats.norm.ppf(1 - self.alpha / 2)
        
        # Confidence interval
        margin = z * se
        ci_lower = diff - margin
        ci_upper = diff + margin
        
        return ci_lower, ci_upper
    
    def _proportion_z_test(self, x1, n1, x2, n2):
        """
        Two-sample z-test for proportions.
        
        Null hypothesis: p1 = p2
        Alternative hypothesis: p1 ≠ p2 (two-sided)
        
        Parameters
        ----------
        x1, x2 : int
            Number of successes in each group
        n1, n2 : int
            Sample sizes for each group
        
        Returns
        -------
        p_value : float
            Two-sided p-value
        """
        p1 = x1 / n1
        p2 = x2 / n2
        
        # Pooled proportion (under null hypothesis)
        p_pooled = (x1 + x2) / (n1 + n2)
        
        # Standard error under null (using pooled proportion)
        se_null = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
        
        # Z-statistic
        z_stat = (p2 - p1) / se_null
        
        # Two-sided p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        return p_value
    
    def compute_mde(self, baseline_rate, n_per_variant, power=0.8):
        """
        Compute Minimum Detectable Effect (MDE).
        
        This is the smallest lift we can reliably detect given:
        - baseline conversion rate
        - sample size per variant
        - desired power
        - alpha level
        
        Useful for experiment sizing and retrospective power analysis.
        
        Parameters
        ----------
        baseline_rate : float
            Baseline proportion (e.g., control CVR)
        n_per_variant : int
            Sample size per variant
        power : float
            Statistical power (1 - Type II error rate)
        
        Returns
        -------
        mde : float
            Minimum detectable effect (absolute, in proportion units)
        """
        # Z-scores for alpha and power
        z_alpha = stats.norm.ppf(1 - self.alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        # Simplified MDE formula (assumes similar variance in both groups)
        # MDE = (z_alpha + z_beta) * sqrt(2 * p * (1-p) / n)
        p = baseline_rate
        mde = (z_alpha + z_beta) * np.sqrt(2 * p * (1 - p) / n_per_variant)
        
        return mde


def main():
    """CLI for running inference on metrics."""
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    import pandas as pd
    from src.metrics.compute import MetricComputer
    
    data_path = 'data/experiment_users.parquet'
    print(f"Loading data from {data_path}...")
    df = pd.read_parquet(data_path)
    
    # Compute metrics
    computer = MetricComputer(df, eligible_only=True)
    ctr_metric = computer.compute_ctr()
    cvr_metric = computer.compute_cvr()
    
    # Run inference
    engine = InferenceEngine()
    
    print("\n" + "="*70)
    print("STATISTICAL INFERENCE")
    print("="*70)
    
    ctr_inference = engine.analyze_metric(ctr_metric)
    print(ctr_inference)
    
    cvr_inference = engine.analyze_metric(cvr_metric)
    print(cvr_inference)
    
    # Compute MDE for reference
    print("\n" + "="*70)
    print("MINIMUM DETECTABLE EFFECT (MDE)")
    print("="*70)
    mde_cvr = engine.compute_mde(
        baseline_rate=cvr_metric.control_rate,
        n_per_variant=cvr_metric.control_n
    )
    print(f"MDE for CVR: {mde_cvr:.4f} ({mde_cvr*100:.2f}pp) at 80% power")
    print(f"Observed lift: {cvr_metric.absolute_lift:.4f} ({cvr_metric.absolute_lift*100:.2f}pp)")
    print(f"Lift / MDE ratio: {cvr_metric.absolute_lift / mde_cvr:.2f}x")


if __name__ == '__main__':
    main()
