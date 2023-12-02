from flask import render_template, redirect, url_for, flash, request
from ERP import app, database, bcrypt, login_manager
from ERP.forms import FormCriarConta, FormLogin, FormCadastroCNPJ, FormCadastroEmpresa, FormCadastroCPF
from ERP.forms import FormTiposRoupas, FormCores, FormMarcas, FormTamanhos, FormTiposUnidades
from ERP.forms import FormItensEstoque
from ERP.models import Usuarios, CadastroEmpresa, TiposCadastros, ClientesFornecedores, TiposUsuarios
from ERP.models import TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, ItensEstoque
from ERP.models import TransacoesEstoque, TiposTransacoesEstoque
from flask_login import login_user, logout_user, current_user, login_required
import secrets
from datetime import datetime
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
            # Atualizar campos específicos do formulário CNPJ
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
            cliente_fornecedor.data_fundacao = form.fundacao.data
            cliente_fornecedor.telefone = form.telefone.data
            cliente_fornecedor.telefone2 = form.telefone2.data
            cliente_fornecedor.telefone3 = form.telefone3.data
            cliente_fornecedor.email = form.email.data
            cliente_fornecedor.obs = form.obs.data

            # Atualizar o usuário cadastrador
            cliente_fornecedor.id_usuario_cadastro = current_user.id

            database.session.commit()
            flash('Cadastro atualizado com sucesso!', 'success')
            return redirect(url_for('clientes_fornecedor_cpf_cnpj', cliente_fornecedor_id=cliente_fornecedor.id, tipo_emp='cnpj'))

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
            database.session.commit()

            # Atualizar o usuário cadastrador
            cliente_fornecedor.id_usuario_cadastro = current_user.id

            flash('Cadastro atualizado com sucesso!', 'success')
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

    # Certifique-se de passar o objeto `tipo_roupa` para o formulário para preenchimento inicial
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
        marca = Marcas(nome_marca=form.nome_marca.data)
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

def string_to_float(flo):
    if type(flo) is str:
        flo = flo.replace('.', '_')
        flo = flo.replace(',', '.')
        flo = flo.replace('_', ',')
        return float(flo)
    else:
        return flo

@app.route('/estoque/itensestoque/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_itens_estoque():
    form = FormItensEstoque()
    form.tipos_roupas.choices = [(tipo.id, tipo.nome_tipo_roupa) for tipo in TiposRoupas.query.all()]
    form.cores.choices = [(cor.id, cor.nome_cor) for cor in Cores.query.all()]
    form.tamanho.choices = [(tamanho.id, tamanho.nome_tamanho) for tamanho in Tamanhos.query.all()]
    form.marca.choices = [(marca.id, marca.nome_marca) for marca in Marcas.query.all()]
    form.tipo_unidade.choices = [(tipo_unidade.id, tipo_unidade.nome_tipo_unidade) for tipo_unidade in TiposUnidades.query.all()]
    if form.validate_on_submit():
        vlr_estoque_custo = string_to_float(form.valor_total_custo.data)
        vlr_medio_venda = string_to_float(form.valor_unitario_venda.data)
        try:
            valor_unitario_medio_custo = string_to_float(form.valor_total_custo.data) / string_to_float(form.qtd_inicial.data)
        except:
            valor_unitario_medio_custo = 0
        try:
            valor_total_medio_venda = string_to_float(form.valor_unitario_venda.data) * string_to_float(form.qtd_inicial.data)
        except:
            valor_total_medio_venda = 0
        itens_estoque = ItensEstoque(id_tipo_roupa=int(form.tipos_roupas.data),
                                     id_tamanho=int(form.tamanho.data),
                                     id_marca=int(form.marca.data),
                                     id_cor=int(form.cores.data),
                                     codigo_item=form.codigo_item.data,
                                     id_tipo_unidade=int(form.tipo_unidade.data),
                                     qtd=int(form.qtd_inicial.data),
                                     valor_estoque_custo=vlr_estoque_custo,
                                     valor_unitario_medio_venda=vlr_medio_venda,
                                     qtd_minima=string_to_float(form.quantidade_minima.data),
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
        item_estoque.data_entrada = tran_estoque.data_transacao
        database.session.commit()
        flash(f"Cadastro concluído!", 'alert-success')
        return redirect(url_for('itens_estoque_', itens_estoque_id=item_estoque.id))
    return render_template('cadastro_itens_estoque.html', form=form)

def cria_nome_item_estoque(itens_estoque):
    tipo_roupa = TiposRoupas.query.filter_by(id=itens_estoque.id_tipo_roupa).first()
    tamanho = Tamanhos.query.filter_by(id=itens_estoque.id_tamanho).first()
    marca = Marcas.query.filter_by(id=itens_estoque.id_marca).first()
    cor = Cores.query.filter_by(id=itens_estoque.id_cor).first()
    nome_produto = tipo_roupa.nome_tipo_roupa + ' ' + cor.nome_cor + ' ' + marca.nome_marca + ' ' + tamanho.nome_tamanho
    return nome_produto

@app.route('/estoque/itens_estoque/<itens_estoque_id>', methods=['GET', 'POST'])
@login_required
def itens_estoque_(itens_estoque_id):
    itens_estoque = ItensEstoque.query.get_or_404(itens_estoque_id)
    nome_roupa = cria_nome_item_estoque(itens_estoque)
    return render_template('itens_estoque.html', itens_estoque=itens_estoque, nome_roupa=nome_roupa)


