"""
Tests for statistical inference.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.stats.inference import InferenceEngine
from src.metrics.compute import MetricReport


def test_confidence_interval_bounds():
    """Test that CI bounds are reasonable and ordered correctly."""
    # Create a metric report with known values
    metric = MetricReport(
        metric_name='Test CVR',
        control_n=10000,
        control_successes=350,
        control_rate=0.035,
        treatment_n=10000,
        treatment_successes=430,
        treatment_rate=0.043,
        absolute_lift=0.008,
        relative_lift_pct=22.86
    )
    
    engine = InferenceEngine(confidence_level=0.95)
    inference = engine.analyze_metric(metric)
    
    # CI should contain the point estimate
    assert inference.ci_lower <= inference.absolute_lift <= inference.ci_upper, \
        "CI should contain point estimate"
    
    # CI bounds should be ordered
    assert inference.ci_lower < inference.ci_upper, \
        "Lower bound should be less than upper bound"


def test_no_effect_confidence_interval():
    """Test CI when there's no difference between groups."""
    # Identical rates should give CI around zero
    metric = MetricReport(
        metric_name='Test CVR - No Effect',
        control_n=5000,
        control_successes=350,
        control_rate=0.07,
        treatment_n=5000,
        treatment_successes=350,
        treatment_rate=0.07,
        absolute_lift=0.0,
        relative_lift_pct=0.0
    )
    
    engine = InferenceEngine(confidence_level=0.95)
    inference = engine.analyze_metric(metric)
    
    # CI should be narrow and centered around zero
    assert abs(inference.ci_lower) < 0.01, "Lower bound should be close to zero"
    assert abs(inference.ci_upper) < 0.01, "Upper bound should be close to zero"
    
    # P-value should be high (not significant)
    assert inference.p_value > 0.05, "P-value should be > 0.05 for no effect"


def test_large_effect_significance():
    """Test that large effects are detected as significant."""
    # Create a metric with substantial lift
    metric = MetricReport(
        metric_name='Test CVR - Large Effect',
        control_n=5000,
        control_successes=175,
        control_rate=0.035,
        treatment_n=5000,
        treatment_successes=350,
        treatment_rate=0.07,
        absolute_lift=0.035,
        relative_lift_pct=100.0
    )
    
    engine = InferenceEngine(confidence_level=0.95)
    inference = engine.analyze_metric(metric)
    
    # Should be statistically significant
    assert inference.statistically_significant, "Large effect should be significant"
    assert inference.p_value < 0.001, "P-value should be very small"
    
    # CI should not include zero
    assert inference.ci_lower > 0, "Lower bound should be positive for positive effect"


def test_mde_computation():
    """Test that MDE computation returns reasonable values."""
    engine = InferenceEngine(confidence_level=0.95)
    
    # Compute MDE for typical A/B test
    baseline_cvr = 0.035
    n_per_variant = 25000
    
    mde = engine.compute_mde(baseline_cvr, n_per_variant, power=0.8)
    
    # MDE should be positive and reasonable
    assert mde > 0, "MDE should be positive"
    assert mde < baseline_cvr, "MDE should be smaller than baseline rate"
    
    # Larger sample size should give smaller MDE
    mde_large = engine.compute_mde(baseline_cvr, n_per_variant * 4, power=0.8)
    assert mde_large < mde, "Larger sample should give smaller MDE"


def test_p_value_bounds():
    """Test that p-values are always between 0 and 1."""
    metric = MetricReport(
        metric_name='Test',
        control_n=1000,
        control_successes=100,
        control_rate=0.1,
        treatment_n=1000,
        treatment_successes=120,
        treatment_rate=0.12,
        absolute_lift=0.02,
        relative_lift_pct=20.0
    )
    
    engine = InferenceEngine()
    inference = engine.analyze_metric(metric)
    
    assert 0 <= inference.p_value <= 1, "P-value must be between 0 and 1"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
