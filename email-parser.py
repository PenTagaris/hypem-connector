import re
from bs4 import BeautifulSoup
from email import message_from_file
from email.policy import default
import json

#import the email
email = message_from_file(open('s3-email/vbd7s83v7eg9apr0peh9ebqi8ujfh4sepogr7381', 'r'), policy=default)

#build our regex
regex = re.compile(r'(.*)\s-\s(.*)')

#pretty dictionary thing
d = {}

#do we have html?
email_html = email.get_body(preferencelist='html')
if email_html is not None:
    soup = BeautifulSoup(email_html.get_content(), 'html.parser')
    for links in soup.find_all('a'):
        mo = regex.findall(links.get_text())
        if len(mo):
            d[mo[0][0]] = mo[0][1]

    with open('gmusic.json', 'w', encoding='utf-8') as json_file:
        json.dump(d, json_file, ensure_ascii=False)

