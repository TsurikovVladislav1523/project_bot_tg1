import io
import os
import shutil
import requests
from PIL import Image

CLOUD_TOKEN = '8e34e01b502a43c68fb0bb9ba2956df5'
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}


def load_dirs(TOKEN):
    global headers
    headers["Authorization"] = f'OAuth {TOKEN}'
    shutil.rmtree("Images/")
    os.mkdir('Images/')
    r = requests.get(f"{URL}?path=photos", headers=headers).json()
    dirs = []
    for item in r['_embedded']['items']:
        if item['type'] == 'dir':
            dirs.append(item['name'])
    for dir in dirs:
        os.mkdir(f'Images/{dir}/')
        r = requests.get(f"{URL}?path=photos/{dir}", headers=headers).json()
        for elem in r['_embedded']['items']:
            img = requests.get(f'{URL}/download?path=photos/{dir}/{elem["name"]}', headers=headers)
            img = img.json()['href']
            img = requests.get(img)
            img = Image.open(io.BytesIO(img.content))
            img.save(f'Images/{dir}/{elem["name"]}', format="PNG")
            img.close()
