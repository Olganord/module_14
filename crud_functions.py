import sqlite3


def initiate_db():
    # Подключаемся к базе данных (или создаем её, если не существует)
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # SQL запрос для создания таблицы Products
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    ''')



    for i in range(1, 5):
        cursor.execute('INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
            (f'Продукт{i}', f'Описание{i}', i * 100)
                      )

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def get_all_products():
    # Подключаемся к базе данных
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # SQL запрос для получения всех записей из таблицы Products
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()


    # Закрываем соединение
    conn.close()

    return products
