"""
main.py
Defining all functions used for this program.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def balances(url):

    driver = webdriver.Firefox()
    driver.get(url)

    dropdownMenuBalance = driver.find_element(By.ID, "dropdownMenuBalance").get_attribute('innerHTML')

    try:
        element = WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID,"analytics_pageiframe")))
    except:
        print("Can't load page.")
        pass
    high_bal_eth_value = driver.find_element(By.ID, "high_bal_eth_value").get_attribute('innerHTML')
    high_bal_usd_value = driver.find_element(By.ID, "high_bal_usd_value").get_attribute('innerHTML')
    driver.quit()

    return dropdownMenuBalance,high_bal_eth_value,high_bal_usd_value

def main():
    # URL of the web page
    url = "https://etherscan.io/address/0xfa31a00a87c766579f0790be73c3763b3e952e94#analytics"
    print(balances(url))

main()
