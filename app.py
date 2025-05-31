from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty


class MainGrid(Widget):
    couriers = ObjectProperty(None)
    vehicles = ObjectProperty(None)
    packages = ObjectProperty(None)
    solutions = ObjectProperty(None)
    attempts = ObjectProperty(None)
    iterations = ObjectProperty(None)

    def generate(self):
        print(f"Couriers: {self.couriers.text}")
        print(f"Vehicles: {self.vehicles.text}")
        print(f"Packages: {self.packages.text}")
        print(f"Solutions to find: {self.solutions.text}")
        print(f"Max attempts: {self.attempts.text}")
        print(f"Max iterations: {self.iterations.text}")
        self.couriers.text = ""
        self.vehicles.text = ""
        self.packages.text = ""
        self.solutions.text = ""
        self.attempts.text = ""
        self.iterations.text = ""




class OptimiserApp(App):
    def build(self):
        return MainGrid()


app = OptimiserApp()
app.run()