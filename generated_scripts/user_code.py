from playwright.sync_api import Playwright, sync_playwright

# Explicitly handling the Playwright event loop

def run(playwright: Playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.joinef.com')

    programs_elements = page.query_selector_all("text='PROGRAMS'")
    for element in programs_elements:
        try:
            element.click()
            print("Clicked on 'PROGRAMS'")
            break
        except Exception as e:
            print(e)
            continue
    
    page.wait_for_selector("text='FIND'")
    find_button = page.query_selector("text='FIND'")
    if find_button:
        find_button.click()
        print("Clicked on 'FIND'")
    else:
        print("'FIND' button not found!")
        browser.close()
        return

    page.wait_for_navigation()

    specific_text = "A weekend-long, accelerated taste of our startup building program."
    text_element = page.query_selector(f"text='{specific_text}'")
    if text_element:
        print("Good to go")
    else:
        print("missing")
    
    browser.close()

playwright = sync_playwright().start()
run(playwright)
playwright.stop()