import sqlite3
from time import sleep
import requests
from bs4 import BeautifulSoup



URL = "https://www.vilajar.com"

def get_users_url() -> list[str]:
    # page = open('index.html', 'r')
    page = requests.get(URL).content.decode()
    soup = BeautifulSoup(page, "html.parser")
    villaBox = soup.find(id="villaBox")
    villa_item = villaBox.find_all("figure", class_="villa-item")
    x = []
    for i in villa_item:
        x.append(i.find("a", href=True)["href"])
    return x


def get_phone(user_page) -> tuple[str]:
    print(user_page)
    req = requests.Session()
    page = req.get(user_page).content.decode()
    soup2 = BeautifulSoup(page, "html.parser")
    span = soup2.find("span", class_="ms-2 d-flex")
    print(span)
    phone_number = span.get_text(strip=True).replace("موبایل", "")
    name = soup2.find("h4", class_="my-1 fs-6").get_text()

    return (name, phone_number)


def put_in_db(data) -> None:
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phone_number TEXT NOT NULL
        )
        """
    )
    conn.commit()
    cur.execute("insert into users (username, phone_number) values(?, ?)", data)
    conn.commit()


main_page = get_users_url()

for k, i in enumerate(main_page):
    sleep(15)
    print(k)
    data = get_phone(URL + i)
    put_in_db(data)