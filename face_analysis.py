from imutils import paths
import face_recognition
import pickle
import cv2
import os
from load_dirs import load_dirs



CLOUD_TOKEN = '8e34e01b502a43c68fb0bb9ba2956df5'
# CLOUD_URL = f"https://oauth.yandex.ru/authorize?response_type=token&client_id={CLOUD_TOKEN}"
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = 'y0_AgAAAAAntKPVAAqnjgAAAADvHae-eQmDRNXeThaqoPlbkr24VwMpuXY'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}



def update_emb(TOKEN):
    # в директории Images хранятся папки со всеми изображениями
    load_dirs(TOKEN)
    imagePaths = list(paths.list_images('Images'))
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
        # loop over the encodings
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)
    # сохраним эмбеддинги вместе с их именами в формате словаря
    data = {"encodings": knownEncodings, "names": knownNames}
    # для сохранения данных в файл используем метод pickle
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()


def search(path):
    # find path of xml file containing haarcascade file
    cascPathface = os.path.dirname(
        cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())
    # Find path to the image you want to detect face and pass it here
    image = cv2.imread(path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # convert image to Greyscale for haarcascade
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(60, 60),
                                         flags=cv2.CASCADE_SCALE_IMAGE)

    # the facial embeddings for face in input
    encodings = face_recognition.face_encodings(rgb)
    names = []
    # loop over the facial embeddings incase
    # we have multiple embeddings for multiple fcaes
    for encoding in encodings:
        # Compare encodings with encodings in data["encodings"]
        # Matches contain array with boolean values and True for the embeddings it matches closely
        # and False for rest
        matches = face_recognition.compare_faces(data["encodings"],
                                                 encoding)
        # set name =inknown if no encoding matches
        name = "Unknown"
        # check to see if we have found a match
        if True in matches:
            # Find positions at which we get True and store them
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                # Check the names at respective indexes we stored in matchedIdxs
                name = data["names"][i]
                # increase count for the name we got
                counts[name] = counts.get(name, 0) + 1
                # set name which has highest count
                name = max(counts, key=counts.get)

            # update the list of names
            names.append(name)
            # loop over the recognized faces
            return names

