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
from bs4 import BeautifulSoup
import requests

def balances(driver,url):
    """
    Web scrape etherscan for details and balances
    """
    list = []
    driver.set_page_load_timeout(600)
    driver.get(url)

    try:
        span = WebDriverWait(driver,30).until(EC.visibility_of_any_elements_located((By.CLASS_NAME, "text-muted")))
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
        eth_value = driver.find_element(By.XPATH, "/html/body/main/section[3]/div[2]/div[1]/div/div/div[2]/div/div").get_attribute('innerHTML')
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
        publicName = driver.find_element(By.XPATH, "/html/body/main/section[3]/div[1]/div[1]/a/div/span").get_attribute('innerHTML')
    except:
        publicName = None
        pass
    list.append(publicName)

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

    driver.switch_to.default_content()

    try:
        dropdownlist = driver.find_element(By.ID, "availableBalance").get_attribute('innerHTML')
        data = BeautifulSoup(dropdownlist, 'html.parser') 
        parent = data.find_all('li')
        token_count_li = str(data.find("span", {"class": "fw-medium"}))
        token_count_li = re.findall('\d+', token_count_li.split()[3])
        token_count_li = int(token_count_li[0])
        list.append(token_count_li)
        
        i = 1
        while((i<token_count_li+1) and ('$0.00' not in dropdownMenuBalance)):
            
            coin = parent[i] #individual coin

            link = coin.find_all('a', href=True)
            link = link[0]['href']
            
            token = coin.find_all("span", {"class": "list-name hash-tag text-truncate"})
            
            if(len(token) == 1):
                token = token[0].getText()
            elif(len(token) == 0):
                print("No token")
                token = None
            else:
                token = token[1].getText()
            token_usd = coin.find("div", {"class": "list-usd-value"}).getText()
            list.append(token)
            list.append(link)
            list.append(token_usd)
            
            i=i+1

    except:
        token_count_li = None
        token = None
        link = None
        token_usd = None
        list.append(token_count_li)
        list.append(token)
        list.append(link)
        list.append(token_usd)
        pass
    
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
    publicName = account_details[4]
    high_bal_eth_value = account_details[5]
    high_bal_usd_value = account_details[6]
    token_count = account_details[7]

    if lastTXN is not None:
        lastTXN = lastTXN.split()  #[0] from, [1] number, [2] days/hrs, [3] number, [4] hrs/mins, [5] ago
        list.append(lastTXN[1].replace(",", ""))
        list.append(lastTXN[2].replace(",", ""))
    else:
        list.append(None)
        list.append(None)

    if firstTXN is not None:
        firstTXN = firstTXN.split()  #[0] from, [1] number, [2] days/hrs, [3] number, [4] hrs/mins, [5] ago
        list.append(firstTXN[1].replace(",", ""))
        list.append(firstTXN[2].replace(",", ""))
    else:
        list.append(None)
        list.append(None)

    if eth_value is not None:
        eth_value = eth_value.split()
        eth_value = eth_value[4].split(">")
        whole_number = eth_value[2]
        whole_number = re.search(r'\d+', whole_number).group().replace(",", "")
        list.append(whole_number)
    else:
        list.append(None)

    if dropdownMenuBalance is not None:
        dropdownMenuBalance = dropdownMenuBalance.split()
        dropdownMenuBalance = ''.join(dropdownMenuBalance)
        i = 0
        string = ""
        rs_price = False
        ls_price = False
        
        while(i<len(dropdownMenuBalance) and (rs_price == False or ls_price == False)): #purposely not using regex due to dynamic html complexities
            if(dropdownMenuBalance[i] == '$'): #find price
                ls_price = True
            elif(dropdownMenuBalance[i] == "<" and ls_price == True): #end of price string
                rs_price = True
            elif(ls_price == True and rs_price == False): #add digits to string
                string = string + dropdownMenuBalance[i]
            i = i + 1
        string = string.replace(",","")

        list.append(remove_periods(string))
    else:
        list.append(None)

    if publicName is not None:
        publicName = publicName.replace(",", "")
        list.append(publicName)
    else:
        list.append(None)

    if high_bal_usd_value is not None:
        high_bal_usd_value = high_bal_usd_value.split()[1].replace(",", "")
        list.append(high_bal_usd_value)
    else:
        list.append(None)

    if high_bal_eth_value is not None:
        high_bal_eth_value = high_bal_eth_value.split()[0].replace(",", "")
        list.append(high_bal_eth_value)
    else:
        list.append(None)
    
    if token_count is not None and len(account_details) > 8:
        j=8
        i=0
        while(i<token_count):
            if(account_details[j] is not None):
                list.append(account_details[j].replace(",", ""))
                list.append(account_details[j+1].replace(",", ""))
                if(account_details[j+2].isspace()):
                    list.append(None)
                else:
                    list.append(account_details[j+2].replace(",", "").replace("$", ""))
            i=i+1
            j=j+3
    else:
        list.append(None)
        list.append(None)
        list.append(None)
    return list

def remove_periods(string):
    string = str(string)
    i=0
    string1 = ""
    firstPeriod = False
    secondPeriod = False
    while(i<len(string) and secondPeriod == False):
        if(string[i].isdigit() and secondPeriod == False):
            string1 = string1 + string[i]
        elif(string[i] == "." and firstPeriod == False):
            string1 = string1 + string[i]
            firstPeriod = True
        elif(string[i].isdigit() == False and firstPeriod == True):
            secondPeriod == True
        i=i+1

    if(string1[-1] == '.'):
        string1 = string1 + "00"

    return string1

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
    f.write(item.strip()+","+url)
    i=0
    while(i<len(account_details)):
        f.write(","+str(account_details[i]))
        i=i+1
    f.write("\n")
    return

def lookback_csv(input_days,input_money):
    if input_days == '':
        input_days = 30
    if input_money == '':
        input_money = 1000000
    return

def tokens_sum(f):
    '''
    []loop for the coin
    []remove the link extension that is attached to the wallet address, we just want address only.
    []i need to run this program for a full list because i need to use that list as a testing ground for this function to repeat stuff
    []need to exlude public addresses (companies) and only include individuals
    []need to make holders functionality
    '''
    readFile = f.readlines()
    line = 1
    list = []
    while(line<(len(readFile))):
        tokenPOS = 11
        addressPOS = 12
        usdPOS = 13
        addressInfo = readFile[line].split(",")
        while(addressPOS<len(addressInfo) and addressInfo[addressPOS] != "None"):
            if(addressInfo[usdPOS] == "None" or addressInfo[usdPOS] == "None\n" or addressInfo[usdPOS] == ""):
                addressInfo[usdPOS] = 0.00
            address1 = addressInfo[addressPOS].rstrip()
            address2 = address1.split("/")[2].split("?")[0]
            if(address2 not in list):
                list.append(addressInfo[tokenPOS].rstrip())
                list.append(1)
                list.append(address2)
                usd_value = remove_periods(addressInfo[usdPOS])
                list.append(float(str(usd_value).rstrip()))
            elif(address2 in list):
                listAddressIndex = list.index(address2)
                listOccurrenceIndex = listAddressIndex - 1 #occurrence
                listUSDIndex = listAddressIndex + 1 #USD
                list[listOccurrenceIndex] = int(list[listOccurrenceIndex]) + 1
                list[listUSDIndex] = float(list[listUSDIndex]) + float(addressInfo[addressPOS+1])
            tokenPOS = tokenPOS + 3
            addressPOS = addressPOS + 3
            usdPOS = usdPOS + 3
        line = line + 1

    return list

def tokens_sum_file(list):
    f1 = open("results/tokens_sum"+time.strftime("%Y%m%d-%H%M%S")+".csv", "w")
    f1.write("coin,numHolders,link,sum\n")
    i=0
    while(i<len(list)):
        f1.write(str(list[i])+","+str(list[i+1])+","+str(list[i+2])+","+str(list[i+3])+"\n")
        i=i+4
    f1.close()
    return

def clean_addresses(address_filename):
    f = open(address_filename, "r")
    readFile = f.readlines()
    readFile = list(dict.fromkeys(readFile))
    with open("input_files/addresses.csv", "w") as outfile:
        outfile.write("".join(readFile))
    return

def main():
    """
    Finds account details of address
    """
    # URL of the web page
    url_base = "https://etherscan.io/address/"
    #'''
    #input_days = input("Lookback (Example, 30 = 30 days from today): ")
    #input_money = input("Amount (Example, 1000000 = Only look at accounts with greater than $1000000): ")
    address_filename = "input_files/addresses.csv"
    clean_addresses(address_filename)
    
    filename = "results/results"+time.strftime("%Y%m%d-%H%M%S")+".csv"
    f = open(filename, "w")
    f.write("address,url,numdayshrs (lastTXN),dayshrs (lastTXN),numdayshrs (firstTXN),dayshrs (firstTXN),current_eth_portfolio,dropdownMenuBalance,publicName,usdATH,ethATH,tokens\n")
    
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    
    i=1
    with open(address_filename) as file: #addresses only, no column names
      for item in file:
        url = url_base+item.strip()+"#analytics"

        original_window = driver.current_window_handle
        driver.switch_to.new_window('tab')
        account_details = balances(driver,url)
        account_details = cleanup(account_details)
        details_to_file(f,item,url,account_details)
        time.sleep(.5)
        driver.close()
        driver.switch_to.window(original_window)
        print("==========================================================Success==========================================================",i)
        i=i+1
    f.close()
    driver.quit()
    #'''
    f = open(filename, "r") #must close file and reopen as read only
    #f = open("results/results.csv", "r") #must close file and reopen as read only
    list = tokens_sum(f)

    tokens_sum_file(list)
    f.close()
    

    

    #lookback_csv(input_days,input_money)

main()
