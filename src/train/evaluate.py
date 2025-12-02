"""
Evaluation utilities for CitySafeSense.

Usage:
    python -m src.train.evaluate --checkpoint checkpoints/best_model.h5 --out_dir eval_outputs
"""
import os
import numpy as np
import tensorflow as tf
import json
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def _load_demo_test(n_samples=128, seq_len=100, features=10, num_classes=3):
    X = np.random.randn(n_samples, seq_len, features).astype('float32')
    y = np.random.randint(0, num_classes, size=(n_samples,))
    return X, y

def evaluate_checkpoint(checkpoint_path, out_dir='eval_outputs'):
    ensure_dir(out_dir)
    # build model with matching shape - in practice persist model architecture to disk or reconstruct appropriately
    # For demo we will build a model that matches the train_demo defaults
    from src.model.tcn import build_tcn
    num_classes = 3
    dummy_input = (100, 10)
    model = build_tcn(input_shape=dummy_input, num_classes=num_classes)
    # load weights - support both h5 and keras checkpoints
    if args.full_model:
        try:
            model = tf.keras.models.load_model(args.full_model)
            print('Loaded full model from', args.full_model)
        except Exception as e:
            print('Failed to load full model path:', e)
            # fallback to checkpoint if provided
            if checkpoint_path:
                try:
                    model.load_weights(checkpoint_path)
                except Exception as e2:
                    print('Failed to load weights from checkpoint:', e2)
                    raise RuntimeError('Unable to load model from full_model or checkpoint')
            else:
                raise RuntimeError('No valid model to load')
    else:
        try:
            model.load_weights(checkpoint_path)
        except Exception as e:
            print('Failed to load weights directly:', e)
            # try loading as a keras model file
            try:
                model = tf.keras.models.load_model(checkpoint_path)
                print('Loaded full model from file.')
            except Exception as e2:
                raise RuntimeError('Unable to load checkpoint: ' + str(e2))
    X_test, y_test = _load_demo_test()
    y_pred_probs = model.predict(X_test, batch_size=16)
    y_pred = np.argmax(y_pred_probs, axis=1)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)
    # save metrics
    metrics = {
        'accuracy': float(acc),
        'report': report,
        'confusion_matrix': cm.tolist()
    }
    with open(os.path.join(out_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    # plot confusion matrix
    plt.figure(figsize=(5,5))
    plt.imshow(cm, interpolation='nearest')
    plt.title('Confusion matrix')
    plt.colorbar()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'confusion_matrix.png'))
    print(f"Saved metrics to {out_dir}")
    return metrics

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', required=False)
    parser.add_argument('--full_model', required=False, help='Path to a full .keras model file to evaluate (preferred)')
    parser.add_argument('--out_dir', default='eval_outputs')
    args = parser.parse_args()
    evaluate_checkpoint(args.checkpoint, args.out_dir)
