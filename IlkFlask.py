# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, flash, redirect, g, url_for, session
import sqlite3, os

DATABASE = os.path.dirname(__file__) + '/database.db'

app = Flask(__name__)
app.secret_key = 'abc'

def db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS post (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT, created TEXT)")
    return db

def checkLogin():
    if 'username' in session:
        return True
    else:
        flash("Bu sayfada işlem yapabilmek için giriş yapmanız gerekiyor")
        return False

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    c = db().cursor()
    c.execute("SELECT * FROM post ORDER BY created DESC")
    return render_template('index.html', posts=c.fetchall())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            session['username'] = request.form['username']
            flash('Kullanıcı girişi başarıyla tamamlanmıştır')
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı ya da şifreniz yalnış yeniden deneyin')
            return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Çıkış başarıyla tamamlandı")
    return redirect(url_for('index'))

@app.route('/read/<int:id>')
def read(id):
    c = db().cursor()
    c.execute("SELECT * FROM post WHERE id=?", [id])
    return render_template('read.html', post=c.fetchone())

@app.route('/create', methods=['GET', 'POST'])
def create():
    if not checkLogin():
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        if request.form['title'] == '':
            flash("Başlık alanını doldurunuz")
            return redirect(url_for('create'))
        c = db().cursor()
        c.execute("INSERT INTO post (title, body, created) VALUES (?,?,?)", (request.form['title'], request.form['body'], request.form['created']))
        db().commit()
        flash("Gönderi başarıyla eklenmiştir")
        return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if not checkLogin():
        return redirect(url_for('login'))

    if request.method == 'GET':
        c = db().cursor()
        c.execute("SELECT * FROM post WHERE id=?", [id])
        return render_template('create.html', post=c.fetchone())
    elif request.method == 'POST':
        if request.form['title'] == '':
            flash("Lütfen başlık alanını doldurunuz")
            return redirect(url_for('update', id=id))
        c = db().cursor()
        c.execute("UPDATE post SET title=?, body=?, created=? WHERE id=?", (request.form['title'], request.form['body'], request.form['created'], id))
        db().commit()
        flash("Gönderi başarıyla düzenlenmiştir")
        return redirect(url_for('read', id=id))

@app.route('/delete/<int:id>')
def delete(id):
    if not checkLogin():
        return redirect(url_for('login'))

    c = db().cursor()
    c.execute("DELETE FROM post WHERE id=?", [id])
    db().commit()
    flash("Gönderi başarıyla silinmiştir")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
