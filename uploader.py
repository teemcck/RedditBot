from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json

# tags - #boyredditor #boy_redditor #reddit #redditstories #redditreadings #minecraftparkour 

MAX_UPLOAD_RETRIES = 3

thread_titles = ["", "", ""]

# Inefficient, find a different mode of uploading later.
def upload_videos(thread_titles):
    # Assign a driver path and declare chrome options
    chromedriver_path = 'chromedriver.exe'
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--window-size=640,1080")

    instances = []

    # List of port numbers for each instance
    port_numbers = [9515, 9516, 9517]

    # Launch each instance
    for i, port in enumerate(port_numbers):
        driver = webdriver.Chrome(service=Service(chromedriver_path, port=port), options=chrome_options)
        driver.get("https://www.tiktok.com/")
        driver.set_window_size(640, 1080)
        driver.set_window_position(i * 640, 0)
        instances.append(driver)

        # Try to import session cookies
        with open('tiktokcookies.json', 'r') as file:
            cookies = json.load(file)

        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()

    for i, instance in enumerate(instances):
        retries = 0
        while retries < MAX_UPLOAD_RETRIES:
            try:
                # Get tiktok home page
                instance.get("https://www.tiktok.com/")

                # Navigate to upload page
                WebDriverWait(instance, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div[3]/div[1]"))).click()
                
                # Wait for iframe
                WebDriverWait(instance, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div/iframe")))
                instance.switch_to.frame(instance.find_element(by=By.XPATH, value="/html/body/div[1]/div[2]/div/div/iframe"))
                
                # Attempt to input file
                WebDriverWait(instance, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div/div/div/div/input")))
                input = instance.find_element(
                    by=By.XPATH, value="/html/body/div[1]/div/div/div/div/div/div/div/input")
                input.send_keys(
                    f"C:/Users/bigbr/Desktop/redditbot v2/temp/videos/{i}.mp4")
                break  # Success, exit the loop

            except Exception as e:
                print(f"An error occurred while navigating to URL: {e}")
                retries += 1

                if retries == MAX_UPLOAD_RETRIES:
                    print(f"Reached maximum retries for tiktok instance {i}. Removing it from the list.")
                    instance.quit()  # Close the bugged instance
                    instances.remove(instance)  # Remove the instance from the list
                continue  # Continue to the next iteration of the loop

    for i, uploader in enumerate(instances):
        # Wait for video to be uploaded
        WebDriverWait(uploader, 3600).until(
            EC.text_to_be_present_in_element((By.XPATH, "/html/body/div[1]/div/div/div/div[1]/div[1]/div[2]/button/div/div"), "Edit video"))
        
        # Try to kill stupid pop up notification for longer length videos
        try:
            # Look for close button, if present, click
            element = WebDriverWait(uploader, 5).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[3]/div/div/div/div/div[2]/div[2]/div[2]/button[2]"))
            )
            
            element.click()
        except TimeoutException:
            # If not present, continue as normal
            pass
            
        # Find the element using the provided CSS_SELECTOR
        title = WebDriverWait(uploader, 5).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/div/div/div/div/div/div'))
        )

        # Clear any existing content (optional, if needed)
        title.clear()

        title.click()  # Focus on the element
        title.send_keys(thread_titles[i])  # Type the new text

    # Close all instances
    for instance in instances:
        instance.quit()
