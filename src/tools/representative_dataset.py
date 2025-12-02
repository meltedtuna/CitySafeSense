"""
Representative dataset generator that samples from a folder of .npy window files or from data/sample.npy.

It looks for:
- data/rep_windows/*.npy  (each file is a single window shaped (seq_len, features))
- fallback to data/sample.npy (T x F) and generate sliding windows
- final fallback to synthetic random samples

Yields representative samples shaped as [1, seq_len, features]
"""
import numpy as np
import os
import glob
import random
import json

def _standardize_window(win):
    mean = np.mean(win, axis=0, keepdims=True)
    std = np.std(win, axis=0, keepdims=True) + 1e-6
    return (win - mean) / std

def representative_generator_from_folder(folder="data/rep_windows", num_samples=100):
    """
    Samples random .npy window files from a folder. Each .npy should be (seq_len, features).
    Yields lists of numpy arrays as required by the TFLite converter.
    """
    if not os.path.exists(folder):
        return None
    files = glob.glob(os.path.join(folder, "*.npy"))
    if not files:
        return None
    for _ in range(num_samples):
        fn = random.choice(files)
        try:
            win = np.load(fn).astype('float32')
        except Exception:
            # skip corrupted
            continue
        # ensure 2D
        if win.ndim == 1:
            win = win.reshape(-1,1)
        win = _standardize_window(win)
        yield [win.reshape(1, win.shape[0], win.shape[1])]

def _load_sample(path="data/sample.npy"):
    if os.path.exists(path):
        try:
            data = np.load(path)
            if data.ndim == 1:
                data = data.reshape(-1,1)
            return data.astype('float32')
        except Exception:
            return None
    return None

def representative_generator(num_samples=100, seq_len=100, features=10, sample_path="data/sample.npy", folder="data/rep_windows"):
    """
    Top-level representative generator. Prefers folder of precomputed windows, then data/sample.npy, then synthetic.
    """
    # try folder of .npy windows
    gen = representative_generator_from_folder(folder=folder, num_samples=num_samples)
    if gen is not None:
        for item in gen:
            yield item
        return

    # try aggregated sample file
    data = _load_sample(sample_path)
    if data is None or data.shape[0] < seq_len:
        for _ in range(num_samples):
            sample = np.random.randn(1, seq_len, features).astype('float32')
            yield [sample]
        return

    T, F = data.shape
    if F < features:
        pad_width = features - F
        data = np.pad(data, ((0,0),(0,pad_width)), mode='constant')
        F = features
    elif F > features:
        data = data[:, :features]
        F = features

    for _ in range(num_samples):
        if T == seq_len:
            start = 0
        else:
            start = np.random.randint(0, max(1, T - seq_len))
        win = data[start:start+seq_len]
        if win.shape[0] < seq_len:
            pad_len = seq_len - win.shape[0]
            win = np.vstack([win, np.zeros((pad_len, F), dtype='float32')])
        win = _standardize_window(win)
        yield [win.reshape(1, seq_len, F)]
