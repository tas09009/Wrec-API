from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up Chrome driver options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without a GUI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver executable (update with your own path)
webdriver_service = Service('/path/to/chromedriver')

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Open Google login page
driver.get("https://accounts.google.com")

# Find and fill in the email field
email_input = driver.find_element("id", "identifierId")
email_input.send_keys("your-email@gmail.com")
email_input.send_keys(Keys.RETURN)

# Find and fill in the password field
password_input = driver.find_element("name", "password")
password_input.send_keys("your-password")
password_input.send_keys(Keys.RETURN)

# Wait for the login process to complete
driver.implicitly_wait(10)

# Verify successful login by checking the page title
if "Gmail" in driver.title:
    print("Login successful!")
else:
    print("Login failed.")

# Close the browser
driver.quit()
