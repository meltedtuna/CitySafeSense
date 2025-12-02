# Visualization Examples

This page shows how to generate a test CSV, convert it into windows, and visualize a sample window.

Steps:

1. Generate a synthetic CSV with irregular timestamps:
```
python scripts/generate_test_csv.py --out raw_csvs/test_demo.csv --n 600
```

2. Convert CSVs to windows (resample to 50 Hz):
```
python -m src.tools.csv_to_windows --input_dir raw_csvs --out_dir data --seq_len 100 --stride 50 --features ax,ay,az,gx,gy,gz --target_hz 50
```

3. Plot a random window:
```
python -m src.tools.visualize_windows --out figures/demo_window.png
```

4. (Optional) Run a short training + export:
```
python -m src.train.train_demo --epochs 1 --save_full_model --export_tflite --tflite_quantize
```
