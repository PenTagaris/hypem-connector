import re
import sys
import argparse
from bs4 import BeautifulSoup
from email import message_from_file
from email.policy import default
from gmusicapi import Mobileclient

def parse_email(email_file):
    #build our regex
    regex = re.compile(r'(.*)\s-\s(.*)')

    #import the email
    email = message_from_file(open(email_file, 'r'), 
                policy=default)

    #instantiate artist_title
    artist_title = []
    
    #do we have html?
    email_html = email.get_body(preferencelist='html')
    if email_html is not None:
        soup = BeautifulSoup(email_html.get_content(), 'html.parser')
        for links in soup.find_all('a'):
            mo = regex.findall(links.get_text())
            if len(mo):
                temp = '{} {}'.format(mo[0][0], mo[0][1])
                artist_title.append(temp.split('(', 1)[0].lower().rstrip())

    return artist_title

def add_to_gmusic_playlist(search_list, 
                            email , 
                            password, 
                            android_id, 
                            playlist_id = 'b65f8c76-8ff7-41d1-a775-a3bfdc20920a'):

    #Instatiate the songId list
    song_ids = []

    #Log in
    api = Mobileclient()
    logged_in = api.login(email, password, android_id)

    #start searching through the search list. Append IDs to song_ids
    for search_string in search_list:
        songsearch = api.search(search_string, 1)
        if (songsearch['song_hits']):
            song_ids.append(songsearch['song_hits'][0]['track']['storeId'])

    #Add songs to the playlist
    api.add_songs_to_playlist(playlist_id, song_ids)

    api.logout()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", type=str, help="The email address")
    parser.add_argument("-p", "--password", type=str, help="The password")
    parser.add_argument("-a", "--android_id", type=str, help="The android_id")
    parser.add_argument("-f", "--file", type=str, help="The email file to parse")
    args = parser.parse_args()

    search_list = parse_email(args.file)
    add_to_gmusic_playlist(search_list, args.email, args.password, args.android_id)

if __name__ == "__main__":
    main()
