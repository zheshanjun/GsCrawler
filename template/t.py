import sys
from selenium import webdriver
import time

if __name__ == '__main__':
    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(firefox_profile=profile)
    print driver.binary.process.pid
    time.sleep(1000)