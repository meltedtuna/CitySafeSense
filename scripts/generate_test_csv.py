"""
Generate synthetic CSVs with irregular timestamps and sensor columns for demo/testing.
"""
import argparse
import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_csv(path, n=600, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    times = []
    t = datetime.now()
    for i in range(n):
        jitter_ms = random.randint(15, 30)  # ~50Hz average
        t = t + timedelta(milliseconds=jitter_ms)
        times.append(t.isoformat())
    df = pd.DataFrame({
        'timestamp': times,
        'ax': np.random.randn(n),
        'ay': np.random.randn(n),
        'az': np.random.randn(n),
        'gx': np.random.randn(n),
        'gy': np.random.randn(n),
        'gz': np.random.randn(n),
        'speed': np.abs(np.random.randn(n)) * 1.2
    })
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print("Wrote test CSV to", path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='raw_csvs/test_demo.csv')
    parser.add_argument('--n', type=int, default=600)
    args = parser.parse_args()
    generate_csv(args.out, n=args.n)
