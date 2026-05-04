import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

product_code = input("Provide product code")
page = 1
next = True

headers = {
    "Host" : "www.ceneo.pl",
    "Cookie": "",
    "User-Agent": "",
}

url = f"https://www.ceneo.pl/{product_code}/opinie-{page}"

path_to_driver = "D:\\chromedriver_win32\\chromedriver.exe"
s = Service(path_to_driver)
driver = webdriver.Chrome(service=s)
driver.get(url)
driver.maximize_window()
driver.find_element(by="xpath",value="//*[@id='js_cookie-consent-general']/div/div[2]/button[1]").click()



all_opinions = []
while next: 
    url = f"https://www.ceneo.pl/{product_code}/opinie-{page}"
    print(url)

    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        page_dom = BeautifulSoup(response.text, "html.parser")
        product_name = page_dom.select_one("h1").get_text() if page == 1 else product_name
        opinions = page_dom.select("div.js_product-review:not(.user-post--highlight)")
        print(len(opinions))
        for opinion in opinions:
            single_opinion = {
                'opinion_id': opinion.get("data-entry-id"),
                'author': opinion.select_one("span.user-post__author-name").get_text().strip(),
                'recommendation': opinion.select_one('span.user-post__author-recommendation > em').get_text() if opinion.select_one('span.user-post__author-recommendation > em')else None,
                'score': opinion.select_one('span.user-post__score-count').get_text().strip(),
                'content': opinion.select_one('div.user-post__text').get_text().strip(),
                'pros': [p.get_text() for p in opinion.select('div.review-feature__item--positive')],
                'cons': [c.get_text() for c in opinion.select('div.review-feature__item--negative')],
                'helpful': opinion.select_one('button.vote-yes > span').get_text().strip(),
                'unhelpful': opinion.select_one('button.vote-no > span').get_text().strip(),
                'publish_date': opinion.select_one('span.user-post__published >  time:nth-child(1)').get("datetime").strip(),
                'purchase_date': opinion.select_one('span.user-post__published >  time:nth-child(2)').get("datetime").strip()if opinion.select_one('span.user-post__author-recommendation > em')else None,
        
            }
            all_opinions.append(single_opinion)

    next = True if page_dom.select_one('button.pagination__next') else False
    if next: page += 1

if not os.path.exists("./opinions"):
    os.mkdir("./opinions")

with open(f'./opinions/{product_code}.json',"w", encoding="UTF-8") as jf:
    json.dump(all_opinions, jf, indent=4, ensure_ascii=False)