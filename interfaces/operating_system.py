class OperatingSystem:
    def __init__(self, user):
        self.user = user

    @property
    def downloads_path(self):
        raise NotImplementedError("downloads_path method must be implemented")

    def get_driver_command(self, browser):
        raise NotImplementedError("get_driver_command method must be implemented")

    def get_driver_executable(self, browser):
        raise NotImplementedError("get_driver_executable method must be implemented")
