"""
Synthetic experiment data generator for A/B testing analysis.

Generates realistic user-level experiment data with:
- Random variant assignment
- Binary outcomes (clicks, conversions)
- Segment attributes (device, country)
- Optional heterogeneous treatment effects

All generation is deterministic (seeded) for reproducibility.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src import config


class ExperimentDataGenerator:
    """
    Generates synthetic A/B test data for homepage redesign experiment.
    
    The data simulates a realistic scenario where:
    - Users are randomly assigned to control or treatment
    - Treatment improves CTR and CVR by specified amounts
    - Effects may vary by segment (e.g., device type)
    - Some users are ineligible (bots, crawlers filtered out)
    """
    
    def __init__(self, n_users=None, seed=None):
        """
        Initialize the generator.
        
        Parameters
        ----------
        n_users : int, optional
            Number of users to generate. Defaults to config.N_USERS
        seed : int, optional
            Random seed for reproducibility. Defaults to config.RANDOM_SEED
        """
        self.n_users = n_users or config.N_USERS
        self.seed = seed or config.RANDOM_SEED
        self.rng = np.random.default_rng(self.seed)
        
    def generate(self):
        """
        Generate complete experiment dataset.
        
        Returns
        -------
        pd.DataFrame
            User-level experiment data with all required fields
        """
        print(f"Generating synthetic data for {self.n_users:,} users...")
        
        # Start with user IDs
        df = pd.DataFrame({
            'user_id': [f'user_{i:07d}' for i in range(self.n_users)]
        })
        
        df['experiment_id'] = config.EXPERIMENT_ID
        
        # Random variant assignment (this is the core of randomization)
        df['variant'] = self.rng.choice(
            ['control', 'treatment'],
            size=self.n_users,
            p=[config.ALLOCATION_RATIO, 1 - config.ALLOCATION_RATIO]
        )
        
        # Assignment timestamp (random within first day of experiment)
        assignment_window_hours = 24
        df['assigned_at'] = [
            config.EXPERIMENT_START + timedelta(
                hours=self.rng.uniform(0, assignment_window_hours)
            )
            for _ in range(self.n_users)
        ]
        
        # Exposure timestamp (a bit after assignment)
        # Some users are exposed quickly, others take longer
        exposure_delays_hours = self.rng.exponential(scale=2.0, size=self.n_users)
        df['first_exposed_at'] = df['assigned_at'] + pd.to_timedelta(exposure_delays_hours, unit='h')
        
        # Eligibility: filter out bots, crawlers, etc.
        df['eligible'] = self.rng.choice(
            [True, False],
            size=self.n_users,
            p=[config.ELIGIBILITY_RATE, 1 - config.ELIGIBILITY_RATE]
        )
        
        # Assign segments (these are independent of variant assignment)
        df = self._assign_segments(df)
        
        # Generate outcomes conditional on variant and segments
        df = self._generate_outcomes(df)
        
        # Add optional guardrail metrics
        df = self._generate_guardrails(df)
        
        print(f"✓ Generated {len(df):,} users")
        print(f"  - Control: {(df['variant'] == 'control').sum():,}")
        print(f"  - Treatment: {(df['variant'] == 'treatment').sum():,}")
        print(f"  - Eligible: {df['eligible'].sum():,}")
        
        return df
    
    def _assign_segments(self, df):
        """Assign device and country segments independently of variant."""
        n = len(df)
        
        # Device assignment (weighted by realistic distribution)
        devices = list(config.DEVICE_DISTRIBUTION.keys())
        device_probs = list(config.DEVICE_DISTRIBUTION.values())
        df['device_category'] = self.rng.choice(devices, size=n, p=device_probs)
        
        # Country assignment
        countries = list(config.COUNTRY_DISTRIBUTION.keys())
        country_probs = list(config.COUNTRY_DISTRIBUTION.values())
        df['country'] = self.rng.choice(countries, size=n, p=country_probs)
        
        return df
    
    def _generate_outcomes(self, df):
        """
        Generate binary outcomes (clicked, converted) based on variant.
        
        Key assumptions:
        - Control group has baseline CTR and CVR
        - Treatment group has lift in both metrics
        - If heterogeneity is enabled, lift varies by device
        - Conversion implies click (logical dependency)
        """
        n = len(df)
        
        # Initialize outcomes
        df['clicked'] = False
        df['converted'] = False
        
        for idx, row in df.iterrows():
            variant = row['variant']
            device = row['device_category']
            
            # Determine CTR and CVR for this user
            if variant == 'control':
                ctr = config.CONTROL_CTR
                cvr = config.CONTROL_CVR
            else:
                # Apply base lift
                ctr_lift = config.TREATMENT_CTR_LIFT_PP
                cvr_lift = config.TREATMENT_CVR_LIFT_PP
                
                # Apply device-specific multiplier if heterogeneity is enabled
                if config.ENABLE_HETEROGENEITY:
                    multiplier = config.DEVICE_EFFECT_MULTIPLIERS.get(device, 1.0)
                    ctr_lift *= multiplier
                    cvr_lift *= multiplier
                
                ctr = config.CONTROL_CTR + ctr_lift
                cvr = config.CONTROL_CVR + cvr_lift
            
            # Generate outcomes (Bernoulli trials)
            clicked = self.rng.random() < ctr
            converted = self.rng.random() < cvr if clicked else False
            
            df.at[idx, 'clicked'] = clicked
            df.at[idx, 'converted'] = converted
        
        return df
    
    def _generate_guardrails(self, df):
        """
        Add optional guardrail metrics (bounce, session duration).
        
        These help catch cases where the treatment improves conversion
        but harms user experience.
        """
        n = len(df)
        
        # Bounce rate: treatment might have slightly higher bounce
        # This creates a tradeoff scenario
        base_bounce_prob = 0.35
        df['bounce'] = False
        
        for idx, row in df.iterrows():
            if row['variant'] == 'treatment':
                bounce_prob = base_bounce_prob + 0.02  # Slight increase
            else:
                bounce_prob = base_bounce_prob
            
            df.at[idx, 'bounce'] = self.rng.random() < bounce_prob
        
        # Session duration: generate realistic durations
        # Treatment might have slightly shorter sessions (people convert faster)
        control_mean_duration = 180  # seconds
        treatment_mean_duration = 165  # slightly shorter
        
        durations = []
        for variant in df['variant']:
            mean_dur = treatment_mean_duration if variant == 'treatment' else control_mean_duration
            # Use lognormal for realistic session duration distribution
            dur = self.rng.lognormal(mean=np.log(mean_dur), sigma=0.8)
            durations.append(int(max(10, dur)))  # At least 10 seconds
        
        df['session_duration_sec'] = durations
        df['sessions'] = self.rng.integers(1, 5, size=n)  # Random session count
        
        return df
    
    def save(self, df, output_path='data/experiment_users.parquet'):
        """Save dataset to parquet for efficient storage."""
        full_path = os.path.join(
            os.path.dirname(__file__), 
            '../../', 
            output_path
        )
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        df.to_parquet(full_path, index=False)
        print(f"✓ Saved to {output_path}")
        return full_path


def main():
    """CLI entry point for generating data."""
    generator = ExperimentDataGenerator()
    df = generator.generate()
    generator.save(df)
    
    print("\n" + "="*60)
    print("Sample of generated data:")
    print("="*60)
    print(df.head(10).to_string())
    print("\n" + "="*60)
    print("Variant distribution:")
    print(df['variant'].value_counts())
    print("\n" + "="*60)
    print("Outcome summary:")
    print(df[['clicked', 'converted']].describe())


if __name__ == '__main__':
    main()
