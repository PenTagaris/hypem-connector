import re
from os import listdir
from bs4 import BeautifulSoup
from email import message_from_file
from email.policy import default
import json

#build our regex
regex = re.compile(r'(.*)\s-\s(.*)')

#get all the email files in the directory
#this loop will go away eventually. Right now, I'm using it for testing
for i in listdir('s3-email'):

    #import the email
    email = message_from_file(open('s3-email/{}'.format(i), 'r'), 
            policy=default)

    #instantiate the dictionary
    d = {}

    #do we have html?
    email_html = email.get_body(preferencelist='html')
    if email_html is not None:
        soup = BeautifulSoup(email_html.get_content(), 'html.parser')
        for links in soup.find_all('a'):
            mo = regex.findall(links.get_text())
            if len(mo):
                d[mo[0][0]] = mo[0][1]

        #write the json
        with open('json/{}.json'.format(i), 'w', encoding='utf-8') as json_file:
            json.dump(d, json_file, ensure_ascii=False)

