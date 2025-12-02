"""
Synthetic sensor data generator for IMU (accel, gyro), GNSS speed/direction, and acoustic spikes.
Produces a numpy array with shape (T, features).
"""
import numpy as np
import argparse

def _simulate_segment(kind='walk', length=100, fs=50):
    t = np.linspace(0, length/ fs, length)
    if kind == 'walk':
        accel = 0.5 * np.sin(2 * np.pi * 1.5 * t) + 0.05 * np.random.randn(len(t))
        gyro = 0.1 * np.sin(2 * np.pi * 0.5 * t) + 0.02 * np.random.randn(len(t))
        speed = 1.3 + 0.1 * np.random.randn(len(t))
        acoustic = 0.01 * np.random.randn(len(t))
    elif kind == 'drive':
        accel = 0.1 * np.random.randn(len(t))
        gyro = 0.05 * np.random.randn(len(t))
        speed = 8.0 + 0.5 * np.random.randn(len(t))
        acoustic = 0.005 * np.random.randn(len(t))
    elif kind == 'mugging':
        accel = 2.0 * np.exp(-t*5) + 0.3 * np.random.randn(len(t))
        gyro = 1.0 * np.exp(-t*3) + 0.1 * np.random.randn(len(t))
        speed = 0.0 * t + 0.2 * np.random.randn(len(t))
        acoustic = 0.5 * (t<0.05) + 0.1 * np.random.randn(len(t))
    else:
        accel = 0.1 * np.random.randn(len(t))
        gyro = 0.1 * np.random.randn(len(t))
        speed = 0.5 * np.random.randn(len(t))
        acoustic = 0.01 * np.random.randn(len(t))
    # 3-axis accel/gyro simulated by duplicating with small rotations
    accel3 = np.vstack([accel, accel*0.9 + 0.01*np.random.randn(len(t)), accel*1.1 + 0.01*np.random.randn(len(t))]).T
    gyro3 = np.vstack([gyro, gyro*0.95 + 0.005*np.random.randn(len(t)), gyro*1.05 + 0.005*np.random.randn(len(t))]).T
    features = np.hstack([accel3, gyro3, speed.reshape(-1,1), np.unwrap(np.angle(np.exp(1j*speed))) .reshape(-1,1), acoustic.reshape(-1,1)])
    return features

def generate_sequence(duration_s=60, fs=50):
    segments = []
    total = 0
    while total < duration_s:
        kind = np.random.choice(['walk','walk','drive','mugging'], p=[0.6,0.1,0.2,0.1])
        length = int(min(fs*duration_s - total*fs, np.random.randint(50, 200)))
        seg = _simulate_segment(kind=kind, length=length, fs=fs)
        segments.append(seg)
        total += length / fs
    data = np.vstack(segments)
    return data

def main(out='data/synthetic.npy', duration=60):
    data = generate_sequence(duration_s=duration)
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    np.save(out, data)
    print(f"Saved synthetic data to {out}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='data/synthetic.npy')
    parser.add_argument('--duration', type=int, default=60)
    args = parser.parse_args()
    main(args.out, args.duration)
