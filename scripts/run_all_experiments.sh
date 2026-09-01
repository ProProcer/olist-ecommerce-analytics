#!/usr/bin/env bash
# Run the default Hydra configuration, then every config in configs/experiment.
# Usage: bash scripts/run_all_experiments.sh
# Optional: PYTHON_BIN=python3.12 bash scripts/run_all_experiments.sh

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON_BIN:-python}"

cd "$project_root"

echo "==> Running default configuration"
"$python_bin" train.py

shopt -s nullglob
experiment_configs=(configs/experiment/*.yaml)

for config_path in "${experiment_configs[@]}"; do
    experiment_name="$(basename "$config_path" .yaml)"
    echo "==> Running experiment: $experiment_name"
    "$python_bin" train.py "experiment=$experiment_name"
done

echo "==> All experiments completed successfully."
