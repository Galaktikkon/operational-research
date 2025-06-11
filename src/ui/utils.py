class ValidationError(Exception):
    pass


def get_number(text):
    try:
        number = int(text)
    except ValueError:
        raise ValidationError(f"Invalid number: '{text}'")
    if number <= 0:
        raise ValidationError(f"Number '{number}' should be positive")
    return number
