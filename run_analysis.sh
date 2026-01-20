#!/bin/bash

# A/B Testing Analysis - Complete Workflow
# This script runs the entire analysis pipeline step by step

echo "======================================================================"
echo "A/B TESTING EXPERIMENTATION ANALYSIS"
echo "======================================================================"
echo ""

# Step 1: Generate synthetic data
echo "Step 1: Generating synthetic experiment data..."
python3 src/data_generation/generator.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Data generation failed"
    exit 1
fi
echo "✓ Data generation complete"
echo ""

# Step 2: Validate data quality
echo "Step 2: Running data validation checks..."
PYTHONPATH=. python3 src/validation/checks.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Data validation failed"
    exit 1
fi
echo "✓ Validation complete"
echo ""

# Step 3: Compute metrics
echo "Step 3: Computing metrics (CTR, CVR)..."
PYTHONPATH=. python3 src/metrics/compute.py
echo "✓ Metrics computed"
echo ""

# Step 4: Run statistical inference
echo "Step 4: Running statistical inference..."
PYTHONPATH=. python3 src/stats/inference.py
echo "✓ Statistical inference complete"
echo ""

# Step 5: Generate visualizations
echo "Step 5: Generating visualizations..."
PYTHONPATH=. python3 src/utils/visualizations.py
if [ $? -ne 0 ]; then
    echo "❌ Error: Visualization generation failed"
    exit 1
fi
echo "✓ Visualizations created"
echo ""

# Step 6: Run automated tests (optional)
echo "Step 6: Running automated tests..."
python3 -m pytest tests/ -v --tb=short
echo ""

echo "======================================================================"
echo "✓ ANALYSIS COMPLETE!"
echo "======================================================================"
echo ""
echo "📊 View Results:"
echo "  - Executive Summary: reports/executive_summary.md"
echo "  - Visualizations: figures/*.png"
echo "  - One-Pager: reports/experiment_one_pager.md"
echo ""
echo "📁 All outputs saved in current directory"
echo "======================================================================"
