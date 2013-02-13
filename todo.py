#encoding: utf-8
import sqlite3
from contextlib import closing
import hashlib
import json
from functools import wraps

from flask import Flask, render_template, g, request, session, flash, redirect, url_for, jsonify

app = Flask(__name__)
app.config.from_object('config')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def authenticate(username, password):
    q = "SELECT id FROM app_user WHERE username = ? AND password = ?;"
    c = g.db.cursor()
    c.execute(q, (username, hashlib.sha1(password).hexdigest()))
    row = c.fetchone()
    print username, password, hashlib.sha1(password).hexdigest(), row
    return row[0] if row else -1


def authenticate_api(api_key):
    q = "SELECT id FROM app_user WHERE api_key = ?;"
    c = g.db.cursor()
    c.execute(q, (api_key,))
    row = c.fetchone()
    print row
    return row[0] if row else -1


def apify(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'ApiKey' in request.headers:
            api_key = request.headers['ApiKey']
            session['user_id'] = authenticate_api(api_key)
        return f(*args, **kwargs)

    return decorated_function


def get_user(user_id):
    q = "SELECT id, username, password FROM app_user WHERE id = ?;"
    c = g.db.cursor()
    c.execute(q, (user_id,))
    row = c.fetchone()
    return dict(zip(['id', 'username', 'password'], row))


def get_todos(user_id):
    fields = ['id', 'text', 'done', 'priority']
    q = "SELECT %s FROM todo WHERE app_user = ?;" % ",".join(fields)
    c = g.db.cursor()
    c.execute(q, (user_id,))

    todos = []
    for row in c.fetchall():
        todo = dict(zip(fields, row))
        todo['done'] = True if todo['done'] == 1 else 0
        todos.append(todo)
    return todos


@app.route('/')
def todos():
    context = {'logged_in': session.get('logged_in', False), 'todos': []}
    if context['logged_in']:
        context['username'] = get_user(session['user_id'])['username']
        context['todos'] = json.dumps(get_todos(session['user_id']))
    return render_template('index.html', **context)


@app.route('/todo', methods=['GET'])
@apify
def list_todos():
    return jsonify(todos=get_todos(session.get('user_id', -1)))


@app.route('/todo', methods=['POST'])
@apify
def new_todo():
    c = g.db.cursor()
    todo_data = json.loads(request.data)
    fields = ['text', 'done', 'priority']
    q = "INSERT INTO todo(app_user, %s) VALUES (%d, %s)" % (
        ", ".join(fields), session['user_id'], ", ".join('?' for _ in fields)
    )
    c.execute(q, tuple(todo_data[f] for f in fields))
    g.db.commit()
    return jsonify(id=c.lastrowid, **todo_data)


@app.route('/todo/<todo_id>', methods=['GET'])
@apify
def get_todo(todo_id):
    c = g.db.cursor()
    fields = ['id', 'text', 'done', 'priority']
    q = "SELECT %s FROM todo WHERE id = ? and app_user = ?" % ",".join(fields)
    c.execute(q, (todo_id, session.get('user_id', -1)))
    row = c.fetchone()
    if row:
        return jsonify(**dict(zip(fields, row)))
    else:
        return jsonify({})


@app.route('/todo/<todo_id>', methods=['PUT'])
@apify
def update_todo(todo_id):
    c = g.db.cursor()
    todo_data = json.loads(request.data)

    fields = ['text', 'done', 'priority']
    q = "UPDATE todo SET %s WHERE id = ? and app_user = ?;" % ", ".join(
        ["%s=?" % f for f in fields if f in todo_data]
    )
    values = tuple([todo_data[f] for f in fields if f in todo_data])
    c.execute(q, values + (todo_id, session.get('user_id', -1)))
    g.db.commit()

    return jsonify(**todo_data)


@app.route('/todo/<todo_id>', methods=['DELETE'])
@apify
def delete_todo(todo_id):
    c = g.db.cursor()

    q = "DELETE FROM todo WHERE id = ? and app_user = ?;"
    c.execute(q, (todo_id, session.get('user_id', -1)))
    g.db.commit()

    return jsonify()


@app.route('/login', methods=['POST'])
def login():
    username, password = request.form['username'], request.form['password']
    todos = request.form.getlist('todos')
    user_id = authenticate(username, password)

    if user_id != -1:
        c = g.db.cursor()
        session['logged_in'] = True
        session['user_id'] = user_id

        # Loading todos
        fields = ['text', 'done', 'priority']
        q = "INSERT INTO todo(app_user, %s) VALUES (%d, %s)" % (
            ", ".join(fields), user_id, ", ".join('?' for _ in fields)
        )
        for todo in todos:
            data = json.loads(todo)
            c.execute(q, tuple(data[f] for f in fields))
        g.db.commit()
    else:
        flash(u"Wrong user or password")

    return redirect(url_for('todos'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('todos'))

if __name__ == '__main__':
    app.run()
