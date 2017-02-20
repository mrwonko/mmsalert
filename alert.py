#!/usr/bin/env python3

from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

import local_config

msg = MIMEText( "test", "html", "utf-8" )
msg[ "Subject" ] = "Media Markt Alert"
msg[ "From" ] = local_config.MAIL_FROM
msg[ "To" ]  = u", ".join( local_config.MAIL_TO )

with smtplib.SMTP(local_config.SMTP_SERVER) as s:
  s.login(local_config.SMTP_USER, local_config.SMTP_PASS)
  s.send_message(msg)
