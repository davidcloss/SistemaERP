from flask import render_template, redirect, url_for, flash, request, session
from ERP import app, database, bcrypt, login_manager
from ERP.forms import FormCriarConta, FormLogin, FormCadastroCNPJ, FormCadastroEmpresa, FormCadastroCPF
from ERP.forms import FormTiposRoupas, FormCores, FormMarcas, FormTamanhos, FormTiposUnidades
from ERP.forms import FormItensEstoque, FormBancos, FormAgenciaBancoCadastro, FormAgenciaBancoEdicao
from ERP.forms import FormContaBancariaCadastro, FormContaBancariaEdicao, FormGeneros
from ERP.forms import FormCartaoCredito
from ERP.models import Usuarios, CadastroEmpresa, TiposCadastros, ClientesFornecedores, TiposUsuarios
from ERP.models import TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, ItensEstoque
from ERP.models import TransacoesEstoque, TiposTransacoesEstoque, Bancos, AgenciaBanco, ContasBancarias
from ERP.models import CartaoCredito, FaturaCartaoCredito, GeneroRoupa
from flask_login import login_user, logout_user, current_user, login_required
import secrets
from datetime import datetime
import os
from PIL import Image
from sqlalchemy import or_, and_


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


#TODO: TRazer datas ajustadas para horário local
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
            data_fundacao=form.data_fundacao.data,
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
        flash('Cadastro realizado com sucesso!', 'alert-success')
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
        flash('Cadastro realizado com sucesso!', 'alert-success')
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


def obter_nome_tipo_por_id(id_tipo):
    tipo = TiposCadastros.query.get(id_tipo)

    if tipo:
        return tipo.nome_tipo
    else:
        return None


@app.route('/clientesfornecedores/<tipo_emp>/<cliente_fornecedor_id>/edicao', methods=['GET', 'POST'])
@login_required
def edicao_clientes_fornecedores(tipo_emp, cliente_fornecedor_id):
    cliente_fornecedor = ClientesFornecedores.query.get_or_404(cliente_fornecedor_id)

    if tipo_emp == 'cnpj':
        form = FormCadastroCNPJ(obj=cliente_fornecedor)
        form.tipo_cadastro.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposCadastros.query.all()]

        if form.validate_on_submit():

            form.populate_obj(cliente_fornecedor)
            cliente_fornecedor.razao_social = form.razao_social.data
            cliente_fornecedor.nome_fantasia = form.nome_fantasia.data
            cliente_fornecedor.cnpj = form.cnpj.data
            cliente_fornecedor.rua = form.rua.data
            cliente_fornecedor.complemento = form.complemento.data
            cliente_fornecedor.bairro = form.bairro.data
            cliente_fornecedor.cidade = form.cidade.data
            cliente_fornecedor.uf = form.uf.data
            cliente_fornecedor.cep = form.cep.data
            cliente_fornecedor.data_fundacao = form.data_fundacao.data
            cliente_fornecedor.telefone = form.telefone.data
            cliente_fornecedor.telefone2 = form.telefone2.data
            cliente_fornecedor.telefone3 = form.telefone3.data
            cliente_fornecedor.email = form.email.data
            cliente_fornecedor.obs = form.obs.data


            cliente_fornecedor.id_usuario_cadastro = current_user.id

            database.session.commit()
            flash('Cadastro atualizado com sucesso!', 'alert-success')
            return redirect(
                url_for('clientes_fornecedor_cpf_cnpj', cliente_fornecedor_id=cliente_fornecedor.id, tipo_emp='cnpj'))
        return render_template('cadastro_cnpj.html', form=form)

#TODO: ajustar carregamento datas
    elif tipo_emp == 'cpf':
        form = FormCadastroCPF(obj=cliente_fornecedor)
        form.nome_completo.data = cliente_fornecedor.nome
        form.tipo_cadastro.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposCadastros.query.all()]

        if form.validate_on_submit():
            # Atualizar campos específicos do formulário CPF
            form.populate_obj(cliente_fornecedor)
            cliente_fornecedor.nome = form.nome_completo.data
            cliente_fornecedor.cpf = form.cpf.data
            cliente_fornecedor.rua = form.rua.data
            cliente_fornecedor.complemento = form.complemento.data
            cliente_fornecedor.bairro = form.bairro.data
            cliente_fornecedor.cidade = form.cidade.data
            cliente_fornecedor.uf = form.uf.data
            cliente_fornecedor.cep = form.cep.data
            cliente_fornecedor.data_aniversario = form.aniversario.data
            cliente_fornecedor.telefone = form.telefone.data
            cliente_fornecedor.telefone2 = form.telefone2.data
            cliente_fornecedor.telefone3 = form.telefone3.data
            cliente_fornecedor.email = form.email.data
            cliente_fornecedor.obs = form.obs.data
            cliente_fornecedor.id_usuario_cadastro = current_user.id
            cliente_fornecedor.data_cadastro = datetime.utcnow()
            database.session.commit()


            flash('Cadastro atualizado com sucesso!', 'alert-success')
            return redirect(
                url_for('clientes_fornecedor_cpf_cnpj', cliente_fornecedor_id=cliente_fornecedor.id, tipo_emp='cpf'))

        return render_template('cadastro_cpf.html', form=form)
#TODO: corrigir selectfield


@app.route('/estoque/tiporoupa/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_tipo_roupa():
    form = FormTiposRoupas()
    if form.validate_on_submit():
        tipo_roupa = TiposRoupas(nome_tipo_roupa=form.nome_tipo_roupa.data)
        database.session.add(tipo_roupa)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_tipo_roupa.data}!", 'alert-success')
        tipo_roupa = TiposRoupas.query.filter_by(nome_tipo_roupa=form.nome_tipo_roupa.data).first()
        return redirect(url_for('tipo_roupa', tipo_roupa_id=tipo_roupa.id))
    return render_template('cadastro_tipo_roupa.html', form=form)

@app.route('/estoque/tiporoupa/<tipo_roupa_id>')
@login_required
def tipo_roupa(tipo_roupa_id):
    tipo_roupa = TiposRoupas.query.get_or_404(tipo_roupa_id)
    return render_template('tipo_roupa.html', tipo_roupa=tipo_roupa)


@app.route('/estoque/tiporoupa/<int:tipo_roupa_id>/edicao', methods=['GET', 'POST'])
@login_required
def editar_tipo_roupa(tipo_roupa_id):
    tipo_roupa = TiposRoupas.query.get_or_404(tipo_roupa_id)
    form = FormTiposRoupas()

    if form.validate_on_submit():
        tipo_roupa.nome_tipo_roupa = form.nome_tipo_roupa.data
        database.session.commit()
        flash(f"Edição concluída: {form.nome_tipo_roupa.data}!", 'alert-success')
        return redirect(url_for('tipo_roupa', tipo_roupa_id=tipo_roupa.id))


    elif request.method == 'GET':
        form.nome_tipo_roupa.data = tipo_roupa.nome_tipo_roupa

        return render_template('cadastro_tipo_roupa.html', form=form, tipo_roupa=tipo_roupa)

    return render_template('cadastro_tipo_roupa.html', tipo_roupa=tipo_roupa, form=form)


@app.route('/estoque/cores/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_cores():
    form = FormCores()
    if form.validate_on_submit():
        cor = Cores(nome_cor=form.nome_cor.data)
        database.session.add(cor)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_cor.data}!", 'alert-success')
        cor = Cores.query.filter_by(nome_cor=form.nome_cor.data).first()
        return redirect(url_for('cor', cor_id=cor.id))
    return render_template('cadastro_cores.html', form=form)


@app.route('/estoque/cores/<cor_id>')
@login_required
def cor(cor_id):
    cor = Cores.query.get_or_404(cor_id)
    return  render_template('cor.html', cor=cor)


@app.route('/estoque/cor/<int:cor_id>/edicao', methods=['GET', 'POST'])
@login_required
def editar_cor(cor_id):
    cor = Cores.query.get_or_404(cor_id)
    form = FormCores()

    if form.validate_on_submit():
        cor.nome_cor = form.nome_cor.data
        database.session.commit()
        flash(f"Edição concluída: {form.nome_cor.data}!", 'alert-success')
        return redirect(url_for('cor', cor_id=cor.id))

    elif request.method == 'GET':
        form.nome_cor.data = cor.nome_cor

        return render_template('cadastro_cores.html', form=form, cor=cor)

    return render_template('cadastro_cores.html', form=form, cor=cor)
#TODO: Lista de marcas, cores,tipo_roupa e etc


@app.route('/estoque/marcas/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_marcas():
    form = FormMarcas()
    if form.validate_on_submit():
        marca = Marcas(nome_marca=form.nome_marca.data,
                       id_usuario_cadastro=current_user.id)
        database.session.add(marca)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_marca.data}!", 'alert-success')
        marca = Marcas.query.filter_by(nome_marca=form.nome_marca.data).first()
        return redirect(url_for('marcas', marca_id=marca.id))
    return render_template('cadastro_marcas.html', form=form)


@app.route('/estoque/marcas/<marca_id>', methods=['GET', 'POST'])
@login_required
def marcas(marca_id):
    marca = Marcas.query.get_or_404(marca_id)
    return render_template('marcas.html', marca=marca)


@app.route('/estoque/marca/editar/<int:marca_id>', methods=['GET', 'POST'])
@login_required
def editar_marca(marca_id):
    marca = Marcas.query.get_or_404(marca_id)
    form = FormMarcas()

    if form.validate_on_submit():
        marca.nome_marca = form.nome_marca.data
        database.session.commit()
        flash(f"Edição concluída: {form.nome_marca.data}!", 'alert-success')
        return redirect(url_for('marcas', marca_id=marca.id))

    elif request.method == 'GET':
        form.nome_marca.data = marca.nome_marca

    return render_template('cadastro_marcas.html', form=form, marca=marca)


@app.route('/estoque/tamanhos/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_tamanhos():
    form = FormTamanhos()
    if form.validate_on_submit():
        tamanho = Tamanhos(nome_tamanho=form.tamanho.data)
        database.session.add(tamanho)
        database.session.commit()
        flash(f"Cadastro concluído: {form.tamanho.data}!", 'alert-success')
        tamanho = Tamanhos.query.filter_by(nome_tamanho=form.tamanho.data).first()
        return redirect(url_for('tamanhos', tamanho_id=tamanho.id))
    return render_template('cadastro_tamanhos.html', form=form)


@app.route('/estoque/tamanhos/<tamanho_id>', methods=['GET', 'POST'])
@login_required
def tamanhos(tamanho_id):
    tamanho = Tamanhos.query.get_or_404(tamanho_id)
    return render_template('tamanhos.html', tamanho=tamanho)


@app.route('/estoque/tamanho/editar/<int:tamanho_id>', methods=['GET', 'POST'])
@login_required
def editar_tamanho(tamanho_id):
    tamanho = Tamanhos.query.get_or_404(tamanho_id)
    form = FormTamanhos()

    if form.validate_on_submit():
        tamanho.nome_tamanho = form.tamanho.data
        database.session.commit()
        flash(f"Edição concluída: {form.tamanho.data}!", 'alert-success')
        return redirect(url_for('tamanhos', tamanho_id=tamanho.id))

    elif request.method == 'GET':
        form.tamanho.data = tamanho.nome_tamanho

    return render_template('cadastro_tamanhos.html', form=form, tamanho=tamanho)


@app.route('/estoque/generos/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_generos():
    form = FormGeneros()
    if form.validate_on_submit():
        genero = GeneroRoupa(nome_genero=form.nome_genero.data)
        database.session.add(genero)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_genero.data}!", 'alert-success')
        genero = GeneroRoupa.query.filter_by(nome_genero=form.nome_genero.data).first()
        return redirect(url_for('generos', genero_id=genero.id))
    return render_template('cadastro_generos.html', form=form)


@app.route('/estoque/generos/<genero_id>', methods=['GET', 'POST'])
@login_required
def generos(genero_id):
    genero = GeneroRoupa.query.get_or_404(genero_id)
    return render_template('generos.html', genero=genero)


@app.route('/estoque/generos/editar/<int:genero_id>', methods=['GET', 'POST'])
@login_required
def editar_genero(genero_id):
    genero = GeneroRoupa.query.get_or_404(genero_id)
    form = FormGeneros()

    if form.validate_on_submit():
        genero.nome_genero = form.nome_genero.data
        database.session.commit()
        flash(f"Edição concluída: {form.nome_genero.data}!", 'alert-success')
        return redirect(url_for('generos', genero_id=genero.id))

    elif request.method == 'GET':
        form.nome_genero.data = genero.nome_genero

    return render_template('cadastro_generos.html', form=form, genero=genero)


@app.route('/estoque/tiposunidades/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_tiposunidades():
    form = FormTiposUnidades()
    if form.validate_on_submit():
        tipos_unidades = TiposUnidades(nome_tipo_unidade=form.tipo_unidade.data)
        database.session.add(tipos_unidades)
        database.session.commit()
        flash(f"Cadastro concluído: {form.tipo_unidade.data}!", 'alert-success')
        tipos_unidades = TiposUnidades.query.filter_by(nome_tipo_unidade=form.tipo_unidade.data).first()
        return redirect(url_for('tipos_unidades', tipos_unidades_id=tipos_unidades.id))
    return render_template('cadastro_tipos_unidades.html', form=form)

@app.route('/estoque/tiposunidades/<tipos_unidades_id>', methods=['GET', 'POST'])
@login_required
def tipos_unidades(tipos_unidades_id):
    tipos_unidades = TiposUnidades.query.get_or_404(tipos_unidades_id)
    return render_template('tipos_unidades.html', tipos_unidades=tipos_unidades)
#TODO: ajustar usuarios edição


@app.route('/estoque/tiposunidades/<int:tipos_unidades_id>/edicao', methods=['GET', 'POST'])
@login_required
def editar_tipos_unidades(tipos_unidades_id):
    tipos_unidades = TiposUnidades.query.get_or_404(tipos_unidades_id)
    form = FormTiposUnidades()

    if form.validate_on_submit():
        tipos_unidades.nome_tipo_unidade = form.tipo_unidade.data
        database.session.commit()
        flash(f"Edição concluída: {form.tipo_unidade.data}!", 'alert-success')
        return redirect(url_for('tipos_unidades', tipos_unidades_id=tipos_unidades.id))

    elif request.method == 'GET':
        form.tipo_unidade.data = tipos_unidades.nome_tipo_unidade

    return render_template('cadastro_tipos_unidades.html', form=form, tipos_unidades=tipos_unidades)

def busca_ultima_transacao_estoque():
    busca = TransacoesEstoque.query.order_by(TransacoesEstoque.id_lote.desc()).first()
    if busca:
        return busca.id + 1
    else:
        return 1

@app.route('/estoque/itensestoque/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_itens_estoque():
    form = FormItensEstoque()
    form.id_genero.choices = [(genero.id, genero.nome_genero) for genero in GeneroRoupa.query.all()]
    form.id_tipo_roupa.choices = [(tipo.id, tipo.nome_tipo_roupa) for tipo in TiposRoupas.query.all()]
    form.id_cor.choices = [(cor.id, cor.nome_cor) for cor in Cores.query.all()]
    form.id_tamanho.choices = [(tamanho.id, tamanho.nome_tamanho) for tamanho in Tamanhos.query.all()]
    form.id_marca.choices = [(marca.id, marca.nome_marca) for marca in Marcas.query.all()]
    form.id_tipo_unidade.choices = [(tipo_unidade.id, tipo_unidade.nome_tipo_unidade) for tipo_unidade in TiposUnidades.query.all()]
    if form.validate_on_submit():
        vlr_estoque_custo = string_to_float(form.valor_total_custo.data)
        vlr_medio_venda = string_to_float(form.valor_unitario_venda.data)
        try:
            valor_unitario_medio_custo = string_to_float(form.valor_total_custo.data) / string_to_float(form.qtd_inicial.data)
        except:
            valor_unitario_medio_custo = float(0)
        try:
            valor_total_medio_venda = string_to_float(form.valor_unitario_venda.data) * string_to_float(form.qtd_inicial.data)
        except:
            valor_total_medio_venda = float(0)
        itens_estoque = ItensEstoque(id_tipo_roupa=int(form.id_tipo_roupa.data),
                                     id_tamanho=int(form.id_tamanho.data),
                                     id_genero = int(form.id_genero.data),
                                     id_marca=int(form.id_marca.data),
                                     id_cor=int(form.id_cor.data),
                                     codigo_item=form.codigo_item.data,
                                     id_tipo_unidade=int(form.id_tipo_unidade.data),
                                     qtd=int(form.qtd_inicial.data),
                                     valor_estoque_custo=vlr_estoque_custo,
                                     valor_unitario_medio_venda=vlr_medio_venda,
                                     qtd_minima=string_to_float(form.qtd_minima.data),
                                     valor_unitario_medio_custo=string_to_float(valor_unitario_medio_custo),
                                     valor_estoque_venda=string_to_float(valor_total_medio_venda))

        database.session.add(itens_estoque)
        database.session.commit()
        item_estoque = ItensEstoque.query.filter_by(codigo_item=form.codigo_item.data).first()
        tipo_transacao = TiposTransacoesEstoque.query.filter_by(nome_tipo_transacao='Entrada').first()
        id_lote = busca_ultima_transacao_estoque()
        transacao_estoque = TransacoesEstoque(id_lote=int(id_lote),
                                              tipo_transacao=int(tipo_transacao.id),
                                              data_transacao=datetime.utcnow(),
                                              id_item=int(item_estoque.id),
                                              qtd_transacao=int(form.qtd_inicial.data),
                                              valor_total_transacao_custo=vlr_estoque_custo,
                                              valor_total_transacao_venda=valor_total_medio_venda,
                                              valor_unitario_medio_custo=valor_unitario_medio_custo,
                                              valor_unitario_medio_venda=vlr_medio_venda)
        database.session.add(transacao_estoque)
        database.session.commit()
        tran_estoque = TransacoesEstoque.query.filter_by(id_lote=id_lote).first()
        setattr(item_estoque, 'data_ultima_entrada', tran_estoque.data_transacao)
        database.session.commit()
        flash(f"Cadastro concluído!", 'alert-success')
        return redirect(url_for('itens_estoque_', itens_estoque_id=item_estoque.id))
    return render_template('cadastro_itens_estoque.html', form=form)

@app.route('/estoque/tiposunidades/<int:tipos_unidades_id>/edicao', methods=['GET', 'POST'])
@login_required
def editar_tipos_unidades_(tipos_unidades_id):
    tipos_unidades = TiposUnidades.query.get_or_404(tipos_unidades_id)
    form = FormTiposUnidades()

    if form.validate_on_submit():
        tipos_unidades.nome_tipo_unidade = form.tipo_unidade.data
        database.session.commit()
        flash(f"Edição concluída: {form.tipo_unidade.data}!", 'alert-success')
        return redirect(url_for('tipos_unidades', tipos_unidades_id=tipos_unidades.id))

    elif request.method == 'GET':
        form.tipo_unidade.data = tipos_unidades.nome_tipo_unidade

    return render_template('cadastro_tipos_unidades.html', form=form, tipos_unidades=tipos_unidades)

#TODO: Fazer verificação de dados que precisam ser unicos antes de mandar pra bd em todos
def cria_nome_item_estoque(itens_estoque):
    tipo_roupa = TiposRoupas.query.filter_by(id=itens_estoque.id_tipo_roupa).first()
    tamanho = Tamanhos.query.filter_by(id=itens_estoque.id_tamanho).first()
    marca = Marcas.query.filter_by(id=itens_estoque.id_marca).first()
    genero = GeneroRoupa.query.filter_by(id=itens_estoque.id_genero).first()
    cor = Cores.query.filter_by(id=itens_estoque.id_cor).first()
    nome_produto = tipo_roupa.nome_tipo_roupa + ' ' + genero.nome_genero +  ' ' + cor.nome_cor + ' ' + marca.nome_marca + ' ' + tamanho.nome_tamanho
    return nome_produto

def string_to_float(flo):
    if flo == 0:
        return float(0)
    elif type(flo) is str:
        flo = flo.replace('.', '')
        flo = flo.replace(',', '.')
        return float(flo)
    else:
        return flo

@app.route('/estoque/itensestoque/<itens_estoque_id>', methods=['GET', 'POST'])
@login_required
def itens_estoque_(itens_estoque_id):
    itens_estoque = ItensEstoque.query.get_or_404(itens_estoque_id)
    nome_roupa = cria_nome_item_estoque(itens_estoque)
    return render_template('itens_estoque.html', itens_estoque=itens_estoque, nome_roupa=nome_roupa)


@app.route('/estoque/itensestoque/<itens_estoque_id>/edicao', methods=['GET', 'POST'])
@login_required
def edicao_itens_estoque(itens_estoque_id):
    itens_estoque = ItensEstoque.query.get_or_404(itens_estoque_id)
    form = FormItensEstoque(obj=itens_estoque)
    form.id_genero.choices = [(genero.id, genero.nome_genero) for genero in GeneroRoupa.query.all()]
    form.id_tipo_roupa.choices = [(tipo.id, tipo.nome_tipo_roupa) for tipo in TiposRoupas.query.all()]
    form.id_cor.choices = [(cor.id, cor.nome_cor) for cor in Cores.query.all()]
    form.id_marca.choices = [(marca.id, marca.nome_marca) for marca in Marcas.query.all()]
    form.id_tamanho.choices = [(tamanho.id, tamanho.nome_tamanho) for tamanho in Tamanhos.query.all()]
    form.id_tipo_unidade.choices = [(tipo.id, tipo.nome_tipo_unidade) for tipo in TiposUnidades.query.all()]

    if form.validate_on_submit():
        itens_estoque = ItensEstoque.query.get_or_404(itens_estoque_id)
        itens_estoque.id_tipo_roupa = form.id_tipo_roupa.data
        itens_estoque.id_cor = form.id_cor.data
        itens_estoque.id_marca = form.id_marca.data
        itens_estoque.id_tamanho = form.id_tamanho.data
        itens_estoque.id_tipo_unidade = form.id_tipo_unidade.data
        itens_estoque.id_genero = form.id_genero.data
        itens_estoque.qtd_minima = string_to_float(form.qtd_minima.data)
        database.session.commit()
        flash("Edição concluída!", 'alert-success')
        return redirect(url_for('itens_estoque_', itens_estoque_id=itens_estoque.id))

    return render_template('edicao_itens_estoque.html', form=form, itens_estoque=itens_estoque.id)


@app.route('/financeiro/bancos/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_banco():
    form = FormBancos()
    if form.validate_on_submit():
        verifica_cod = Bancos.query.filter_by(cod_banco=form.cod_banco.data).first()
        verifica_nome = Bancos.query.filter_by(nome_banco=form.nome_banco.data).first()
        if verifica_cod:
            flash("Código do banco já utilizado em outro cadastro!", 'alert-danger')

        elif verifica_nome:
            flash("Nome do banco já utilizado em outro cadastro!", 'alert-danger')
        else:
            banco = Bancos(cod_banco=form.cod_banco.data,
                           nome_banco=form.nome_banco.data)
            database.session.add(banco)
            database.session.commit()
            banco = Bancos.query.filter_by(cod_banco=form.cod_banco.data).first()
            flash("Cadastro concluído!", 'alert-success')
            return redirect(url_for('bancos', banco_id=banco.id))
    return render_template('cadastro_bancos.html', form=form)


@app.route('/financeiro/bancos/<banco_id>', methods=['GET', 'POST'])
@login_required
def bancos(banco_id):
    banco = Bancos.query.filter_by(id=banco_id).first()
    return render_template('bancos.html', banco=banco)


@app.route('/financeiro/bancos/<banco_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_bancos(banco_id):
    banco = Bancos.query.get_or_404(banco_id)
    form = FormBancos(obj=banco)
    if form.validate_on_submit():
        verifica_cod = Bancos.query.filter((Bancos.cod_banco == form.cod_banco.data) & (Bancos.id != banco.id)).first()
        verifica_nome = Bancos.query.filter(
            (Bancos.nome_banco == form.nome_banco.data) & (Bancos.id != banco.id)).first()
        if verifica_cod:
            flash("Código do banco já utilizado em outro cadastro!", 'alert-danger')
        elif verifica_nome:
            flash("Nome do banco já utilizado em outro cadastro!", 'alert-danger')
        else:
            form.populate_obj(banco)
            database.session.commit()
            flash("Cadastro atualizado!", 'alert-success')
            return redirect(url_for('bancos', banco_id=banco.id))
    return render_template('cadastro_bancos.html', form=form)


@app.route('/financeiro/bancos/agencias/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_agencias_bancos():
    form_agencia = FormAgenciaBancoCadastro()
    form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in Bancos.query.all()]
    if form_agencia.validate_on_submit():
        if 'cadastrar' in request.form:
            session['agencia'] = form_agencia.agencia.data
            session['digito_agencia'] = form_agencia.digito_agencia.data
            session['id_banco'] = form_agencia.id_banco.data
            session['apelido_agencia'] = form_agencia.apelido_agencia.data
            return redirect(url_for('cadastro_fornecedor_banco'))
        elif 'pesquisar' in request.form:
            session['agencia'] = form_agencia.agencia.data
            session['digito_agencia'] = form_agencia.digito_agencia.data
            session['id_banco'] = form_agencia.id_banco.data
            session['apelido_agencia'] = form_agencia.apelido_agencia.data
            if form_agencia.campo_pesquisa.data:
                session['campo_pesquisa'] = form_agencia.campo_pesquisa.data
                session['pesquisa_bancos'] = form_agencia.campo_pesquisa.data
                return redirect(url_for('busca_fornecedor_banco'))
            else:
                flash('Por favor preencha campo pesquisa', 'alert-danger')
        else:
            flash('Verifique', 'alert-warning')
    return render_template('cadastro_agencias_bancos.html', form_agencia=form_agencia)


def buscar_cliente_fornecedor_cnpj(busca):
    resultados = (
        ClientesFornecedores.query
        .filter(
            and_(
                ClientesFornecedores.cnpj.isnot(None),
                or_(
                    ClientesFornecedores.razao_social.ilike(f'%{busca}%'),
                    ClientesFornecedores.nome_fantasia.ilike(f'%{busca}%'),
                    ClientesFornecedores.email.ilike(f'%{busca}%'),
                    ClientesFornecedores.cidade.ilike(f'%{busca}%'),
                    ClientesFornecedores.bairro.ilike(f'%{busca}%'),
                    ClientesFornecedores.rua.ilike(f'%{busca}%'),
                    ClientesFornecedores.complemento.ilike(f'%{busca}%'),
                    ClientesFornecedores.uf.ilike(f'%{busca}%')
                )
            )
        )
        .all()
    )
    return resultados


def buscar_cliente_fornecedor_cpf(busca):
    resultados = (
        ClientesFornecedores.query
        .filter(
            and_(
                ClientesFornecedores.cpf.isnot(None),
                or_(
                    ClientesFornecedores.nome.ilike(f'%{busca}%'),
                    ClientesFornecedores.email.ilike(f'%{busca}%'),
                    ClientesFornecedores.cidade.ilike(f'%{busca}%'),
                    ClientesFornecedores.bairro.ilike(f'%{busca}%'),
                    ClientesFornecedores.rua.ilike(f'%{busca}%'),
                    ClientesFornecedores.complemento.ilike(f'%{busca}%'),
                    ClientesFornecedores.uf.ilike(f'%{busca}%')
                )
            )
        )
        .all()
    )
    return resultados


def busca_todos_clientes_fornecedores_cpf():
    resultado = ClientesFornecedores.query.filter(ClientesFornecedores.cpf.isnot(None)).all()
    return resultado


def busca_todos_clientes_fornecedores_cnpj():
    resultado = ClientesFornecedores.query.filter(ClientesFornecedores.cnpj.isnot(None)).all()
    return resultado


@app.route('/financeiro/bancos/agencias/cadastro/<id_banco>', methods=['GET', 'POST'])
@login_required
def cadastro_fornecedor_selecionado_agencia(id_banco):
    form_agencia = FormAgenciaBancoEdicao(agencia=session.get('agencia'),
                                          digito_agencia=session.get('digito_agencia'),
                                          id_banco=session.get('id_banco'),
                                          id_cliente=id_banco,
                                          apelido_agencia=session.get('apelido_agencia'))
    form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in Bancos.query.all()]
    form_agencia.id_cliente.choices = [(fornecedor.id, fornecedor.razao_social) for fornecedor in buscar_cliente_fornecedor_cnpj(session.get('pesquisa_bancos'))]
    if form_agencia.validate_on_submit():
        pesquisa_agencia = AgenciaBanco.query.filter_by(agencia=form_agencia.agencia.data).first()
        pesquisa_apelido = AgenciaBanco.query.filter_by(apelido_agencia=form_agencia.apelido_agencia.data).first()
        if pesquisa_agencia:
            flash('Agência já existe em outro cadastro.', 'alert-danger')
        elif pesquisa_apelido:
            flash('Apelido agência já existe em outro cadastro.', 'alert-danger')
        else:
            agencia = AgenciaBanco(agencia=session.get('agencia'),
                                   digito_agencia=session.get('digito_agencia'),
                                   id_banco=session.get('id_banco'),
                                   id_cliente=id_banco,
                                   apelido_agencia=session.get('apelido_agencia'))
            database.session.add(agencia)
            database.session.commit()
            flash("Agencia cadastrada com sucesso!", 'alert-success')
            return redirect(url_for('agencias_bancarias', id_agencia=agencia.id))
    return render_template('cadastro_fornecedor_selecionado_agencia.html', form_agencia=form_agencia)


@app.route('/financeiro/bancos/agencias/pesquisafornecedor', methods=['GET', 'POST'])
@login_required
def busca_fornecedor_banco():
    search = buscar_cliente_fornecedor_cnpj(session.get('pesquisa_bancos'))
    form_agencia = FormAgenciaBancoCadastro(agencia=session.get('agencia'),
                                            digito_agencia=session.get('digito_agencia'),
                                            id_banco=session.get('id_banco'),
                                            apelido_agencia=session.get('apelido_agencia'))
    form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in Bancos.query.all()]
    return render_template('pesquisa_fornecedor_banco.html', form_agencia=form_agencia, search=search)


@app.route('/financeiro/bancos/agencias/cadastro/cnpj', methods=['GET', 'POST'])
@login_required
def cadastro_fornecedor_banco():
    form_agencia = FormAgenciaBancoCadastro(agencia=session.get('agencia'),
                                            digito_agencia=session.get('digito_agencia'),
                                            id_banco=session.get('id_banco'),
                                            apelido_agencia=session.get('apelido_agencia'))
    form = FormCadastroCNPJ()
    form.tipo_cadastro.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposCadastros.query.all()]
    form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in Bancos.query.all()]
    if form.validate_on_submit() and form_agencia.validate_on_submit():
        cadastro_agencia = AgenciaBanco(agencia=form_agencia.agencia.data,
                                        digito_agencia=form_agencia.digito_agencia.data,
                                        id_banco=form_agencia.id_banco.data,
                                        apelido_agencia=form_agencia.apelido_agencia.data)
        database.session.add(cadastro_agencia)
        database.session.commit()
        cad_banco = ClientesFornecedores(nome_fantasia=form.nome_fantasia.data,
                                            razao_social=form.razao_social.data,
                                            cnpj=trata_documento(form.cnpj.data),
                                            rua=form.rua.data, nro=form.nro.data,
                                            complemento=form.complemento.data,
                                            cidade=form.cidade.data,
                                            bairro=form.bairro.data,
                                            uf=form.uf.data, cep=form.cep.data,
                                            data_fundacao=form.data_fundacao.data,
                                            telefone=form.telefone.data,
                                            telefone2=form.telefone2.data,
                                            telefone3=form.telefone3.data,
                                            email=form.email.data, obs=form.obs.data,
                                            tipo_cadastro=int(form.tipo_cadastro.data),
                                            id_usuario_cadastro=int(current_user.id))
        database.session.add(cad_banco)
        database.session.commit()
        banco_cadastrado = ClientesFornecedores.query.filter_by(cnpj=trata_documento(form.cnpj.data)).first()
        if banco_cadastrado:
            agencia_cadastrada = AgenciaBanco.query.filter_by(agencia=form_agencia.agencia.data).first()
            agencia_cadastrada.id_cliente = banco_cadastrado.id
            database.session.commit()
            flash("Agencia cadastrada com sucesso!", 'alert-success')
            return redirect(url_for('editar_agencias_bancarias', id_agencia=agencia_cadastrada.id))
        else:
            flash("Cadastro não encontrado!", 'alert-danger')
    return render_template('cadastro_cnpj_agencia_bancaria.html', form_agencia=form_agencia, form=form)


@app.route('/financeiro/bancos/agencias/<id_agencia>')
@login_required
def agencias_bancarias(id_agencia):
    agencia = AgenciaBanco.query.get_or_404(id_agencia)
    banco = Bancos.query.get_or_404(agencia.id_banco)
    fornecedor = ClientesFornecedores.query.get_or_404(agencia.id_cliente)
    return render_template('agencia_bancaria.html', agencia=agencia, banco=banco, fornecedor=fornecedor)


@app.route('/financeiro/bancos/agencias/<id_agencia>/edicao', methods=['GET', 'POST'])
@login_required
def editar_agencias_bancarias(id_agencia):
    agencia = AgenciaBanco.query.get_or_404(id_agencia)
    form_agencia = FormAgenciaBancoEdicao(obj=agencia)
    form_agencia.id_cliente.choices = [(cnpj.id, cnpj.razao_social) for cnpj in ClientesFornecedores.query.filter(ClientesFornecedores.cnpj.isnot(None)).all()]
    form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in Bancos.query.all()]
    if form_agencia.validate_on_submit():
        if 'finalizar' in request.form:
            form_agencia.populate_obj(agencia)
            agencia.id_cliente = form_agencia.id_cliente.data
            database.session.commit()
            flash("Agencia editada com sucesso!", 'alert-success')
            return redirect(url_for('agencias_bancarias', id_agencia=id_agencia))
    return render_template('edicao_agencias_bancos.html', form_agencia=form_agencia)

@app.route('/financeiro/bancos/agencias/contas/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_conta_bancaria():
    form = FormContaBancariaCadastro()
    form.id_agencia.choices = [(agencia.id, agencia.apelido_agencia) for agencia in AgenciaBanco.query.all()]
    if form.validate_on_submit():
        session['id_agencia'] = form.id_agencia.data
        session['apelido_conta'] = form.apelido_conta.data
        session['nro_conta'] = form.nro_conta.data
        session['digito_conta'] = form.digito_conta.data
        session['campo_pesquisa'] = form.campo_pesquisa.data
        session['cheque_especial'] = form.cheque_especial.data
        session['saldo_conta'] = form.saldo_conta.data
        if 'cpf' in request.form:
            return redirect(url_for('busca_titular_conta_cpf'))
        elif 'cnpj' in request.form:
            return redirect(url_for('busca_titular_conta_cnpj'))
    return render_template('cadastro_contas.html', form=form)

@app.route('/financeiro/bancos/agencias/contas/buscatitularcpf', methods=['GET', 'POST'])
@login_required
def busca_titular_conta_cpf():
    search = buscar_cliente_fornecedor_cpf(session.get('campo_pesquisa'))
    form = FormContaBancariaCadastro(id_agencia=session.get('id_agencia'),
                                     apelido_conta=session.get('apelido_conta'),
                                     nro_conta=session.get('nro_conta'),
                                     digito_conta=session.get('digito_conta'),
                                     campo_pesquisa=session.get('campo_pesquisa'),
                                     cheque_especial=session.get('cheque_especial'),
                                     saldo_conta=session.get('saldo_conta'))
    form.id_agencia.choices = [(agencia.id, agencia.apelido_agencia) for agencia in AgenciaBanco.query.all()]
    return render_template('pesquisa_titular_conta_cpf.html', form=form, search=search)

@app.route('/financeiro/bancos/agencias/contas/buscatitularcnpj', methods=['GET', 'POST'])
@login_required
def busca_titular_conta_cnpj():
    search = buscar_cliente_fornecedor_cnpj(session.get('campo_pesquisa'))
    form = FormContaBancariaCadastro(id_agencia=session.get('id_agencia'),
                                     apelido_conta=session.get('apelido_conta'),
                                     nro_conta=session.get('nro_conta'),
                                     digito_conta=session.get('digito_conta'),
                                     campo_pesquisa=session.get('campo_pesquisa'),
                                     cheque_especial=session.get('cheque_especial'),
                                     saldo_conta=session.get('saldo_conta'))
    form.id_agencia.choices = [(agencia.id, agencia.apelido_agencia) for agencia in AgenciaBanco.query.all()]
    return render_template('pesquisa_titular_conta_cnpj.html', form=form, search=search)

def string_to_integer(string):
    string = string.replace('-', '')
    string = string.replace('.', '')
    string = string.replace(',', '')
    string = string.replace(' ', '')
    return int(string)

@app.route('/financeiro/bancos/agencias/contas/cadastro/<id_titular>', methods=['GET', 'POST'])
@login_required
def cadastro_titular_selecionado_conta(id_titular):
    titular = ClientesFornecedores.query.get_or_404(id_titular)
    form = FormContaBancariaEdicao(id_agencia=session.get('id_agencia'),
                                   apelido_conta=session.get('apelido_conta'),
                                   nro_conta=session.get('nro_conta'),
                                   digito_conta=session.get('digito_conta'),
                                   id_titular_conta=id_titular,
                                   cheque_especial=session.get('cheque_especial'),
                                   saldo_conta=session.get('saldo_conta'))
    form.id_agencia.choices = [(agencia.id, agencia.apelido_agencia) for agencia in AgenciaBanco.query.all()]
    if titular.cpf:
        form.id_titular.choices = [(titular_cpf.id, titular_cpf.nome) for titular_cpf in busca_todos_clientes_fornecedores_cpf()]
    else:
        form.id_titular.choices = [(titular_cnpj.id, titular_cnpj.razao_social) for titular_cnpj in busca_todos_clientes_fornecedores_cnpj()]
    if form.validate_on_submit():
        conta_bancaria = ContasBancarias(id_agencia=form.id_agencia.data,
                                         apelido_conta=form.apelido_conta.data,
                                         nro_conta=string_to_integer(form.nro_conta.data),
                                         digito_conta=string_to_integer(form.digito_conta.data),
                                         id_titular=form.id_titular.data,
                                         cheque_especial=string_to_float(form.cheque_especial.data),
                                         cheque_especial_disponivel=string_to_float(form.cheque_especial.data),
                                         saldo_conta=string_to_float(form.saldo_conta.data))
        database.session.add(conta_bancaria)
        database.session.commit()
        #TODO: transação financeira de saldo atual
        flash("Conta cadastrada com sucesso!", 'alert-success')
        return redirect(url_for('contas_bancarias', id_conta=conta_bancaria.id))
    return render_template('cadastro_titular_selecionado_conta.html', form=form)


@app.route('/financeiro/bancos/agencias/contas/<id_conta>')
@login_required
def contas_bancarias(id_conta):
    conta = ContasBancarias.query.get_or_404(id_conta)
    titular = ClientesFornecedores.query.get_or_404(conta.id_titular)
    agencia = AgenciaBanco.query.get_or_404(conta.id_agencia)
    banco = Bancos.query.get_or_404(agencia.id_banco)
    fornecedor = ClientesFornecedores.query.get_or_404(agencia.id_cliente)
    return render_template('conta_bancaria.html', conta=conta, titular=titular, agencia=agencia, banco=banco, fornecedor=fornecedor)


@app.route('/financeiro/bancos/agencias/contas/<int:id_conta>/editar', methods=['GET', 'POST'])
@login_required
def editar_contas(id_conta):
    conta = ContasBancarias.query.get_or_404(id_conta)
    form = FormContaBancariaEdicao(obj=conta)
    titular = ClientesFornecedores.query.get_or_404(conta.id_titular)
    form.id_agencia.choices = [(agencia.id, agencia.apelido_agencia) for agencia in AgenciaBanco.query.all()]
    if titular.cpf:
        form.id_titular.choices = [(titularr.id, titularr.nome) for titularr in
                                         ClientesFornecedores.query.filter(ClientesFornecedores.cpf.isnot(None)).all()]
    else:
        form.id_titular.choices = [(titularr.id, titularr.razao_social) for titularr in
                                    ClientesFornecedores.query.filter(
                                    ClientesFornecedores.cnpj.isnot(None)).all()]
    if form.validate_on_submit():
        verifica_apelido = ContasBancarias.query.filter(and_(ContasBancarias.apelido_conta == form.apelido_conta.data, ContasBancarias.id != conta.id)).first()
        if verifica_apelido:
            flash("Apelido conta já utilizado em outro cadastro!", 'alert-danger')
        else:
            form.populate_obj(conta)
            database.session.commit()
            flash("Cadastro atualizado!", 'alert-success')
            return redirect(url_for('contas_bancarias', id_conta=conta.id))
    return render_template('edicao_contas.html', form=form)


@app.route('/financeiro/bancos/agencias/contas/cartaocredito/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_cartao_credito():
    form = FormCartaoCredito()
    form.id_conta_bancaria.choices = [(conta.id, conta.apelido_conta) for conta in ContasBancarias.query.all()]
    if form.validate_on_submit():
        if form.dia_inicial.data > 31 or form.dia_inicial.data < 1:
            flash('Dia inicial deve ser um dia entre 1 e 31', 'alert-danger')
        elif form.dia_final.data > 31 or form.dia_final.data < 1:
            flash('Dia final deve ser um dia entre 1 e 31', 'alert-danger')
        elif form.dia_pgto.data > 31 or form.dia_pgto.data < 1:
            flash('Dia pagamento deve ser um dia entre 1 e 31', 'alert-danger')
        else:
            cartao = CartaoCredito(id_conta_bancaria=form.id_conta_bancaria.data,
                                   apelido_cartao=form.apelido_cartao.data,
                                   dia_inicial=form.dia_inicial.data,
                                   dia_final=form.dia_final.data,
                                   dia_pgto=form.dia_pgto.data,
                                   valor_limite=form.valor_limite.data,
                                   valor_disponivel=form.valor_limite.data,
                                   id_usuario_cadastro=current_user.id)
            database.session.add(cartao)
            database.session.commit()
            cartao2 = CartaoCredito.query.filter_by(apelido_cartao=form.apelido_cartao.data).first()
            flash('Cartão cadastrado com sucesso!', 'alert-success')
            return redirect(url_for('cartao_credito', id_cartao=cartao2.id))
    return render_template('cadastro_cartao_credito.html', form=form)


@app.route('/financeiro/bancos/agencias/contas/cartaocredito/<id_cartao>')
@login_required
def cartao_credito(id_cartao):
    cartao = CartaoCredito.query.get_or_404(id_cartao)
    conta = ContasBancarias.query.get_or_404(cartao.id_conta_bancaria)
    usuario = Usuarios.query.get_or_404(cartao.id_usuario_cadastro)
    return render_template('cartao_credito.html', cartao=cartao, conta=conta, usuario=usuario)

@app.route('/financeiro/bancos/agencias/contas/cartaocredito/<id_cartao>/edicao', methods=['GET', 'POST'])
@login_required
def editar_cartao(id_cartao):
    cartao = CartaoCredito.query.get_or_404(id_cartao)
    form = FormCartaoCredito(obj=cartao)
    form.id_conta_bancaria.choices = [(conta.id, conta.apelido_conta) for conta in ContasBancarias.query.all()]
    if form.validate_on_submit():
        form.populate_obj(cartao)
        cartao.data_cadastro = datetime.utcnow()
        database.session.commit()
        flash('Cartão atualizado com sucesso!', 'alert-success')
        return redirect(url_for('cartao_credito', id_cartao=cartao.id))
    return render_template('cadastro_cartao_credito.html', form=form)
