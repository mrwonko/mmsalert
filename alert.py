#!/usr/bin/env python3

from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import requests

import local_config

FETCH = False
CACHE = "cachedresult.html"

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

#soup.find( attrs = { "data-gtm-prop-list-name": "Search result list" } )

#print(soup)

"""
msg = MIMEText( "test", "html", "utf-8" )
msg[ "Subject" ] = "Media Markt Alert"
msg[ "From" ] = local_config.MAIL_FROM
msg[ "To" ]  = u", ".join( local_config.MAIL_TO )

with smtplib.SMTP(local_config.SMTP_SERVER) as s:
  s.login(local_config.SMTP_USER, local_config.SMTP_PASS)
  s.send_message(msg)
"""
