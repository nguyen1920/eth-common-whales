import requests
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}

def block_chain_explorer_block_id(url):
    import requests
    from bs4 import BeautifulSoup

    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    tags = soup.find_all('div', attrs = {'class':'col-md-9'})
    print(soup.find_all('span'))

    f = open("demofile2.txt", "a")
    f.write(str(soup.find_all('span')))
    f.close()

block_chain_explorer_block_id('https://etherscan.io/address/0x471F6E20fA1bc196591b92a4a17b7F9f4E68D484#analytics')
