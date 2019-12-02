from interface import main_interface


class InterfaceHolder:

    def __init__(self):
        self.main_interface = main_interface.MainInterface()

    def get_scaled(self, dt, force=False):
        self.main_interface.get_scaled(dt, force)
