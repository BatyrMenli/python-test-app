from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_for_session'
DATABASE = 'users.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return render_template('index.html', username=user['username'])
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        error = None
        
        if not username:
            error = 'Введите имя пользователя'
        elif not password:
            error = 'Введите пароль'
        elif password != confirm_password:
            error = 'Пароли не совпадают'
        elif len(password) < 4:
            error = 'Пароль должен быть не менее 4 символов'
        
        if error is None:
            conn = get_db()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'Пользователь с таким именем уже существует'
            conn.close()
        
        return render_template('register.html', error=error)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        error = None
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user is None:
            error = 'Неверное имя пользователя'
        elif not check_password_hash(user['password'], password):
            error = 'Неверный пароль'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/tests')
@login_required
def tests():
    return render_template('tests.html')

@app.route('/test/python')
@login_required
def test_python():
    all_questions = [
        # 1-10
        {'id': 1, 'text': 'Как вывести текст на экран в Python?', 'options': ['print()', 'display()', 'show()', 'output()'], 'correct': 0},
        {'id': 2, 'text': 'Какой тип данных используется для хранения текста?', 'options': ['int', 'string', 'str', 'text'], 'correct': 2},
        {'id': 3, 'text': 'Как создать список в Python?', 'options': ['list = [1, 2, 3]', 'list = (1, 2, 3)', 'list = {1, 2, 3}', 'list = <1, 2, 3>'], 'correct': 0},
        {'id': 4, 'text': 'Какой оператор используется для сравнения двух значений?', 'options': ['=', '==', '===', '!='], 'correct': 1},
        {'id': 5, 'text': 'Как создать словарь в Python?', 'options': ['dict = [1, 2, 3]', 'dict = {"key": "value"}', 'dict = (1, 2, 3)', 'dict = {1, 2, 3}'], 'correct': 1},
        {'id': 6, 'text': 'Какое ключевое слово используется для создания функции?', 'options': ['function', 'def', 'func', 'define'], 'correct': 1},
        {'id': 7, 'text': 'Как получить длину списка?', 'options': ['size(list)', 'length(list)', 'len(list)', 'count(list)'], 'correct': 2},
        {'id': 8, 'text': 'Какое условие используется для проверки "если"?', 'options': ['when', 'if', 'case', 'check'], 'correct': 1},
        {'id': 9, 'text': 'Как повторить действие несколько раз?', 'options': ['repeat', 'for', 'loop', 'do'], 'correct': 1},
        {'id': 10, 'text': 'Что вернет выражение: 5 + 3 * 2?', 'options': ['16', '11', '13', '20'], 'correct': 2},
        # 11-20
        {'id': 11, 'text': 'Какое значение вернет: len("hello")?', 'options': ['4', '5', '6', 'hello'], 'correct': 1},
        {'id': 12, 'text': 'Как получить первый элемент списка?', 'options': ['list[1]', 'list[0]', 'list.first()', 'list.get(0)'], 'correct': 1},
        {'id': 13, 'text': 'Что такое переменная?', 'options': ['функция', 'контейнер для значения', 'список', 'цикл'], 'correct': 1},
        {'id': 14, 'text': 'Какой результат: "3" + "5"?', 'options': ['8', '"35"', '35', 'ошибка'], 'correct': 1},
        {'id': 15, 'text': 'Как добавить элемент в список?', 'options': ['list.add()', 'list.append()', 'list.push()', 'list.insert()'], 'correct': 1},
        {'id': 16, 'text': 'Что будет при делении: 7 / 2?', 'options': ['3', '3.5', '2', 'ошибка'], 'correct': 1},
        {'id': 17, 'text': 'Как получить остаток от деления?', 'options': ['/', '//', '%', '**'], 'correct': 2},
        {'id': 18, 'text': 'Какой оператор для возведения в степень?', 'options': ['**', '^', 'pow', '^^'], 'correct': 0},
        {'id': 19, 'text': 'Как создать пустой список?', 'options': ['list()', '[]', 'list([])', 'new list()'], 'correct': 1},
        {'id': 20, 'text': 'Что вернет: "Python"[0]?', 'options': ['Python', '"P"', 'P', 'ошибка'], 'correct': 2},
        # 21-30
        {'id': 21, 'text': 'Какое значение: not True?', 'options': ['True', 'False', 'None', 'ошибка'], 'correct': 1},
        {'id': 22, 'text': 'Что вернет: 10 > 5?', 'options': ['True', 'False', '5', 'ошибка'], 'correct': 0},
        {'id': 23, 'text': 'Как проверить, существует ли ключ в словаре?', 'options': ['if key in dict', 'if dict.has(key)', 'if key.exists()', 'if dict[key]'], 'correct': 0},
        {'id': 24, 'text': 'Что такое None?', 'options': ['число', 'текст', 'отсутствие значения', 'функция'], 'correct': 2},
        {'id': 25, 'text': 'Как получить значение по ключу из словаря?', 'options': ['dict.key', 'dict[key]', 'dict.get(key)', 'dict[key] и dict.get(key)'], 'correct': 3},
        {'id': 26, 'text': 'Что будет: "abc" * 3?', 'options': ['"abc"', '"abcabcabc"', '3', 'ошибка'], 'correct': 1},
        {'id': 27, 'text': 'Как проверить тип переменной?', 'options': ['var.type()', 'type(var)', 'var.getType()', 'typeof(var)'], 'correct': 1},
        {'id': 28, 'text': 'Какой результат: [1, 2] + [3, 4]?', 'options': ['[4, 6]', '[1, 2, 3, 4]', '[1, 2, [3, 4]]', 'ошибка'], 'correct': 1},
        {'id': 29, 'text': 'Как преобразовать строку в число?', 'options': ['number()', 'int()', 'to_int()', 'str()'], 'correct': 1},
        {'id': 30, 'text': 'Что вернет: sorted([3, 1, 2])?', 'options': ['[3, 1, 2]', '[1, 2, 3]', 'ошибка', '[2, 1, 3]'], 'correct': 1},
        # 31-40
        {'id': 31, 'text': 'Как использовать переменную в строке?', 'options': ['f"число = {x}"', '"число = " + x', 'format("число = {}", x)', 'все варианты'], 'correct': 3},
        {'id': 32, 'text': 'Что такое индекс?', 'options': ['функция', 'переменная', 'позиция элемента', 'оператор'], 'correct': 2},
        {'id': 33, 'text': 'Как удалить элемент из списка?', 'options': ['list.remove()', 'list.delete()', 'del list[]', 'list.remove() и del list[]'], 'correct': 3},
        {'id': 34, 'text': 'Что вернет: [1, 2, 3][1:3]?', 'options': ['[1, 2, 3]', '[2, 3]', '[2]', '[1, 2]'], 'correct': 1},
        {'id': 35, 'text': 'Какой результат: "hello".upper()?', 'options': ['hello', 'Hello', 'HELLO', 'hELLO'], 'correct': 2},
        {'id': 36, 'text': 'Как преобразовать список в строку?', 'options': ['list.join()', '", ".join(list)', 'str(list)', 'list.toString()'], 'correct': 1},
        {'id': 37, 'text': 'Что делает функция range()?', 'options': ['создает список чисел', 'проверяет диапазон', 'удаляет диапазон', 'ошибка'], 'correct': 0},
        {'id': 38, 'text': 'Как получить последний элемент списка?', 'options': ['list[len(list)]', 'list[-1]', 'list.last()', 'list[len(list)-1]'], 'correct': 1},
        {'id': 39, 'text': 'Что вернет: 2 ** 3?', 'options': ['6', '8', '5', '9'], 'correct': 1},
        {'id': 40, 'text': 'Как прочитать файл в Python?', 'options': ['open()', 'read()', 'file()', 'load()'], 'correct': 0},
        # 41-50
        {'id': 41, 'text': 'Что такое цикл while?', 'options': ['цикл для каждого элемента', 'цикл пока условие истинно', 'функция', 'оператор'], 'correct': 1},
        {'id': 42, 'text': 'Как выйти из цикла раньше?', 'options': ['exit()', 'break', 'return', 'stop()'], 'correct': 1},
        {'id': 43, 'text': 'Как пропустить итерацию цикла?', 'options': ['skip', 'continue', 'next', 'pass'], 'correct': 1},
        {'id': 44, 'text': 'Что вернет: len({})?', 'options': ['0', '1', 'ошибка', 'None'], 'correct': 0},
        {'id': 45, 'text': 'Как получить значения словаря?', 'options': ['dict.values()', 'dict.get_values()', 'values(dict)', 'dict.vals()'], 'correct': 0},
        {'id': 46, 'text': 'Как получить ключи словаря?', 'options': ['dict.keys()', 'dict.get_keys()', 'keys(dict)', 'dict.getKeys()'], 'correct': 0},
        {'id': 47, 'text': 'Что вернет: isinstance(5, int)?', 'options': ['5', 'False', 'True', 'int'], 'correct': 2},
        {'id': 48, 'text': 'Как округлить число?', 'options': ['round()', 'floor()', 'ceil()', 'int()'], 'correct': 0},
        {'id': 49, 'text': 'Что такое срез?', 'options': ['удаление', 'выделение части последовательности', 'копирование', 'вставка'], 'correct': 1},
        {'id': 50, 'text': 'Как создать кортеж?', 'options': ['tuple = (1, 2, 3)', 'tuple = [1, 2, 3]', 'tuple = {1, 2, 3}', 'tuple = 1, 2, 3'], 'correct': 0},
        # 51-60
        {'id': 51, 'text': 'Какое отличие списка от кортежа?', 'options': ['нет отличия', 'кортеж неизменяемый', 'список неизменяемый', 'разный синтаксис'], 'correct': 1},
        {'id': 52, 'text': 'Как сравнить две строки?', 'options': ['str1 == str2', 'str1.equals(str2)', 'compare(str1, str2)', 'str1 is str2'], 'correct': 0},
        {'id': 53, 'text': 'Что вернет: "abc" in "abcdef"?', 'options': ['False', 'True', '0', 'None'], 'correct': 1},
        {'id': 54, 'text': 'Как найти индекс элемента в списке?', 'options': ['list.find()', 'list.index()', 'list.search()', 'indexOf(list)'], 'correct': 1},
        {'id': 55, 'text': 'Что делает функция abs()?', 'options': ['абсолютное значение', 'сумма', 'произведение', 'вычитание'], 'correct': 0},
        {'id': 56, 'text': 'Как получить минимум из списка?', 'options': ['min(list)', 'list.min()', 'minimum(list)', 'list.minimum()'], 'correct': 0},
        {'id': 57, 'text': 'Как получить максимум из списка?', 'options': ['max(list)', 'list.max()', 'maximum(list)', 'list.maximum()'], 'correct': 0},
        {'id': 58, 'text': 'Как получить сумму элементов?', 'options': ['sum(list)', 'list.sum()', 'add(list)', 'list.add()'], 'correct': 0},
        {'id': 59, 'text': 'Что вернет: list(range(3))?', 'options': ['[0, 1, 2]', '[1, 2, 3]', '[0, 1, 2, 3]', '[3]'], 'correct': 0},
        {'id': 60, 'text': 'Как скопировать список?', 'options': ['list2 = list1', 'list2 = list1.copy()', 'list2 = list(list1)', 'все верно'], 'correct': 3},
        # 61-70
        {'id': 61, 'text': 'Что такое аргумент функции?', 'options': ['результат', 'входное значение', 'переменная', 'условие'], 'correct': 1},
        {'id': 62, 'text': 'Что делает return?', 'options': ['заканчивает программу', 'возвращает значение', 'повторяет код', 'удаляет переменную'], 'correct': 1},
        {'id': 63, 'text': 'Как задать значение по умолчанию?', 'options': ['def func(x=5):', 'def func(x:', 'def func(x:=5):', 'def func(x)=5:'], 'correct': 0},
        {'id': 64, 'text': 'Что такое *args?', 'options': ['одна переменная', 'несколько аргументов', 'строка', 'число'], 'correct': 1},
        {'id': 65, 'text': 'Что такое **kwargs?', 'options': ['список', 'словарь аргументов', 'кортеж', 'множество'], 'correct': 1},
        {'id': 66, 'text': 'Как получить остаток: 10 % 3?', 'options': ['3', '1', '7', 'ошибка'], 'correct': 1},
        {'id': 67, 'text': 'Что вернет: 10 // 3?', 'options': ['3', '3.333', '2', '1'], 'correct': 0},
        {'id': 68, 'text': 'Как проверить пустой ли список?', 'options': ['if list:', 'if len(list) == 0:', 'if not list:', 'все верно'], 'correct': 3},
        {'id': 69, 'text': 'Как объединить две строки?', 'options': ['str1 + str2', 'str1.concat(str2)', 'concat(str1, str2)', 'str1.add(str2)'], 'correct': 0},
        {'id': 70, 'text': 'Что вернет: str.split()?', 'options': ['строку', 'список слов', 'число', 'ошибка'], 'correct': 1},
        # 71-80
        {'id': 71, 'text': 'Как заменить часть строки?', 'options': ['str.replace()', 'str.sub()', 'str.change()', 'substitute()'], 'correct': 0},
        {'id': 72, 'text': 'Что вернет: "123".isdigit()?', 'options': ['False', 'True', '123', 'ошибка'], 'correct': 1},
        {'id': 73, 'text': 'Как преобразовать в строку?', 'options': ['int()', 'str()', 'float()', 'string()'], 'correct': 1},
        {'id': 74, 'text': 'Как преобразовать в число с точкой?', 'options': ['int()', 'float()', 'double()', 'number()'], 'correct': 1},
        {'id': 75, 'text': 'Что такое комментарий?', 'options': ['код', 'объяснение кода', 'функция', 'переменная'], 'correct': 1},
        {'id': 76, 'text': 'Как написать комментарий?', 'options': ['//', '/*/', '#', '<!---->'], 'correct': 2},
        {'id': 77, 'text': 'Что вернет: len("")?', 'options': ['1', '0', 'ошибка', 'None'], 'correct': 1},
        {'id': 78, 'text': 'Как проверить четное ли число?', 'options': ['x % 2 == 0', 'x.isEven()', 'x / 2 == 0', 'even(x)'], 'correct': 0},
        {'id': 79, 'text': 'Как создать множество?', 'options': ['set = {1, 2, 3}', 'set = [1, 2, 3]', 'set = (1, 2, 3)', 'set()'], 'correct': 0},
        {'id': 80, 'text': 'Как добавить элемент в множество?', 'options': ['set.add()', 'set.append()', 'set.push()', 'set.insert()'], 'correct': 0},
        # 81-90
        {'id': 81, 'text': 'Как удалить элемент из множества?', 'options': ['set.remove()', 'set.discard()', 'set.pop()', 'все верно'], 'correct': 3},
        {'id': 82, 'text': 'Что вернет: {1, 2} | {2, 3}?', 'options': ['[1, 2, 3]', '{1, 2, 3}', '{2}', 'ошибка'], 'correct': 1},
        {'id': 83, 'text': 'Что вернет: {1, 2} & {2, 3}?', 'options': ['{1, 2, 3}', '{2}', 'ошибка', '{}'], 'correct': 1},
        {'id': 84, 'text': 'Как получить количество элементов?', 'options': ['count()', 'len()', 'size()', 'length()'], 'correct': 1},
        {'id': 85, 'text': 'Что такое лямбда функция?', 'options': ['циклю', 'безымянная функция', 'переменная', 'оператор'], 'correct': 1},
        {'id': 86, 'text': 'Как написать лямбду?', 'options': ['lambda x: x*2', 'func x: x*2', '=> x*2', 'lambda (x): x*2'], 'correct': 0},
        {'id': 87, 'text': 'Что такое map()?', 'options': ['карта', 'применение функции к элементам', 'поиск', 'сортировка'], 'correct': 1},
        {'id': 88, 'text': 'Что такое filter()?', 'options': ['фильтр изображения', 'выбор элементов по условию', 'удаление', 'сортировка'], 'correct': 1},
        {'id': 89, 'text': 'Как получить элемент по индексу?', 'options': ['list()', 'list[]', 'list.get()', 'get_element()'], 'correct': 1},
        {'id': 90, 'text': 'Что вернет: "hello"[1:4]?', 'options': ['"hello"', '"ell"', '"hell"', '"ello"'], 'correct': 1},
        # 91-100
        {'id': 91, 'text': 'Как конвертировать в логический тип?', 'options': ['bool()', 'boolean()', 'logical()', 'to_bool()'], 'correct': 0},
        {'id': 92, 'text': 'Что вернет: bool(0)?', 'options': ['True', 'False', '0', 'ошибка'], 'correct': 1},
        {'id': 93, 'text': 'Что вернет: bool("")?', 'options': ['True', 'False', '""', 'ошибка'], 'correct': 1},
        {'id': 94, 'text': 'Как получить тип переменной?', 'options': ['getType()', 'type()', 'var.type', 'typeof()'], 'correct': 1},
        {'id': 95, 'text': 'Что такое индексирование?', 'options': ['индекс', 'доступ элемента по позиции', 'сортировка', 'цикл'], 'correct': 1},
        {'id': 96, 'text': 'Как создать вложенный список?', 'options': ['[[1, 2], [3, 4]]', '[1, 2, 3, 4]', '[1, [2, 3], 4]', '[1, 2], [3, 4]'], 'correct': 0},
        {'id': 97, 'text': 'Как получить длину строки с пробелами?', 'options': ['не считает пробелы', 'считает пробелы', 'ошибка', 'None'], 'correct': 1},
        {'id': 98, 'text': 'Что вернет: "test".startswith("te")?', 'options': ['False', 'True', 'te', 'ошибка'], 'correct': 1},
        {'id': 99, 'text': 'Что вернет: "test".endswith("st")?', 'options': ['False', 'True', 'st', 'ошибка'], 'correct': 1},
        {'id': 100, 'text': 'Как получить случайное число?', 'options': ['random.random()', 'random.randint()', 'randint()', 'все верно'], 'correct': 3},
    ]
    
    # Выбираем случайные 15 вопросов
    selected_questions = random.sample(all_questions, 15)
    # Сортируем по ID для удобства
    selected_questions.sort(key=lambda x: x['id'])
    
    return render_template('test_python.html', questions=selected_questions)

@app.route('/test/python/submit', methods=['POST'])
@login_required
def test_python_submit():
    answers = request.form
    
    # Все 100 вопросов с правильными ответами
    all_questions = [
        {'id': 1, 'correct': 0}, {'id': 2, 'correct': 2}, {'id': 3, 'correct': 0},
        {'id': 4, 'correct': 1}, {'id': 5, 'correct': 1}, {'id': 6, 'correct': 1},
        {'id': 7, 'correct': 2}, {'id': 8, 'correct': 1}, {'id': 9, 'correct': 1},
        {'id': 10, 'correct': 2}, {'id': 11, 'correct': 1}, {'id': 12, 'correct': 1},
        {'id': 13, 'correct': 1}, {'id': 14, 'correct': 1}, {'id': 15, 'correct': 1},
        {'id': 16, 'correct': 1}, {'id': 17, 'correct': 2}, {'id': 18, 'correct': 0},
        {'id': 19, 'correct': 1}, {'id': 20, 'correct': 2}, {'id': 21, 'correct': 1},
        {'id': 22, 'correct': 0}, {'id': 23, 'correct': 0}, {'id': 24, 'correct': 2},
        {'id': 25, 'correct': 3}, {'id': 26, 'correct': 1}, {'id': 27, 'correct': 1},
        {'id': 28, 'correct': 1}, {'id': 29, 'correct': 1}, {'id': 30, 'correct': 1},
        {'id': 31, 'correct': 3}, {'id': 32, 'correct': 2}, {'id': 33, 'correct': 3},
        {'id': 34, 'correct': 1}, {'id': 35, 'correct': 2}, {'id': 36, 'correct': 1},
        {'id': 37, 'correct': 0}, {'id': 38, 'correct': 1}, {'id': 39, 'correct': 1},
        {'id': 40, 'correct': 0}, {'id': 41, 'correct': 1}, {'id': 42, 'correct': 1},
        {'id': 43, 'correct': 1}, {'id': 44, 'correct': 0}, {'id': 45, 'correct': 0},
        {'id': 46, 'correct': 0}, {'id': 47, 'correct': 2}, {'id': 48, 'correct': 0},
        {'id': 49, 'correct': 1}, {'id': 50, 'correct': 0}, {'id': 51, 'correct': 1},
        {'id': 52, 'correct': 0}, {'id': 53, 'correct': 1}, {'id': 54, 'correct': 1},
        {'id': 55, 'correct': 0}, {'id': 56, 'correct': 0}, {'id': 57, 'correct': 0},
        {'id': 58, 'correct': 0}, {'id': 59, 'correct': 0}, {'id': 60, 'correct': 3},
        {'id': 61, 'correct': 1}, {'id': 62, 'correct': 1}, {'id': 63, 'correct': 0},
        {'id': 64, 'correct': 1}, {'id': 65, 'correct': 1}, {'id': 66, 'correct': 1},
        {'id': 67, 'correct': 0}, {'id': 68, 'correct': 3}, {'id': 69, 'correct': 0},
        {'id': 70, 'correct': 1}, {'id': 71, 'correct': 0}, {'id': 72, 'correct': 1},
        {'id': 73, 'correct': 1}, {'id': 74, 'correct': 1}, {'id': 75, 'correct': 1},
        {'id': 76, 'correct': 2}, {'id': 77, 'correct': 1}, {'id': 78, 'correct': 0},
        {'id': 79, 'correct': 0}, {'id': 80, 'correct': 0}, {'id': 81, 'correct': 3},
        {'id': 82, 'correct': 1}, {'id': 83, 'correct': 1}, {'id': 84, 'correct': 1},
        {'id': 85, 'correct': 1}, {'id': 86, 'correct': 0}, {'id': 87, 'correct': 1},
        {'id': 88, 'correct': 1}, {'id': 89, 'correct': 1}, {'id': 90, 'correct': 1},
        {'id': 91, 'correct': 0}, {'id': 92, 'correct': 1}, {'id': 93, 'correct': 1},
        {'id': 94, 'correct': 1}, {'id': 95, 'correct': 1}, {'id': 96, 'correct': 0},
        {'id': 97, 'correct': 1}, {'id': 98, 'correct': 1}, {'id': 99, 'correct': 1},
        {'id': 100, 'correct': 3}
    ]
    
    score = 0
    answered = 0
    for q in all_questions:
        question_id = str(q['id'])
        if question_id in answers:
            answered += 1
            try:
                if int(answers[question_id]) == q['correct']:
                    score += 1
            except:
                pass
    
    percentage = (score / answered) * 100 if answered > 0 else 0
    return render_template('test_result.html', score=score, total=answered, percentage=percentage)

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
