import re
import os
import uuid
from base64 import b64decode
from email import message_from_file
from email.policy import default

import boto3
from bs4 import BeautifulSoup
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
    try:
        email_html = email.get_body(preferencelist='html')
        soup = BeautifulSoup(email_html.get_content(), 'html.parser')
        for links in soup.find_all('a'):
            mo = regex.findall(links.get_text())
            if len(mo):
                temp = '{} {}'.format(mo[0][0], mo[0][1])
                artist_title.append(temp.split('(', 1)[0].lower().rstrip())

        print("I found some songs and such: {}".format(artist_title))
        return artist_title

    except Exception as e:
        print("Looks like no HTML here, boss. Dying.")
        raise

def add_to_gmusic_playlist(search_list, 
                            email , 
                            password, 
                            android_id, 
                            playlist_id):

    #Instatiate the songId list
    song_ids = []

    #Log in
    api = Mobileclient()
    try:
        logged_in = api.login(email, password, android_id)
    except Exception as e:
        print("Doesn't look like we were able to log in. Sucks.")
        print(e)
        raise

    #start searching through the search list. Append IDs to song_ids
    for search_string in search_list:
        songsearch = api.search(search_string, 1)
        if (songsearch['song_hits']):
            song_ids.append(songsearch['song_hits'][0]['track']['storeId'])

    #print the song_ids
    print ("Song IDs found: {}".format(song_ids))
    #Add songs to the playlist
    try:
        result = api.add_songs_to_playlist(playlist_id, song_ids)
        api.logout()
        return (result)
    except Exception as d:
        print("Adding songs to the playlist didn't work.")
        print(d)
        raise

def lambda_main(event, context):
    s3_client = boto3.client('s3')
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        #make key equal to the last string, and change switch / to __ 
        #this fixes an issue where lambda wasn't able to see the file
        key = record['s3']['object']['key']
        download_key = key.replace('/','__')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), download_key) 
        s3_client.download_file(bucket, key, download_path)

    search_list = parse_email(download_path)

    #Note that putting the decryption here *should* result in it being run only
    #once per container
    DECRYPTED_EMAIL = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(os.environ['email']))['Plaintext']
    DECRYPTED_PASSWORD = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(os.environ['password']))['Plaintext']
    DECRYPTED_ANDROID = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(os.environ['android_id']))['Plaintext']
    DECRYPTED_PLAYLIST = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(os.environ['playlist']))['Plaintext']

    add_to_gmusic_playlist(search_list, 
			    DECRYPTED_EMAIL.decode("utf-8"), 
			    DECRYPTED_PASSWORD.decode("utf-8"),
                            DECRYPTED_ANDROID.decode("utf-8"),
                            DECRYPTED_PLAYLIST.decode("utf-8"))

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--email", type=str, help="The email address")
    parser.add_argument("-p", "--password", type=str, help="The password")
    parser.add_argument("-a", "--android_id", type=str, help="The android_id")
    parser.add_argument("-f", "--file", type=str, help="The email file to parse")
    parser.add_argument("-l", "--playlist", type=str, help="The playlist to add to")
    args = parser.parse_args()

    try:
        search_list = parse_email(args.file)
    except Exception as search_list_except:
        print (search_list_except)
        return 128

    try:
        add_to_gmusic_playlist(search_list, 
                                    args.email, 
                                    args.password, 
                                    args.android_id,
                                    args.playlist)
    except Exception as playlist_exception:
        print(playlist_exception)
        return 128

if __name__ == "__main__":
    main()
