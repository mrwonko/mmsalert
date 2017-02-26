#!/usr/bin/env python3

from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import requests
import re

import local_config

FETCH = False
CACHE = "cachedresult.html"

RESULT_COUNT_RE = re.compile("(\d+)\s+Ergebnisse")
ARTICLE_NO_RE = re.compile("Artikelnummer\s+(\d+)")

def fetchSoup():
  req = requests.get("https://www.mediamarkt.de/de/search.html?searchProfile=onlineshop&query=nintendo+Switch")
  assert( req.status_code / 100 == 2 )
  soup = BeautifulSoup(req.text, "html.parser")
  return soup

if FETCH:
  soup = fetchSoup()
  with open(CACHE, "w") as f:
    f.write(soup.prettify())
else:
  with open(CACHE) as f:
    soup = BeautifulSoup(f.read(), "html.parser")

class Result:
  def __init__(self, count, articles):
    self.count = count
    self.articles = articles
  def diff(self, rhs):
    selfKeys = set(self.articles.keys())
    rhsKeys = set(rhs.articles.keys())
    newKeys = rhsKeys.difference(selfKeys)
    removedKeys = selfKeys.difference(rhsKeys)
    diffs = []
    if self.count != rhs.count:
      diffs.append("number of results changed from {} to {}".format(self.count, rhs.count))
    if len(newKeys) > 0:
      diffs.append("new results:\n{}".format(
          "\n".join(["- " + str(rhs.articles[k]) for k in newKeys])))
    if len(removedKeys) > 0:
      diffs.append("removed results:\n{}".format(
          "\n".join(["- " + str(self.articles[k]) for k in removedKeys])))
    return diffs


class Article:
  def __init__(self, no, name, link):
    self.no = no
    self.name = name
    self.link = link
  def __str__(self):
    return "{self.no}: {self.name} @ {self.link}".format(self=self)


def parse(soup):
  resultCountText = soup.select_one("hgroup.cf").find("h1").text
  resultCount = int(RESULT_COUNT_RE.search(resultCountText).group(1))

  articles = {}

  resultList = soup.find(attrs={"data-gtm-prop-list-name": "Search result list"})
  for content in resultList.find_all(class_ = "content"):
    link = content.find("h2").find("a")
    title = link.text.strip()
    articleNoText = content.find(string=ARTICLE_NO_RE)
    articleNo = int(ARTICLE_NO_RE.search(articleNoText).group(1))
    articles[articleNo] = Article(
        articleNo, title, "http://www.mediamarkt.de" + link.get("href"))

  return Result(resultCount, articles)

with open("newresults.html") as f:
  newSoup = BeautifulSoup(f.read(), "html.parser")
oldResult = parse(soup)
newResult = parse(newSoup)
print("\n".join(oldResult.diff(newResult)))

"""
msg = MIMEText( "test", "html", "utf-8" )
msg[ "Subject" ] = "Media Markt Alert"
msg[ "From" ] = local_config.MAIL_FROM
msg[ "To" ]  = u", ".join( local_config.MAIL_TO )

with smtplib.SMTP(local_config.SMTP_SERVER) as s:
  s.login(local_config.SMTP_USER, local_config.SMTP_PASS)
  s.send_message(msg)
"""
