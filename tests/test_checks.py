"""
Tests for validation checks.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.validation.checks import DataValidator, ValidationReport


def create_valid_dataset(n=1000):
    """Helper to create valid experiment data for testing."""
    rng = np.random.default_rng(42)
    
    df = pd.DataFrame({
        'user_id': [f'user_{i}' for i in range(n)],
        'experiment_id': ['homepage_redesign_v1'] * n,
        'variant': rng.choice(['control', 'treatment'], n),
        'assigned_at': pd.Timestamp('2024-10-01'),
        'first_exposed_at': pd.Timestamp('2024-10-01'),
        'eligible': [True] * n,
        'clicked': rng.choice([True, False], n),
        'converted': rng.choice([True, False], n),
        'device_category': rng.choice(['mobile', 'desktop', 'tablet'], n),
        'country': rng.choice(['US', 'IN', 'CA'], n)
    })
    
    return df


def test_schema_check_passes():
    """Test that schema check passes with valid data."""
    df = create_valid_dataset()
    validator = DataValidator(df)
    report = validator.validate()
    
    # Check that schema check passed
    schema_result = [r for r in report.results if r.check_name == "Schema Check"][0]
    assert schema_result.passed, "Schema check should pass with valid data"


def test_schema_check_fails_missing_columns():
    """Test that schema check fails when required columns are missing."""
    df = create_valid_dataset()
    df = df.drop(columns=['clicked'])  # Remove required column
    
    validator = DataValidator(df)
    report = validator.validate()
    
    schema_result = [r for r in report.results if r.check_name == "Schema Check"][0]
    assert not schema_result.passed, "Schema check should fail with missing columns"


def test_null_check_fails():
    """Test that null check fails when required fields have nulls."""
    df = create_valid_dataset()
    df.loc[0:10, 'variant'] = None  # Introduce nulls
    
    validator = DataValidator(df)
    report = validator.validate()
    
    null_result = [r for r in report.results if r.check_name == "Null Check"][0]
    assert not null_result.passed, "Null check should fail with null values"


def test_variant_integrity_fails():
    """Test that variant check fails with invalid variants."""
    df = create_valid_dataset()
    df.loc[0:10, 'variant'] = 'invalid_variant'
    
    validator = DataValidator(df)
    report = validator.validate()
    
    variant_result = [r for r in report.results if r.check_name == "Variant Integrity"][0]
    assert not variant_result.passed, "Variant check should fail with invalid variants"


def test_sample_ratio_mismatch_detection():
    """Test that SRM is detected when allocation is severely skewed."""
    df = create_valid_dataset(n=10000)
    
    # Artificially create severe imbalance (90/10 instead of 50/50)
    n_control = int(0.9 * len(df))
    df['variant'] = ['control'] * n_control + ['treatment'] * (len(df) - n_control)
    
    validator = DataValidator(df)
    report = validator.validate()
    
    srm_result = [r for r in report.results if "SRM" in r.check_name][0]
    assert not srm_result.passed, "SRM should be detected with severe imbalance"


def test_contamination_detection():
    """Test that contamination is detected when users have multiple variants."""
    df = create_valid_dataset()
    
    # Duplicate a user with different variant (contamination)
    contaminated_row = df.iloc[0:1].copy()
    contaminated_row['variant'] = 'treatment' if contaminated_row['variant'].iloc[0] == 'control' else 'control'
    df = pd.concat([df, contaminated_row], ignore_index=True)
    
    validator = DataValidator(df)
    report = validator.validate()
    
    contamination_result = [r for r in report.results if "Contamination" in r.check_name][0]
    assert not contamination_result.passed, "Contamination should be detected"


def test_overall_validation_passes():
    """Test that overall validation passes with clean data."""
    df = create_valid_dataset()
    validator = DataValidator(df)
    report = validator.validate()
    
    assert report.passed, "Overall validation should pass with valid data"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
