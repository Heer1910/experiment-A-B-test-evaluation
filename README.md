# A/B Testing Experimentation Analysis

> End-to-end experiment evaluation workflow for product decision-making

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

This repository implements an experiment analysis pipeline that answers:

> **Did the homepage redesign improve conversion, or is the observed difference just noise?**

Using synthetic experiment data with documented ground truth, this demonstrates:
- Proper randomization and experimental design
- Statistical inference with confidence intervals and effect sizes  
- Data quality validation (SRM detection, contamination checks)
- Evidence-based ship/no-ship decision framework
- Object-oriented Python implementation with tests

---

## Key Results

### Primary Metric: Conversion Rate (CVR)

| Group | CVR | Sample Size | Absolute Lift | Relative Lift | 95% CI |
|-------|-----|-------------|---------------|---------------|--------|
| Control | 0.40% | 23,557 | - | - | - |
| Treatment | 0.65% | 23,844 | +0.25pp | +63% | [+0.12pp, +0.38pp] |

**Decision: SHIP** - CI lower bound is positive, primary metric improved significantly.

### Secondary Metric: Click-Through Rate (CTR)

| Group | CTR | Sample Size | Absolute Lift | Relative Lift |
|-------|-----|-------------|---------------|---------------|
| Control | 12.13% | 23,557 | - | - |
| Treatment | 13.91% | 23,844 | +1.78pp | +14.6% |

---

## Decision Criteria

**Primary metric:** Conversion Rate (CVR)

**Ship if:**
1. Absolute lift > 0
2. 95% CI lower bound ≥ 0 (excludes negative outcomes)
3. Guardrail metrics do not degrade beyond tolerance

**This experiment:** All three conditions met.

---

## Sanity Check Results

| Check | Result | Details |
|-------|--------|---------|
| Sample Ratio Mismatch | Pass | Expected 50/50, observed 24,814/25,186 (χ²=2.77, p=0.10) |
| Contamination | Pass | 0 users assigned to multiple variants |
| Eligibility Filtering | Pass | 94.8% users retained after bot/crawler removal |
| Schema Validation | Pass | All required columns present, correct types |
| Null Values | Pass | No nulls in critical fields |

---

## Quick Start

### Using Makefile (Recommended)

```bash
make data validate metrics visualize test
```

### Manual Steps

```bash
# 1. Install dependencies (pinned versions)
pip install -r requirements.txt

# 2. Generate synthetic data
python src/data_generation/generator.py

# 3. Validate data quality
PYTHONPATH=. python src/validation/checks.py

# 4. Compute metrics and run inference
PYTHONPATH=. python src/metrics/compute.py
PYTHONPATH=. python src/stats/inference.py

# 5. Generate visualizations
PYTHONPATH=. python src/utils/visualizations.py

# 6. Run tests
pytest tests/ -v
```

### View Outputs

- **Executive Summary:** `reports/executive_summary.md`
- **Figures:** `figures/*.png`
- **Notebook:** `notebooks/ab_test_analysis.ipynb`

---

## Project Structure

```
experiment-ab-test-evaluation/
├── Makefile                    # Workflow automation
├── src/
│   ├── config.py               # Central configuration (seed, parameters)
│   ├── data_generation/        # Synthetic data generator
│   ├── validation/             # Data quality checks (SRM, contamination)
│   ├── metrics/                # CTR/CVR computation
│   ├── stats/                  # Statistical inference (CIs, p-values)
│   ├── reporting/              # Report generation
│   └── utils/                  # I/O and visualization utilities
├── sql/                        # Validation and breakdown queries
├── tests/                      # Automated test suite
├── reports/                    # Generated summaries
├── figures/                    # Generated visualizations
└── requirements.txt            # Pinned dependencies
```

---

## Synthetic Data Generation

### Why Synthetic

Public A/B test datasets with complete documentation are scarce. Synthetic data with known ground truth enables:
- Reproducible analysis (seeded random generation)
- Demonstration of validation checks that catch real-world problems
- Clear documentation of assumptions

### Ground Truth Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Control CTR | 12.0% | Baseline engagement |
| Control CVR | 0.4% | Baseline conversion |
| Treatment CTR Lift | +1.5pp | Redesign effect on clicks |
| Treatment CVR Lift | +0.8pp | Redesign effect on conversions |
| Sample Size | 50,000 | 25,000 per variant |
| Allocation | 50/50 | Random assignment |

### Key Features

**Independent Randomization:** Variant assignment is random, independent of user attributes.

**Segment Heterogeneity:** Treatment effect varies by device (mobile: +30% stronger, tablet: -20% weaker).

**Guardrail Trade-offs:** Bounce rate increases +2pp in treatment, session duration decreases.

**Binary Outcomes:** Click and conversion events generated via Bernoulli trials.

### Reproducibility

All randomness uses `numpy.random.Generator` with seed=42. Running the generator multiple times produces byte-identical outputs.

```python
from src.data_generation.generator import ExperimentDataGenerator
gen = ExperimentDataGenerator(seed=42)
df = gen.generate()  # Produces identical results every time
```

---

## Statistical Methodology

### Inference Approach

- **Estimation First:** Report lift + 95% CI before p-values
- **Two-Sample Z-Test:** For binary proportions (standard for CTR/CVR)
- **Multiple Metrics:** Primary (CVR) drives decision, secondary supports interpretation
- **What We Avoid:** P-hacking, post-hoc hypotheses, cherry-picked segments

### Decision Framework

```
IF cvr_lift > 0 
   AND ci_lower >= 0 
   AND guardrails_ok 
THEN ship
ELSE investigate/iterate
```

---

## Testing

### Automated Tests

```bash
pytest tests/ -v
```

Validates:
- Schema detection (fails on missing columns)
- SRM detection (flags skewed 90/10 allocations)
- Confidence interval bounds (correct ordering)
- MDE computation (scales inversely with sample size)

### Reproducibility Test

```bash
python src/data_generation/generator.py  # Run 1
mv data/experiment_users.parquet data/v1.parquet
python src/data_generation/generator.py  # Run 2
diff data/experiment_users.parquet data/v1.parquet  # Should be identical
```

---

## Design Decisions

### Object-Oriented Structure

Classes like `MetricComputer`, `InferenceEngine`, `DataValidator` separate concerns and enable:
- Unit testing of statistical logic
- Replacement of components (e.g., swap inference method)
- Extension to new metrics or checks

### SQL Inclusion

Many organizations use SQL for experiment analysis. Including validation and breakdown queries demonstrates:
- Cross-language verification (SQL results match Python)
- Understanding of when SQL is appropriate
- Ability to work in SQL-first environments

### Makefile Over Scripts

`make data validate metrics` is more discoverable and conventional than custom bash scripts for engineers reviewing code.

---

## Technology Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Core | Python 3.9+ | Standard for data analysis |
| Data | pandas, numpy | Industry-standard libraries |
| Stats | scipy, statsmodels | Mature statistical inference |
| Viz | matplotlib | Publication-quality figures |
| Format | Parquet | Efficient columnar storage |
| Tests | pytest | Standard Python testing |

---

## Assumptions and Limitations

### Assumptions

1. Random assignment independent of user characteristics
2. No interference between users (SUTVA)
3. Treatment effect is stable over experiment window
4. No novelty effects

### Limitations

1. Synthetic data lacks real-world messiness (outliers, missing values, fraud)
2. Single experiment; production needs sequential testing frameworks
3. No time-of-day or seasonality modeling
4. Binary metrics only (no continuous outcomes like revenue)

### What This Still Demonstrates

- Statistical rigor: confidence intervals, effect sizes, power analysis
- Data quality awareness: SRM is a critical check often overlooked
- Decision framing: ship criteria defined upfront, not after seeing results
- Production patterns: OOP, tests, reproducibility

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Appendix

### File Reference

| File | Purpose |
|------|---------|
| `config.py` | Experiment parameters (seed, rates, thresholds) |
| `generator.py` | Deterministic synthetic data creation |
| `checks.py` | SRM, contamination, schema validation |
| `compute.py` | Metric calculation (CTR, CVR, lifts) |
| `inference.py` | Confidence intervals, p-values, MDE |
| `summary.py` | Markdown report generation |
| `visualizations.py` | Figure creation (tables, CI plots) |

### Metrics Definitions

**CTR (Click-Through Rate):** `P(clicked | eligible)` - measures engagement

**CVR (Conversion Rate):** `P(converted | eligible)` - measures desired actions

---

**End-to-end experiment evaluation with statistical rigor.**
