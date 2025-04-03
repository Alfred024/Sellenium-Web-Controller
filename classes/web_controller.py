import getpass
import time
import os
import zipfile
import subprocess
import re
import sys
import requests

# SELLENIUM IMPORS
from selenium import webdriver
    # SELLENIUM SERVICES
# ? Cómo hace la distinción de la utilización de la clase Service?
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.service import Service

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

    # TODO: Crear una interfáz o clase que permita definir algunos atributos estáticos de cada navegador, como el comando para obtener el driver de Edge y Chrome
    
class WebController():
    browsers_allowed = [ 'Google', 'Edge' ]

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
        """
        Abre una nueva ventana del navegador.
        :param url: La URL opcional que se cargará en la nueva ventana. Si no se proporciona, abrirá una ventana vacía.
        """
        if self.browser:
            # Ejecutar script de JavaScript para abrir una nueva ventana
            self.browser.execute_script("window.open('');")
            
            # Cambiar a la nueva ventana (que será la última en window_handles)
            new_window = self.browser.window_handles[-1]
            self.browser.switch_to.window(new_window)
            
            # Si se proporciona una URL, cargarla
            if url:
                self.browser.get(url)
            
            print("Nueva ventana abierta.")
        else:
            print("No browser instance found. Please start the browser first.")

    def changeWindow(self, window_index):
        """
        Switches to the specific window by index.
        - param window_index (int): Index of the window to switch to (0 for the first, 1 for the second, etc.).
        """
        if self.browser:
            windows = self.browser.window_handles  # Obtener todas las ventanas
            if 0 <= window_index < len(windows):  # Verificar si el índice es válido
                self.browser.switch_to.window(windows[window_index])  # Cambiar a la ventana especificada
                print(f"Cambiado a la ventana con el índice {window_index}")
            else:
                print(f"El índice {window_index} está fuera del rango de ventanas abiertas.")
        else:
            print("No browser instance found. Please start the browser first.")

    def close_window(self):
        """
        Closes the instance of selenium/webdriver
        """
        if self.browser:
            try:
                self.browser.quit()
            except Exception as close_error:
                print(f"Error closing web driver: {self.browser}: {close_error}")
        print("Session and window closed")

    def openNewTab(self, url):
        if self.browser:
            self.browser.execute_script("window.open('');")  # Open a new blank tab
            self.browser.switch_to.window(self.browser.window_handles[-1])  # Switch to the new tab
            self.browser.get(url)  # Load the URL in the new tab
        else:
            print("No browser instance found. Please start the browser first.")

    def changeTab(self, tab_index):
        """
        Switches to the specific tab by index.
        - param tab_index (int): Index of the tab you want to switch to (0 for the first, 1 for the second, etc.).
        """
        if self.browser:
            tabs = self.browser.window_handles  # Obtain all tabs
            if 0 <= tab_index < len(tabs):  # Check if the index is within the range
                self.browser.switch_to.window(tabs[tab_index])  # Switch to the specified tab
            else:
                print(f"The index {tab_index} are outside the range of open tabs.")
        else:
            print("No browser instance found. Please start the browser first.")
    
    def closeTab(self, tab_index):
        """
        Closes a specific tab by index.
        - param tab_index (int): Index of the tab to be closed (0 for the first, 1 for the second, etc.).
        """
        if self.browser:
            tabs = self.browser.window_handles  # Obtain all tabs
            if 0 <= tab_index < len(tabs):  # Check if the index is within the range
                self.browser.switch_to.window(tabs[tab_index])  # Switch to the specified tab
                self.browser.close()  # Close the actual and selected tab

                # Then, switch to an active tab if it exists
                remaining_tabs = self.browser.window_handles
                if remaining_tabs:  # If there are still tabs open, switch to the first one 
                    self.browser.switch_to.window(remaining_tabs[0])
                else:
                    print("All tabs have been closed.")
            else:
                print(f"The index {tab_index} are outside the range of open tabs.")
        else:
            print("No browser instance found. Please start the browser first.")

    def changePage(self, url):
        self.browser.get(url)
    
    def get_driver_version(self, command):
        try:
            # TODO: Revisar cómo se haría la implementación de esta clase en una MAC
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
            version = result.stdout.strip()
            if re.match(r'^(\d+\.){3}\d+$', version): # ! Revisar que acepte números con el formato 1.1.1.1
                return version
            else:
                print(f"The driver version couldn´t be obtanied {self.browser_name}")
                return None
        except Exception as e:
            print(f"Error getting the driver version of {self.browser_name}: {e}")
            return None

    def __download_web_driver(self):
        # Convertir la versión en partes para el decremento
        major_version = ".".join(self.driver_version.split('.')[0:3])
        minor_version = int(self.driver_version.split('.')[-1])
        driver_version = f'{major_version.strip()}.{str(minor_version).strip()}'

        if self.browser_name == "Google":
            zip_file_name = 'chromedriver-win64.zip'
            driver_name = 'chromedriver.exe'

            # Cambio de lugar del chromedriver.exe a la raíz del proyecto
            extracted_folder = "chromedriver-win64"

        elif self.browser_name == "Edge":
            zip_file_name = 'msedgedriver.zip'
            driver_name = 'msedgedriver.exe'

            # Cambio de lugar del chromedriver.exe a la raíz del proyecto
            extracted_folder = "msedgedriver"

        while minor_version >= 0:
            
            if self.browser_name == "Google":
                driver_url_download = f'https://storage.googleapis.com/chrome-for-testing-public/{major_version}.{minor_version}/win64/chromedriver-win64.zip'
                response = requests.get(driver_url_download)# verify=False)
                time.sleep(2) # TODO: Reemplazar este sleep por un método que haga una espera verdadera
                print(f"Trying to download driver: {driver_url_download}")
            elif self.browser_name == "Edge":
                driver_url_download = f'https://msedgedriver.azureedge.net/{major_version}.{minor_version}/edgedriver_win64.zip'
                response = requests.get(driver_url_download, verify=False)
                time.sleep(2)
                print(f"Trying to download driver: {driver_url_download}")
            
            if response.status_code == 200:
                with open(zip_file_name, 'wb') as file:
                    file.write(response.content)
                print(f"Succesfull driver installation!!")
                break
            else:
                print(f"The driver version couldnt be found {major_version}.{minor_version}. Searching older version...")
                minor_version -= 1  

        if response.status_code != 200:
            print(f"Error en la descarga del Driver después de intentar varias versiones. Código de estado: {response.status_code}")
            return

        # Eliminar el driver anterior, si existe
        time.sleep(2)
        if os.path.exists(self.driver_path):
            os.remove(self.driver_path)

        # Descompresión del archivo ZIP
        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
            zip_ref.extractall()

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)  # If the application is an .exe, we save the folder path where it is located
        elif __file__:
            application_path = os.path.dirname(__file__)  
        
        if self.browser_name == "Google":
            new_driver_path = os.path.join(extracted_folder, driver_name)
        elif self.browser_name == "Edge":
            new_driver_path = os.path.join(application_path, driver_name)
            

        print(new_driver_path)
        if os.path.exists(new_driver_path) and self.browser_name == "Google":
            os.rename(new_driver_path, driver_name)
            print(f"{driver_name} movido a la raíz del proyecto.")
            #Eliminación del archivo ZIP descargado
            os.remove(zip_file_name)
            print(f"Archivo ZIP eliminado: {zip_file_name}")
            
            return True
        elif os.path.exists(new_driver_path) and self.browser_name == "Edge":
            #Eliminación del archivo ZIP descargado
            os.remove(zip_file_name)
            print(f"Archivo ZIP eliminado: {zip_file_name}")
            
            return True
        else:
            print(f"El nuevo {driver_name} no se encuentra en {extracted_folder}.")
            return False
    
    @staticmethod
    def select_other_profile(x):
        for i in range(0,x):
            print("Profile"+str(i))
            yield "Profile"+str(i)
        
        while True:
            yield "No more profiles available"

    def click_button_by_id(self, itemId : str, timeout : int = 60):
        '''
        Search a button by the id and then click it 
        '''
        try:
            button = WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.ID, itemId)))
            button.click()
        except:
            print(f'Couldn´t find a button with the id: {itemId}')
    
    def click_button_by_classname(self, itemClass : str, timeout : int = 60):
        '''
        Search a button by the class name and then click it 
        '''
        try:
            button = WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.CLASS_NAME, itemClass)))
            button.click()
        except:
            print(f'Couldn´t find a button with the class: {itemClass}')
           
    def click_button_by_xpath(self, itemxPath : str, timeout : int = 60):
        '''
        Search a button by the XPath and then click it 
        '''
        try:
            button = WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.XPATH, itemxPath)))
            button.click()
        except:
            print(f'Couldn´t find a button with the Xpath: {itemxPath}')
    
    def click_button_by_css_selector(self, itemxCss : str, timeout : int = 60):
        '''
        Search a button by the CSS and then click it 
        '''
        try:
            button = WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, itemxCss)))
            button.click()
        except:
            print(f'Couldn´t find a button with the Xpath: {itemxCss}')
    
    def get_web_element_by_tagname(self, itam_tagname: str, timeout : int = 60) -> WebElement:
        try:
            element = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.TAG_NAME, itam_tagname)))
            return element
        except:
            print(f'Coludn´t find the element with the id {itam_tagname}')        
    
    def get_web_element_by_id(self, itemId: str, timeout : int = 60) -> WebElement:
        try:
            element = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.ID, itemId)))
            return element
        except:
            print(f'Coludn´t find the element with the id {itemId}')
            
    def get_web_element_by_class_name(self, itemClass: str, timeout : int = 60) -> WebElement:
        try:
            element = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, itemClass)))
            return element
        except:
            print(f'Coludn´t find the element with the class {itemClass}')

    def get_web_element_by_xpath(self, itemxPath, timeout : int = 60):
        try:
            item = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.XPATH, itemxPath)))
            return item
        except:
            print(f'Coludn´t find the element with the xpath {itemxPath}')
        
    def get_web_element_by_css_selector(self, itemCss: str, timeout : int = 60) -> WebElement:
        try:
            element = WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, itemCss)))
            return element
        except:
            print(f'Coludn´t find the element with the css selector {itemCss}')    

    def write(self, item, text):
        item.send_keys(text)
    
    def eraseAndWrite(self, item, text):
        item.clear()
        item.send_keys(text)

    def writeAndTab(self, item, text):
        item.send_keys(text)
        item.send_keys(Keys.TAB)

    def writeAndEnter(self, item, text):
        item.send_keys(text)
        item.send_keys(Keys.ENTER)

    def switchToFrame(self, frame, timeout):
        # self.browser.switch_to.frame(frame)
        WebDriverWait(self.browser, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, frame)))
        print(f"Se cambio a {frame}")