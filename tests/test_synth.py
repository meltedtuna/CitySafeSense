from src.tools.generate_synthetic import generate_sequence
def test_generate_shape():
    data = generate_sequence(duration_s=1)
    assert data.ndim == 2
    assert data.shape[1] >= 8
