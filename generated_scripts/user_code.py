from playwright.sync_api import sync_playwright


def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    page.set_viewport_size({'width': 1920, 'height': 1080})
    # Maximize window
    page.evaluate("window.moveTo(0, 0);")
    page.evaluate("window.resizeTo(screen.width, screen.height);")

    # Navigate to hevodata homepage
    page.goto('https://www.hevodata.com', wait_until='load')
    page.wait_for_timeout(10000)

    # Click on the Pricing link to navigate to the Pricing page
    pricing_xpath = "//a[@data-track-click='Pricing Click']"
    pricing_link = page.is_visible(pricing_xpath)
    if pricing_link:
        page.click(pricing_xpath)
        page.wait_for_timeout(10000)
        print('Navigated to Pricing page.')
    else:
        print('Pricing page link was not found.')
        browser.close()
        return

    # Look for the billing frequency toggle and click on it to switch to monthly
    billing_toggle_xpath = "//span[@id='billed_monthly']"
    billing_toggle = page.is_visible(billing_toggle_xpath)
    if billing_toggle:
        page.click(billing_toggle_xpath)
        page.wait_for_timeout(10000)
        print('Switched to monthly billing.')
    else:
        print('Billing frequency toggle was not found.')
        browser.close()
        return

    # Check if pricing reflects monthly prices
    prices_xpath = "//span[contains(@class,'price') and contains(text(),'$')]"
    prices_visible = page.locator(prices_xpath).is_visible()
    if prices_visible:
        monthly_prices = page.locator(prices_xpath).all_text_contents()
        print('Monthly prices are visible.')
        print(f'Prices: {monthly_prices}')
    else:
        print('Monthly prices were not found.')

    # Close the browser
    browser.close()

with sync_playwright() as playwright:
    run(playwright)