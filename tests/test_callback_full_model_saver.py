import os
import tempfile
import numpy as np
import tensorflow as tf
from src.train.callback_full_model_saver import FullModelSaver

def test_full_model_saver_saves_best(tmp_path):
    # build tiny model
    model = tf.keras.Sequential([tf.keras.layers.Input(shape=(10,)), tf.keras.layers.Dense(2, activation='softmax')])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

    out_dir = str(tmp_path / "checkpoints")
    cb = FullModelSaver(out_dir=out_dir, save_best_only=True, monitor='val_loss')
    # attach model to callback (normally Keras does this)
    cb.set_model(model)
    # simulate epoch logs improving
    logs_epoch1 = {'val_loss': 1.0}
    cb.on_epoch_end(0, logs_epoch1)
    # Expect file created
    files = os.listdir(out_dir)
    assert any(f.startswith("full_model_best") for f in files)

def test_full_model_saver_saves_every_epoch(tmp_path):
    model = tf.keras.Sequential([tf.keras.layers.Input(shape=(10,)), tf.keras.layers.Dense(2, activation='softmax')])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

    out_dir = str(tmp_path / "checkpoints2")
    cb = FullModelSaver(out_dir=out_dir, save_best_only=False)
    cb.set_model(model)
    # simulate two epochs
    cb.on_epoch_end(0, {'loss': 0.5})
    cb.on_epoch_end(1, {'loss': 0.4})
    files = os.listdir(out_dir)
    assert any(f.startswith("full_model_epoch1") for f in files)
    assert any(f.startswith("full_model_epoch2") for f in files)
