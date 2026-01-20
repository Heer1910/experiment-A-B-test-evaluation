# Quick Start Guide

## Running the Analysis Yourself

### Option 1: Use the Automated Script (Easiest)

```bash
cd /Users/heerpatel/.gemini/antigravity/scratch/experiment-ab-test-evaluation
./run_analysis.sh
```

This will run all 6 steps automatically and show you the results.

---

### Option 2: Run Steps Manually

```bash
# Navigate to project
cd /Users/heerpatel/.gemini/antigravity/scratch/experiment-ab-test-evaluation

# Step 1: Generate data
python3 src/data_generation/generator.py

# Step 2: Validate data
PYTHONPATH=. python3 src/validation/checks.py

# Step 3: Compute metrics
PYTHONPATH=. python3 src/metrics/compute.py

# Step 4: Run inference
PYTHONPATH=. python3 src/stats/inference.py

# Step 5: Generate visualizations
PYTHONPATH=. python3 src/utils/visualizations.py

# Step 6: Run tests (optional)
python3 -m pytest tests/ -v
```

---

## Viewing the Results

### Executive Summary (Decision Document)
```bash
cat reports/executive_summary.md
```

### Visualizations
```bash
open figures/metric_comparison.png
open figures/cvr_confidence_interval.png
open figures/segment_lifts_by_device.png
```

### One-Pager
```bash
cat reports/experiment_one_pager.md
```

---

## Where Are All the Files?

**Current location:**
```
/Users/heerpatel/.gemini/antigravity/scratch/experiment-ab-test-evaluation
```

**To move to another location (e.g., Desktop):**
```bash
cp -r /Users/heerpatel/.gemini/antigravity/scratch/experiment-ab-test-evaluation ~/Desktop/
cd ~/Desktop/experiment-ab-test-evaluation
./run_analysis.sh
```

---

## What Each File Does

| File/Folder | Purpose |
|-------------|---------|
| `src/config.py` | All experiment parameters (seed, rates, lifts) |
| `src/data_generation/generator.py` | Creates synthetic experiment data |
| `src/validation/checks.py` | Validates data quality (SRM, contamination) |
| `src/metrics/compute.py` | Calculates CTR and CVR |
| `src/stats/inference.py` | Computes confidence intervals and p-values |
| `src/utils/visualizations.py` | Generates all 3 figures |
| `data/experiment_users.parquet` | Generated experiment dataset |
| `figures/*.png` | Output visualizations |
| `reports/*.md` | Executive summary and one-pager |
| `tests/` | Automated test suite |
| `run_analysis.sh` | One-command to run everything |

---

## Troubleshooting

### If you get "Module not found" errors:
```bash
pip3 install -r requirements.txt
```

### If run_analysis.sh won't execute:
```bash
chmod +x run_analysis.sh
```

### To regenerate everything from scratch:
```bash
rm -rf data/ figures/ reports/
./run_analysis.sh
```

---

## Key Results Summary

- **CVR Lift:** +0.25pp (+63% relative)
- **CTR Lift:** +1.78pp (+15% relative)
- **95% CI for CVR:** [+0.12pp, +0.38pp]
- **Decision:** SHIP ✓

---

**For full documentation, see README.md**
