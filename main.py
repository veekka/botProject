#wildberries_bot

import telebot
import requests
from bs4 import BeautifulSoup
import sqlite3

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}

def get_html(url, params=''):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    header = [item.get_text() for item in soup.find('h1', class_='same-part-kt__header').find_all('span')]
    brand = header[0]
    title = header[1].split('/')[0]
    products = {
        'brand': brand,
        'title': title
    }
    return products

def parser(article):
    URL = 'https://www.wildberries.ru/catalog/' + article + '/detail.aspx'
    if requests.head(URL).status_code == 200:
        html = get_html(URL)
        return get_content(html.text)
    else:
        error_dict = {}
        return error_dict


def data_b(product):
    conn = sqlite3.connect('product_requests.db')
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS items(
       art TEXT PRIMARY KEY ,
       brand TEXT,
       title TEXT);
    """)
    conn.commit()
    cur.execute(f"DELETE FROM items WHERE art = {product[0]};")
    conn.commit()

    cur.execute("INSERT INTO items VALUES(?,?,?);", product)
    conn.commit()

    cur.execute("SELECT * FROM items;")
    all_results = cur.fetchall()
    print(all_results)


bot = telebot.TeleBot('2121362236:AAHbEwplS5qaW3Uq3c9JTFV1IiXZmAynH6s')
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    req = message.text.split()
    br = None
    tit = None
    if req[0] in "/get_brand" and len(req) == 2:
        br = parser(req[1]).get('brand', 'Товара с таким артикулом не существует')
        bot.send_message(message.from_user.id, br)
    elif req[0] in "/start":
        bot.send_message(message.from_user.id, "Введите команду и номер артикула.")
    elif req[0] in "/get_title" and len(req) == 2:
        tit = parser(req[1]).get('title', 'Товара с таким артикулом не существует')
        bot.send_message(message.from_user.id, tit)
    else:
        bot.send_message(message.from_user.id, "Команда или номер артикула введены неверно")

    if br is not None or tit is not None:
        br = parser(req[1]).get('brand')
        tit = parser(req[1]).get('title')
        product = (req[1], br, tit)
        data_b(product)

bot.polling(none_stop=True, interval=0)
