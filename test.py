import time
# SELEENIUM
from classes.web_controller import WebController
from selenium.webdriver.common.by import By

web_controller = WebController(
    browser_name="Google", 
    profile=None,
    headless=False,
    downloads_path='',
)

web_controller.start_window('https://www.cyberpuerta.mx/?gad_source=1&gclid=Cj0KCQjwtJ6_BhDWARIsAGanmKeLDmPrLPCDFsj0laItfXBcgDxqd8uuamBDoVuJ-DEMgiYIbQlSBCMaApQUEALw_wcB')


form_container = web_controller.get_web_element_by_class_name('search-form')
input_search = web_controller.get_web_element_by_css_selector('input[name="searchparam"]')
# Escribir por teclado ⌨️
input_search.send_keys('Laptops')
submit_button = form_container.find_element(By.CLASS_NAME, 'submitButton')
submit_button.click()
filter_estatus = web_controller.get_web_element_by_css_selector("input[name='cpsp[instock]']")
# Injección JS a través de al instancia del broswer 💉
web_controller.browser.execute_script('arguments[0].click();', filter_estatus)
# Selectores CSS anidados 🔵
filter_calification = web_controller.get_web_element_by_css_selector("input[name='cpsp[ranking][]'][value='5']")
web_controller.browser.execute_script('arguments[0].click();', filter_calification)

# ***********************************************************************************************

try:
    page = web_controller.get_web_element_by_id('page')
    scroll_start = 0
    scroll_end = 1000
    scroll_increment = 300
    
    for _ in range(5):
        web_controller.browser.execute_script(f"arguments[0].scrollBy({scroll_start}, {scroll_end});", page)
        scroll_start = scroll_end
        scroll_end += scroll_increment
    
except Exception as error:
    print (error)
    
time.sleep(20)

try:
    filter_ram_capacity = web_controller.get_web_element_by_css_selector("input[name='cpsp[cklist][56d9cf36c2c9295c47e28238fda80532][]'][value='16GB']")
    web_controller.browser.execute_script('arguments[0].click()')
except Exception as error:
    print (error)
    
try:
    product_list = web_controller.get_web_element_by_id('productList')
except Exception as error:
    print (error)
    
try:
    items_product_list = product_list.find_elements(By.TAG_NAME, 'li')
except Exception as error:
    print (error)

for list_item in items_product_list:
    pass
    
web_controller.close_window()