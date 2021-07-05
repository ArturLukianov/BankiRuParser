#!/usr/bin/env python3
import requests
import re
import argparse
import math
from collections import namedtuple
import html
import csv


Review = namedtuple('Review', ['datetime', 'header', 'rating', 'text', 'reply', 'status'])


def parse_reviews(url):
    main_page_html = requests.get(url).text
    total_entries = int(re.findall('totalItems: (\d+)', main_page_html)[0])
    entries_per_page = int(re.findall('itemsPerPage: (\d+)', main_page_html)[0])
    num_pages = math.ceil(total_entries / entries_per_page)
    print(num_pages)
    parsed_data = []
    for i in range(1, num_pages + 1):
        page_html = requests.get(url + f'?page={i}&isMobile=0').text
        reviews = page_html.split('class="flexbox flexbox--row flexbox--gap_xxsmall flexbox--align-items_flex-start"')[1:]
        for review in reviews:
            rating = re.findall('data-test="responses-estimate"(?:.|\n)*?>(.*?)<', review)[0]
            if rating == 'Без оценки': rating = -1
            else: rating = re.findall('rating-grade--value-(\d)', review)[0]
            
            datetime = re.findall('\d\d.\d\d.\d\d\d\d \d\d?:\d\d', review)[0]
            
            header = re.findall('data-test="responses-header".*?>(.*?)<\/a>', review)[0]
            
            if 'data-full' in review: text = re.findall(' data-full>(.*?(?:.|\n)*?)<\/div>', review)[0]
            else: text = re.findall('data-test="responses-message">(.*?(?:.|\n)*?)<\/div>', review)[0]
            text = text.strip().replace('<br/>', '\n')
            text = html.unescape(text)

            reply = ''
            if '<div class="thread-item__text">' in review:
                reply = re.findall('<div class="thread-item__text">((?:.|\n)*?)<\/div>', review)[0]
                reply = reply.strip().replace('<br/>', '\n')
                reply = html.unescape(reply)

            status = ''
            if rating != -1:
                status = re.findall('data-test="responses-status">((?:.|\n)*?)<', review)[0].strip()
                if status == '' and '<span class="text-label">Проблема решена</span>' in review:
                        status = 'Проблема решена'
            
            parsed_data.append(Review(datetime=datetime, header=header, rating=rating, text=text, reply=reply, status=status))
        print(f'[!] page {i} parsed')
    with open('output.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(['datetime', 'header', 'rating', 'text', 'reply', 'status'])
        for review in parsed_data:
            w.writerow([review.datetime, review.header, review.rating, review.text, review.reply, review.status])
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse banki.ru reviews')
    parser.add_argument("url", help="URL to banki.ru page")
    args = parser.parse_args()
    url = args.url
    parse_reviews(url)
