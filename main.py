import io
import os
import shutil

import requests
from aiogram import Bot, Dispatcher, types, executor
from PIL import Image
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state, Text
from aiogram.dispatcher.filters.state import StatesGroup, State
import random
from face_analysis import search, update_emb, fast_umdate_emb, create_emb
from texts import *
from add_token import add_token
# from detect_pet import search_pet
from db import *

TOKEN_ID = "6497123928:AAE_TTI7TKoI9iB1W1Ys_1NuEJtKs9wSQSk"
bot = Bot(token=TOKEN_ID)
dp = Dispatcher(bot, storage=MemoryStorage())
CLOUD_TOKEN = '8e34e01b502a43c68fb0bb9ba2956df5'
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = ''
all_headers = {}
types_acc = {}
URI_INFO = f'https://api.telegram.org/bot{TOKEN_ID}/getFile?file_id=AgACAgIAAxkBAANYZSBoUZeuyA1XuR4JfzVLgbWQ4mQAAvnPMRsQEgABSbK7DYRZJAwBAQADAgADbQADMAQ'
URI = f'https://api.telegram.org/file/bot{TOKEN_ID}/'


class Form(StatesGroup):
    login = State()
    code_ind = State()
    code_fam = State()


class LoadIm(StatesGroup):
    path = State()


class LoadIm1(StatesGroup):
    path = State()


class LoadIm2(StatesGroup):
    path = State()


class Output(StatesGroup):
    path = State()


def create_folder(path, tg_id):
    """Создание папки"""
    requests.put(f'{URL}?path=photos/{path}', headers=all_headers[tg_id])


def upload_file(path, tg_id, name, replace=False):
    """Загрузка файла.
    name: Название фото
    path: Папка на диске
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'{URL}/upload?path=photos/{path}/{name}.png&overwrite={replace}',
                       headers=all_headers[tg_id]).json()
    with open(f'Images_{tg_id}/{name}.png', 'rb') as f:
        try:
            requests.put(res['href'], files={'file': f})
        except KeyError:
            print(res)


@dp.message_handler(commands=['start'], state=None)
async def start(message: types.Message):
    tg_id = message.from_user.id
    types_acc[tg_id] = 1
    if os.path.exists(f'Images_{tg_id}/'):
        shutil.rmtree(f"Images_{tg_id}/")
    os.mkdir(f"Images_{tg_id}/")
    print(tg_id)
    if get_token_by_tg_id(tg_id):
        TOKEN = get_token_by_tg_id(tg_id)
        all_headers[tg_id] = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        all_headers[tg_id]["Authorization"] = f'OAuth {TOKEN}'
        await message.answer(TOKEN)
    else:
        await message.answer(WELCOME)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Вход в семейный аккаунт", "Регистрация семейного аккаунта", "Индивидуальный аккаунт"]
        keyboard.add(*buttons)
        await message.answer(PUSH, reply_markup=keyboard)

        @dp.message_handler(Text(equals="Регистрация семейного аккаунта"))
        async def fam(message: types.Message):
            await message.answer(IND)
            await message.answer(URL_TXT)
            await Form.code_fam.set()

            @dp.message_handler(state=Form.code_fam)
            async def text(message: types.Message, state: FSMContext):
                code = message.text
                TOKEN = add_token(code)
                tg_id = message.from_user.id
                all_headers[tg_id] = {'Content-Type': 'application/json', 'Accept': 'application/json'}
                all_headers[tg_id]["Authorization"] = f'OAuth {TOKEN}'
                await message.answer(TOKEN)
                key = ''
                for i in range(16):
                    key += str(random.randint(0, 9))
                key += str(message.from_user.id)
                await message.answer(FAM_REG)
                await message.answer(key)
                tg_id = message.from_user.id
                add_main_family_user(tg_id, TOKEN, key)
                requests.put(f'{URL}?path=photos', headers=all_headers[tg_id])
                await message.answer('Успешно')
                await state.finish()

        @dp.message_handler(Text(equals="Вход в семейный аккаунт"))
        async def fam(message: types.Message):
            await message.answer('Для входа в семейный аккаунт введите серетный ключ')
            await Form.login.set()

        @dp.message_handler(state=Form.login)
        async def text(message: types.Message, state: FSMContext):
            tg_id = message.from_user.id
            secret_key = message.text
            add_other_family_user(tg_id, secret_key)
            TOKEN = get_token_by_tg_id(tg_id)
            all_headers[tg_id] = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            all_headers[tg_id]["Authorization"] = f'OAuth {TOKEN}'
            await message.answer('Успешно')
            await state.finish()

        @dp.message_handler(Text(equals="Индивидуальный аккаунт"))
        async def individual(message: types.Message):
            await message.answer(IND)
            await message.answer(URL_TXT)
            await Form.code_ind.set()

        @dp.message_handler(state=Form.code_ind)
        async def text(message: types.Message, state: FSMContext):
            code = message.text
            TOKEN = add_token(code)
            tg_id = message.from_user.id
            all_headers[tg_id] = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            all_headers[tg_id]["Authorization"] = f'OAuth {TOKEN}'
            '''' добвавить бд'''
            tg_id = message.from_user.id
            add_solo_user(tg_id, TOKEN)
            requests.put(f'{URL}?path=photos', headers=all_headers[tg_id])
            update_emb(TOKEN, tg_id)
            await message.answer('Успешно')
            await state.finish()


@dp.message_handler(commands=['sort_image'])
async def load(message: types.Message):
    tg_id = message.from_user.id
    if not os.path.exists(f"face_enc_{tg_id}"):
        update_emb(TOKEN, tg_id)
    if not os.path.exists(f"Images_{tg_id}/"):
        os.mkdir(f"Images_{tg_id}/")
    global path_flag
    '''было бы непохо потом переписать на state'''
    path_flag = False
    await LoadIm.path.set()
    await message.answer("Отправьте фотографии. Для остановки загрузки фотографий напишите /stop")

    @dp.message_handler(commands=['stop'], state=LoadIm.path)
    async def stop(message: types.Message, state: FSMContext):
        await state.finish()
        tg_id = message.from_user.id
        shutil.rmtree(f"Images_{tg_id}/")
        print("Функция завершена")

    @dp.message_handler(content_types=['text'], state=LoadIm.path)
    async def name(message: types.Message):
        global name
        if path_flag:
            path = message.text
            tg_id = message.from_user.id
            create_folder(path, tg_id)
            upload_file(path, tg_id, name)
            fast_umdate_emb(f'Images_{tg_id}/{name}.png', path, tg_id)
            os.remove(f'Images_{tg_id}/{name}.png')
            await message.answer(f'Сохранение фото в папку "{path}"')

    @dp.message_handler(content_types=['photo'], state=LoadIm.path)
    async def process_photo(message: types.Message):
        global name, path_flag
        file_id = message.photo[-1]["file_id"]
        URI_INFO = f'https://api.telegram.org/bot{TOKEN_ID}/getFile?file_id=' + file_id
        resp = requests.get(URI_INFO)
        img_path = resp.json()['result']['file_path']
        img = requests.get(URI + img_path)
        img = Image.open(io.BytesIO(img.content))
        tg_id = message.from_user.id
        name = str(tg_id) + str(random.randint(0, 1000000))
        print(name)
        img.save(f'Images_{tg_id}/{name}.png', format="PNG")
        img.close()
        tg_id = message.from_user.id
        pathes = search(f'Images_{tg_id}/{name}.png', tg_id)

        # # pet_search_result = search_pet(f'Images/{name}.png', tg_id)
        # pet_flag = pet_search_result[0]
        # pet_flag = pet_search_result[0]
        # pet_type = pet_search_result[1]
        #
        # if pet_search_result is not None:
        #     if pet_flag:
        #         upload_file(pet_type, tg_id, name)
        #     else:
        #         if pet_type is not None:
        #             create_folder(pet_type, tg_id)
        #             upload_file(pet_type, tg_id, name)

        print(pathes)
        if pathes:
            for path in pathes:
                upload_file(path, tg_id, name)
            os.remove(f'Images_{tg_id}/{name}.png')
            await message.answer(f'Сохранение фото в папку "{path}"')
        else:
            await message.answer(
                'Данный человек не найден в базе данных, пожалуйста, введите название папки для этого человека на латинице')
            path_flag = True


@dp.message_handler(commands=['load_image'])
async def load_w_s(message: types.Message):
    tg_id = message.from_user.id
    if not os.path.exists(f"Images_{tg_id}/"):
        os.mkdir(f"Images_{tg_id}/")
    await LoadIm1.path.set()
    await message.answer(WITOUT_AI)

    @dp.message_handler(commands=['stop'], state=LoadIm1.path)
    async def stop(message: types.Message, state: FSMContext):
        await state.finish()
        print("Функция завершена")

    @dp.message_handler(content_types=['text'], state=LoadIm1.path)
    async def name_path(message: types.Message):
        path = message.text

        @dp.message_handler(content_types=['photo'], state=LoadIm1.path)
        async def name_path(message: types.Message):
            file_id = message.photo[-1]["file_id"]
            tg_id = message.from_user.id
            URI_INFO = f'https://api.telegram.org/bot{TOKEN_ID}/getFile?file_id=' + file_id
            resp = requests.get(URI_INFO)
            img_path = resp.json()['result']['file_path']
            img = requests.get(URI + img_path)
            res = requests.get(f'{URL}/upload?path={path}/{tg_id}{random.randint(0, 1000000)}.png&overwrite=False',
                               headers=all_headers[tg_id]).json()
            print(res.keys())
            if "error" in res.keys():
                requests.put(f'{URL}?path={path}', headers=all_headers[tg_id])
                res = requests.get(f'{URL}/upload?path={path}/{tg_id}{random.randint(0, 1000000)}.png&overwrite=False',
                                   headers=all_headers[tg_id]).json()
            requests.put(res['href'], files={'file': io.BytesIO(img.content)})
            await message.answer("Загрузка завершена")


@dp.message_handler(commands=['one_path_sort'])
async def load_w_s(message: types.Message):
    tg_id = message.from_user.id
    TOKEN = get_token_by_tg_id(tg_id)
    create_emb(TOKEN, tg_id)
    if not os.path.exists(f"Images_{tg_id}/"):
        os.mkdir(f"Images_{tg_id}/")
    await LoadIm2.path.set()
    await message.answer(SORT_ONE_PATH)

    @dp.message_handler(commands=['stop'], state=LoadIm2.path)
    async def stop(message: types.Message, state: FSMContext):
        await state.finish()
        print("Функция завершена")

@dp.message_handler(content_types=['photo'], state=LoadIm2.path)
async def name_path(message: types.Message):
    file_id = message.photo[-1]["file_id"]
    URI_INFO = f'https://api.telegram.org/bot{TOKEN_ID}/getFile?file_id=' + file_id
    resp = requests.get(URI_INFO)
    img_path = resp.json()['result']['file_path']
    img1 = requests.get(URI + img_path)
    img = Image.open(io.BytesIO(img1.content))
    tg_id = message.from_user.id
    name = str(tg_id) + str(random.randint(0, 1000000))
    print(1111111)
    img.save(f'Images_{tg_id}/{name}.png', format="PNG")
    img.close()
    pathes = "_".join(search(f'Images_{tg_id}/{name}.png', tg_id))
    if not pathes:
        await message.answer("Лицо не найдено. Ведите имя*")
        @dp.message_handler(content_types=['text'], state=LoadIm2.path)
        async def name_path(message: types.Message):
            path = message.text
            fast_umdate_emb(f'Images_{tg_id}/{name}.png', path, tg_id)
            pathes = "_".join(search(f'Images_{tg_id}/{name}.png', tg_id))
            os.remove(f'Images_{tg_id}/{name}.png')
            res = requests.get(
                f'{URL}/upload?path=sorted_photo/{pathes}_{tg_id}{random.randint(0, 1000000)}.png&overwrite=False',
                headers=all_headers[tg_id]).json()
            print(res.keys())
            if "error" in res.keys():
                requests.put(f'{URL}?path=sorted_photo', headers=all_headers[tg_id])
                res = requests.get(
                    f'{URL}/upload?path=sorted_photo/{pathes}_{tg_id}{random.randint(0, 1000000)}.png&overwrite=False',
                    headers=all_headers[tg_id]).json()
            requests.put(res['href'], files={'file': io.BytesIO(img1.content)})
            await message.answer("Загрузка завершена")
    else:
        os.remove(f'Images_{tg_id}/{name}.png')
        res = requests.get(
            f'{URL}/upload?path=sorted_photo/{pathes}_{tg_id}{random.randint(0, 1000000)}.png&overwrite=False',
            headers=all_headers[tg_id]).json()
        print(res.keys())
        if "error" in res.keys():
            requests.put(f'{URL}?path=sorted_photo', headers=all_headers[tg_id])
            res = requests.get(
                f'{URL}/upload?path=sorted_photo/{pathes}_{tg_id}{random.randint(0, 1000000)}.png&overwrite=False',
                headers=all_headers[tg_id]).json()
        requests.put(res['href'], files={'file': io.BytesIO(img1.content)})
        await message.answer("Загрузка завершена")


@dp.message_handler(commands=['output'])
async def load_w_s(message: types.Message):
    tg_id = message.from_user.id
    await Output.path.set()
    await message.answer(OUTPUT_MEESAGE)

    @dp.message_handler(content_types=['text'], state=Output.path)
    async def name_path(message: types.Message):
        path = message.text
        tg_id = message.from_user.id
        r = requests.get(f"{URL}?path=sorted_photo", headers=all_headers[tg_id]).json()
        for elem in r['_embedded']['items']:
            if path in elem["name"]:
                img = requests.get(f'{URL}/download?path=sorted_photo/{elem["name"]}', headers=all_headers[tg_id])
                img = img.json()['href']
                img = requests.get(img)
                img = io.BytesIO(img.content)
                await message.answer_photo(img)


if __name__ == "__main__":
    create_db()
    executor.start_polling(dp, skip_updates=True)
