from kivy.factory import Factory

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


def create_popup(title, message):
    popup = Factory.InfoPopup()
    popup.title = title
    popup.ids.message_label.text = message
    popup.open()
