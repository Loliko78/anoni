import requests
from bs4 import BeautifulSoup

url = 'https://cabinet.sut.ru/pps_info2?spec=2893&profil=118&kval=62&plan=3172'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
all_paragraphs = soup.find_all('tr')
print(all_paragraphs)