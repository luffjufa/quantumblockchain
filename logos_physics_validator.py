def validate_logos_field_invariant(tensor_metrics, invariant):
    entropy = tensor_metrics.get("spectral_entropy", 0.0)
    shear = tensor_metrics.get("shear_factor", 0.0)
    
    if not (0.3 <= entropy <= 0.7):
        return False
    if abs(shear) > 0.8:
        return False
    if invariant < 2.0 or invariant > 15.0:
        return False
    return True
