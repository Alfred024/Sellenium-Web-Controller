from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
import getpass
import time
import os
import zipfile
from requests import get
import subprocess
import re
import sys
import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class WebController():
    #no_wndws = 4 #Number of possible windows
    def __init__(self, browser, profile=None, headless=False, downloads_path="") -> None:
        """
            WebController constructor.
            
            PARAMS:
            - browser(str): This is the web browser to be used (Google or Edge).
            - profile(str): Is the name of the profile in the “SelemiumProfiles” folder.
            - headless(bool): Is the browser mode where the user interface is not shown. True if you don't want to see the browser window.
            - downloads_path (str): Is the absolute path where the downloaded files will be stored.
        """
        self.driver_path =  os.getcwd()
        self.browser = browser
        self.pc_user = getpass.getuser()
        self.profile = profile #This is the selenium profile for a new instance of web browser
        self.browser = None #Variable for intance of selenium
        self.options = ""
        self.driver_version = None #Variable that stores the driver_version
        self.default_download_path = f"C:\\Users\\{self.pc_user}\\Downloads"  # Default download path
        self.downloads_path = downloads_path if downloads_path else self.default_download_path

        try:
            if self.browser == "Google":
                self.options = webdriver.ChromeOptions()
                self.driver_path = self.driver_path+r"\chromedriver.exe"
                self.service = Service(self.driver_path)
                command = r'(Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.ProductVersion'
                self.driver_version = self.getDriverVersion(command)
                if self.profile is None:
                    self.options.add_argument(f'user-data-dir=C:\\Users\\{self.pc_user}\\AppData\\Local\\Google\\Chrome\\User Data')
                    self.options.add_argument("--profile-directory=Default")
                else:
                    self.options.add_argument(f'user-data-dir=C:/SeleniumProfiles/{self.profile}')
                    self.options.add_argument(f"--profile-directory={self.profile}")
                
            elif self.browser == "Edge":
                self.options = webdriver.EdgeOptions()
                self.driver_path = self.driver_path+r"\msedgedriver.exe"
                self.service = Service(self.driver_path)
                command = r'(Get-Item "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe").VersionInfo.ProductVersion'
                self.driver_version = self.getDriverVersion(command)
                if self.profile is None:
                    self.options.add_argument(f'user-data-dir=C:\\Users\\{self.pc_user}\\AppData\\Local\\Microsoft\\Edge\\User')
                    self.options.add_argument("--profile-directory=Default")
                else:
                    self.options.add_argument(f'user-data-dir=C:/SeleniumProfiles/{self.profile}')
                    self.options.add_argument("--profile-directory=Default")
            else:
                print("Seleccione un navegador adecuado, Edge o Google")
                return
        
        except Exception as e:
            print(e)
        
        

        if headless: #To activate the headless mode if it's True
            self.options.add_argument("--headless")
        
        if downloads_path: #Add the path to a specific folder where the downloaded files are going to be stored
            self.downloads_path = downloads_path
            # print("Dwn path 1", self.downloads_path)
            self.options.add_experimental_option("prefs", {
                "safebrowsing.enabled": True,
                #"profile.default_content_setting_values.automatic_downloads": 1,  #Allows automatic downloads (if necessary)
                "download.prompt_for_download": False,  # Evitar preguntar dónde guardar cada archivo
                "download.directory_upgrade": True,  # Permitir cambiar la carpeta de descargas
                "download.default_directory": self.downloads_path,
                "safebrowsing.disable_download_protection": False,  #Maintain download protection to review xml and download them without any problem.
            })
        else:
            self.downloads_path = f"C:\\Users\\{self.pc_user}\\Downloads"
            # print("Dwn path 2", self.downloads_path)
            self.options.add_experimental_option("prefs", {
                "safebrowsing.enabled": True,
                "safebrowsing.disable_download_protection": False,  #Maintain download protection to review xml and download them without any problem.
                "profile.default_content_setting_values.automatic_downloads": 1,  #Allows automatic downloads (if necessary)
                "download.default_directory": self.downloads_path,
            })
        

        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    
    def startWindow(self, url="https://www.google.com.mx"):
        if self.browser == "Google":
            if self.browser is None:
                self.browser = webdriver.Chrome(service=self.service, options=self.options)
        elif self.browser == "Edge":
            if self.browser is None:
                self.browser = webdriver.Edge(service=self.service, options=self.options)
        
        self.browser.get(url)
    
    def set_download_path(self, path):
        """Set the download path for the browser."""
        self.options.add_experimental_option("prefs", {
            "safebrowsing.enabled": True,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.default_directory": path,
            "safebrowsing.disable_download_protection": False,
        })
        print(f"Download path set to: {path}")

    def reset_download_path(self):
        """Reset the download path to its default."""
        self.set_download_path(self.default_download_path)
        print(f"Download path reset to default: {self.default_download_path}")

    def quit(self):
        """Quit the browser and reset download path."""
        if self.browser:
            self.reset_download_path()  # Restore default settings
            self.browser.quit()
            self.browser = None


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


    def closeWindow(self):
        """Closes the instance of selenium/webdriver"""
        if self.browser:
                try:
                    self.browser.quit()  #To close WebDriver if exists
                except Exception as close_error:
                    print(f"Error al cerrar el WebDriver de {self.browser}: {close_error}")

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
    
    # TODO: Checar si se puden 

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

    @staticmethod
    def selectOtherProfile(x):
        for i in range(0,x):
            print("Profile"+str(i))
            yield "Profile"+str(i)
        
        while True:
            yield "No more profiles available"
    

    def downloadDriver(self, chromeVersion):
        # Definimos la versión de ChromeDriver y la URL de descarga
        driverDownload = f'https://storage.googleapis.com/chrome-for-testing-public/{chromeVersion}/win64/chromedriver-win64.zip'

        zip_file_name = 'chromedriver-win64.zip'
        chromedriver_name = 'chromedriver.exe'

        # Descarga del archivo ZIP
        response = get(driverDownload)
        if response.status_code == 200:
            with open(zip_file_name, 'wb') as file:
                file.write(response.content)
        else:
            print(f"Driver download error. Status code: {response.status_code}")
            exit()

        # Descompresión del archivo ZIP
        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
            zip_ref.extractall()  

        # Eliminamos el driver anterior
        if os.path.exists(chromedriver_name):
            os.remove(chromedriver_name)

        # Cambio de lugar del chromedriver.exe a la raíz del proyecto
        extracted_folder = "chromedriver-win64"
        new_chromedriver_path = os.path.join(extracted_folder, chromedriver_name)
        if os.path.exists(new_chromedriver_path):
            os.rename(new_chromedriver_path, chromedriver_name)
        else:
            print(f"The new {chromedriver_name} is not found in {extracted_folder}.")

        # Eliminación del archivo ZIP descargado
        os.remove(zip_file_name)


    def getDriverVersion(self, command):
        # if self.browser == "Google":
            try:
                # Ejecutar un comando de PowerShell para obtener la versión de Chrome
                result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
                
                # Extraer la versión usando una expresión regular
                version = result.stdout.strip()
                if re.match(r'\d+\.\d+\.\d+\.\d+', version):
                    #print(f"Version actual de Google Chrome: {version}")
                    return version
                else:
                    print(f"No se pudo obtener la version de {self.browser}")
                    return None
            except Exception as e:
                print(f"Error al obtener la version de {self.browser}: {e}")
                return None

        # elif self.browser == "Edge":
        #     try:
        #         # Ejecutar un comando de PowerShell para obtener la versión de Chrome
        #         command = r'(Get-Item "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe").VersionInfo.ProductVersion'
        #         result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
                
        #         # Extraer la versión usando una expresión regular
        #         version = result.stdout.strip()
        #         if re.match(r'\d+\.\d+\.\d+\.\d+', version):
        #             print(f"Versión actual de Edge: {version}")
        #             return version
        #         else:
        #             print("No se pudo obtener la versión de Edge.")
        #             return None
        #     except Exception as e:
        #         print(f"Error al obtener la versión de Chrome: {e}")
        #         return None


    def downloadWebDriver(self):
        # Convertir la versión en partes para el decremento
        major_version = ".".join(self.driver_version.split('.')[0:3])
        minor_version = int(self.driver_version.split('.')[-1])
        driver_version = f'{major_version.strip()}.{str(minor_version).strip()}'

        if self.browser == "Google":
            zip_file_name = 'chromedriver-win64.zip'
            driver_name = 'chromedriver.exe'

            # Cambio de lugar del chromedriver.exe a la raíz del proyecto
            extracted_folder = "chromedriver-win64"

        elif self.browser == "Edge":
            zip_file_name = 'msedgedriver.zip'
            driver_name = 'msedgedriver.exe'

            # Cambio de lugar del chromedriver.exe a la raíz del proyecto
            extracted_folder = "msedgedriver"

        while minor_version >= 0:
            
            if self.browser == "Google":
                # Definir la URL de descarga de ChromeDriver basada en la versión actual
                driverDownload = f'https://storage.googleapis.com/chrome-for-testing-public/{major_version}.{minor_version}/win64/chromedriver-win64.zip'
                # Hacer la solicitud para descargar el archivo ZIP
                response = requests.get(driverDownload)# verify=False)
                time.sleep(2)
                print(f"Intentando descargar: {driverDownload}")
            elif self.browser == "Edge":
                # Definir la URL de descarga de msedgedriver basada en la versión actual
                driverDownload = f'https://msedgedriver.azureedge.net/{major_version}.{minor_version}/edgedriver_win64.zip'
                # Hacer la solicitud para descargar el archivo ZIP
                response = requests.get(driverDownload, verify=False)
                time.sleep(2)
                print(f"Intentando descargar: {driverDownload}")
            
            
            # Si se encuentra la versión
            if response.status_code == 200:
                with open(zip_file_name, 'wb') as file:
                    file.write(response.content)
                print(f"Descarga exitosa: {driverDownload}")
                break
            else:
                print(f"No se encontró la versión {major_version}.{minor_version}. Probando una versión menor...")
                minor_version -= 1  # Decrementar la versión menor

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
        
        if self.browser == "Google":
            new_driver_path = os.path.join(extracted_folder, driver_name)
        elif self.browser == "Edge":
            new_driver_path = os.path.join(application_path, driver_name)
            

        print(new_driver_path)
        if os.path.exists(new_driver_path) and self.browser == "Google":
            os.rename(new_driver_path, driver_name)
            print(f"{driver_name} movido a la raíz del proyecto.")
            #Eliminación del archivo ZIP descargado
            os.remove(zip_file_name)
            print(f"Archivo ZIP eliminado: {zip_file_name}")
            
            return True
        elif os.path.exists(new_driver_path) and self.browser == "Edge":
            #Eliminación del archivo ZIP descargado
            os.remove(zip_file_name)
            print(f"Archivo ZIP eliminado: {zip_file_name}")
            
            return True
        else:
            print(f"El nuevo {driver_name} no se encuentra en {extracted_folder}.")
            return False


    def file_exists(self, filename, directory, timeout=1200):
        """ Verifica que un archivo esté completamente descargado en el directorio especificado """
        end_time = time.time() + timeout
        while time.time() < end_time:
            print("Esperando archivo en: ", directory)
            for fname in os.listdir(directory):
                if fname.startswith(filename) and not fname.endswith('.crdownload'):
                    full_path = os.path.join(directory, fname)
                    if os.path.isfile(full_path):
                        time.sleep(1)  # espera un poco más para asegurarte de que el archivo está completamente escrito
                        return full_path
            time.sleep(1)
        return None


    def bFiskurReport(self,user, pwd, PCuser, ini_date, fin_date):
        """This function manages the download of bFiskur report from the browser
        - user (str): The email to log in bFiskur.
        - pwd (str): The password to log in bFiskur.
        - PCuser(str): it's the user of pc.
        - ini_date(str): it's the initial date of the range (mm/dd/yy).
        - fin_date(str): it's the final date of the range (mm/dd/yy).
        """
        #shared.status = "Se generará el reporte de Bfiskur"
        print(ini_date,fin_date)
        ini_date = ini_date[:6]+'20'+ini_date[6:]
        fin_date = fin_date[:6]+'20'+fin_date[6:]
        print(ini_date,fin_date)
        # Crear opciones de Edge
        #options = webdriver.EdgeOptions()
        # Especifica la ruta al ChromeDriver
        #PATH_TO_CHROMEDRIVER = "chromedriver.exe"
        #options = webdriver.ChromeOptions()
        # Crea una instancia de Service con la ruta al ChromeDriver
        #service = Service(executable_path=PATH_TO_CHROMEDRIVER)
        #options.use_chromium = True
        #options.add_argument("--headless")
        # Especificar las credenciales
        #options.add_argument(f'user-data-dir=C:\\Users\\{PCuser.strip()}\\AppData\\Local\\Google\\Chrome\\User Data')
        #options.add_argument("--profile-directory=Default")
        #options.add_argument("--remote-debugging-port=9222")
        # options.add_argument("--start-maximized")

        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        #options.add_argument("--disable-blink-features=AutomationControlled")
        #print(options.capabilities)


        try:
            self.startWindow("https://bfiskurapp.bitam.com/bFiskur/app/fbm_bmd_0244/BAPPE4E3720E/login")
            
            #"C:/Users/pvzqueer/OneDrive - Clarios/Documents/Pruebas/proyectos/19 Conciliacion SAT vs MFG/Codigo Fuente v1.2/chromedriver.exe",
            #driver = webdriver.Chrome(service=service,options=options)
            #driver = webdriver.Edge(options=options)
            time.sleep(1)
            #https://bitam.com/solucionesfiscales/
            print("Despues de crear el objeto")
            #shared.status = "Cargando la página"
            #driver.get("https://bfiskurapp.bitam.com/bFiskur/app/fbm_bmd_0244/BAPPE4E3720E/login")
            #driver.get("https://bfiskurapp.bitam.com/bFiskur/app/fbm_bmd_0244/BAPPE4E3720E/login")
            time.sleep(2)

            #El siguiente código se comentó debido a un cambio en la página de inicio de sesión
            """print("Presionando boton iniciar sesion")
            login_button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[2]/div[2]/a")))
            login_button.click()
            time.sleep(10)
            #Cambiamos de pestaña

            window_handles = driver.window_handles
            print("pestañas: ", window_handles)
            # Cambiar a la nueva pestaña (asumiendo que es la última abierta)
            driver.switch_to.window(window_handles[-1])"""

            #login_button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[1]/button")))
            #login_button.click()
            #time.sleep(5)
            #shared.status = "Iniciando sesión"
            for letter in user.strip():
                login_user = WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.ID, 'userman')))
                time.sleep(0.1)
                login_user.send_keys(letter)
            login_user.send_keys(Keys.TAB)
            time.sleep(1)
            for letter in pwd.strip():
                login_pwd = WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.ID, 'password')))
                time.sleep(0.1)
                login_pwd.send_keys(letter)

            login_user.send_keys(Keys.TAB)  
            login_button = WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/form/div[6]/button')))
            login_button.click()
            print("inicio sesion")
            elemento = WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-name="CFDIs"]')))
            elemento.click()

            #elemento = WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-name="CFDIs Recibidos"]')))
            #elemento.click()
            #shared.status = "Seleccionando tipo de CFDI's"
            elemento = WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-name="CFDIs Emitidos"]')))
            elemento.click()

            time.sleep(1.5)
            elemento = WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-name="CFDIs Emitidos"]')))
            elemento.click()
            print("emitidos")
            #logout_button = WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div[1]/div/div/div[2]/div[2]/div[4]/ul/li[5]')))
            #logout_button.click()
            #login_user.send_keys(Keys.ENTER)
            #login_user.send_keys(user)

            #shared.status = "Colocando rango de fechas"
            input_date = WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, 'startdate')))
            input_date.send_keys(ini_date.replace("/",""))
            
            input_date = WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, 'enddate')))
            input_date.send_keys(fin_date.replace("/",""))
            
            #checkbox = WebDriverWait(self.browser, 120).until(EC.element_to_be_clickable((By.ID, "FFRMS_42176F5E_1"))) # FFRMS_0F5BE219_1
            print("Antes del click en checkbox")
            checkbox = WebDriverWait(self.browser, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='FFRMS_42176F5E_1']")))
            #if not checkbox.is_selected():
            checkbox.click()
            print("Después del click en checkbox")
            #shared.status = "Escogiendo vista"
            filter_button = WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div[3]/button[2]')))
            filter_button.click()
            print("escogiendo vista")
            vistas_button = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Vistas']")))
            vistas_button.click()

            # Espera a que la lista sea visible
            #WebDriverWait(self.browser, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.dropdown-menu')))
            time.sleep(0.2)
            print("Click en vista cdfi sat")
            Report = WebDriverWait(self.browser, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Reporte CFDI SAT']")))
            Report.click()

            print("Vista escogida")
            
            #shared.status = "Esperando aparición de fechas, no cierre el programa"
            while True:
                print("Buscando fechas")
                try:
                    time.sleep(4)
                    filter_button2 = WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Filtros']"))) #/html/body/div[7]/div/div
                    filter_button2.click()
                    input_date = WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'startdate')))
                    input_date.send_keys(ini_date)
                    
                    input_date = WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'enddate')))
                    input_date.send_keys(fin_date)

                    print("Antes del click en checkbox 2")
                    #checkbox = WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((By.ID, 'FFRMS_9CFB967C_1')))
                    checkbox = WebDriverWait(self.browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[title='JOHNSON CONTROLS ENTERPRISES MEXICO S DE RL DE CV']")))
                    if not checkbox.is_selected():
                        checkbox.click()
                    print("Despues del click en checkbox 2")
                    
                    filter_button3 = WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[3]/button[2]"))) #/html/body/div[7]/div/div /html/body/div[7]/div/div/div[3]/button[2]
                    filter_button3.click() #/html/body/div[6]/div/div/div[3]/button[2]
                    
                    print("Despues del botón filtro")
                    break  
                except:
                    self.browser.refresh()

            time.sleep(10)

            #shared.status = "Intentando exportar a excel"
            print("Intentando hacer click en 3 puntos")
            filter_button = WebDriverWait(self.browser, 120).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Acciones']")))
            filter_button.click()

            # Espera a que la lista sea visible
            #WebDriverWait(self.browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.dropdown-menu')))
            time.sleep(1)
            print("Click en exportar")
            #export_excel = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div[2]/div[1]/div/ul[2]/li[6]/div/ul/li[1]/a')))
            export_excel = WebDriverWait(self.browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='Exportar a Excel']")))
            export_excel.click()

            time.sleep(10)
            # Asegúrate de que el modal está visible
            #WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.fade.in")))
            #shared.status = "Exportando y esperando descarga"
            print("click exportar en modal")
            time.sleep(5)
            # Localiza el botón "Exportar" en el modal y haz clic en él
            #boton_exportar = driver.find_element(By.XPATH, "//div[contains(@class, 'modal-footer')]/button[text()='Exportar']")
            boton_exportar = WebDriverWait(self.browser, 120).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div/div/div[3]/button[2]")))
            #boton_exportar = WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[text()='Exportar']")))
            boton_exportar.click()
            print("Se hizo click")
            # self.file_exists("Reporte CFDI SAT.xlsx", f"C:/Users/{self.pc_user}/Downloads", timeout=1300)
            self.file_exists("Reporte CFDI SAT.xlsx", self.downloads_path, timeout=1300)
            time.sleep(15)
            self.browser.refresh()
            #shared.status = "Intentando cerrar sesión, no cierre la ventana ni el pograma"
            while True:
                print("Buscando usuario para cerrar sesion")
                filter_button3 = ''

                try:
                    try:
                        filter_button3 = WebDriverWait(self.browser, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[3]/button[2]"))) 
                        if filter_button3: 
                            filter_button3.click()
                            print("Cerrando sesion")
                            #log_out = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div/div/div[2]/div[2]/div[4]/a/span")))
                            log_out = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/div/div/div[2]/div[2]/div[4]/a")))
                            log_out.click()
                            print("Haciendo click en cerrar sesion")
                            log_out = WebDriverWait(self.browser, 50).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Cerrar sesión')))
                            log_out.click()
                            print("Sesion cerrada")
                            break

                
                    except:
                        
                        print("Cerrando sesion")
                        #log_out = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div/div/div[2]/div[2]/div[4]/a/span")))
                        log_out = WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/div/div/div[2]/div[2]/div[4]/a")))
                        log_out.click()
                        print("Haciendo click en cerrar sesion")
                        log_out = WebDriverWait(self.browser, 50).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Cerrar sesión')))
                        log_out.click()
                        print("Sesion cerrada")
                        break
                except:
                    self.browser.refresh()



            self.browser.quit()
            #shared.status = "Proceso con Bfiskur terminado"
            print("Proceso con Bfiskur terminado")
        except Exception as e:
            print(e)
            #shared.status = e
            if 'driver' in locals():
                self.browser.quit()


# profile = selectOtherProfile(4)
user = "consultasclarios@clarios.com"
pwd = "Clarios2023."
ini_date = "07/01/24"
fin_date = "07/31/24"
dwn_path = os.getcwd()
#print("Dwn path", dwn_path)
#bFiskurReport(user,pwd,'pvzqueer',ini_date,fin_date)
# *********************************** Crear una única instancia con el perfil predeterminado "Default" ***************************************
# browserDefaultEdge = WebController("Edge", downloads_path=dwn_path)
# browserDefaultGoogle = WebController("Google")
# browserDefaultEdge.startWindow("https://www.twitch.tv")
# browserDefaultEdge.openNewTab('https://www.yahoo.com')
# browserDefaultEdge.openNewTab('https://www.youtube.com')
# browserDefaultEdge.closeTab(0)
# browserDefaultEdge.changeTab(1)
# browserDefaultEdge.openNewWindow("https://clarios.sharepoint.com/")
# browserDefaultEdge.changeWindow(0)
# browserDefaultEdge.changeWindow(1)
#*********************************************************************************************************************************************
# browserDefaultEdge.startWindow("")

#browserDefaultEdge.bFiskurReport(user,pwd,'pvzqueer',ini_date,fin_date)
# browserDefaultGoogle.startWindow('https://www.yahoo.com')

# time.sleep(10)

# browserDefaultEdge.closeWindow()
#browserDefaultGoogle.closeWindow()
#*********************************************************************************************************************************************



#profile = browserDefault.selectOtherProfile(4)

# browser = WebController("Google", headless=False)#, downloads_path=dwn_path)
# #browser.bFiskurReport(user,pwd,'pvzqueer',ini_date,fin_date)

# #browserDefault.startWindow('https://www.yahoo.com')
# # #browser = WebController(1, "msedgedriver.exe", "Edge")
# #browser = WebController("chromedriver.exe", "Google", next(profile))
# success = True#browser.downloadWebDriver()
# if success:
#     browser.startWindow('https://www.twitch.tv')
# else:
#     print("Hubo problemas al descargar el driver")
#     exit()

# time.sleep(5)
# browser.openNewTab('https://www.yahoo.com')
# time.sleep(5)

# browser2 = WebController("chromedriver.exe", "Google", next(profile))
# browser2.startWindow('https://www.google.com.mx')
# browser3 = WebController("chromedriver.exe", "Google", next(profile))
# browser3.startWindow('https://www.google.com.mx')
# browser4 = WebController("chromedriver.exe", "Google", next(profile))
# browser4.startWindow('https://www.twitch.tv')