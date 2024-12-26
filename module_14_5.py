from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *
import logging
import re

initiate_db()

logging.basicConfig(level=logging.INFO)
api = '***'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создаем клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_buy = KeyboardButton('Купить')
button_info = KeyboardButton('Информация')
button_reg = KeyboardButton('Регистрация')
keyboard.add(button_calculate, button_info, button_reg)
keyboard.row(button_buy)

kb = InlineKeyboardMarkup()
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb.row(button, button2)


def create_inline_menu(products):
    inline_menu = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for product in products:
        id_, title, _, _ = product
        button = InlineKeyboardButton(text=title, callback_data=f'product_{id_}')
        buttons.append(button)

    while len(buttons) > 0:
        row_buttons = [buttons.pop(0)] if len(buttons) % 2 != 0 else [buttons.pop(0), buttons.pop(0)]
        inline_menu.row(*row_buttons)

    return inline_menu


products = get_all_products()
inline_menu = create_inline_menu(products)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_message(message):
    await message.answer(
        "Привет! Я бот, помогающий твоему здоровью", reply_markup=keyboard)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Чтобы начать, нажмите кнопку "Рассчитать".')


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
        img_path = f'_photo/Продукт{id_}.jpg'
        with open(img_path, 'rb') as img:
            await message.answer_photo(img, caption=f'Название: {title}\nОписание: {description}\nЦена: {price}p.',
                                       reply_markup=inline_menu)
    await message.answer('Выберите продукт для покупки:', reply_markup=inline_menu)


@dp.callback_query_handler(lambda c: c.data.startswith('product'))
async def send_confirm_message(call):
    product_id = call.data.split('_')[1]
    product = next((p for p in products if str(p[0]) == product_id), None)
    if product:
        await call.message.answer(f'Вы успешно приобрели продукт "{product[1]}".')
    else:
        await call.message.answer('Ошибка обработки заказа.')
    await call.answer()


@dp.message_handler(state=UserState.age)
async def process_age(message, state: FSMContext):
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
        await message.answer('Пожалуйста, введите целое число.')


@dp.message_handler(state=UserState.growth)
async def process_growth(message, state: FSMContext):
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
        await message.answer('Пожалуйста, введите целое число.')


@dp.message_handler(state=UserState.weight)
async def process_weight(message, state: FSMContext):
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
        await message.answer('Пожалуйста, введите целое число.')


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


@dp.message_handler(lambda message: message.text == 'Регистрация')
async def sign_up(message: types.Message):
    await message.answer('Введите имя пользователя (латиницей):')
    await RegistrationState.username.set()


def validate_email(email):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return bool(re.fullmatch(pattern, email))


@dp.message_handler(state=RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    username = message.text
    if not is_included(username):
        await state.update_data(username=username)
        await message.answer('Введите свой email:')
        await RegistrationState.next()
    else:
        await message.answer('Пользователь с таким именем уже существует. Попробуйте другое.')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text
    if validate_email(email):
        await state.update_data(email=email)
        await message.answer('Введите свой возраст:')
        await RegistrationState.next()
    else:
        await message.answer('Неверный формат email. Пожалуйста, попробуйте снова.')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 18 or age > 100:
            await message.answer('Возраст должен быть между 18 и 100 годами.')
            return

        async with state.proxy() as data:
            username = data['username']
            email = data['email']

        # Добавляем пользователя в базу данных
        add_user(username, email, age)
        await message.answer('Регистрация прошла успешно!')


        # Завершаем состояния
        await state.finish()

    except ValueError:
        await message.answer('Возраст должен быть целым числом. Попробуйте еще раз')

@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
