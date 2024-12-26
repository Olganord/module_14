import sqlite3

def initiate_db():
    # Подключение к базе данных (создание новой базы, если она не существует)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Создание таблицы Products, если она ещё не создана
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    ''')

    # Заполнение данными (если таблица пустая)
    cursor.execute('SELECT COUNT(*) FROM Products')
    count = cursor.fetchone()[0]
    if count == 0:
        for i in range(1, 5):
            cursor.execute('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
                           (f'Продукт{i}', f'Описание{i}', i * 100))

    # Создание таблицы Users, если она ещё не создана
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL DEFAULT 1000
    )
    ''')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()

def get_all_products():
    # Подключение к базе данных
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Получение всех записей из таблицы Products
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()

    # Закрытие соединения
    conn.close()

    return products

def add_user(username, email, age):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Проверка существования пользователя по имени
    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()

    if existing_user is None:
        # Вставка нового пользователя
        cursor.execute('''
        INSERT INTO Users (username, email, age, balance) 
        VALUES (?, ?, ?, ?)''', (username, email, age, 1000))
        conn.commit()
    else:
        print(f"Пользователь с именем '{username}' уже существует.")

    conn.close()

def is_included(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()

    return user is not None
