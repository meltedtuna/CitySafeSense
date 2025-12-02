"""
Utilities to save model architecture and a human-readable model summary alongside checkpoints.

Usage:
    from src.train.save_model_architecture import save_model_architecture
    save_model_architecture(model, out_dir='checkpoints', name='citysafesense_model')
This will create:
- {out_dir}/{name}.json  (model.to_json())
- {out_dir}/{name}_summary.txt  (model.summary() output)
"""
import os
import json
import io
import sys

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def save_model_architecture(model, out_dir='checkpoints', name='model_arch'):
    """
    Save model.to_json() and a text summary to out_dir with the given name.
    Returns the paths of the files written.
    """
    ensure_dir(out_dir)
    json_path = os.path.join(out_dir, f"{name}.json")
    summary_path = os.path.join(out_dir, f"{name}_summary.txt")

    # Save JSON architecture
    model_json = model.to_json()
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(model_json)

    # Save text summary
    stream = io.StringIO()
    model.summary(print_fn=lambda x: stream.write(x + '\n'))
    summary_str = stream.getvalue()
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_str)

    return json_path, summary_path

if __name__ == "__main__":
    # simple CLI to load a keras model and save architecture; expects a Keras saved model file or weights won't be loaded
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', help='Path to a saved Keras model (full model) to load before saving architecture', default=None)
    parser.add_argument('--out_dir', help='Directory to save artifacts', default='checkpoints')
    parser.add_argument('--name', help='Base name for files', default='model_arch')
    args = parser.parse_args()

    # If checkpoint provided, attempt to load model and then save its architecture
    if args.checkpoint:
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(args.checkpoint)
            save_model_architecture(model, out_dir=args.out_dir, name=args.name)
            print(f"Saved architecture and summary to {args.out_dir}")
        except Exception as e:
            print("Failed to load model:", e)
            raise
    else:
        print("No checkpoint provided. This script is intended to be used programmatically to save model.to_json().")
