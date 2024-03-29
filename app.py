import sqlite3
import json
from time import sleep
import fake_useragent
import random

import requests
from bs4 import BeautifulSoup

# URL2 = "https://www.vilajar.com/RentVilla/22/price-30000-2400000,home-0-3,sort-date-desc"
URL = "https://www.vilajar.com"



# if u have v2ray config and using nekoray, u can use this proxy
proxies = {"https": "127.0.0.1:2081"}
# else u have to make it empty like below line of code
# proxies = {}


def get_users_url(url) -> list[str]:
    page = requests.get(url).content.decode()
    soup = BeautifulSoup(page, "html.parser")
    villaBox = soup.find(id="villaBox")
    villa_item = villaBox.find_all("figure", class_="villa-item")
    x = []
    for i in villa_item:
        x.append(i.find("a", href=True)["href"])
    return x


def get_phone(user_page) -> tuple[str]:
    header = {"User-Agent": fake_useragent.UserAgent().random}
    req = requests.Session()
    req = req.get(user_page, headers=header, proxies=proxies)
    page = req.content.decode()
    print(req.status_code)
    if req.status_code == 429:
        print("Too Many Requests")
        sleep(15)
    soup2 = BeautifulSoup(page, "html.parser")
    span = soup2.find("span", class_="ms-2 d-flex")
    phone_number = span.get_text(strip=True).replace("موبایل", "")
    name = soup2.find("h4", class_="my-1 fs-6").get_text()
    address = (
        soup2.find("h1", class_="d-none d-sm-flex fs-1 mb-0 pb-0").find("a").get_text()
    )
    city = soup2.find("a", class_="city").get_text()
    return (name, phone_number, address, city)


def put_in_db(data) -> None:
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL
        )
        """
    )
    conn.commit()
    cur.execute(
        "insert into users (username, phone_number, address, city) values(?, ?, ?, ?)",
        data,
    )
    conn.commit()


def get_from_db() -> None:
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    return cur.execute("select * from users").fetchall()


def put_in_json(data):
    _all = [
        {
            "name": name[1].strip("\r"),
            "phone": name[2],
            "villa": name[3],
            "city": name[4],
        }
        for name in data
    ]
    f = open("result.json", "w")
    f.write(str(_all))


count = 0
# get data from from page 93 to 127
for j in range(93, 127):
    url = f"https://www.vilajar.com/RentVilla/{j}/price-30000-2400000,home-0-3,sort-date-desc"
    main_page = get_users_url(url)
    for k, i in enumerate(main_page):
        try:
            data = get_phone(URL + i)
            put_in_db(data)
            count += 1
            print(count)
        except KeyboardInterrupt:
            exit()
        except:
            pass

"""
first comment above code from first of for loop
then uncomment blow code to insert all data from
database to a json file.
"""
# put_in_json(get_from_db())
