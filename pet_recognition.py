from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions
import numpy as np
from read_pet_lists import read_pet_lists

model = VGG16(weights='imagenet')

cats_list, dogs_list = read_pet_lists()

# если узнало одного из питомцев пользователя - True, порода; если не узнало - False, порода; если не распознала питомцев - None


def predict_pet(image_path, user_cat='', user_dog=''):
    img_path = image_path
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    predictions = model.predict(x)
    preds = decode_predictions(predictions, top=3)[0]

    predictions = [preds[0][1], preds[1][1], preds[2][1]]

    print(predictions)

    for i in predictions:
        if i == user_cat or i == user_dog:
            return True, i
    for i in predictions:
        if i in cats_list or i in dogs_list:
            return False, i
    return None
