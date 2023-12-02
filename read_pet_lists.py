import os


def read_values_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return None

    with open(file_path, 'r') as file:
        values = [line.strip() for line in file.readlines()]

    return values


def read_pet_lists():
    cats_list = read_values_from_file('categories_names/cats_list.txt')
    dogs_list = read_values_from_file('categories_names/dogs_list.txt')
    return cats_list, dogs_list
