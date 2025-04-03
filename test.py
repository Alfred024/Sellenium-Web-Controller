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


try:
    form_container = web_controller.get_web_element_by_class_name('search-form')
except Exception as error:
    print(error)

try:
    input_search = web_controller.get_web_element_by_css_selector('input[name="searchparam"]')
    print(input_search)
except Exception as error:
    print (error)
    
try:
    input_search.send_keys('Monitores')
    pass
except Exception as error:
    print (error)

try:
    submit_button = form_container.find_element(By.CLASS_NAME, 'submitButton')
    submit_button.click()
    print('Submit button pressed...')
except Exception as error:
    print (error)
    
try:
    # Selección de un filtro para 
    filter_estatus = web_controller.get_web_element_by_css_selector("cpsp[instock]")
except Exception as error:
    print (error)

try:
    pass
except Exception as error:
    print (error)
    
try:
    # HTML: <input type="checkbox" name="cpsp[ranking][]" value="5" checked="" data-cp-pf-check-box="Opiniones" data-cp-seo-val="5">
    filter_calification = web_controller.get_web_element_by_css_selector("cpsp[ranking][]")
    
    # HTML: <input type="checkbox" name="cpsp[cklist][56d9cf36c2c9295c47e28238fda80532][]" value="3GB" data-cp-pf-check-box="Capacidad-de-memoria-RAM" data-cp-seo-val="3GB" class="disabled">
    filter_ram_capacity = web_controller.get_web_element_by_css_selector("cpsp[cklist][56d9cf36c2c9295c47e28238fda80532][]")
except Exception as error:
    print (error)
    
    
try:
    pass
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