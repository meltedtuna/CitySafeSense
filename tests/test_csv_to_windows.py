import os
import numpy as np
import pandas as pd
import tempfile
from src.tools import csv_to_windows

def create_irregular_csv(path, n=500):
    # create irregular timestamps and random sensor columns
    import random
    import pandas as pd
    times = []
    t = pd.Timestamp.now()
    for i in range(n):
        # random jitter between 15ms and 30ms (approx ~50Hz average)
        jitter_ms = random.randint(15, 30)
        t = t + pd.Timedelta(milliseconds=jitter_ms)
        times.append(t)
    df = pd.DataFrame({
        'timestamp': times,
        'ax': np.random.randn(n),
        'ay': np.random.randn(n),
        'az': np.random.randn(n),
        'gx': np.random.randn(n),
        'gy': np.random.randn(n),
    })
    df.to_csv(path, index=False)

def test_csv_to_windows_resamples_and_writes(tmp_path):
    input_dir = tmp_path / "raw_csvs"
    out_dir = tmp_path / "data"
    input_dir.mkdir()
    out_dir.mkdir()
    csv_path = input_dir / "test1.csv"
    create_irregular_csv(str(csv_path), n=300)
    # run main with target_hz 50
    csv_to_windows.main(input_dir=str(input_dir), out_dir=str(out_dir), seq_len=100, stride=50, feature_list=['ax','ay','az','gx','gy'], target_hz=50)
    rep_folder = os.path.join(str(out_dir), "rep_windows")
    assert os.path.exists(rep_folder)
    files = os.listdir(rep_folder)
    assert len(files) > 0
    # check sample.npy exists
    sample = np.load(os.path.join(str(out_dir), "sample.npy"))
    assert sample.ndim == 2
