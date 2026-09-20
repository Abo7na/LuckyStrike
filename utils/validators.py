def is_valid_number(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
