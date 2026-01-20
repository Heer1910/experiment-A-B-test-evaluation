# A/B Testing Experimentation Analysis

> A production-style statistical experimentation framework for evaluating product changes through rigorous A/B testing

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

This project demonstrates a complete A/B testing analysis workflow that answers a key business question:

> **Did the homepage redesign improve conversion, or is the observed difference just noise?**

Using synthetic experiment data, this project showcases:
- ✅ Proper randomization and experiment design
- ✅ Statistical inference with confidence intervals and effect sizes
- ✅ Data quality validation (SRM detection, contamination checks)
- ✅ Ship/no-ship decision framework based on evidence
- ✅ Production-ready object-oriented Python package

This work is designed for **portfolio demonstration** targeting Data Analyst, Product Analyst, and Data Scientist roles that require experimentation expertise.

---

## Key Results

### Primary Metric: Conversion Rate (CVR)

| Group | CVR | Sample Size | Absolute Lift | Relative Lift | 95% CI |
|-------|-----|-------------|---------------|---------------|--------|
| **Control** | 3.50% | 23,557 | - | - | - |
| **Treatment** | 4.39% | 23,844 | **+0.89pp** | **+25.3%** | [+0.67pp, +1.11pp] |

**Decision:** ✓ **SHIP** - The treatment shows a statistically significant improvement in conversion rate with high confidence.

### Secondary Metric: Click-Through Rate (CTR)

| Group | CTR | Sample Size | Absolute Lift | Relative Lift |
|-------|-----|-------------|---------------|---------------|
| **Control** | 12.00% | 23,557 | - | - |
| **Treatment** | 13.67% | 23,844 | **+1.67pp** | **+13.9%** |

---

## Project Structure

```
experiment-ab-test-evaluation/
├── data/
│   └── experiment_users.parquet          # Generated synthetic dataset
├── figures/
│   ├── metric_comparison.png             # Results table with lifts
│   ├── cvr_confidence_interval.png       # CI plot for primary metric
│   └── segment_lifts_by_device.png       # Device-level heterogeneity
├── reports/
│   ├── executive_summary.md              # 1-page decision summary
│   └── experiment_one_pager.md           # Quick-reference bulleted summary
├── src/
│   ├── config.py                         # Central configuration (seed, params)
│   ├── data_generation/
│   │   └── generator.py                  # Synthetic data generator
│   ├── validation/
│   │   └── checks.py                     # Data quality checks (SRM, contamination)
│   ├── metrics/
│   │   └── compute.py                    # CTR/CVR computation
│   ├── stats/
│   │   └── inference.py                  # Statistical inference (CIs, p-values)
│   ├── reporting/
│   │   └── summary.py                    # Report generation
│   └── utils/
│       ├── io.py                         # Load/save utilities
│       └── visualizations.py             # Figure generation
├── sql/
│   ├── sanity_checks.sql                 # Data validation queries
│   └── segment_breakdowns.sql            # Segment-level analysis
├── tests/
│   ├── test_checks.py                    # Validation tests
│   └── test_inference.py                 # Statistical tests
├── notebooks/
│   └── ab_test_analysis.ipynb            # End-to-end analysis narrative
├── requirements.txt
└── README.md
```

---

## Quick Start

### Installation

```bash
# Clone or download the project
cd experiment-ab-test-evaluation

# Install dependencies
pip install -r requirements.txt
```

### Run Complete Analysis

```bash
# 1. Generate synthetic data
python src/data_generation/generator.py

# 2. Validate data quality
PYTHONPATH=. python src/validation/checks.py

# 3. Compute metrics and run inference
PYTHONPATH=. python src/metrics/compute.py
PYTHONPATH=. python src/stats/inference.py

# 4. Generate visualizations
PYTHONPATH=. python src/utils/visualizations.py

# 5. Run tests
pytest tests/ -v
```

### View Results

- **Executive Summary:** `reports/executive_summary.md`
- **Visualizations:** `figures/*.png`
- **Interactive Analysis:** `notebooks/ab_test_analysis.ipynb`

---

## How the Synthetic Data Was Built

### Design Philosophy

Real, public A/B test datasets with proper randomization are rare. This project uses **deterministic synthetic data** with documented assumptions to:
1. Demonstrate realistic experimentation workflows
2. Enable reproducibility (seeded generation)
3. Showcase validation checks that catch real-world problems

### Data Generation Process

The synthetic dataset simulates a **homepage redesign experiment** with:

**Sample Size:** 50,000 users (25,000 per variant)

**Experiment Window:** October 1-21, 2024 (3 weeks)

**Allocation:** 50/50 random split (control/treatment)

#### Ground Truth Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Control CTR** | 12.0% | Baseline click-through rate |
| **Control CVR** | 3.5% | Baseline conversion rate |
| **Treatment CTR Lift** | +1.5pp | Homepage redesign improves engagement |
| **Treatment CVR Lift** | +0.8pp | Redesign drives more conversions |
| **Eligibility Rate** | 95% | Filters out bots/crawlers |

#### Realistic Features

1. **Independent Randomization**
   - Variant assignment is random and independent of user characteristics
   - No pre-existing bias in treatment assignment

2. **Segment Attributes**
   - **Device:** 55% mobile, 38% desktop, 7% tablet
   - **Country:** 45% US, 20% IN, 12% CA, 10% UK, 13% other
   - Mirrors typical web traffic patterns

3. **Heterogeneous Treatment Effects**
   - Mobile users see 30% **stronger** effect (+1.95pp CTR lift vs +1.5pp baseline)
   - Tablet users see 20% **weaker** effect (+1.2pp CTR lift)
   - Desktop users see baseline effect (+1.5pp CTR lift)
   - This simulates realistic device-level variation

4. **Guardrail Metrics**
   - Bounce rate increases slightly in treatment (+2pp trade-off)
   - Session duration decreases as users convert faster

5. **Binary Outcomes**
   - Generated via Bernoulli trials with variant-specific probabilities
   - Conversion implies click (logical dependency enforced)

### Reproducibility

All randomness uses `numpy.random.Generator` with **seed=42**:

```python
from src.data_generation.generator import ExperimentDataGenerator

# Run 1
gen1 = ExperimentDataGenerator(seed=42)
df1 = gen1.generate()

# Run 2 (same seed)
gen2 = ExperimentDataGenerator(seed=42)
df2 = gen2.generate()

# Verify identical outputs
assert df1.equals(df2)  # ✓ True
```

### What This Demonstrates

- ✅ Understanding of experimental design principles
- ✅ Awareness of common pitfalls (SRM, contamination)
- ✅ Ability to document assumptions transparently
- ✅ Recognition that synthetic data is valid when ground truth is known

---

## How to Test This Project

### 1. Reproducibility Test

Verify that results are identical across runs:

```bash
# Generate data twice
python src/data_generation/generator.py  # Run 1
mv data/experiment_users.parquet data/experiment_users_v1.parquet

python src/data_generation/generator.py  # Run 2
mv data/experiment_users.parquet data/experiment_users_v2.parquet

# Compare (should be byte-identical)
diff data/experiment_users_v1.parquet data/experiment_users_v2.parquet
```

**Expected:** No differences (files are identical)

### 2. Data Quality Validation

Run validation checks to ensure no SRM or contamination:

```bash
PYTHONPATH=. python src/validation/checks.py
```

**Expected output:**
```
✓ PASS Schema Check: All required columns present
✓ PASS Null Check: No nulls in required fields
✓ PASS Variant Integrity: Valid variants only
✓ PASS Sample Ratio Mismatch: No SRM detected
✓ PASS Contamination Check: No contamination detected
✓ PASS Eligibility Check: 95% eligibility rate
```

### 3. Statistical Inference Test

Verify confidence intervals and p-values:

```bash
PYTHONPATH=. python src/stats/inference.py
```

**Expected:**
- CVR lift: ~+0.8pp (+23%)
- 95% CI: Does NOT include zero
- P-value: < 0.05 (statistically significant)

### 4. Unit Tests

Run automated test suite:

```bash
pytest tests/ -v
```

**Expected:** All tests pass
- ✅ Schema validation detects missing columns
- ✅ SRM detection triggers on skewed allocations
- ✅ CI bounds are correctly ordered
- ✅ MDE computation returns reasonable values

### 5. End-to-End Integration Test

Run the complete notebook:

```bash
jupyter notebook notebooks/ab_test_analysis.ipynb
```

**Expected:**
- All cells execute without errors
- Figures display correctly
- Decision matches reports (SHIP)

### 6. SQL Consistency Check

If you have SQLite or DuckDB:

```python
import duckdb
import pandas as pd

# Load data into SQL
conn = duckdb.connect()
df = pd.read_parquet('data/experiment_users.parquet')
conn.register('experiment_users', df)

# Run validation queries
result = conn.execute(open('sql/sanity_checks.sql').read()).fetchdf()
print(result)
```

**Expected:** SQL metrics match Python outputs

---

## Statistical Methodology

### Decision Framework

**Ship if:**
1. Primary metric (CVR) shows positive lift
2. 95% CI lower bound ≥ 0
3. Guardrails do not degrade beyond tolerance

**This project meets all criteria** → Decision: **SHIP**

### Inference Approach

- **Estimation First:** Always report lift and CI before p-values
- **Confidence Intervals:** 95% CI using normal approximation
- **Two-Sample Z-Test:** For binary proportions (CTR, CVR)
- **Multiple Metrics Policy:**
  - Primary metric (CVR) drives decision
  - Secondary metrics support interpretation
  - Guardrails must not regress

### What is NOT Done (Intentionally)

- ❌ P-hacking or changing hypotheses post-hoc
- ❌ Cherry-picking segments without adjustment
- ❌ Using p-values alone without effect sizes
- ❌ Running tests until significance is reached

---

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Core** | Python 3.9+ | Industry standard for analytics |
| **Data** | pandas, numpy | Tabular data manipulation |
| **Stats** | scipy, statsmodels | Statistical inference |
| **Viz** | matplotlib | Publication-quality figures |
| **Storage** | Parquet | Efficient columnar format |
| **Testing** | pytest | Automated quality checks |

---

## Design Decisions

### Why Synthetic Data?

Public A/B test datasets with proper documentation are scarce. Synthetic data enables:
- Complete control over ground truth
- Reproducibility for portfolio review
- Demonstration of validation checks
- Clear documentation of assumptions

### Why OOP Design?

Object-oriented structure (`MetricComputer`, `InferenceEngine`, `DataValidator`) demonstrates:
- Production-ready code organization
- Testability and maintainability
- Separation of concerns
- Scalability to more complex experiments

### Why SQL Included?

Many companies use SQL for experiment analysis. Including SQL queries shows:
- Versatility across languages
- Ability to validate Python results
- Understanding of when SQL is appropriate

---

## Metrics Explained

### Click-Through Rate (CTR)

**Definition:** Percentage of users who clicked the primary CTA

**Formula:** `CTR = (# clicks) / (# eligible users)`

**Business Value:** Measures engagement and attention capture

### Conversion Rate (CVR)

**Definition:** Percentage of users who completed desired action (signup/purchase)

**Formula:** `CVR = (# conversions) / (# eligible users)`

**Business Value:** Directly impacts revenue and growth

### Why These Metrics?

- Binary outcomes (easy to interpret)
- Commonly used in product experiments
- Demonstrate understanding of funnel metrics

---

## Assumptions and Limitations

### Assumptions

1. **Random Assignment:** Variant assignment is truly random
2. **No Interference:** One user's outcome doesn't affect another's
3. **Stable Unit Treatment Value (SUTV):** Treatment effect is consistent over experiment period
4. **No Novelty Effect:** Results are sustainable post-launch

### Limitations

1. **Synthetic Data:** Real experiments have messier data (bots, outliers, missing values)
2. **Single Test:** Production requires sequential testing frameworks
3. **No Seasonality:** Real experiments must account for day-of-week, holidays
4. **Binary Metrics Only:** Real products track continuous metrics (time-on-site, revenue)

### What This Demonstrates Anyway

Even with synthetic data, this project shows:
- ✅ Statistical rigor (CI, effect sizes, power)
- ✅ Data quality awareness (SRM, contamination)
- ✅ Decision framing (ship criteria)
- ✅ Production mindset (OOP, tests, documentation)

---

## Next Steps for Extension

Potential enhancements for deeper exploration:

1. **Sequential Testing:** Implement always-valid inference
2. **Multi-Armed Bandits:** Adaptive allocation based on performance
3. **Bayesian Inference:** Posterior distributions and credible intervals
4. **Time-Series Analysis:** Detect when treatment effect stabilizes
5. **Segment Discovery:** Automated heterogeneity analysis
6. **Causal Inference:** Propensity score matching for observational data

---

## Contact

**Author:** Heer Patel  
**Purpose:** Portfolio demonstration for data analyst and product analyst roles  
**Focus:** Statistical experimentation, A/B testing, product analytics

---

## License

This project is for educational and portfolio purposes.

---

## Appendix: File Descriptions

| File | Purpose |
|------|---------|
| `config.py` | Central configuration (seed, params, thresholds) |
| `generator.py` | Deterministic synthetic data generation |
| `checks.py` | Data quality validation (SRM, contamination, schema) |
| `compute.py` | Metric calculation (CTR, CVR, lifts) |
| `inference.py` | Statistical inference (CI, p-values, MDE) |
| `summary.py` | Report generation with ship/no-ship logic |
| `visualizations.py` | Figure generation (tables, CI plots, segments) |
| `test_checks.py` | Unit tests for validation checks |
| `test_inference.py` | Unit tests for statistical inference |

---

**Built with statistical rigor and production mindset.**
