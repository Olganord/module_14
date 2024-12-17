from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *
import logging



logging.basicConfig(level=logging.INFO)
api = '***'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Создаём клавиатуру
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_buy = KeyboardButton('Купить')
button_info = KeyboardButton('Информация')
keyboard.add(button_calculate, button_info)
keyboard.row(button_buy)

kb = InlineKeyboardMarkup()
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb.row(button, button2)

inline_menu = InlineKeyboardMarkup()
button3 = InlineKeyboardButton(text='Продукт1', callback_data='product_buying')
button4 = InlineKeyboardButton(text='Продукт2', callback_data='product_buying')
button5 = InlineKeyboardButton(text='Продукт3', callback_data='product_buying')
button6 = InlineKeyboardButton(text='Продукт4', callback_data='product_buying')
inline_menu.row(button3, button4, button5, button6)


initiate_db()
products = get_all_products()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer(
        "Привет! Я бот, помогающий твоему здоровью", reply_markup=keyboard)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Чтобы начать, нажми кнопку "Рассчитать".')


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for product in products:
        id_, title, description, price = product
        # img_path = f'_photo/{id_}.jpg'
        with open(f'_photo/Продукт{id_}.jpg', 'rb') as img:
            await message.answer_photo(img, caption=f'Название: {title} | Описание: {description} | Цена: {price}p',
                                       reply_markup=inline_menu)
    await message.answer('Выберите продукт для покупки: ', reply_markup=inline_menu)



@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.message_handler(state=UserState.age)
async def process_age(message, state):
    try:
        age = int(message.text)
        if age < 1 or age > 100:
            await message.answer('Возраст должен быть положительным числом от 1 до 100 лет.')
            return

        async with state.proxy() as data:
            data["age"] = age

        await message.answer('Введите свой рост (в см):')
        await UserState.next()

    except ValueError:
        await message.answer('Пожалуйста, введите число.')


@dp.message_handler(state=UserState.growth)
async def process_growth(message, state):
    try:
        growth = int(message.text)
        if growth <= 0:
            await message.answer('Рост должен быть положительным числом.')
            return

        async with state.proxy() as data:
            data['growth'] = growth

        await message.answer('Введите свой вес (в кг):')
        await UserState.next()

    except ValueError:
        await message.answer('Пожалуйста, введите число.')


@dp.message_handler(state=UserState.weight)
async def process_weight(message, state):
    try:
        weight = int(message.text)
        if weight <= 0:
            await message.answer('Вес должен быть положительным числом.')
            return

        async with state.proxy() as data:
            data['weight'] = weight

        # Рассчитываем норму калорий
        age = data['age']
        growth = data['growth']
        weight = data['weight']
        calories_norm = int(10 * weight + 6.25 * growth - 5 * age - 161)

        await message.answer(f'Ваша норма калорий: {calories_norm}')
        await state.finish()

    except ValueError:
        await message.answer('Пожалуйста, введите число.')


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
