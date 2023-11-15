from flask import render_template, redirect, url_for, flash, request
from ERP import app, database, bcrypt, login_manager
from ERP.forms import FormCriarConta, FormLogin, FormCadastroCNPJ, FormCadastroEmpresa, FormCadastroCPF
from ERP.models import Usuarios, CadastroEmpresa, TiposCadastros, ClientesFornecedores, TiposUsuarios
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/criarconta', methods=['GET', 'POST'])
def criar_conta():
    form = FormCriarConta()
    form.tipo_usuario.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposUsuarios.query.all()]
    if form.validate_on_submit():
        senha_crip = bcrypt.generate_password_hash(form.senha.data)
        usuario = Usuarios(username=form.username.data,
                          senha=senha_crip,
                           tipo_usuario=int(form.tipo_usuario.data))
        database.session.add(usuario)
        database.session.commit()
        flash(f"Conta criada para: {form.username.data}!", 'alert-success')
        return redirect(url_for('home'))
    return render_template('criar_conta.html', form_criar_conta=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = FormLogin()
    if form.validate_on_submit():
        usuario = Usuarios.query.filter_by(username=form.username.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form.senha.data):
            login_user(usuario, remember=form.lembrar_dados.data)
            flash(f"Login bem sucedido em: {form.username.data}!", 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f"Usuário ou senha incorretos ou não cadastrados!", 'alert-danger')
    return render_template('login.html', form=form)

def trata_documento(doc):
    doc = doc.replace('.', '')
    doc = doc.replace(',', '')
    doc = doc.replace('/', '')
    doc = doc.replace('-', '')
    return doc


#TODO: verificação se valores são ou não unicos quando necessário para nao dar bug quando estiver em produção
@app.route('/clientesfornecedores/cnpj/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_cnpj():
    form = FormCadastroCNPJ()
    form.tipo_cadastro.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposCadastros.query.all()]

    if form.validate_on_submit():
        cadastro = ClientesFornecedores(
            nome_fantasia=form.nome_fantasia.data,
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
            tipo_cadastro=int(form.tipo_cadastro.data),
            id_usuario_cadastro=int(current_user.id)
        )
        database.session.add(cadastro)
        database.session.commit()
        cliente_fornecedor = ClientesFornecedores.query.filter_by(cnpj=trata_documento(form.cnpj.data)).first()
        flash('Cadastro realizado com sucesso!', 'success')
        if cliente_fornecedor.cnpj:
            return redirect(url_for('clientes_fornecedor_cpf_cnpj', cliente_fornecedor_id=cliente_fornecedor.id, tipo_emp='cnpj'))
        else:
            return redirect(url_for('clientes_fornecedor_cpf_cnpj', cliente_fornecedor_id=cliente_fornecedor.id, tipo_emp='cpf'))

    return render_template('cadastro_cnpj.html', form=form)


@app.route('/clientesfornecedores/<tipo_emp>/<cliente_fornecedor_id>')
@login_required
def clientes_fornecedor_cpf_cnpj(cliente_fornecedor_id, tipo_emp):
    cliente_fornecedor = ClientesFornecedores.query.get(cliente_fornecedor_id)
    if tipo_emp == 'cnpj':
        return render_template('cliente_fornecedor_cnpj.html', cliente_fornecedor=cliente_fornecedor)
    else:
        return render_template('cliente_fornecedor_cpf.html', cliente_fornecedor=cliente_fornecedor)
@app.route('/clientesfornecedores/cpf/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_cpf():
    form = FormCadastroCPF()
    form.tipo_cadastro.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposCadastros.query.all()]
    if form.validate_on_submit():
        cadastro = ClientesFornecedores(nome=form.nome_completo.data,
                                        cpf=trata_documento(form.cpf.data),
                                        rua=form.rua.data, nro=form.nro.data,
                                        complemento=form.complemento.data,
                                        cidade=form.cidade.data,
                                        bairro=form.bairro.data,
                                        uf=form.uf.data, cep=form.cep.data,
                                        data_aniversario=form.aniversario.data,
                                        telefone=form.telefone.data,
                                        telefone2=form.telefone2.data,
                                        telefone3=form.telefone3.data,
                                        email=form.email.data, obs=form.obs.data,
                                        tipo_cadastro=int(form.tipo_cadastro.data),
                                        id_usuario_cadastro=int(current_user.id))
        database.session.add(cadastro)
        database.session.commit()
        cliente_fornecedor = ClientesFornecedores.query.filter_by(cpf=trata_documento(form.cpf.data)).first()
        flash('Cadastro realizado com sucesso!', 'success')
        if cliente_fornecedor.cnpj:
            return redirect(url_for('clientes_fornecedor_cpf_cnpj', cliente_fornecedor_id=cliente_fornecedor.id, tipo_emp='cnpj'))
        else:
            return redirect(url_for('clientes_fornecedor_cpf_cnpj', cliente_fornecedor_id=cliente_fornecedor.id, tipo_emp='cpf'))
    return render_template('cadastro_cpf.html', form=form)

@app.route('/clientesfornecedores/lista')
@login_required
def lista_clientes_fornecedores():
    clientes_fornecedores = ClientesFornecedores.query.all()
    return render_template('lista_clientes_fornecedores.html', clientes_fornecedores=clientes_fornecedores)

@app.route('/cadastroinicial', methods=['GET', 'POST'])
@login_required
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

@app.route('/clientesfornecedores/<tipo_emp>/<cliente_fornecedor_id>/edicao', methods=['GET', 'POST'])
@login_required
def edicao_clientes_fornecedores(tipo_emp, cliente_fornecedor_id):
    cliente_fornecedor = ClientesFornecedores.query.get(cliente_fornecedor_id)
    if tipo_emp == 'cnpj':
        form = FormCadastroCNPJ()
    pass
