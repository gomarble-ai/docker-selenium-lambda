from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By
import time
import json

# Initialize the WebDriver outside the handler function
chrome = None

def initialize_browser():
    global chrome
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    chrome = webdriver.Chrome(options=options, service=service)

def get_image_urls(url):
    try:
        # Navigate to the specified URL
        chrome.get(url)

        # Find all image elements and extract their URLs
        images = chrome.find_elements(by=By.TAG_NAME, value="img")
        image_urls = [image.get_attribute("src") for image in images]

        return {
            'statusCode': 200,
            'body': json.dumps(image_urls)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

def perform_operation(event):
    # Get the operation from the query parameters
    operation = event.get('queryStringParameters', {}).get('operation')

    if not operation:
        return {
            'statusCode': 400,
            'body': 'Missing "operation" in query parameters'
        }

    body = json.loads(event.get('body', '{}'))

    if operation == 'get_image_urls':
        url = body.get('url')
        if not url:
            return {
                'statusCode': 400,
                'body': 'Missing "url" in body'
            }
        return get_image_urls(url)

    return {
        'statusCode': 400,
        'body': f'Unsupported operation: {operation}'
    }

def handler(event=None, context=None):
    global chrome
    # Initialize the browser if it is not already running
    if chrome is None:
        initialize_browser()

    return perform_operation(event)