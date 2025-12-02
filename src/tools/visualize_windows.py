"""
Visualize a saved window (.npy) or random sample from data/rep_windows directory.
Saves plot to figures/window_plot.png
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from glob import glob

def plot_window(path, out='figures/window_plot.png'):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    win = np.load(path)
    if win.ndim == 2:
        seq_len, features = win.shape
        plt.figure(figsize=(8,4))
        for i in range(min(features,6)):
            plt.plot(win[:,i], label=f'feat{i}')
        plt.legend()
        plt.title(os.path.basename(path))
        plt.xlabel('t')
        plt.ylabel('value')
        plt.tight_layout()
        plt.savefig(out)
        print(f"Saved window plot to {out}")
    else:
        print("Unsupported window shape:", win.shape)

def plot_random_window(folder='data/rep_windows', out='figures/window_plot.png'):
    files = glob(os.path.join(folder, '*.npy'))
    if not files:
        print("No windows found in", folder)
        return
    path = files[0]
    plot_window(path, out)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default=None, help='Path to .npy window')
    parser.add_argument('--out', default='figures/window_plot.png')
    args = parser.parse_args()
    if args.path:
        plot_window(args.path, args.out)
    else:
        plot_random_window(out=args.out)
