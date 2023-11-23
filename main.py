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
    list = []
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
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

    list.append(lastTXN)
    list.append(firstTXN)


    try:
    	eth_value = driver.find_element(By.XPATH, "/html/body/main/section[3]/div[2]/div[1]/div/div/div[3]").get_attribute('innerHTML')
    except:
        eth_value = None
        pass
    list.append(eth_value)

    try:
        dropdownMenuBalance = driver.find_element(By.ID, "dropdownMenuBalance").get_attribute('innerHTML')
    except:
        dropdownMenuBalance = None
        pass

    list.append(dropdownMenuBalance)

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

    list.append(high_bal_eth_value)

    try:
        high_bal_usd_value = driver.find_element(By.ID, "high_bal_usd_value").get_attribute('innerHTML')
    except:
        high_bal_usd_value = None
        pass

    list.append(high_bal_usd_value)

    driver.quit()


    return list

def cleanup(account_details):
    """
    Expects a list of 5 values and cleans up data for each entry
    """
    list = []
    lastTXN = account_details[0]
    firstTXN = account_details[1]
    eth_value = account_details[2]
    dropdownMenuBalance = account_details[3]
    high_bal_eth_value = account_details[4]
    high_bal_usd_value = account_details[5]

    if lastTXN is not None:
        lastTXN = lastTXN.split()  #[0] from, [1] number, [2] days/hrs, [3] number, [4] hrs/mins, [5] ago
        list.append(lastTXN[1])
        list.append(lastTXN[2])
        list.append(lastTXN[3])
        list.append(lastTXN[4])
    if firstTXN is not None:
        firstTXN = firstTXN.split()  #[0] from, [1] number, [2] days/hrs, [3] number, [4] hrs/mins, [5] ago
        list.append(firstTXN[1])
        list.append(firstTXN[2])
        list.append(firstTXN[3])
        list.append(firstTXN[4])
    if eth_value is not None:
        eth_value = eth_value.split()
        current_usd_portfolio = eth_value[6]
        current_eth_price = eth_value[10]
        current_usd_portfolio = re.search(r'(?:[\£\$\€]{1}[,\d]+.?\d*)', current_usd_portfolio).group().replace(",", "").replace("$", "")
        current_eth_price = re.search(r'(?:[\£\$\€]{1}[,\d]+.?\d*)', current_eth_price).group().replace(",", "").replace("$", "")
        current_eth_portfolio = float(current_usd_portfolio)/float(current_eth_price)
        list.append(current_eth_portfolio)
        list.append(current_usd_portfolio)
        list.append(current_eth_price)
    if dropdownMenuBalance is not None:
        dropdownMenuBalance = dropdownMenuBalance.split()
        dropdownMenuBalance = re.search(r'(?:[\£\$\€]{1}[,\d]+.?\d*)', dropdownMenuBalance[0]).group().replace(",", "").replace("$", "")
        list.append(dropdownMenuBalance)
    if high_bal_eth_value is not None:
        high_bal_eth_value = high_bal_eth_value.split()[0]
        list.append(high_bal_eth_value)
    if high_bal_usd_value is not None:
        high_bal_usd_value = high_bal_usd_value.split()[1].replace(",", "")
        list.append(high_bal_usd_value)


    return list

def details_to_file(f,item,url,account_details):
    """
    [0] - address                           [1] - url address
    [2] - number of days/hrs (lastTXN)      [3] - days/hrs (lastTXN)
    [4] - number of hrs/mins (lastTXN)      [5] - hrs/mins (lastTXN)
    [6] - number of days/hrs (firstTXN)     [7] - days/hrs (firstTXN)
    [8] - number of hrs/mins (firstTXN)     [9] - hrs/mins (firstTXN)
    [10] - eth in current_eth_portfolio     [11] - money in current_usd_portfolio
    [12] - current eth price                [13] - dropdownMenuBalance
    [14] - ETH all time high                [15] - USD all time high
    """
    f.write(item.strip()+","+url+","+str(account_details[0])+","+str(account_details[1])+","+str(account_details[2])+","+str(account_details[3])+","+str(account_details[4])+","+str(account_details[5])+","+str(account_details[6])+","+str(account_details[7])+","+str(account_details[8])+","+str(account_details[9])+","+str(account_details[10])+","+str(account_details[11])+","+str(account_details[12])+","+str(account_details[13])+"\n")
    return

def main():
    """
    Finds account details of address
    """
    # URL of the web page
    #url = "https://etherscan.io/address/0xfa31a00a87c766579f0790be73c3763b3e952e94#analytics"
    url_base = "https://etherscan.io/address/"

    #f = open("demofile2.csv", "a")
    f = open("results.csv", "w")
    f.write("address,url,numdayshrs (lastTXN),dayshrs (lastTXN),numhrsmins (lastTXN),hrsmins (lastTXN),numdayshrs (firstTXN),dayshrs (firstTXN),numhrsmins (firstTXN),hrsmins (firstTXN),current_eth_portfolio,current_usd_portfolio,current_eth_price,dropdownMenuBalance,ethATH,usdATH\n")
    i=1
    with open("addresses.csv") as file: #addresses only, no column names
      for item in file:
        url = url_base+item.strip()+"#analytics"
        account_details = balances(url)
        account_details = cleanup(account_details)
        details_to_file(f,item,url,account_details)
        time.sleep(0.05)
        print("Success",i)
        i=i+1
    f.close()

    #time.sleep(3)

main()
