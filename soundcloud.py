import requests
import re
import time
import io
from pydub import AudioSegment
BASE_URL = "https://api-v2.soundcloud.com"

class Soundcloud:
    def __init__(self, o_auth, client_id):
        if len(client_id) != 32:
            raise ValueError("Client_IDの形式が間違っています。")
        self.client_id = client_id
        self.o_auth =  o_auth
        json_ver = dict(requests.get("https://product-details.mozilla.org/1.0/firefox_versions.json").json())
        firefox_ver = json_ver.get('LATEST_FIREFOX_VERSION')
        self.headers = {"Authorization" : o_auth, "Accept": "application/json","User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{firefox_ver}) Gecko/20100101 Firefox/{firefox_ver}"}
        app_json = requests.get("https://soundcloud.com/versions.json")
        self.app_version = dict(app_json.json()).get('app')
    def download(self,link):
        m3ulist = []
        dl_mp3 = []
        def combine_mp3s(mp3_files, output_file):
            combined = AudioSegment.empty()

            for mp3_file in mp3_files:
                sound = AudioSegment.from_mp3(mp3_file)
                combined += sound
            combined.export(output_file, format="mp3")
        
        if "utm_source" in link:
            link = re.sub(r'\?.*', '', link)
        while True:
            try:
                response = requests.get(f"https://api-widget.soundcloud.com/resolve?url={link}&format=json&client_id={self.client_id}&app_version=1718026023")
                resolve_response = response.json()
                if not resolve_response:
                    time.sleep(1)
                    continue
                break
            except:
                time.sleep(1)
                continue
        urls = [transcoding['url'] for transcoding in resolve_response['media']['transcodings']]
        uuid = re.search(r'/([^/]+)/stream', urls[0]).group(1)
        track_auth = resolve_response["track_authorization"]
        ids = resolve_response["id"]
        get_track_info_url = f"https://api-v2.soundcloud.com/media/soundcloud:tracks:{ids}/{uuid}/stream/hls?client_id={self.client_id}&track_authorization={track_auth}"
        while True:
            response = requests.get(get_track_info_url)
            get_track_info = response.json()
            if not get_track_info:
                time.sleep(1)
                continue
            break
        response = requests.get(get_track_info["url"])
        filedata = io.BytesIO(response.content)
        readdata = filedata.read()
        p = r'https?://[^\s]+'
        moji =  str(readdata).replace("\\n","\n")
        urls = re.findall(p, moji)
        for url in urls:
            dl_mp3.append(url)
        for fileurl in dl_mp3:
            response = requests.get(fileurl)
            file_like_object = io.BytesIO(response.content)
            m3ulist.append(file_like_object)
        combine_mp3s(m3ulist, f"test.mp3")