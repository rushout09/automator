from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})

    # Navigate to the URL
    page.goto('https://asia.hevodata.com', wait_until='load')
    print('Page loaded')

    # Close the browser if operation fails
    try:
        # Enter the email address
        page.fill('input[name="email"]', 'hevo@test.com')
        print('Email entered')

        # Click on Continue
        page.click('text=Continue', timeout=5000)
        print('Continue clicked')

        # Enter the password
        page.fill('input[name="password"]', 'password')
        print('Password entered')

        # Click on LOG IN button
        page.click('text=LOG IN', timeout=5000)
        print('LOG IN button clicked')

        # Wait for navigation
        page.wait_for_timeout(5000)

    except Exception as e:
        print(f'An error occurred: {e}')

    # Close the browser
    browser.close()
    print('Browser closed')