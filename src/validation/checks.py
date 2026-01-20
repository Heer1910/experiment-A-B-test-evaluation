"""
Data validation checks for experiment datasets.

Implements fail-fast validation to catch data quality issues before analysis.
Critical for preventing false positives and contamination.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src import config


@dataclass
class ValidationResult:
    """Container for a single validation check result."""
    check_name: str
    passed: bool
    message: str
    severity: str = 'error'  # 'error' or 'warning'
    
    def __str__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"[{status}] {self.check_name}: {self.message}"


@dataclass
class ValidationReport:
    """Aggregated results from all validation checks."""
    results: List[ValidationResult]
    
    @property
    def passed(self):
        """Returns True only if all error-level checks passed."""
        return all(r.passed for r in self.results if r.severity == 'error')
    
    @property
    def warnings(self):
        """Returns warnings (non-blocking issues)."""
        return [r for r in self.results if r.severity == 'warning' and not r.passed]
    
    def print_report(self):
        """Print formatted validation report."""
        print("\n" + "="*70)
        print("EXPERIMENT DATA VALIDATION REPORT")
        print("="*70)
        
        for result in self.results:
            print(result)
        
        print("="*70)
        if self.passed:
            print("✓ All critical checks passed")
            if self.warnings:
                print(f"⚠ {len(self.warnings)} warning(s) detected")
        else:
            print("✗ Validation FAILED - fix errors before proceeding")
        print("="*70 + "\n")


class DataValidator:
    """
    Validates experiment data quality and integrity.
    
    Implements multiple checks to catch common experiment issues:
    - Schema problems (missing columns, wrong types)
    - Null values in required fields
    - Invalid variant assignments
    - Sample Ratio Mismatch (SRM)
    - Contamination (users in multiple variants)
    - Eligibility filtering
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.results = []
    
    def validate(self) -> ValidationReport:
        """Run all validation checks and return aggregated report."""
        print("Running validation checks...")
        
        self._check_schema()
        self._check_nulls()
        self._check_variants()
        self._check_sample_ratio_mismatch()
        self._check_contamination()
        self._check_eligibility()
        
        return ValidationReport(self.results)
    
    def _check_schema(self):
        """Verify required columns are present with correct types."""
        required_cols = [
            'user_id', 'experiment_id', 'variant', 'assigned_at',
            'first_exposed_at', 'eligible', 'clicked', 'converted',
            'device_category', 'country'
        ]
        
        missing = [col for col in required_cols if col not in self.df.columns]
        
        if missing:
            self.results.append(ValidationResult(
                check_name="Schema Check",
                passed=False,
                message=f"Missing required columns: {missing}"
            ))
        else:
            self.results.append(ValidationResult(
                check_name="Schema Check",
                passed=True,
                message=f"All {len(required_cols)} required columns present"
            ))
    
    def _check_nulls(self):
        """Check for null values in required fields."""
        required_non_null = [
            'user_id', 'variant', 'eligible', 'clicked', 'converted'
        ]
        
        null_counts = self.df[required_non_null].isnull().sum()
        has_nulls = null_counts.sum() > 0
        
        if has_nulls:
            problematic = null_counts[null_counts > 0].to_dict()
            self.results.append(ValidationResult(
                check_name="Null Check",
                passed=False,
                message=f"Found nulls in required fields: {problematic}"
            ))
        else:
            self.results.append(ValidationResult(
                check_name="Null Check",
                passed=True,
                message="No nulls in required fields"
            ))
    
    def _check_variants(self):
        """Ensure only valid variants (control/treatment) are present."""
        valid_variants = {'control', 'treatment'}
        actual_variants = set(self.df['variant'].unique())
        
        invalid = actual_variants - valid_variants
        
        if invalid:
            self.results.append(ValidationResult(
                check_name="Variant Integrity",
                passed=False,
                message=f"Invalid variants found: {invalid}"
            ))
        else:
            counts = self.df['variant'].value_counts().to_dict()
            self.results.append(ValidationResult(
                check_name="Variant Integrity",
                passed=True,
                message=f"Valid variants only: {counts}"
            ))
    
    def _check_sample_ratio_mismatch(self):
        """
        Check for Sample Ratio Mismatch (SRM).
        
        SRM occurs when the observed allocation differs significantly
        from the expected allocation. This can indicate:
        - Randomization bugs
        - Biased filtering
        - Technical issues in assignment
        
        We use a chi-square test to detect significant deviations.
        """
        variant_counts = self.df['variant'].value_counts()
        total = len(self.df)
        
        expected_control = total * config.ALLOCATION_RATIO
        expected_treatment = total * (1 - config.ALLOCATION_RATIO)
        
        observed_control = variant_counts.get('control', 0)
        observed_treatment = variant_counts.get('treatment', 0)
        
        # Chi-square test for goodness of fit
        chi_square = (
            ((observed_control - expected_control) ** 2 / expected_control) +
            ((observed_treatment - expected_treatment) ** 2 / expected_treatment)
        )
        
        # Critical value for alpha=0.001 with 1 degree of freedom is ~10.83
        # Using a stricter threshold since SRM is serious
        critical_value = 10.83
        has_srm = chi_square > critical_value
        
        if has_srm:
            self.results.append(ValidationResult(
                check_name="Sample Ratio Mismatch (SRM)",
                passed=False,
                message=f"SRM detected! χ²={chi_square:.2f} (critical={critical_value:.2f}). "
                        f"Observed: {observed_control}/{observed_treatment}, "
                        f"Expected: {expected_control:.0f}/{expected_treatment:.0f}",
                severity='error'
            ))
        else:
            pct_diff = abs(observed_control - expected_control) / expected_control * 100
            self.results.append(ValidationResult(
                check_name="Sample Ratio Mismatch (SRM)",
                passed=True,
                message=f"No SRM detected (χ²={chi_square:.2f}, deviation={pct_diff:.2f}%)"
            ))
    
    def _check_contamination(self):
        """
        Check for contamination (users assigned to multiple variants).
        
        This should NEVER happen in a properly randomized experiment.
        """
        user_variant_counts = self.df.groupby('user_id')['variant'].nunique()
        contaminated_users = user_variant_counts[user_variant_counts > 1]
        
        if len(contaminated_users) > 0:
            self.results.append(ValidationResult(
                check_name="Contamination Check",
                passed=False,
                message=f"{len(contaminated_users)} users in multiple variants!"
            ))
        else:
            self.results.append(ValidationResult(
                check_name="Contamination Check",
                passed=True,
                message="No contamination detected (1 variant per user)"
            ))
    
    def _check_eligibility(self):
        """Check eligibility distribution and warn if too many ineligible users."""
        eligible_count = self.df['eligible'].sum()
        total = len(self.df)
        eligible_pct = eligible_count / total * 100
        
        # Warn if less than 80% eligible (might indicate filtering issues)
        if eligible_pct < 80:
            self.results.append(ValidationResult(
                check_name="Eligibility Check",
                passed=False,
                message=f"Low eligibility rate: {eligible_pct:.1f}% ({eligible_count:,}/{total:,})",
                severity='warning'
            ))
        else:
            self.results.append(ValidationResult(
                check_name="Eligibility Check",
                passed=True,
                message=f"Eligibility rate: {eligible_pct:.1f}% ({eligible_count:,}/{total:,})"
            ))


def main():
    """CLI for running validation on saved dataset."""
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    data_path = 'data/experiment_users.parquet'
    print(f"Loading data from {data_path}...")
    df = pd.read_parquet(data_path)
    
    validator = DataValidator(df)
    report = validator.validate()
    report.print_report()
    
    if not report.passed:
        sys.exit(1)  # Exit with error code if validation failed


if __name__ == '__main__':
    main()
