from soundcloud import Soundcloud

#Oauth2 TokenとSoundCloud Client ID
oauth2,client_id = ""
track_url = input()
account = Soundcloud(f"{oauth2}", f"{client_id}")
account.download(f"{track_url}")