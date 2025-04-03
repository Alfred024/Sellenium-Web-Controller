from interfaces.operating_system import OperatingSystem

class WindowsOS(OperatingSystem):
    @property
    def downloads_path(self):
        return f"C:\\Users\\{self.user}\\Downloads"
    
    def get_driver_command(self, browser):
        if browser == "Google":
            return r'(Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.ProductVersion'
        elif browser == "Edge":
            return r'(Get-Item "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe").VersionInfo.ProductVersion'
        else:
            raise ValueError("Navegador no soportado para Windows.")
    
    def get_driver_executable(self, browser):
        if browser == "Google":
            return "chromedriver.exe"
        elif browser == "Edge":
            return "msedgedriver.exe"
        else:
            raise ValueError("Navegador no soportado para Windows.")
