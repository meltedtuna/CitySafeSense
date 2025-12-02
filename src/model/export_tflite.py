"""
Export a Keras model (or .keras file) to a TFLite file with optional quantization.
Works with a loaded tf.keras.Model or a path to a saved model.
"""
import tensorflow as tf
import os

def export_model_to_tflite(model_or_path, out_path='model.tflite', quantize=False, representative_data=None):
    """
    model_or_path: tf.keras.Model instance or path to saved model (.keras or SavedModel dir)
    quantize: bool, if True apply default post-training quantization
    representative_data: a generator function returning representative tensor samples for full-int8 quantization (optional)
    """
    # Load if a path is supplied
    if isinstance(model_or_path, str):
        model = tf.keras.models.load_model(model_or_path)
    else:
        model = model_or_path

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    if quantize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        # Optionally set representative dataset for better quantization (if provided)
        if representative_data is not None:
            converter.representative_dataset = representative_data
    tflite_model = converter.convert()
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(tflite_model)
    print(f"Exported TFLite model to {out_path}")
    return out_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='Path to .keras model or SavedModel dir')
    parser.add_argument('--out', default='model.tflite')
    parser.add_argument('--quantize', action='store_true')
    args = parser.parse_args()
    export_model_to_tflite(args.model, args.out, args.quantize)
