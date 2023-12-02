from db import get_user_pets, add_user_pet
from pet_recognition import predict_pet
from read_pet_lists import *


cats_list, dogs_list = read_pet_lists()
# return: если питомец найден - True и породу питомца, если найден впервые - False и породу питомца, если не совпало - False, None, если не найден - None


def search_pet(file_path, tg_id):
    pets = get_user_pets(tg_id)
    cat = pets[0]
    dog = pets[1]
    res = predict_pet(file_path)

    # если питомец на фото не найден
    if res is None:
        return None

    flag = res[0]

    # порода питомца на фото
    pet = res[1]

    # если нашло и питомец совпал с пользовательским
    if flag:
        return True, pet
    # если нашло, но питомец не совпал
    else:
        if ((dog is None or dog == '') and pet in dogs_list) or ((cat is None or cat == '') and pet in cats_list):
            add_user_pet(tg_id, pet)
            return False, pet
        return False, None
