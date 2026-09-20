from utils.validators import is_valid_number


def format_currency(value):
    return f"{float(value):,.2f}"


def format_balance(value):
    return format_currency(value)


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
