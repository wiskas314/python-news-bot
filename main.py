import requests
import json
from bs4 import BeautifulSoup
import re
import argparse

def get_clothes(pages=5):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

    news_dict = {}
    for i in range(pages+1):
        url = "https://www.csoonline.com/security/page/{}/".format(i)
        r = requests.get(url=url, headers=headers)

        soup = BeautifulSoup(r.text, "lxml")
        articles_cards = soup.find_all("a", class_="grid content-row-article")


        for article in articles_cards:
            article_title = article.find("h3", class_="card__title").text.strip()
            article_url = f'{article.get("href")}'
            article_id = article_url.split("/")[-2]
            article_desc=article.find("p",class_="card__description").text.strip()


            time_element = article.find("span", class_=re.compile(r"reading-time|minutes", re.I))
            if not time_element:
                time_element = article.find("span", string=re.compile(r"\d+\s*mins?", re.I))

            reading_time = "N/A"
            if time_element:
                time_text = time_element.get_text(strip=True)
                time_match = re.search(r"(\d+)\s*(mins?|minutes?)", time_text, re.I)
                if time_match:
                    reading_time = f"{time_match.group(1)} mins"
            if article_id not in news_dict and int(reading_time[:2])>11:
                news_dict[article_id] = {
                    "article_title": article_title,
                    "article_url": article_url,
                    "reading_time": reading_time,
                    "article_desc":  article_desc
                }
            else:
                continue

        with open("news_dict.json", "w") as file:
            json.dump(news_dict, file, indent=4, ensure_ascii=False)




def main():
    parser = argparse.ArgumentParser(description='Парсер новостей')
    parser.add_argument('pages', type=int, nargs='?', default=9,
                        help='Количество страниц для парсинга')
    args = parser.parse_args()

    return get_clothes(args.pages)

if __name__=="__main__":
    main()
