"""
main.py
Defining all functions used for this program.
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

def balances(url):
    driver = webdriver.Firefox()
    driver.get(url)

    span = driver.find_elements(By.CLASS_NAME, "text-muted")
    findlastTXN=False
    i=0
    while findlastTXN == False:
        if("from" in str(span[i].get_attribute('innerHTML')) and "ago" in str(span[i].get_attribute('innerHTML'))):
            findlastTXN = i
        i=i+1

    findfirstTXN=False
    while findfirstTXN == False:
        if("from" in str(span[i].get_attribute('innerHTML')) and "ago" in str(span[i].get_attribute('innerHTML'))):
            findfirstTXN = i
        i=i+1

    lastTXN = str(span[findlastTXN].get_attribute('innerHTML'))
    firstTXN = str(span[findfirstTXN].get_attribute('innerHTML'))

    dropdownMenuBalance = driver.find_element(By.ID, "dropdownMenuBalance").get_attribute('innerHTML')

    try:
        element = WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID,"analytics_pageiframe")))
    except:
        print("Can't load page.")
        pass

    high_bal_eth_value = driver.find_element(By.ID, "high_bal_eth_value").get_attribute('innerHTML')
    high_bal_usd_value = driver.find_element(By.ID, "high_bal_usd_value").get_attribute('innerHTML')
    driver.quit()

    return lastTXN,firstTXN,dropdownMenuBalance,high_bal_eth_value,high_bal_usd_value

def main():
    # URL of the web page
    #url = "https://etherscan.io/address/0xfa31a00a87c766579f0790be73c3763b3e952e94#analytics"
    url_base = "https://etherscan.io/address/"


    f = open("demofile2.csv", "a")

    with open("UseMe.csv") as file:
      for item in file:
        url = url_base+item.strip()+"#analytics"
        potential_addresses = balances(url)
        f.write(url+","+str(potential_addresses)+"\n")

    f.close()

    #time.sleep(3)

main()
