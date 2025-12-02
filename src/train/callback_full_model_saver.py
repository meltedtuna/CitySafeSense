
"""
Custom Keras callback that automatically saves the FULL model (.keras)
at the end of each epoch OR only when validation improves.

Usage:
    FullModelSaver(out_dir="checkpoints", save_best_only=True)

Produces:
    checkpoints/full_model_epochX.keras
or
    checkpoints/full_model_best.keras
"""

import os
import tensorflow as tf

class FullModelSaver(tf.keras.callbacks.Callback):
    def __init__(self, out_dir="checkpoints", save_best_only=True, monitor="val_loss"):
        super().__init__()
        self.out_dir = out_dir
        self.save_best_only = save_best_only
        self.monitor = monitor
        os.makedirs(out_dir, exist_ok=True)
        self.best = float("inf")

    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            return
        if self.save_best_only:
            current = logs.get(self.monitor)
            if current is None:
                return
            if current < self.best:
                self.best = current
                path = os.path.join(self.out_dir, "full_model_best.keras")
                self.model.save(path)
                print(f"[FullModelSaver] Saved improved full model → {path}")
        else:
            path = os.path.join(self.out_dir, f"full_model_epoch{epoch+1}.keras")
            self.model.save(path)
            print(f"[FullModelSaver] Saved full model → {path}")
