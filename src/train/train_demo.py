"""
Training demo with callbacks and improved training utilities.
Saves best checkpoint and training history (json). Demonstrates early stopping, LR scheduling, and TensorBoard.
"""
import numpy as np
import tensorflow as tf
import os, json
from src.model.tcn import build_tcn
from src.train.save_model_architecture import save_model_architecture
from src.model.export_tflite import export_model_to_tflite
from src.tools.representative_dataset import representative_generator

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
from src.train.callback_full_model_saver import FullModelSaver

def _load_demo_data(n_samples=256, seq_len=100, features=10, num_classes=3):
    # synthetic balanced dataset with simple patterns
    X = np.random.randn(n_samples, seq_len, features).astype('float32')
    y = np.random.randint(0, num_classes, size=(n_samples,))
    y = tf.keras.utils.to_categorical(y, num_classes)
    # split train/val
    split = int(0.8 * n_samples)
    return (X[:split], y[:split]), (X[split:], y[split:])

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def main(epochs=10, batch_size=16, out_dir='checkpoints'):
    ensure_dir(out_dir)
    (X_train, y_train), (X_val, y_val) = _load_demo_data()
    model = build_tcn(input_shape=X_train.shape[1:], num_classes=y_train.shape[1])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    # Save model architecture and human-readable summary for robust recovery
    try:
        save_model_architecture(model, out_dir=out_dir, name='citysafesense_model')
    except Exception as e:
        print('Warning: failed to save model architecture:', e)

    # callbacks
    cb_early = EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True)
    cb_ckpt = ModelCheckpoint(os.path.join(out_dir, 'best_model.h5'), monitor='val_loss', save_best_only=True)
    cb_reduce = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6)
    tb_logdir = os.path.join('runs', 'demo')
    cb_tb = TensorBoard(log_dir=tb_logdir)
    cb_full = FullModelSaver(out_dir=out_dir, save_best_only=True)
    if not save_full_model:
        cb_full = None

    history = model.fit(X_train, y_train,
                        validation_data=(X_val, y_val),
                        epochs=epochs,
                        batch_size=batch_size,
                        callbacks=[cb_early, cb_ckpt, cb_reduce, cb_tb])
    # save final weights and history
    model.save_weights(os.path.join(out_dir, 'final_weights.ckpt'))
    with open(os.path.join(out_dir, 'history.json'), 'w') as f:
        json.dump(history.history, f, indent=2)
    print(f"Training complete. Best checkpoint: {os.path.join(out_dir, 'best_model.h5')}")
    return model, history.history

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--save_full_model', action='store_true', help='Save full .keras model each time val improves')
    parser.add_argument('--export_tflite', action='store_true', help='Export a TFLite model after training using the best full model if available')
    parser.add_argument('--tflite_quantize', action='store_true', help='Apply default post-training quantization when exporting TFLite')
    args = parser.parse_args()
    save_full_model = args.save_full_model
    main(epochs=args.epochs)
