from interfaces.operating_system import OperatingSystem

class MacOS(OperatingSystem):
    @property
    def downloads_path(self):
        return f"/Users/{self.user}/Downloads"
    
    def get_driver_command(self, browser):
        if browser == "Google":
            return '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version'
        elif browser == "Edge":
            return '"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --version'
        else:
            raise ValueError("Navegador no soportado para macOS.")
    
    def get_driver_executable(self, browser):
        if browser == "Google":
            return "chromedriver"
        elif browser == "Edge":
            return "msedgedriver"
        else:
            raise ValueError("Navegador no soportado para macOS.")
