from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- Функции для работы с базой данных ---

def init_db():
    """Создает таблицу tasks, если её нет"""
    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    conn.commit()
    conn.close()

def get_all_tasks():
    """Возвращает все задачи из БД"""
    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, created, status FROM tasks ORDER BY created DESC")
    tasks = cur.fetchall()
    conn.close()
    # Преобразуем результат в список словарей для удобства в шаблоне
    task_list = []
    for task in tasks:
        task_list.append({
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'created': task[3],
            'status': task[4]
        })
    return task_list

def add_task_to_db(title, description):
    """Добавляет новую задачу"""
    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    conn.close()

def delete_task_from_db(task_id):
    """Удаляет задачу по id"""
    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def complete_task_in_db(task_id):
    """Отмечает задачу как выполненную"""
    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# --- Маршруты (страницы) веб-приложения ---

@app.route('/')
def index():
    """Главная страница со списком задач"""
    tasks = get_all_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Добавляет задачу из формы"""
    title = request.form.get('title')
    description = request.form.get('description')
    if title:  # Проверяем, что название не пустое
        add_task_to_db(title, description)
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    """Отмечает задачу выполненной"""
    complete_task_in_db(task_id)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Удаляет задачу"""
    delete_task_from_db(task_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)