from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.properties import ObjectProperty

from src.ui.input_popup import InputPopup

class InputScreen(Screen):
    display_label = ObjectProperty(None)

    def open_popup(self):
        content = InputPopup()
        popup = Popup(title="Enter Text", content=content,
                      size_hint=(None, None), size=(300, 200), auto_dismiss=False)
        content.parent_popup = popup
        content.input_screen = self
        popup.open()

    def update_label(self, text):
        self.display_label.text = f"Entered: {text}"