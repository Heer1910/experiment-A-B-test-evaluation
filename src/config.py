"""
Configuration for A/B test experimentation analysis.

This module centralizes all experiment parameters to ensure reproducibility
and make it easy to adjust assumptions for sensitivity testing.
"""

import pandas as pd
from datetime import datetime, timedelta

# =============================================================================
# Reproducibility
# =============================================================================
RANDOM_SEED = 42  # For consistent results across runs


# =============================================================================
# Experiment Design
# =============================================================================
EXPERIMENT_ID = "homepage_redesign_v1"
N_USERS = 50000  # Sample size for synthetic dataset
ALLOCATION_RATIO = 0.5  # 50-50 split between control and treatment

# Experiment window
EXPERIMENT_START = datetime(2024, 10, 1)
EXPERIMENT_END = datetime(2024, 10, 21)  # 3-week test


# =============================================================================
# Baseline Metrics (Control Group)
# =============================================================================
# These represent the current production homepage performance
CONTROL_CTR = 0.12  # 12% of users click on primary CTA
CONTROL_CVR = 0.035  # 3.5% of users convert (signup/purchase)


# =============================================================================
# Treatment Effects
# =============================================================================
# Expected lifts from the redesign (in percentage points)
# Note: These are the "ground truth" for the synthetic data.
# In a real experiment, we wouldn't know these upfront.
TREATMENT_CTR_LIFT_PP = 0.015  # +1.5pp lift in CTR
TREATMENT_CVR_LIFT_PP = 0.008  # +0.8pp lift in CVR


# =============================================================================
# Segment Distributions
# =============================================================================
# Realistic device mix based on typical web traffic
DEVICE_DISTRIBUTION = {
    'mobile': 0.55,
    'desktop': 0.38,
    'tablet': 0.07
}

# Top countries by traffic volume
COUNTRY_DISTRIBUTION = {
    'US': 0.45,
    'IN': 0.20,
    'CA': 0.12,
    'UK': 0.10,
    'Other': 0.13
}


# =============================================================================
# Segment-Level Heterogeneity (Optional)
# =============================================================================
# The treatment might work better on certain devices
# This adds realism to the synthetic data
ENABLE_HETEROGENEITY = True

# Device-specific treatment effects (multipliers on base lift)
# Example: mobile users might see a larger CTR lift from the redesign
DEVICE_EFFECT_MULTIPLIERS = {
    'mobile': 1.3,   # 30% stronger effect
    'desktop': 1.0,  # baseline effect
    'tablet': 0.8    # 20% weaker effect
}


# =============================================================================
# Data Quality Parameters
# =============================================================================
# Eligibility rate: what % of assigned users actually saw the experiment
# (In production, not everyone assigned will be exposed due to bots, crawlers, etc.)
ELIGIBILITY_RATE = 0.95

# Contamination rate: should be 0 for a clean experiment
# We keep this at 0 but the validation checks will catch it if it happens
CONTAMINATION_RATE = 0.0


# =============================================================================
# Statistical Inference
# =============================================================================
CONFIDENCE_LEVEL = 0.95
ALPHA = 1 - CONFIDENCE_LEVEL


# =============================================================================
# Decision Thresholds
# =============================================================================
# Ship if the CI lower bound is at or above this threshold
MIN_ACCEPTABLE_CVR_LIFT = 0.0  # Zero or positive lift required

# Guardrail degradation tolerance (if we add guardrails)
MAX_ACCEPTABLE_BOUNCE_INCREASE = 0.02  # 2pp increase tolerable
