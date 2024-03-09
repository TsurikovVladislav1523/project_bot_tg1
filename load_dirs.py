import io
import os
import shutil
import requests
from PIL import Image

CLOUD_TOKEN = '8e34e01b502a43c68fb0bb9ba2956df5'
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}


def load_dirs(TOKEN, tg_id):
    global headers
    headers["Authorization"] = f'OAuth {TOKEN}'
    shutil.rmtree(f"Images_{tg_id}/")
    os.mkdir(f"Images_{tg_id}/")
    r = requests.get(f"{URL}?path=photos", headers=headers).json()
    dirs = []
    for item in r['_embedded']['items']:
        if item['type'] == 'dir':
            dirs.append(item['name'])
    for dir in dirs:
        os.mkdir(f'Images_{tg_id}/{dir}/')
        r = requests.get(f"{URL}?path=photos/{dir}", headers=headers).json()
        for elem in r['_embedded']['items']:
            img = requests.get(f'{URL}/download?path=photos/{dir}/{elem["name"]}', headers=headers)
            img = img.json()['href']
            img = requests.get(img)
            img = Image.open(io.BytesIO(img.content))
            img.save(f'Images_{tg_id}/{dir}/{elem["name"]}', format="PNG")
            img.close()
            break


def load_path(TOKEN, tg_id):
    global headers
    names_t = []
    headers["Authorization"] = f'OAuth {TOKEN}'
    if not os.path.exists(f"Images_{tg_id}/one_path"):
        os.mkdir(f"Images_{tg_id}/one_path")
    else:
        shutil.rmtree(f"Images_{tg_id}/one_path")
        os.mkdir(f"Images_{tg_id}/one_path")
    r = requests.get(f"{URL}?path=sorted_photo", headers=headers).json()
    for elem in r['_embedded']['items']:
        name = elem["name"].split("_")[0]
        if name not in names_t:
            img = requests.get(f'{URL}/download?path=sorted_photo/{elem["name"]}', headers=headers)
            img = img.json()['href']
            img = requests.get(img)
            img = Image.open(io.BytesIO(img.content))
            img.save(f'Images_{tg_id}/one_path/{name}.png', format="PNG")
            img.close()
            names_t.append(name)
    return names_t

# load_path("y0_AgAAAAAntKPVAAqnjgAAAADvHae-eQmDRNXeThaqoPlbkr24VwMpuXY",1057505123)