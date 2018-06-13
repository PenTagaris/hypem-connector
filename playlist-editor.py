from gmusicapi import Mobileclient

#Set login variables
email = 'jstnchristian@gmail.com'
password = 'vefcgkyjomvxsdcr'

#This should be my Pixel's ID
android_id = '34f9502c342bfdaa'

api = Mobileclient()
logged_in = api.login(email, password, android_id)


