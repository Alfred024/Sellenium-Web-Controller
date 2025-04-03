import os
import getpass
import subprocess
import re
import requests
import time
import zipfile
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from interfaces.operating_system import OperatingSystem

class WebController:
    browsers_allowed = ['Google', 'Edge']
    
    def __init__(self, browser_name, os_obj: OperatingSystem, profile=None, headless=False, downloads_path="") -> None:
        """
        Constructor de WebController.
        
        Parámetros:
          - browser_name (str): "Google" o "Edge".
          - os_obj (OperatingSystem): Instancia de WindowsOS o MacOS.
          - profile (str): Nombre del perfil a utilizar.
          - headless (bool): Modo sin interfaz gráfica.
          - downloads_path (str): Ruta personalizada para descargas (opcional).
        """
        self.os_obj = os_obj
        self.browser_name = browser_name
        self.profile = profile
        self.browser = None
        self.options = None
        self.driver_version = None
        self.pc_user = os_obj.user
        
        # Se obtiene el directorio de descargas por defecto a partir del S.O.
        self.default_downloads_path = self.os_obj.downloads_path
        self.downloads_path = downloads_path if downloads_path else self.default_downloads_path
        
        # Definir la ruta del driver usando el método del S.O.
        self.driver_path = os.path.join(os.getcwd(), self.os_obj.get_driver_executable(browser_name))
        
        try:
            if browser_name in self.browsers_allowed:
                if browser_name == "Google":
                    self.options = webdriver.ChromeOptions()
                    # Configuración del perfil (según S.O.)
                    if profile is None:
                        if isinstance(self.os_obj, WindowsOS):
                            self.options.add_argument(
                                f'user-data-dir=C:\\Users\\{self.pc_user}\\AppData\\Local\\Google\\Chrome\\User Data'
                            )
                        else:
                            self.options.add_argument(
                                f'user-data-dir=/Users/{self.pc_user}/Library/Application Support/Google/Chrome'
                            )
                        self.options.add_argument("--profile-directory=Default")
                    else:
                        self.options.add_argument(
                            f'user-data-dir={os.path.join("SeleniumProfiles", profile)}'
                        )
                        self.options.add_argument(f"--profile-directory={profile}")
                elif browser_name == "Edge":
                    self.options = webdriver.EdgeOptions()
                    if profile is None:
                        if isinstance(self.os_obj, WindowsOS):
                            self.options.add_argument(
                                f'user-data-dir=C:\\Users\\{self.pc_user}\\AppData\\Local\\Microsoft\\Edge\\User'
                            )
                        else:
                            self.options.add_argument(
                                f'user-data-dir=/Users/{self.pc_user}/Library/Application Support/Microsoft Edge'
                            )
                        self.options.add_argument("--profile-directory=Default")
                    else:
                        self.options.add_argument(
                            f'user-data-dir={os.path.join("SeleniumProfiles", profile)}'
                        )
                        self.options.add_argument("--profile-directory=Default")
            else:
                print("El navegador seleccionado no es válido. Navegadores permitidos:", self.browsers_allowed)
                return
            
            # Configuración común
            self.service = Service(self.driver_path)
            command = self.os_obj.get_driver_command(browser_name)
            self.driver_version = self.get_driver_version(command)
            
            # Si el driver no existe en la ruta, se procede a descargarlo
            if not os.path.exists(self.driver_path):
                self.__download_web_driver()
        except Exception as e:
            print('Error initializing the class')
            print(e)
        
        if headless:
            self.options.add_argument("--headless")
        
        # Configuración de preferencias de descarga
        prefs = {
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": False,
        }
        if downloads_path:
            prefs.update({
                "download.prompt_for_download": True,
                "download.directory_upgrade": True,
                "download.default_directory": self.downloads_path,
            })
        else:
            prefs.update({
                "profile.default_content_setting_values.automatic_downloads": 1,
                "download.default_directory": self.downloads_path,
            })
        self.options.add_experimental_option("prefs", prefs)
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    def start_window(self, url="https://www.google.com.mx"):
        if self.browser_name == "Google":
            if self.browser is None:
                self.browser = webdriver.Chrome(service=self.service, options=self.options)
        elif self.browser_name == "Edge":
            if self.browser is None:
                self.browser = webdriver.Edge(service=self.service, options=self.options)
        self.browser.get(url)
    
    def openNewWindow(self, url=None):
        if self.browser:
            self.browser.execute_script("window.open('');")
            new_window = self.browser.window_handles[-1]
            self.browser.switch_to.window(new_window)
            if url:
                self.browser.get(url)
            print("Nueva ventana abierta.")
        else:
            print("No se encontró instancia del navegador. Inicia el navegador primero.")

    def changeWindow(self, window_index):
        if self.browser:
            windows = self.browser.window_handles
            if 0 <= window_index < len(windows):
                self.browser.switch_to.window(windows[window_index])
                print(f"Cambiado a la ventana con el índice {window_index}")
            else:
                print(f"El índice {window_index} está fuera del rango de ventanas abiertas.")
        else:
            print("No se encontró instancia del navegador. Inicia el navegador primero.")

    def close_window(self):
        if self.browser:
            try:
                self.browser.quit()
            except Exception as close_error:
                print(f"Error cerrando el web driver: {close_error}")
        print("Sesión y ventana cerradas")
    
    def openNewTab(self, url):
        if self.browser:
            self.browser.execute_script("window.open('');")
            self.browser.switch_to.window(self.browser.window_handles[-1])
            self.browser.get(url)
        else:
            print("No se encontró instancia del navegador. Inicia el navegador primero.")
    
    def changeTab(self, tab_index):
        if self.browser:
            tabs = self.browser.window_handles
            if 0 <= tab_index < len(tabs):
                self.browser.switch_to.window(tabs[tab_index])
            else:
                print(f"El índice {tab_index} está fuera del rango de pestañas abiertas.")
        else:
            print("No se encontró instancia del navegador. Inicia el navegador primero.")
    
    def closeTab(self, tab_index):
        if self.browser:
            tabs = self.browser.window_handles
            if 0 <= tab_index < len(tabs):
                self.browser.switch_to.window(tabs[tab_index])
                self.browser.close()
                remaining_tabs = self.browser.window_handles
                if remaining_tabs:
                    self.browser.switch_to.window(remaining_tabs[0])
                else:
                    print("Todas las pestañas han sido cerradas.")
            else:
                print(f"El índice {tab_index} está fuera del rango de pestañas abiertas.")
        else:
            print("No se encontró instancia del navegador. Inicia el navegador primero.")
    
    def changePage(self, url):
        self.browser.get(url)
    
    def get_driver_version(self, command):
        try:
            if isinstance(self.os_obj, WindowsOS):
                result = subprocess.run(["powershell", "-Command", command],
                                        capture_output=True, text=True)
                version = result.stdout.strip()
            else:
                result = subprocess.run(command, shell=True,
                                        capture_output=True, text=True)
                version_output = result.stdout.strip()
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', version_output)
                version = match.group(1) if match else ""
            
            if re.match(r'^(\d+\.){3}\d+$', version):
                return version
            else:
                print(f"No se pudo obtener la versión del driver para {self.browser_name}")
                return None
        except Exception as e:
            print(f"Error al obtener la versión del driver: {e}")
            return None

    def __download_web_driver(self):
        # Lógica de descarga del driver (similar a la versión original, adaptada según el S.O.)
        major_version = ".".join(self.driver_version.split('.')[0:3])
        minor_version = int(self.driver_version.split('.')[-1])
        driver_version = f'{major_version.strip()}.{str(minor_version).strip()}'

        if self.browser_name == "Google":
            if isinstance(self.os_obj, WindowsOS):
                zip_file_name = 'chromedriver-win64.zip'
                driver_name = 'chromedriver.exe'
                extracted_folder = "chromedriver-win64"
            else:
                zip_file_name = 'chromedriver-mac64.zip'
                driver_name = 'chromedriver'
                extracted_folder = "chromedriver-mac64"
        elif self.browser_name == "Edge":
            if isinstance(self.os_obj, WindowsOS):
                zip_file_name = 'msedgedriver-win64.zip'
                driver_name = 'msedgedriver.exe'
            else:
                zip_file_name = 'msedgedriver-mac64.zip'
                driver_name = 'msedgedriver'
            extracted_folder = "msedgedriver"

        response = None
        while minor_version >= 0:
            if self.browser_name == "Google":
                if isinstance(self.os_obj, WindowsOS):
                    driver_url_download = f'https://storage.googleapis.com/chrome-for-testing-public/{major_version}.{minor_version}/win64/chromedriver-win64.zip'
                else:
                    driver_url_download = f'https://storage.googleapis.com/chrome-for-testing-public/{major_version}.{minor_version}/mac64/chromedriver-mac64.zip'
                response = requests.get(driver_url_download)
                time.sleep(2)  # TODO: Reemplazar por una espera activa
                print(f"Intentando descargar el driver: {driver_url_download}")
            elif self.browser_name == "Edge":
                if isinstance(self.os_obj, WindowsOS):
                    driver_url_download = f'https://msedgedriver.azureedge.net/{major_version}.{minor_version}/edgedriver_win64.zip'
                else:
                    driver_url_download = f'https://msedgedriver.azureedge.net/{major_version}.{minor_version}/edgedriver_mac64.zip'
                response = requests.get(driver_url_download, verify=False)
                time.sleep(2)
                print(f"Intentando descargar el driver: {driver_url_download}")
            
            if response.status_code == 200:
                with open(zip_file_name, 'wb') as file:
                    file.write(response.content)
                print("¡Instalación del driver exitosa!")
                break
            else:
                print(f"No se encontró la versión {major_version}.{minor_version}. Buscando versión anterior...")
                minor_version -= 1

        if response is None or response.status_code != 200:
            print(f"Error al descargar el driver. Código de estado: {response.status_code if response else 'No Response'}")
            return

        time.sleep(2)
        if os.path.exists(self.driver_path):
            os.remove(self.driver_path)

        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
            zip_ref.extractall()

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(__file__)
        
        if self.browser_name == "Google":
            new_driver_path = os.path.join(extracted_folder, driver_name)
        elif self.browser_name == "Edge":
            new_driver_path = os.path.join(application_path, driver_name)
            
        print(new_driver_path)
        if os.path.exists(new_driver_path) and self.browser_name == "Google":
            os.rename(new_driver_path, driver_name)
            print(f"{driver_name} movido a la raíz del proyecto.")
            os.remove(zip_file_name)
            print(f"Archivo ZIP eliminado: {zip_file_name}")
            return True
        elif os.path.exists(new_driver_path) and self.browser_name == "Edge":
            os.remove(zip_file_name)
            print(f"Archivo ZIP eliminado: {zip_file_name}")
            return True
        else:
            print(f"No se encontró el nuevo {driver_name} en {extracted_folder}.")
            return False

    @staticmethod
    def select_other_profile(x):
        for i in range(x):
            print("Profile" + str(i))
            yield "Profile" + str(i)
        while True:
            yield "No more profiles available"

    def click_button_by_id(self, itemId: str, timeout: int = 60):
        try:
            button = WebDriverWait(self.browser, timeout).until(
                EC.element_to_be_clickable((By.ID, itemId))
            )
            button.click()
        except Exception:
            print(f'No se encontró un botón con el id: {itemId}')

# --- Ejemplo de uso ---

if __name__ == "__main__":
    # Obtener el usuario actual
    user = getpass.getuser()
    # Para Windows:
    os_instance = WindowsOS(user)
    # Para macOS, descomenta la siguiente línea:
    # os_instance = MacOS(user)
    
    controller = WebController("Google", os_instance, headless=False)
    controller.start_window()
