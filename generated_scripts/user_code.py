from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://hevodata.com')

    try:
        # Assuming 'Login' is a text that can be used to locate the button
        login_button = page.wait_for_selector("text=Login")

        if login_button:
            login_button.click()
            print('Clicked on the Login button.')
        else:
            print('Login button not found.')

    except Exception as e:
        print(f'An exception occurred: {str(e)}')

    browser.close()