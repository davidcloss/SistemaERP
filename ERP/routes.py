from flask import render_template, redirect, url_for, flash, request
from ERP import app, database, bcrypt, login_manager
from ERP.forms import FormCriarConta, FormLogin, FormCadastroCNPJ, FormCadastroEmpresa
from ERP.models import Usuarios, CadastroEmpresa, TiposCadastros, ClientesFornecedores
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

@app.route('/criarconta', methods=['GET', 'POST'])
def criar_conta():
    form_criar_conta = FormCriarConta()
    if form_criar_conta.validate_on_submit():
        senha_crip = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuarios(username=form_criar_conta.username.data,
                          senha=senha_crip,
                           acesso=form_criar_conta.acesso.data)
        database.session.add(usuario)
        database.session.commit()
        flash(f"Conta criada para: {form_criar_conta.username.data}!", 'alert-success')
        return redirect(url_for('home'))
    return render_template('criar_conta.html', form_criar_conta=form_criar_conta)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuarios.query.filter_by(username=form_login.username.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f"Login bem sucedido em: {form_login.username.data}!", 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f"E-mail ou senha incorretos ou não cadastrados!", 'alert-danger')
    return render_template('login.html', form_login=form_login)

def trata_documento(doc):
    doc = doc.replace('.', '')
    doc = doc.replace(',', '')
    doc = doc.replace('/', '')
    doc = doc.replace('-', '')
    return doc

@app.route('/clientes_fornecedores/cnpj/cadastro', methods=['GET', 'POST'])
def cadastro_cnpj():
    form = FormCadastroCNPJ()
    form.tipo_cadastro.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposCadastros.query.all()]
    if form.validate_on_submit():
        cadastro = ClientesFornecedores(nome_fantasia=form.nome_fantasia.data,
                                        razao_social=form.razao_social.data,
                                        cnpj=trata_documento(form.cnpj.data),
                                        rua=form.rua.data, nro=form.nro.data,
                                        complemento=form.complemento.data,
                                        cidade=form.cidade.data,
                                        bairro=form.bairro.data,
                                        uf=form.uf.data, cep=form.cep.data,
                                        data_fundacao=form.fundacao.data,
                                        telefone=form.telefone.data,
                                        telefone2=form.telefone2.data,
                                        telefone3=form.telefone3.data,
                                        email=form.email.data, obs=form.obs.data,
                                        tipo_cadastro=form.tipo_cadastro.id)
        database.session.add(cadastro)
        database.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('home'))
    return render_template('cadastro_cnpj.html', form=form)



@app.route('/cadastroinicial', methods=['GET', 'POST'])
def cadastro_inicial():
    form = FormCadastroEmpresa()
    if form.validate_on_submit():
        cadastro = CadastroEmpresa(nome_empres = form.nome_empresa.data,
                                   email_responsavel=form.email_responsavel.data)
        database.session.add(cadastro)
        database.session.commit()
        flash(f"Conta criada para: {form.nome_empresa.data}!", 'alert-success')
        return redirect(url_for('criar_conta'))
    return render_template('cadastro_empresa.html', form=form)