from flask import render_template, redirect, url_for, flash, request
from ERP import app, database, bcrypt, login_manager
from ERP.forms import FormCriarConta
from ERP.models import Usuarios
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/criarconta')
def criar_conta():
    form_criar_conta = FormCriarConta()
    if form_criar_conta.validate_on_submit():
        senha_crip = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuarios(username=form_criar_conta.username.data,
                          senha=senha_crip)
        database.session.add(usuario)
        database.session.commit()
        flash(f"Conta criada para: {form_criar_conta.username.data}!", 'alert-success')
        return redirect(url_for('home'))
    return render_template('criar_conta.html', form_criar_conta=form_criar_conta)
