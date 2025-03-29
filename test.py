from web_controller import WebController

web_controller = WebController(
    browser_name="Google", 
    profile=None,
    headless=False,
    downloads_path='',
)

web_controller.start_window('https://www.cyberpuerta.mx/?gad_source=1&gclid=Cj0KCQjwtJ6_BhDWARIsAGanmKeLDmPrLPCDFsj0laItfXBcgDxqd8uuamBDoVuJ-DEMgiYIbQlSBCMaApQUEALw_wcB')