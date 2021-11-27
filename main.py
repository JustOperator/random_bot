from aiogram import *
from aiogram.dispatcher import FSMContext # для работы с стостояниями в функциях
from aiogram.dispatcher.filters.state import State, StatesGroup # импортируем машину состояний
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage # импортируем хранилище
import time
import random
from environs import Env # библиотека для импортирования токена бота из .env

env = Env()
env.read_env()   # чтение .env

TOKEN = env.str('BOT_TOKEN') # чтение переменной BOT_TOKEN


bot = Bot(token=TOKEN)  # Создание бота
dp = Dispatcher(bot, storage=MemoryStorage())  # Создание диспетчера и настройка хранилища

class state_func(StatesGroup): # Машина состояний
    diap = State()
    time = State()

@dp.message_handler(commands=['start']) # фильтр на комманду /start
async def start_func(message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id, text='Привет.\nНапиши /help, чтобы узнать поглучить инструкции!')

@dp.message_handler(commands=['help']) # фильтр на комманду /help
async def instruction(message: types.Message):
    await message.answer('Короче, просто рандомайзер. Сейчас надо будет ввести /random и выбрать диапозон и время генерации) ')

@dp.message_handler(commands=['random']) # фильтр на комманду /random
async def diap(message: types.Message):
    await message.answer('Введи диапозон от a до b от меньшего к большему.\nВ формате: a b')
    print(message.text)
    await state_func.diap.set()  # установка состояния


@dp.message_handler(state=state_func.diap)  # филтьтр на состояние
async def time(message: types.Message, state=FSMContext):  # состояние функции
    await message.answer('Введи время (в секундах), за которое произойдет генерация числа. \n'
                         'Извиняюсь, но присутствует задержка, примерно несколько секунд, учитывайте это!')
    await state.update_data(message_diap=message.text)  # сохранение переменной в состояние
    await state_func.time.set()  # установка состояния

@dp.message_handler(state=state_func.time)  # фильтр на состояние
async def processing(message: types.Message, state=FSMContext): # состояние функции
    data = await state.get_data() # получаем данные из состояния
    message_diap = data.get("message_diap") # достаем переменную из состояния
    message_time = int(message.text) # превращаем сообщение пользователя в число
    diap_list = message_diap.split(' ') # создаем список из сообщения пользователя через пробел
    first_diap = int(diap_list[0])
    second_diap = int(diap_list[1])
    answer = random.randint(first_diap, second_diap) # генерируем рандомное число из чисел заданных пользователем
    await message.answer(text=f'*{str(answer)}*', parse_mode= 'Markdown') # отправляем пользователю число
    for i in range(message_time * 5):
        time.sleep(0.2) # пауза 0.2 секунды
        answer = random.randint(first_diap, second_diap) # снова генерируем число
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 1, text=f'*{str(answer)}*', parse_mode= 'Markdown') # меняем старое число на новое
    await bot.send_message(chat_id=message.chat.id, text='Готово!') # по окончанию цикла отправляем пользователю сообщение
    await state.reset_state() # удаляем состояние

executor.start_polling(dp)