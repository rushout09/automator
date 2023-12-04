from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.google.com')
        print('Navigated to Google.')

        # Wait for the selector that identifies the search input to be visible
        search_input = page.wait_for_selector("input[name='q']", timeout=10000)
        print('Search input field found.')

        # Fill the search input with 'rushabh'
        search_input.fill('rushabh')
        print('Filled search input with rushabh.')

        # Submit the search query by pressing Enter
        search_input.press('Enter')
        print('Submitted the search.')

        # Wait for the navigation to happen post-search submission
        page.wait_for_navigation()
        print('Navigation after search submission confirmed.')

        # Check if search results are shown
        if page.locator("#search").count() > 0:
            print('Search results are displayed for rushabh.')
        else:
            print('Failed to display search results.')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        browser.close()
        print('Browser closed.')
