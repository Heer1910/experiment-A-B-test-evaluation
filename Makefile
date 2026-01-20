.PHONY: all data validate metrics inference visualize test clean help

# Default target
all: data validate metrics visualize

# Generate synthetic experiment data
data:
	@echo "Generating experiment data..."
	python3 src/data_generation/generator.py

# Run data validation checks
validate:
	@echo "Running validation checks..."
	PYTHONPATH=. python3 src/validation/checks.py

# Compute metrics (CTR, CVR)
metrics:
	@echo "Computing metrics..."
	PYTHONPATH=. python3 src/metrics/compute.py

# Run statistical inference
inference:
	@echo "Running statistical inference..."
	PYTHONPATH=. python3 src/stats/inference.py

# Generate visualizations
visualize:
	@echo "Generating visualizations..."
	PYTHONPATH=. python3 src/utils/visualizations.py

# Run automated tests
test:
	@echo "Running tests..."
	python3 -m pytest tests/ -v

# Clean generated outputs
clean:
	@echo "Cleaning generated files..."
	rm -rf data/*.parquet figures/*.png reports/*.md
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -rf .pytest_cache

# Display help
help:
	@echo "Available targets:"
	@echo "  make data        - Generate synthetic experiment data"
	@echo "  make validate    - Run data quality checks"
	@echo "  make metrics     - Compute experiment metrics"
	@echo "  make inference   - Run statistical inference"
	@echo "  make visualize   - Generate figures"
	@echo "  make test        - Run automated tests"
	@echo "  make clean       - Remove generated files"
	@echo "  make all         - Run data + validate + metrics + visualize"
