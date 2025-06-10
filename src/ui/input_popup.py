from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

from src.ui.ui_utils import get_number, ValidationError, create_popup
from src.problem_initializer import ProblemInitializer

class InputPopup(BoxLayout):
    # input_text = ObjectProperty(None)
    parent_popup = ObjectProperty(None)
    input_screen = ObjectProperty(None)

    def submit(self):
        input_text_value = self.ids.input_field.text
        self.input_screen.update_label(input_text_value)
        self.parent_popup.dismiss()