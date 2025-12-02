"""
Enhanced TCN model with residual blocks, dropout and optional global pooling.
Designed to be still lightweight but more expressive for CitySafeSense use-cases.
"""
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers

def residual_block(x, filters, kernel_size, dilation_rate, dropout=0.1, name=None):
    conv = layers.Conv1D(filters=filters, kernel_size=kernel_size,
                         dilation_rate=dilation_rate, padding='causal',
                         kernel_regularizer=regularizers.l2(1e-5),
                         name=None if name is None else name + "_conv")(x)
    conv = layers.BatchNormalization(name=None if name is None else name + "_bn")(conv)
    conv = layers.Activation("relu", name=None if name is None else name + "_act")(conv)
    conv = layers.SpatialDropout1D(rate=dropout, name=None if name is None else name + "_drop")(conv)
    # 1x1 conv for residual connection if channels differ
    if x.shape[-1] != filters:
        res = layers.Conv1D(filters=filters, kernel_size=1, padding='same',
                            name=None if name is None else name + "_res_conv")(x)
    else:
        res = x
    return layers.Add(name=None if name is None else name + "_add")([res, conv])

def build_tcn(input_shape=(100, 10),
              num_classes=3,
              num_filters=24,
              kernel_size=3,
              dilation_base=2,
              num_stacks=2,
              blocks_per_stack=3,
              dropout=0.1,
              global_pool='avg'):
    """
    input_shape: tuple (seq_len, features) or (None, features) for variable length
    num_filters: base number of filters
    num_stacks: how many dilation stacks (increases receptive field)
    blocks_per_stack: number of residual blocks per stack
    global_pool: 'avg', 'max', or None (then returns sequence output)
    """
    inp = layers.Input(shape=input_shape, name='input')
    x = inp
    # initial projection to desired channels
    x = layers.Conv1D(filters=num_filters, kernel_size=1, padding='causal', name='proj_conv')(x)

    for stack in range(num_stacks):
        for b in range(blocks_per_stack):
            d = dilation_base ** b
            name = f"stack{stack}_block{b}"
            x = residual_block(x, filters=num_filters, kernel_size=kernel_size, dilation_rate=d, dropout=dropout, name=name)
        # optionally increase filters between stacks
        num_filters = int(num_filters * 1.2)

    if global_pool == 'avg':
        x = layers.GlobalAveragePooling1D(name='gap')(x)
    elif global_pool == 'max':
        x = layers.GlobalMaxPooling1D(name='gmp')(x)
    else:
        # return sequence output flattened
        x = layers.Flatten(name='flat')(x)

    x = layers.Dense(64, activation='relu', name='fc1')(x)
    x = layers.Dropout(0.2, name='fc1_drop')(x)
    out = layers.Dense(num_classes, activation='softmax', name='output')(x)

    model = models.Model(inputs=inp, outputs=out, name='CitySafeSense_TCN')
    return model
