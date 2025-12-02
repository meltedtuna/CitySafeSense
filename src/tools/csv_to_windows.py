"""
Convert raw sensor CSV recordings into sliding window .npy files and aggregate sample file.

Enhancements:
- Detects timestamp column (names: timestamp, ts, time, datetime) and resamples to a fixed sampling rate (--target_hz).
- If timestamp present, rows will be resampled using linear interpolation to uniform sampling.
- If no timestamp, assumes rows are uniformly sampled.
"""
import os
import argparse
import numpy as np
import pandas as pd
import json
from glob import glob

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def _detect_time_column(df):
    candidates = ['timestamp','ts','time','datetime','date','t']
    for c in candidates:
        if c in df.columns:
            return c
    return None

def _resample_dataframe(df, time_col, target_hz):
    # convert to datetime
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col])
    df = df.set_index(time_col)
    # desired period string in milliseconds
    period_ms = int(round(1000.0 / float(target_hz)))
    rule = f"{period_ms}L"  # L = milliseconds
    # reindex to uniform timestamps covering the original span
    start = df.index.min()
    end = df.index.max()
    new_index = pd.date_range(start=start, end=end, freq=rule)
    df = df.reindex(df.index.union(new_index))
    # interpolate numeric columns
    df = df.interpolate(method='time').reindex(new_index)
    return df

def process_file(path, columns, seq_len=100, stride=50, out_folder="data/rep_windows", source_tag=None, target_hz=None):
    df = pd.read_csv(path)
    # detect timestamp and resample if requested
    time_col = _detect_time_column(df)
    if time_col and target_hz:
        try:
            df = _resample_dataframe(df, time_col, target_hz)
            df = df.reset_index(drop=True)
        except Exception as e:
            print("Resampling failed for", path, ":", e)
    # select columns that exist
    cols = [c for c in columns if c in df.columns] if columns else list(df.columns)
    if not cols:
        raise ValueError("None of the requested columns found in " + path)
    data = df[cols].values.astype('float32')
    T, F = data.shape
    windows = []
    metadata = []
    idx = 0
    for start in range(0, max(1, T - seq_len + 1), stride):
        win = data[start:start+seq_len]
        if win.shape[0] < seq_len:
            # pad
            pad_len = seq_len - win.shape[0]
            win = np.vstack([win, np.zeros((pad_len, F), dtype='float32')])
        # simple normalization per-window
        mean = np.mean(win, axis=0, keepdims=True)
        std = np.std(win, axis=0, keepdims=True) + 1e-6
        win = (win - mean) / std
        fname = f"{source_tag or os.path.splitext(os.path.basename(path))[0]}_{idx}.npy"
        out_path = os.path.join(out_folder, fname)
        np.save(out_path, win)
        windows.append(win)
        metadata.append({"file": fname, "source": path, "start_row": int(start), "end_row": int(start+seq_len)})
        idx += 1
    return windows, metadata

def aggregate_windows_to_sample(windows, out_path="data/sample.npy"):
    # concatenate windows along time dimension to create a long T x F array for fallback
    if not windows:
        return
    arrs = [w for w in windows]
    concat = np.vstack(arrs)
    np.save(out_path, concat)

def main(input_dir="raw_csvs", out_dir="data", seq_len=100, stride=50, feature_list=None, target_hz=None):
    ensure_dir(out_dir)
    rep_folder = os.path.join(out_dir, "rep_windows")
    ensure_dir(rep_folder)
    metadata_all = []
    windows_all = []
    csvs = glob(os.path.join(input_dir, "*.csv"))
    if not csvs:
        print("No CSV files found in", input_dir)
        return
    for csv in csvs:
        try:
            wins, meta = process_file(csv, feature_list, seq_len=seq_len, stride=stride, out_folder=rep_folder, source_tag=os.path.splitext(os.path.basename(csv))[0], target_hz=target_hz)
            windows_all.extend(wins)
            metadata_all.extend(meta)
        except Exception as e:
            print("Failed to process", csv, e)
    # save aggregated sample for fallback
    aggregate_windows_to_sample(windows_all, out_path=os.path.join(out_dir, "sample.npy"))
    # save metadata
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump(metadata_all, f, indent=2)
    print(f"Saved {len(windows_all)} windows to {rep_folder} and aggregated sample to {os.path.join(out_dir,'sample.npy')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='raw_csvs')
    parser.add_argument('--out_dir', default='data')
    parser.add_argument('--seq_len', type=int, default=100)
    parser.add_argument('--stride', type=int, default=50)
    parser.add_argument('--features', type=str, default=None, help='Comma-separated feature columns to use, e.g. ax,ay,az,gx,gy,gz,speed')
    parser.add_argument('--target_hz', type=float, default=None, help='Target sampling rate in Hz (e.g. 50). If provided and a timestamp column exists, data will be resampled.')
    args = parser.parse_args()
    feature_list = args.features.split(',') if args.features else None
    main(input_dir=args.input_dir, out_dir=args.out_dir, seq_len=args.seq_len, stride=args.stride, feature_list=feature_list, target_hz=args.target_hz)
