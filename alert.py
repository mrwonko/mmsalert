#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
import requests
import re
import pickle

from bs4 import BeautifulSoup

import local_config

FETCH = False
CACHE = "cachedresult.html"
RESULT_CACHE = "result.pickle"

RESULT_COUNT_RE = re.compile(r"(\d+)\s+Ergebnisse")
ARTICLE_NO_RE = re.compile(r"Artikelnummer\s+(\d+)")

def fetch_soup():
    req = requests.get(
        "https://www.mediamarkt.de/de/search.html?searchProfile=onlineshop&query=nintendo+Switch")
    assert req.status_code / 100 == 2
    soup = BeautifulSoup(req.text, "html.parser")
    return soup

class Result(object):
    def __init__(self, count, articles):
        self.count = count
        self.articles = articles
    def diff(self, rhs):
        self_keys = set(self.articles.keys())
        rhs_keys = set(rhs.articles.keys())
        new_keys = rhs_keys.difference(self_keys)
        removed_keys = self_keys.difference(rhs_keys)
        diffs = []
        if self.count != rhs.count:
            diffs.append("number of results changed from {} to {}".format(self.count, rhs.count))
        if len(new_keys) > 0:
            diffs.append("new results:\n{}".format(
                "\n".join(["- " + str(rhs.articles[k]) for k in new_keys])))
        if len(removed_keys) > 0:
            diffs.append("removed results:\n{}".format(
                "\n".join(["- " + str(self.articles[k]) for k in removed_keys])))
        return diffs


def store(obj):
    with open(RESULT_CACHE, "wb") as f:
        pickle.dump(obj, f)


def load():
    try:
        with open(RESULT_CACHE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return Result(0, {})


class Article(object):
    def __init__(self, no, name, link):
        self.num = no
        self.name = name
        self.link = link
    def __str__(self):
        return "{self.num}: <a href=\"{self.link}\">{self.name}</a>".format(self=self)


def parse(soup):
    result_count_text = soup.select_one("hgroup.cf").find("h1").text
    result_count = int(RESULT_COUNT_RE.search(result_count_text).group(1))

    articles = {}

    result_list = soup.find(attrs={"data-gtm-prop-list-name": "Search result list"})
    for content in result_list.find_all(class_="content"):
        link = content.find("h2").find("a")
        title = link.text.strip()
        article_num_text = content.find(string=ARTICLE_NO_RE)
        article_num = int(ARTICLE_NO_RE.search(article_num_text).group(1))
        articles[article_num] = Article(
            article_num, title, "http://www.mediamarkt.de" + link.get("href"))

    return Result(result_count, articles)


def alert(diff):
    diff_str = "\n".join(diff)
    print(diff_str)
    msg = MIMEText(diff_str.replace("\n", "<br/>\n"), "html", "utf-8")
    msg["Subject"] = "Media Markt Alert"
    msg["From"] = local_config.MAIL_FROM
    msg["To"] = u", ".join(local_config.MAIL_TO)

    with smtplib.SMTP(local_config.SMTP_SERVER) as s:
        s.login(local_config.SMTP_USER, local_config.SMTP_PASS)
        s.send_message(msg)


def main():
    old_result = load()
    if not isinstance(old_result, Result):
        print("we're in a pickle, old_result is {}".format(old_result))
        old_result = Result(0, {})
    soup = fetch_soup()
    # write to file for parsing error post-mortems etc.
    with open(CACHE, "w") as f:
        f.write(soup.prettify())
    result = parse(soup)
    diff = old_result.diff(result)
    print(len(diff))
    if len(diff) > 0:
        store(result)
        alert(diff)


main()
