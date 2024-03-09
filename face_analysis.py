from imutils import paths
import face_recognition
import pickle
import cv2
import os
from load_dirs import load_dirs, load_path

CLOUD_TOKEN = '8e34e01b502a43c68fb0bb9ba2956df5'
# CLOUD_URL = f"https://oauth.yandex.ru/authorize?response_type=token&client_id={CLOUD_TOKEN}"
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = 'y0_AgAAAAAntKPVAAqnjgAAAADvHae-eQmDRNXeThaqoPlbkr24VwMpuXY'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}


def update_emb(TOKEN, tg_id):
    # в директории Images хранятся папки со всеми изображениями
    load_dirs(TOKEN, tg_id)
    imagePaths = list(paths.list_images(f'Images_{tg_id}'))
    knownEncodings = []
    knownNames = []
    # перебираем все папки с изображениями
    for (i, imagePath) in enumerate(imagePaths):
        # извлекаем имя человека из названия папки
        name = imagePath.split(os.path.sep)[-2]
        # загружаем изображение и конвертируем его из BGR (OpenCV ordering)
        # в dlib ordering (RGB)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # используем библиотеку Face_recognition для обнаружения лиц
        boxes = face_recognition.face_locations(rgb, model='hog')
        # вычисляем эмбеддинги для каждого лица
        encodings = face_recognition.face_encodings(rgb, boxes)
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    # сохраним эмбеддинги вместе с их именами в формате словаря
    data = {"encodings": knownEncodings, "names": knownNames}
    # для сохранения данных в файл используем метод pickle
    f = open(f"face_enc_{tg_id}", "wb")
    f.write(pickle.dumps(data))
    f.close()


def search(path, tg_id):
    if os.path.exists(f'face_enc_{tg_id}'):
        data = pickle.loads(open(f'face_enc_{tg_id}', "rb").read())
        # Находим путь к изображению, на котором хотим обнаружить лицо, и передаем его сюда
        image = cv2.imread(path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # встраивание лиц для face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []
        # перебираем выданные нам лица, если у нас есть несколько вложений для нескольких лиц
        for encoding in encodings:
            # Сравниваем кодировки с кодировками в данных["encodings"]
            # Совпадения содержат массив с логическими значениями и True для вложений, которым он точно соответствует
            # и False для остального
            matches = face_recognition.compare_faces(data["encodings"],
                                                     encoding)
            # установливаем имя =Unknown, если кодировка не совпадает
            name = "Unknown"
            # проверяем, нашли ли мы совпадения
            if True in matches:
                # Находим позиции, в которых мы получаем значение True, и сохраняем их
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                # перебираем совпадающие индексы и ведем подсчет для каждого распознанного лица
                for i in matchedIdxs:
                    name = data["names"][i]
                    # увеличиваем количество для полученного нами имени
                    counts[name] = counts.get(name, 0) + 1
                    # установите имя, имеющее наибольшее количество значений
                    name = max(counts, key=counts.get)
                names.append(name)
        res = []
        for i in names:
            if i not in res:
                res.append(i)
        return res
    else:
        return []

def create_emb(TOKEN, tg_id):
    names = load_path(TOKEN, tg_id)
    knownEncodings = []
    knownNames = []
    for path in names:
        image = cv2.imread(f'Images_{tg_id}/one_path/{path}.png')
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # используем библиотеку Face_recognition для обнаружения лиц
        boxes = face_recognition.face_locations(rgb, model='hog')
        # вычисляем эмбеддинги для каждого лица
        encodings = face_recognition.face_encodings(rgb, boxes)
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(path)
    data = {"encodings": knownEncodings, "names": knownNames}
    # для сохранения данных в файл используем метод pickle
    f = open(f"face_enc_{tg_id}", "wb")
    f.write(pickle.dumps(data))
    f.close()


def fast_umdate_emb(path, name, tg_id):
    image = cv2.imread(path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # используем библиотеку Face_recognition для обнаружения лиц
    boxes = face_recognition.face_locations(rgb, model='hog')
    # вычисляем эмбеддинги для каждого лица
    encodings = face_recognition.face_encodings(rgb, boxes)
    data = pickle.loads(open(f'face_enc_{tg_id}', "rb").read())
    data["encodings"].append(encodings[0])
    data['names'].append(name)
    f = open(f"face_enc_{tg_id}", "wb")
    f.write(pickle.dumps(data))
    f.close()

# update_emb(,1057505123)
# print(search(f'photos/vlad1.png'))
