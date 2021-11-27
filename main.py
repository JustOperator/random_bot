from aiogram import *
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import time
import random
from environs import Env

env = Env()
env.read_env()

TOKEN = env.str('BOT_TOKEN')


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Test(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()

@dp.message_handler(commands=['start'])
async def start_func(message: types.Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id, text='Привет.\nНапиши /help, чтобы узнать поглучить инструкции!')

@dp.message_handler(commands=['help'])
async def instruction(message: types.Message):
    await message.answer('Короче, просто рандомайзер. Сейчас надо будет ввести /random и выбрать диапозон и время генерации) ')

@dp.message_handler(commands=['random'])
async def rand(message: types.Message):
    await message.answer('Введи диапозон от a до b от меньшего к большему.\nВ формате: a b')
    print(message.text)
    await Test.Q1.set()


@dp.message_handler(state=Test.Q1)
async def rand2(message: types.Message, state=FSMContext):
    await message.answer('Введи время (в секундах), за которое произойдет генерация числа. \n'
                         'Извиняюсь, но присутствует задержка, примерно несколько секунд, учитывайте это!')
    await state.update_data(message_diap=message.text)
    await Test.Q2.set()

@dp.message_handler(state=Test.Q2)
async def rand3(message: types.Message, state=FSMContext):
    await state.update_data(message_time=int(message.text))
    data = await  state.get_data()
    message_diap = data.get("message_diap")
    message_time = int(message.text)
    diap_list = message_diap.split(' ')
    first_diap = int(diap_list[0])
    second_diap = int(diap_list[1])
    answer = random.randint(first_diap, second_diap)
    await message.answer(text=f'*{str(answer)}*', parse_mode= 'Markdown')
    for i in range(message_time * 5):
        time.sleep(0.2)
        answer = random.randint(first_diap, second_diap)
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 1, text=f'*{str(answer)}*', parse_mode= 'Markdown')
    await bot.send_message(chat_id=message.chat.id, text='Готово!')
    await state.reset_state()

executor.start_polling(dp)