from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from src.ui.ui_utils import get_number, ValidationError, create_popup
from src.problem_initializer import ProblemInitializer


class InputScreen(Screen):
    couriers = ObjectProperty(None)
    vehicles = ObjectProperty(None)
    packages = ObjectProperty(None)
    json_path = ObjectProperty(None)

    def generate(self):
        try:
            couriers_num = get_number(self.couriers.text)
            vehicles_num = get_number(self.vehicles.text)
            packages_num = get_number(self.packages.text)
        except ValidationError as e:
            create_popup("Error", str(e))
            return

        initializer = ProblemInitializer()
        initializer.generate_random(couriers_num, vehicles_num, packages_num)
        try:
            initializer.save_to_json(self.json_path.text)
        except (PermissionError, OSError):
            create_popup("Error", f"Couldn't save the problem to {self.json_path.text}")
            return

        create_popup("Done", f"Saved the problem to {self.json_path.text}")
