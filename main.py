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
import re

def balances(url):
    """
    Web scrape etherscan for details and balances
    """
    driver = webdriver.Firefox()
    driver.get(url)

    try:
        span = driver.find_elements(By.CLASS_NAME, "text-muted")
    except:
        span = None
        lastTXN = None
        firstTXN = None


    if span:
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


    try:
        dropdownMenuBalance = driver.find_element(By.ID, "dropdownMenuBalance").get_attribute('innerHTML')
    except:
        dropdownMenuBalance = None
        pass

    try:
        element = WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID,"analytics_pageiframe")))
    except:
        print("Can't load page.")
        pass

    try:
        high_bal_eth_value = driver.find_element(By.ID, "high_bal_eth_value").get_attribute('innerHTML')
    except:
        high_bal_eth_value = None
        pass
    try:
        high_bal_usd_value = driver.find_element(By.ID, "high_bal_usd_value").get_attribute('innerHTML')
    except:
        high_bal_usd_value = None
        pass

    driver.quit()

    return lastTXN,firstTXN,dropdownMenuBalance,high_bal_eth_value,high_bal_usd_value

def cleanup(account_details):
    """
    Expects a list of 5 values and cleans up data for each entry
    """
    lastTXN = account_details[0]
    firstTXN = account_details[1]
    dropdownMenuBalance = account_details[2]
    high_bal_eth_value = account_details[3]
    high_bal_usd_value = account_details[4]

    if lastTXN is not None:
        lastTXN = lastTXN.split()  #[0] from, [1] number, [2] days/hrs, [3] number, [4] hrs/mins, [5] ago
    if firstTXN is not None:
        firstTXN = firstTXN.split()  #[0] from, [1] number, [2] days/hrs, [3] number, [4] hrs/mins, [5] ago
    if dropdownMenuBalance is not None:
        dropdownMenuBalance = dropdownMenuBalance.split()
        dropdownMenuBalance = re.search(r'(?:[\£\$\€]{1}[,\d]+.?\d*)', dropdownMenuBalance[0]).group().replace(",", "").replace("$", "")
    if high_bal_eth_value is not None:
        high_bal_eth_value = high_bal_eth_value.split()[0]
    if high_bal_usd_value is not None:
        high_bal_usd_value = high_bal_usd_value.split()[1].replace(",", "")


    return lastTXN,firstTXN,dropdownMenuBalance,high_bal_eth_value,high_bal_usd_value

def main():
    """
    Finds account details of address
    """
    # URL of the web page
    #url = "https://etherscan.io/address/0xfa31a00a87c766579f0790be73c3763b3e952e94#analytics"
    url_base = "https://etherscan.io/address/"


    f = open("demofile2.csv", "a")

    with open("UseMe.csv") as file:
      for item in file:
        url = url_base+item.strip()+"#analytics"
        account_details = balances(url)
        account_details = cleanup(account_details)
        f.write(url+","+str(account_details[0])+","+str(account_details[1])+","+str(account_details[2])+","+str(account_details[3])+","+str(account_details[4])+"\n")
        time.sleep(1)

    f.close()

    #time.sleep(3)

main()
