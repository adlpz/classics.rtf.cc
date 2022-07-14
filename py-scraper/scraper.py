#!/usr/bin/env python3

# Please excuse the quality, I haven't written python a _a lot_ of time...

import queue
import threading
import requests
from time import sleep
import sqlite3
from os import path

WAIT_TIME=.75

# Queues
q = queue.Queue()
store_q = queue.Queue()

# Database utils
def get_db():
    f = path.realpath(path.dirname(path.realpath(__file__)) +  '/../articles.db')
    return sqlite3.connect(f)

# Database init
def init_db():
    con = get_db()
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS articles (
        id text not null primary key,
        year integer,
        created integer,
        title text,
        author text,
        url text,
        points integer,
        comments integer)''')

    con.commit()
    con.close()

# Database store thread
def store_worker():
    con = get_db()
    cur = con.cursor() 
    while True:
        rows = store_q.get()
        l = len(rows)
        print(f'Flushing {l} rows to the database')
        cur.executemany("insert or ignore into articles values (?,?,?,?,?,?,?,?)", rows)
        con.commit()
        store_q.task_done()

def build_url(year, page = 0):
    return f'https://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=points%3E100&restrictSearchableAttributes=title&queryType=prefixNone&query=%22({year})%22&page={page}'

# Store
def store(year, hits):
    l = len(hits)
    rows = [
        [h['objectID'], year, h['created_at_i'], h['title'], h['author'], h['url'], h['points'], h['num_comments']]
        for h in hits
        if f'({year})' in h['title']
    ]
    store_q.put(rows)
    print(f'Queued storing {l} hits for year {year}')


# Fetch url and store result. Returns number of pages.
def fetch(year, url = None):
    if not url:
        url = build_url(year)
        
    response = requests.get(url)

    try:
        data = response.json()
    except:
        print('Failed parsing json')
        print(response.text)
        return 0

    store(year, data['hits'])
    return data['nbPages']



def worker():
    while True:
        [year, url] = q.get()
        size = q.qsize()
        print(f'Fetching for year {year}. Queue has {size} items.')
        fetch(year, url)
        sleep(WAIT_TIME)
        q.task_done()

# Main
init_db()
threading.Thread(target=worker, daemon=True).start()
threading.Thread(target=store_worker, daemon=True).start()

for year in range(1950, 2016):
    print(f'Fetching first page for year {year}')
    pages = fetch(year)
    print(f'Found {pages} pages of hits for year {year}')
    if (pages > 1):
        for page in range(1, pages + 1):
            q.put([year, build_url(year, page)])
    sleep(WAIT_TIME)

q.join()
store_q.join()
print('All URLs fetched')
