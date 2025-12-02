# Quantization Best Practices

This document describes best practices for post-training quantization and how to collect a representative dataset for the TFLite converter.

## Why quantize?
Quantization reduces model size and improves inference latency on edge devices by converting weights and/or activations to 8-bit integers.

## Representative dataset
- The TFLite converter uses a **representative dataset** to map floating-point ranges to integer ranges.
- It should consist of **real samples** that reflect the distribution seen at inference time (same preprocessing, windowing, normalization).
- For CitySafeSense, a representative sample should be a single-window of sensor data shaped `(1, seq_len, features)` — exactly the model input.

## How to collect representative samples
1. Collect raw sensor streams (IMU, GNSS, acoustic) from devices in normal operational contexts.
2. Apply the exact preprocessing pipeline used in training:
   - Resampling / interpolation to fixed sampling rate
   - Windowing (e.g., 100-sample windows)
   - Mean/std normalization or other scaling
3. Save several hundred to a few thousand windows (100–1000 recommended).
4. Place them in `data/` and point `src/tools/representative_dataset.py` to your file(s). The default generator samples from `data/sample.npy`.

## Best practices
- Use real, diverse samples (different users, devices, noise conditions).
- If your model uses multiple input branches, ensure the representative dataset yields tuples of numpy arrays matching those inputs.
- Visualize quantized model outputs vs FP32 on a validation set to ensure acceptable accuracy degradation.
- Prefer dynamic range quantization for simplicity; use full-int8 only if you provide good representative data.

## Using the representative generator
The repo includes `src/tools/representative_dataset.py`. Customize it to read from your recorded dataset and apply the preprocessing pipeline.

Example in training:
```
python -m src.train.train_demo --epochs 1 --save_full_model --export_tflite --tflite_quantize
```
This will use the representative samples from `data/sample.npy` by default when quantizing.
