"""
Simple visualization utilities for sequences.
"""
import matplotlib.pyplot as plt
import numpy as np
import os

def overlay_plot(seq_a, seq_b, out='figures/overlay.png'):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.figure()
    plt.plot(seq_a, label='A')
    plt.plot(seq_b, label='B', alpha=0.7)
    plt.legend()
    plt.xlabel('t')
    plt.ylabel('value')
    plt.savefig(out)
    print(f"Saved overlay plot to {out}")
