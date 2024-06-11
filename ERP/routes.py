from flask import render_template, redirect, url_for, flash, request, session
from ERP import app, database, bcrypt, login_manager
from ERP.forms import FormCriarConta, FormLogin, FormCadastroCNPJ, FormCadastroEmpresa, FormCadastroCPF
from ERP.forms import FormTiposRoupas, FormCores, FormMarcas, FormTamanhos, FormTiposUnidades, FormEditarItensEstoque
from ERP.forms import FormItensEstoque, FormBancos, FormAgenciaBancoCadastro, FormAgenciaBancoEdicao, FormAlterarPagamentoFaturaCartaoCredito
from ERP.forms import FormEditarBancos, FormEditarCartaoCredito, FormContaBancariaCadastro2, FormEditarCategoriasFinanceiras
from ERP.forms import FormContaBancariaCadastro, FormContaBancariaEdicao, FormGeneros, FormRedefinirSenha, FormEditarFaturaCartaoCredito
from ERP.forms import FormCartaoCredito, FormCategoriasFinanceiras, FormEditarUsuario, FormEditarSenha, FormEditarTiposUnidades
from ERP.forms import FormEditarTiposRoupas, FormEditarCores, FormEditarMarcas, FormEditarTamanhos, FormEditarGeneros
from ERP.forms import FormCadastroDespesaCartaoCredito
from ERP.models import Usuarios, CadastroEmpresa, TiposCadastros, ClientesFornecedores, TiposUsuarios, TransacoesFinanceiras
from ERP.models import TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, ItensEstoque, SituacoesUsuarios
from ERP.models import TransacoesEstoque, TiposTransacoesEstoque, Bancos, AgenciaBanco, ContasBancarias
from ERP.models import CartaoCredito, GeneroRoupa, CategoriasFinanceiras, ValidacaoFaturasCartaoCredito, FaturaCartaoCredito
from ERP.models import Conferencias
from flask_login import login_user, logout_user, current_user, login_required
import secrets
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, desc, func


def define_data_ultima_entrada_item_estoque(item, transacao):
    item.data_ultima_entrada = transacao.data_transacao
    conferencia = Conferencias(id_funcao=1,
                               id_item=item.id)
    database.session.add(conferencia)
    database.session.commit()


def define_data_ultima_saida_item_estoque(item, transacao):
    item.data_ultima_saida = transacao.data_transacao
    conferencia = Conferencias(id_funcao=2,
                               id_item=item.id)
    database.session.add(conferencia)
    database.session.commit()


def confere_data_entrada_saida_itens_estoque():
    itens_estoque = ItensEstoque.query.filter(ItensEstoque.situacao==1).all()
    for item in itens_estoque:
        ultima_transacao = TransacoesEstoque.query.filter_by(id_item=item.id).order_by(TransacoesEstoque.id.desc()).first()

        if item.data_ultima_entrada is False or item.data_ultima_entrada != ultima_transacao.data_transacao and ultima_transacao.tipo_transacao in [1,3,5,7]:
            item.data_ultima_entrada = ultima_transacao.data_transacao
            conferencia = Conferencias(id_funcao=3,
                                       id_item=item.id)
            database.session.add(conferencia)
            database.session.commit()

        if item.data_ultima_saida is False or item.data_ultima_saida != ultima_transacao.data_transacao and ultima_transacao.tipo_transacao in [2,4,6,8]:
            item.data_ultima_saida = ultima_transacao.data_transacao
            conferencia = Conferencias(id_funcao=3,
                                       id_item=item.id)
            database.session.add(conferencia)
            database.session.commit()


def atualiza_item_estoque(item, tipo=5):
    qtd_entradas = database.session.query(
        func.coalesce(func.sum(TransacoesEstoque.qtd_transacao), 0)
    ).filter(
        TransacoesEstoque.id_item == item.id,
        TransacoesEstoque.tipo_transacao.in_([1, 3, 5, 7])
    ).scalar()

    custo_entradas = database.session.query(
        func.coalesce(func.sum(TransacoesEstoque.valor_total_transacao_custo), 0)
    ).filter(
        TransacoesEstoque.id_item == item.id,
        TransacoesEstoque.tipo_transacao.in_([1, 3, 5, 7])
    ).scalar()

    # Query for sum of saidas
    qtd_saidas = database.session.query(
        func.coalesce(func.sum(TransacoesEstoque.qtd_transacao), 0)
    ).filter(
        TransacoesEstoque.id_item == item.id,
        TransacoesEstoque.tipo_transacao.in_([2, 4, 6, 8])
    ).scalar()

    custo_saidas = database.session.query(
        func.coalesce(func.sum(TransacoesEstoque.valor_total_transacao_custo), 0)
    ).filter(
        TransacoesEstoque.id_item == item.id,
        TransacoesEstoque.tipo_transacao.in_([2, 4, 6, 8])
    ).scalar()

    # Calculate final values
    custo_final = custo_entradas - custo_saidas
    qtd_final = qtd_entradas - qtd_saidas

    valor_unitario_medio_custo = 0
    valor_estoque_venda = 0

    if qtd_final > 0:
        valor_unitario_medio_custo = custo_final / qtd_final
        valor_estoque_venda = item.valor_unitario_venda * qtd_final


    # Update item
    item.qtd = qtd_final
    item.valor_estoque_custo = custo_final
    item.valor_unitario_medio_custo = valor_unitario_medio_custo
    item.valor_estoque_venda = valor_estoque_venda
    conferencia = Conferencias(id_funcao=tipo,
                               id_item=item.id)
    database.session.add(conferencia)
    database.session.commit()


def saldos_itens_estoque(item=False):
    if item:
        atualiza_item_estoque(item)
    else:
        itens_estoque = ItensEstoque.query.filter(ItensEstoque.situacao == 1).all()
        for item in itens_estoque:
            atualiza_item_estoque(item, tipo=4)


def retorna_categorias_financeiras_custos_despesas():
    categorias = CategoriasFinanceiras.query.filter_by(situacao=1).filter(
        CategoriasFinanceiras.tipo_transacao_financeira.in_([2, 3])).all()
    return categorias


def ajusta_mes(mes):
    if len(str(mes)) < 2:
        mes_r = f'0{mes}'
    else:
        mes_r = str(mes)
    return mes_r


def retorna_fatura_cartao_credito():
    data_ref = datetime.now()
    data_ref = data_ref - timedelta(days=180)
    retorno = []
    for i in range(6):
        retorno.append((i, f'{ajusta_mes(data_ref.month)}/{data_ref.year}'))
        data_ref = data_ref + timedelta(days=30)
    data_ref = datetime.now()
    for i in range(6):
        retorno.append((i+6, f'{ajusta_mes(data_ref.month)}/{data_ref.year}'))
        data_ref = data_ref + timedelta(days=30)
    return retorno


def devolve_label_fatura(index_):
    faturas = retorna_fatura_cartao_credito()
    return faturas[int(index_)]


def gera_cod_fatura(cartao, mes_venc, ano_venc):
    if len(str(mes_venc)) < 2:
        mes_venc = f'0{mes_venc}'
    if len(str(cartao.id)) <2:
        cartao.id = f'0{cartao.id}'
    cod_fatura = f'{cartao.id}.{mes_venc}.{ano_venc}'
    return cod_fatura


def gera_cod_fatura2(id_cartao, mes_venc, ano_venc):
    if len(str(mes_venc)) < 2:
        mes_venc = f'0{mes_venc}'
    if len(str(id_cartao)) <2:
        id_cartao = f'0{id_cartao}'
    cod_fatura = f'{id_cartao}.{mes_venc}.{ano_venc}'
    return cod_fatura


def verifica_fat_cartao(id_cartao):
    data_limite = datetime.now() - timedelta(days=31)
    cartao = CartaoCredito.query.filter_by(id=int(id_cartao)).first()
    validacao = ValidacaoFaturasCartaoCredito.query.filter(
        ValidacaoFaturasCartaoCredito.id_cartao == cartao.id,
        ValidacaoFaturasCartaoCredito.data_cadastro <= data_limite
    ).order_by(
        ValidacaoFaturasCartaoCredito.id.desc()
    ).first()
    data_ref = datetime.now()
    if validacao:
        for i in range(24):
            fatura = FaturaCartaoCredito.query.filter_by(id_cartao=cartao.id).first()
            cod_fat = gera_cod_fatura(cartao, data_ref.month, data_ref.month)
            if cod_fat == fatura.cod_fatura:
                pass
            else:
                nova_fatura = FaturaCartaoCredito(
                    cod_fat=cod_fat,
                    id_cartao_credito=cartao.id,
                    id_usuario_cadastro = current_user.id
                )
                nova_validacao = ValidacaoFaturasCartaoCredito(id_cartao=cartao.id)
                data_ref = data_ref + timedelta(days=30)
                database.session.add(nova_validacao)
                database.session.add(nova_fatura)
                database.session.commit()


def recebe_form_valor_monetario(valor):
    valor = valor.replace(',', '.')
    valor = valor.replace('R$', '')
    valor = valor.replace('$', '')
    return float(valor)


def situacao_retorno(sit):
    if sit == 1:
        retorno = 'Ativo'
    elif sit == 2:
        retorno = 'Inativo'
    return retorno


app.add_template_global(situacao_retorno, 'situacao_retorno')


def situacao_fatura_retorno(sit):
    if sit == 0:
        retorno = 'Em aberto'
    elif sit == 1:
        retorno = 'Pago'
    elif sit == 2:
        retorno = 'Em Atraso'
    elif sit == 3:
        retorno = 'Pago em atraso'
        #TODO: Adicionar codições pensando em pagamentos parcias de faturas cartao de credito
    return retorno


app.add_template_global(situacao_fatura_retorno, 'situacao_fatura_retorno')


def busc_lote_transacao():
    lote = TransacoesFinanceiras.query.order_by(desc(TransacoesFinanceiras.id)).first()
    if lote:
        return lote.lote_transacao + 1
    else:
        return 1


def converte_data_string(data):
    if data:
        data_formatada = data.strftime('%d/%m/%Y')
        return data_formatada
    else:
        return ''


app.add_template_global(converte_data_string, 'converte_data_string')


def trata_documento(doc):
    doc = doc.replace('.', '')
    doc = doc.replace(',', '')
    doc = doc.replace('/', '')
    doc = doc.replace('-', '')
    return doc


app.add_template_global(trata_documento, 'trata_documento')


def converte_data_string2(data):
    data_formatada = data.strftime('%d/%m/%Y %H:%M')
    return data_formatada


app.add_template_global(converte_data_string2, 'converte_data_string2')


def pesquisa_tipo_usuario(id_tipo_usuario):
    tipo_usuario = TiposUsuarios.query.filter_by(id=id_tipo_usuario).first()
    return tipo_usuario


app.add_template_global(pesquisa_tipo_usuario, 'pesquisa_tipo_usuario')


def retorna_dados_curent_user():
    usuario = Usuarios.query.filter_by(id=current_user.id).first()
    return usuario


app.add_template_global(retorna_dados_curent_user, 'current_user_data')


def nome_tipo_transacao_categoria_financeira(tipo_transacao):
    tipo_transacao = int(tipo_transacao)
    if tipo_transacao == 1:
        nome = 'Receita'
    elif tipo_transacao == 2:
        nome = 'Custo'
    elif tipo_transacao == 3:
        nome = 'Despesa'
    elif tipo_transacao == 4:
        nome = 'Transferência +'
    elif tipo_transacao == 5:
        nome = 'Transferência -'
    else:
        nome = 'Erro'
    return nome


app.add_template_global(nome_tipo_transacao_categoria_financeira, 'nome_tipo_transacao_categoria_financeira')


def configura_doscs(tipo_doc, doc):
    if tipo_doc == 'cpf':
        retorno = f'{doc[0:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}'
    else:
        retorno = f'{doc[0:2]}.{doc[2:5]}.{doc[5:9]}/{doc[9:13]}-{doc[13:]}'
    return retorno


app.add_template_global(configura_doscs, 'configura_doscs')


def busca_ultima_transacao_estoque():
    busca = TransacoesEstoque.query.order_by(TransacoesEstoque.id_lote.desc()).first()
    if busca:
        return busca.id_lote + 1
    else:
        return 1


app.add_template_global(busca_ultima_transacao_estoque, 'busca_ultima_transacao_estoque')


def retorna_tupla_situacao():
    return [(1, 'Ativo'), (2, 'Inativo')]


@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))


@app.route('/')
@login_required
def home():
    return render_template('home.html')

# GERENCIAMENTO DE CONTAS

@app.route('/usuarios')
@login_required
def gerenciamento_contas():
    return render_template('gerenciamento_contas.html')


@app.route('/usuarios/criarusuario', methods=['GET', 'POST'])
@login_required
def criar_conta():
    form = FormCriarConta()
    form.tipo_usuario.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposUsuarios.query.all()]
    if form.validate_on_submit():
        senha_crip = bcrypt.generate_password_hash(form.senha.data).decode('UTF-8')
        usuario = Usuarios(username=form.username.data,
                           senha=senha_crip,
                           tipo_usuario=int(form.tipo_usuario.data))
        database.session.add(usuario)
        database.session.commit()
        flash(f"Conta criada para: {form.username.data}!", 'alert-success')
        return redirect(url_for('home'))
    return render_template('criar_conta.html', form_criar_conta=form)


@app.route('/usuarios/<id_conta>/usuario')
@login_required
def conta(id_conta):
    conta_selecionada = Usuarios.query.filter_by(id=int(id_conta)).first()
    situacao = SituacoesUsuarios.query.filter_by(id=conta_selecionada.situacao).first()
    tipo_usuario = TiposUsuarios.query.filter_by(id=conta_selecionada.tipo_usuario).first()
    return render_template('conta.html', conta_selecionada=conta_selecionada, situacao=situacao, tipo_usuario=tipo_usuario, str=str)


@app.route('/usuarios/listausuarios')
@login_required
def lista_usuarios():
    usuario_ativo = False
    todos_usuarios = False
    usuario_inativo = False
    if not session.get('usuario_ativo') and not session.get('todos_usuarios') and not session.get('usuario_inativo'):
        usuario_ativo = 'active'
        usuarios = Usuarios.query.filter_by(situacao=1).all()
    if session.get('usuario_ativo'):
        session.pop('usuario_ativo', None)
        usuario_ativo = 'active'
        usuarios = Usuarios.query.filter_by(situacao=1).all()
    if session.get('todos_usuarios'):
        session.pop('todos_usuarios', None)
        todos_usuarios = 'active'
        usuarios = Usuarios.query.all()
    if session.get('usuario_inativo'):
        session.pop('usuario_inativo', None)
        usuario_inativo = 'active'
        usuarios = Usuarios.query.filter_by(situacao=2).all()
    return render_template('lista_usuarios.html', usuario_ativo=usuario_ativo, todos_usuarios=todos_usuarios, usuario_inativo=usuario_inativo, str=str, situacao=SituacoesUsuarios, usuarios=usuarios)


@app.route('/usuarios/listausuarios/enc/<tipo>')
@login_required
def encaminha_lista_usuarios(tipo):
    if tipo == '1':
        session['usuario_ativo'] = True
    elif tipo == '2':
        session['todos_usuarios'] = True
    elif tipo == '3':
        session['usuario_inativo'] = True
    return redirect(url_for('lista_usuarios'))


@app.route('/usuarios/<id_conta>/usuario/editar/usuario', methods=['GET', 'POST'])
@login_required
def editar_usuario(id_conta):
    usuario = Usuarios.query.filter_by(id=int(id_conta)).first()
    form = FormEditarUsuario(obj=usuario)
    form.tipo_usuario.choices = [(tipo.id, tipo.nome_tipo) for tipo in TiposUsuarios.query.all()]
    form.situacao.choices = [(situacao.id, situacao.nome_situacao) for situacao in SituacoesUsuarios.query.all()]
    if form.validate_on_submit():
        form.populate_obj(usuario)
        database.session.commit()
        flash('Usuário atualizado com sucesso!', 'alert-success')
        return redirect(url_for('conta', id_conta=id_conta))
    return render_template('editar_conta.html', form=form)


@app.route('/usuarios/<id_conta>/usuario/editar/senha', methods=['GET', 'POST'])
@login_required
def editar_senha(id_conta):
    usuario = Usuarios.query.filter_by(id=int(id_conta)).first()
    form = FormEditarSenha()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(usuario.senha, form.senha_antiga.data) and form.nova_senha.data == form.confirmar_nova_senha.data:
            usuario.senha = bcrypt.generate_password_hash(form.nova_senha.data).decode('UTF-8')
            database.session.commit()
            flash('Senha atualizada com sucesso', 'alert-success')
            return redirect(url_for('conta', id_conta=id_conta))
        elif not bcrypt.check_password_hash(usuario.senha, form.senha_antiga.data):
            flash('Favor confirme os dados', 'alert-warning')
        elif form.nova_senha.data != form.confirmar_nova_senha.data:
            flash('Favor confirme as senhas inseridas', 'alert-warning')
        else:
            flash('Favor contate o suporte', 'alert-danger')
    return render_template('editar_senha.html', form=form, usuario=usuario)


@app.route('/usuarios/<id_conta>/usuario/redefinir/senha', methods=['GET', 'POST'])
@login_required
def redefinir_senha(id_conta):
    usuario = Usuarios.query.filter_by(id=id_conta).first()
    form = FormRedefinirSenha()
    if form.validate_on_submit():
        if form.nova_senha.data == form.confirmar_nova_senha.data:
            usuario.senha =  bcrypt.generate_password_hash(form.nova_senha.data).decode('UTF-8')
            database.session.commit()
            flash('Senha atualizada com sucesso', 'alert-success')
            return redirect(url_for('conta', id_conta=id_conta))
        else:
            flash('Senhas inseridas não são iguais', 'alert-danger')
    return render_template('redefinir_senha.html', form=form, usuario=usuario)

# LOGIN

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


@app.route('/sair')
@login_required
def sair():
    if current_user.is_authenticated:
        logout_user()
        session.pop('logged_in', None)
        session.clear()
        flash(f"Logout realizado com sucesso!", 'alert-success')
    return redirect(url_for('login'))

# COMERCIAL

@app.route('/comercial')
@login_required
def home_comercial():
    return render_template('home_comercial.html')


@app.route('/comercial/clientesefornecedores')
def clientes_e_fornecedores():
    return render_template('clientes_fornecedores.html')


@app.route('/comercial/clientesfornecedores/cnpj/cadastro', methods=['GET', 'POST'])
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


@app.route('/comercial/clientesfornecedores/<tipo_emp>/<cliente_fornecedor_id>')
@login_required
def clientes_fornecedor_cpf_cnpj(cliente_fornecedor_id, tipo_emp):
    cliente_fornecedor = ClientesFornecedores.query.get(cliente_fornecedor_id)
    if tipo_emp == 'cnpj':
        return render_template('cliente_fornecedor_cnpj.html', cliente_fornecedor=cliente_fornecedor)
    else:
        return render_template('cliente_fornecedor_cpf.html', cliente_fornecedor=cliente_fornecedor)



@app.route('/comercial/clientesfornecedores/cpf/cadastro', methods=['GET', 'POST'])
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
                                        data_aniversario=form.data_aniversario.data,
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


@app.route('/comercial/clientesfornecedores/lista')
@login_required
def lista_clientes_fornecedores():
    cf = False
    c = False
    f = False
    if not session.get('cf') and not session.get('c') and not session.get('f'):
        cf = 'active'
        clientes_fornecedores = ClientesFornecedores.query.filter_by(situacao=1).all()
    if session.get('cf'):
        cf = 'active'
        session.pop('cf', None)
        clientes_fornecedores = ClientesFornecedores.query.filter_by(situacao=1).all()
    if session.get('c'):
        c = 'active'
        session.pop('c', None)
        clientes_fornecedores = ClientesFornecedores.query.filter(
            and_(ClientesFornecedores.situacao == 1,
                 ClientesFornecedores.tipo_cadastro.in_([1, 3]))
        ).all()
    if session.get('f'):
        f = 'active'
        session.pop('f', None)
        clientes_fornecedores = ClientesFornecedores.query.filter(
            and_(ClientesFornecedores.situacao == 1,
                 ClientesFornecedores.tipo_cadastro.in_([2, 3]))
        ).all()
    return render_template('lista_clientes_fornecedores.html', str=str, clientes_fornecedores=clientes_fornecedores, cf=cf, c=c, f=f, tipo_cadastro=TiposCadastros)


@app.route('/comercial/clientesfornecedores/lista/enc/<tipo_enc>')
@login_required
def encaminha_lista_clientes_fornecedores(tipo_enc):
    if tipo_enc == '1':
        session['cf'] = True
    elif tipo_enc == '2':
        session['c'] = True
    elif tipo_enc == '3':
        session['f'] = True
    return redirect(url_for('lista_clientes_fornecedores'))


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

    elif tipo_emp == 'cpf':
        form = FormCadastroCPF(obj=cliente_fornecedor)
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
            cliente_fornecedor.data_aniversario = form.data_aniversario.data
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

# ESTOQUE

@app.route('/estoque')
@login_required
def home_estoque():
    return render_template('home_estoque.html')

# Atributos Estoque

@app.route('/estoque/atributosdeestoque')
@login_required
def atributos_estoque():
    return render_template('atributos_estoque.html')


@app.route('/estoque/atributosdeestoque/tiporoupa')
@login_required
def home_tipo_roupa():
    return render_template('home_tipo_roupa.html')


@app.route('/estoque/atributosdeestoque/tiporoupa/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_tipo_roupa():
    form = FormTiposRoupas()
    if form.validate_on_submit():
        tipo_roupa = TiposRoupas(nome_tipo_roupa=form.nome_tipo_roupa.data,
                                id_usuario_cadastro=current_user.id)
        database.session.add(tipo_roupa)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_tipo_roupa.data}!", 'alert-success')
        tipo_roupa = TiposRoupas.query.filter_by(nome_tipo_roupa=form.nome_tipo_roupa.data).first()
        return redirect(url_for('tipo_roupa', tipo_roupa_id=tipo_roupa.id))
    return render_template('cadastro_tipo_roupa.html', form=form)


@app.route('/estoque/atributosdeestoque/tiporoupa/<tipo_roupa_id>')
@login_required
def tipo_roupa(tipo_roupa_id):
    tipo_roupa = TiposRoupas.query.get_or_404(tipo_roupa_id)
    return render_template('tipo_roupa.html', tipo_roupa=tipo_roupa)


@app.route('/estoque/atributosdeestoque/tiporoupa/<int:tipo_roupa_id>/edicao', methods=['GET', 'POST'])
@login_required
def editar_tipo_roupa(tipo_roupa_id):
    tipo_roupa = TiposRoupas.query.get_or_404(tipo_roupa_id)
    tipo_roupa.id_usuario_cadastro = current_user.id
    form = FormEditarTiposRoupas(obj=tipo_roupa)
    form.situacao.choices = retorna_tupla_situacao()

    if form.validate_on_submit():
        form.populate_obj(tipo_roupa)
        database.session.commit()
        flash(f"Edição concluída: {form.nome_tipo_roupa.data}!", 'alert-success')
        return redirect(url_for('tipo_roupa', tipo_roupa_id=tipo_roupa.id))

    return render_template('editar_tipo_roupa.html', tipo_roupa=tipo_roupa, form=form)


@app.route('/estoque/atributosdeestoque/tiporoupa/lista')
@login_required
def lista_tipo_roupa():
    tipo_roupa_ativo = False
    tipo_roupa_inativo = False
    if not session.get('tipo_roupa_ativo') and not session.get('tipo_roupa_inativo'):
        tipo_roupa_ativo = 'active'
        tipos_roupas = TiposRoupas.query.filter_by(situacao=1).order_by(TiposRoupas.nome_tipo_roupa).all()
    if session.get('tipo_roupa_ativo'):
        tipo_roupa_ativo = 'active'
        session.pop('tipo_roupa_ativo', None)
        tipos_roupas = TiposRoupas.query.filter_by(situacao=1).order_by(TiposRoupas.nome_tipo_roupa).all()
    if session.get('tipo_roupa_inativo'):
        tipo_roupa_inativo = 'active'
        session.pop('tipo_roupa_inativo', None)
        tipos_roupas = TiposRoupas.query.filter_by(situacao=2).order_by(TiposRoupas.nome_tipo_roupa).all()
    return render_template('lista_tipos_roupas.html', str=str, tipo_roupa_ativo=tipo_roupa_ativo, tipo_roupa_inativo=tipo_roupa_inativo, tipos_roupas=tipos_roupas)


@app.route('/estoque/atributosdeestoque/tiporoupa/lista/enc/<situacao>')
@login_required
def encaminha_lista_tipo_roupa(situacao):
    if situacao == '1':
        session['tipo_roupa_ativo'] = True
    elif situacao == '2':
        session['tipo_roupa_inativo'] = True
    return redirect(url_for('lista_tipo_roupa'))


@app.route('/estoque/atributosdeestoque/cores')
@login_required
def home_cores():
    return render_template('home_cores.html')


@app.route('/estoque/atributosdeestoque/cores/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_cores():
    form = FormCores()
    if form.validate_on_submit():
        cor = Cores(nome_cor=form.nome_cor.data,
                    id_usuario_cadastro=current_user.id)
        database.session.add(cor)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_cor.data}!", 'alert-success')
        cor = Cores.query.filter_by(nome_cor=form.nome_cor.data).first()
        return redirect(url_for('cor', cor_id=cor.id))
    return render_template('cadastro_cores.html', form=form)


@app.route('/estoque/atributosdeestoque/cores/lista')
@login_required
def lista_cores():
    cor_ativo = False
    cor_inativo = False
    if not session.get('cor_ativo') and not session.get('cor_inativo'):
        cor_ativo = 'active'
        cores = Cores.query.filter_by(situacao=1).order_by(Cores.nome_cor).all()
    if session.get('cor_ativo'):
        cor_ativo = 'active'
        session.pop('cor_ativo', None)
        cores = Cores.query.filter_by(situacao=1).order_by(Cores.nome_cor).all()
    if session.get('cor_inativo'):
        cor_inativo = 'active'
        session.pop('cor_inativo', None)
        cores = Cores.query.filter_by(situacao=2).order_by(Cores.nome_cor).all()
    return render_template('lista_cores.html', str=str, cor_ativo=cor_ativo, cor_inativo=cor_inativo, cores=cores)


@app.route('/estoque/atributosdeestoque/cores/lista/enc/<situacao>')
@login_required
def encaminha_lista_cores(situacao):
    if situacao == '1':
        session['cor_ativo'] = True
    elif situacao == '2':
        session['cor_inativo'] = True
    return redirect(url_for('lista_cores'))


@app.route('/estoque/atributosdeestoque/cores/<cor_id>')
@login_required
def cor(cor_id):
    cor = Cores.query.get_or_404(cor_id)
    return  render_template('cor.html', cor=cor)


@app.route('/estoque/cor/<int:cor_id>/edicao', methods=['GET', 'POST'])
@login_required
def editar_cor(cor_id):
    cor = Cores.query.get_or_404(cor_id)
    form = FormEditarCores(obj=cor)
    form.situacao.choices = retorna_tupla_situacao()

    if form.validate_on_submit():
        form.populate_obj(cor)
        cor.id_usuario_cadastro = current_user.id
        database.session.commit()
        flash(f"Edição concluída: {form.nome_cor.data}!", 'alert-success')
        return redirect(url_for('cor', cor_id=cor.id))

    return render_template('edicao_cor.html', form=form, cor=cor)


@app.route('/estoque/atributosdeestoque/marcas')
@login_required
def home_marcas():
    return render_template('home_marcas.html')


@app.route('/estoque/atributosdeestoque/marcas/cadastro', methods=['GET', 'POST'])
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


@app.route('/estoque/atributosdeestoque/marcas/<marca_id>', methods=['GET', 'POST'])
@login_required
def marcas(marca_id):
    marca = Marcas.query.get_or_404(marca_id)
    return render_template('marcas.html', marca=marca)


@app.route('/estoque/atributosdeestoque/marcas/lista')
@login_required
def lista_marcas():
    marca_ativo = False
    marca_inativo = False
    if not session.get('marca_ativo') and not session.get('marca_inativo'):
        marca_ativo = 'active'
        marcas = Marcas.query.filter_by(situacao=1).order_by(Marcas.nome_marca).all()
    if session.get('marca_ativo'):
        marca_ativo = 'active'
        session.pop('marca_ativo', None)
        marcas = Marcas.query.filter_by(situacao=1).order_by(Marcas.nome_marca).all()
    if session.get('marca_inativo'):
        marca_inativo = 'active'
        session.pop('marca_inativo', None)
        marcas = Marcas.query.filter_by(situacao=2).order_by(Marcas.nome_marca).all()
    return render_template('lista_marcas.html', str=str, marca_ativo=marca_ativo, marca_inativo=marca_inativo, marcas=marcas)


@app.route('/estoque/atributosdeestoque/marcas/lista/enc/<situacao>')
@login_required
def encaminha_lista_marcas(situacao):
    if situacao == '1':
        session['marca_ativo'] = True
    elif situacao == '2':
        session['marca_inativo'] = True
    return redirect(url_for('lista_marcas'))


@app.route('/estoque/atributosdeestoque/marcas/<int:marca_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_marca(marca_id):
    marca = Marcas.query.get_or_404(marca_id)
    form = FormEditarMarcas(obj=marca)
    form.situacao.choices = retorna_tupla_situacao()

    if form.validate_on_submit():
        form.populate_obj(marca)
        marca.id_usuario_cadastro = current_user.id
        database.session.commit()
        flash(f"Edição concluída: {form.nome_marca.data}!", 'alert-success')
        return redirect(url_for('marcas', marca_id=marca.id))

    return render_template('edicao_marca.html', form=form, marca=marca)


@app.route('/estoque/atributosdeestoque/tamanhos')
@login_required
def home_tamanhos():
    return render_template('home_tamanhos.html')


@app.route('/estoque/atributosdeestoque/tamanhos/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_tamanhos():
    form = FormTamanhos()
    if form.validate_on_submit():
        tamanho = Tamanhos(nome_tamanho=form.tamanho.data,
                           id_usuario_cadastro=current_user.id)
        database.session.add(tamanho)
        database.session.commit()
        flash(f"Cadastro concluído: {form.tamanho.data}!", 'alert-success')
        tamanho = Tamanhos.query.filter_by(nome_tamanho=form.tamanho.data).first()
        return redirect(url_for('tamanhos', tamanho_id=tamanho.id))
    return render_template('cadastro_tamanhos.html', form=form)


@app.route('/estoque/atributosdeestoque/tamanhos/<tamanho_id>', methods=['GET', 'POST'])
@login_required
def tamanhos(tamanho_id):
    tamanho = Tamanhos.query.get_or_404(tamanho_id)
    return render_template('tamanhos.html', tamanho=tamanho)


@app.route('/estoque/atributosdeestoque/tamanhos/lista')
@login_required
def lista_tamanhos():
    tamanho_ativo = False
    tamanho_inativo = False
    if not session.get('tamanho_ativo') and not session.get('tamanho_inativo'):
        tamanho_ativo = 'active'
        tamanhos = Tamanhos.query.filter_by(situacao=1).order_by(Tamanhos.nome_tamanho).all()
    if session.get('tamanho_ativo'):
        tamanho_ativo = 'active'
        session.pop('tamanho_ativo', None)
        tamanhos = Tamanhos.query.filter_by(situacao=1).order_by(Tamanhos.nome_tamanho).all()
    if session.get('tamanho_inativo'):
        tamanho_inativo = 'active'
        session.pop('tamanho_inativo', None)
        tamanhos = Tamanhos.query.filter_by(situacao=2).order_by(Tamanhos.nome_tamanho).all()
    return render_template('lista_tamanhos.html', str=str, tamanho_ativo=tamanho_ativo, tamanho_inativo=tamanho_inativo, tamanhos=tamanhos)


@app.route('/estoque/atributosdeestoque/tamanhos/lista/enc/<situacao>')
@login_required
def encaminha_lista_tamanhos(situacao):
    if situacao == '1':
        session['tamanho_ativo'] = True
    elif situacao == '2':
        session['tamanho_inativo'] = True
    return redirect(url_for('lista_tamanhos'))


@app.route('/estoque/atributosdeestoque/tamanhos/<int:tamanho_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_tamanho(tamanho_id):
    tamanho = Tamanhos.query.get_or_404(tamanho_id)
    form = FormEditarTamanhos(obj=tamanho)
    form.situacao.choices = retorna_tupla_situacao()

    if form.validate_on_submit():
        form.populate_obj(tamanho)
        tamanho.id_usuario_cadastro = current_user.id
        database.session.commit()
        flash(f"Edição concluída: {form.nome_tamanho.data}!", 'alert-success')
        return redirect(url_for('tamanhos', tamanho_id=tamanho.id))

    return render_template('edicao_tamanho.html', form=form, tamanho=tamanho)


@app.route('/estoque/atributosdeestoque/generos')
@login_required
def home_generos():
    return render_template('home_generos.html')


@app.route('/estoque/atributosdeestoque/generos/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_generos():
    form = FormGeneros()
    if form.validate_on_submit():
        genero = GeneroRoupa(nome_genero=form.nome_genero.data,
                             id_usuario_cadastro=current_user.id)
        database.session.add(genero)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_genero.data}!", 'alert-success')
        genero = GeneroRoupa.query.filter_by(nome_genero=form.nome_genero.data).first()
        return redirect(url_for('generos', genero_id=genero.id))
    return render_template('cadastro_generos.html', form=form)


@app.route('/estoque/atributosdeestoque/generos/<genero_id>', methods=['GET', 'POST'])
@login_required
def generos(genero_id):
    genero = GeneroRoupa.query.get_or_404(genero_id)
    return render_template('generos.html', genero=genero)


@app.route('/estoque/atributosdeestoque/generos/lista')
@login_required
def lista_generos():
    genero_ativo = False
    genero_inativo = False
    if not session.get('genero_ativo') and not session.get('genero_inativo'):
        genero_ativo = 'active'
        generos = GeneroRoupa.query.filter_by(situacao=1).order_by(GeneroRoupa.nome_genero).all()
    if session.get('genero_ativo'):
        genero_ativo = 'active'
        session.pop('genero_ativo', None)
        generos = GeneroRoupa.query.filter_by(situacao=1).order_by(GeneroRoupa.nome_genero).all()
    if session.get('genero_inativo'):
        genero_inativo = 'active'
        session.pop('genero_inativo', None)
        generos = GeneroRoupa.query.filter_by(situacao=2).order_by(GeneroRoupa.nome_genero).all()
    return render_template('lista_generos.html', str=str, genero_ativo=genero_ativo, genero_inativo=genero_inativo, generos=generos)


@app.route('/estoque/atributosdeestoque/generos/lista/enc/<situacao>')
@login_required
def encaminha_lista_generos(situacao):
    if situacao == '1':
        session['genero_ativo'] = True
    elif situacao == '2':
        session['genero_inativo'] = True
    return redirect(url_for('lista_generos'))


@app.route('/estoque/atributosdeestoque/generos/<int:genero_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_genero(genero_id):
    genero = GeneroRoupa.query.get_or_404(genero_id)
    form = FormEditarGeneros(obj=genero)
    form.situacao.choices = retorna_tupla_situacao()

    if form.validate_on_submit():
        form.populate_obj(genero)
        genero.id_usuario_cadastro = current_user.id
        database.session.commit()
        flash(f"Edição concluída: {form.nome_genero.data}!", 'alert-success')
        return redirect(url_for('generos', genero_id=genero.id))

    return render_template('edicao_genero.html', form=form, genero=genero)


@app.route('/estoque/atributosdeestoque/tiposunidades')
@login_required
def home_tipos_unidades():
    return render_template('home_tipos_unidades.html')


@app.route('/estoque/atributosdeestoque/tiposunidades/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_tipos_unidades():
    form = FormTiposUnidades()
    if form.validate_on_submit():
        tipos_unidades = TiposUnidades(nome_tipo_unidade=form.nome_tipo_unidade.data,
                                       id_usuario_cadastro=current_user.id)
        database.session.add(tipos_unidades)
        database.session.commit()
        flash(f"Cadastro concluído: {form.nome_tipo_unidade.data}!", 'alert-success')
        tipos_unidades = TiposUnidades.query.filter_by(nome_tipo_unidade=form.nome_tipo_unidade.data).first()
        return redirect(url_for('tipos_unidades', tipos_unidades_id=tipos_unidades.id))
    return render_template('cadastro_tipos_unidades.html', form=form)


@app.route('/estoque/atributosdeestoque/tiposunidades/<tipos_unidades_id>', methods=['GET', 'POST'])
@login_required
def tipos_unidades(tipos_unidades_id):
    tipos_unidades = TiposUnidades.query.get_or_404(tipos_unidades_id)
    return render_template('tipos_unidades.html', tipos_unidades=tipos_unidades)


@app.route('/estoque/atributosdeestoque/tiposunidades/lista')
@login_required
def lista_tipos_unidades():
    tipos_unidades_ativo = False
    tipos_unidades_inativo = False
    if not session.get('tipos_unidades_ativo') and not session.get('tipos_unidades_inativo'):
        tipos_unidades_ativo = 'active'
        tipos_unidades = TiposUnidades.query.filter_by(situacao=1).order_by(TiposUnidades.nome_tipo_unidade).all()
    if session.get('tipos_unidades_ativo'):
        tipos_unidades_ativo = 'active'
        session.pop('tipos_unidades_ativo', None)
        tipos_unidades = TiposUnidades.query.filter_by(situacao=1).order_by(TiposUnidades.nome_tipo_unidade).all()
    if session.get('tipos_unidades_inativo'):
        tipos_unidades_inativo = 'active'
        session.pop('tipos_unidades_inativo', None)
        tipos_unidades = TiposUnidades.query.filter_by(situacao=2).order_by(TiposUnidades.nome_tipo_unidade).all()
    return render_template('lista_tipos_unidades.html', str=str, tipos_unidades_ativo=tipos_unidades_ativo, tipos_unidades_inativo=tipos_unidades_inativo, tipos_unidades=tipos_unidades)


@app.route('/estoque/atributosdeestoque/tiposunidades/lista/enc/<situacao>')
@login_required
def encaminha_lista_tipos_unidades(situacao):
    if situacao == '1':
        session['tipos_unidade_ativo'] = True
    elif situacao == '2':
        session['tipos_unidades_inativo'] = True
    return redirect(url_for('lista_tipos_unidades'))


@app.route('/estoque/atributosdeestoque/tiposunidades/<int:tipos_unidades_id>/edicao', methods=['GET', 'POST'])
@login_required
def editar_tipos_unidades(tipos_unidades_id):
    tipos_unidades = TiposUnidades.query.get_or_404(tipos_unidades_id)
    form = FormEditarTiposUnidades(obj=tipos_unidades)
    form.situacao.choices = retorna_tupla_situacao()

    if form.validate_on_submit():
        form.populate_obj(tipos_unidades)
        tipos_unidades.id_usuario_cadastro = current_user.id
        database.session.commit()
        flash(f"Edição concluída: {form.nome_tipo_unidade.data}!", 'alert-success')
        return redirect(url_for('tipos_unidades', tipos_unidades_id=tipos_unidades.id))

    return render_template('editar_tipos_unidades.html', form=form, tipos_unidades=tipos_unidades)

# ITENS ESTOQUE

@app.route('/estoque/itensestoque')
@login_required
def home_itens_estoque():
    return render_template('home_itens_estoque.html')


@app.route('/estoque/itensestoque/confereitens')
def confere_itens_estoque():
    confere_data_entrada_saida_itens_estoque()
    saldos_itens_estoque()
    return redirect(url_for('home_itens_estoque'))


@app.route('/estoque/itensestoque/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_itens_estoque():
    form = FormItensEstoque()
    form.id_genero.choices = [(genero.id, genero.nome_genero) for genero in GeneroRoupa.query.filter_by(situacao=1).all()]
    form.id_tipo_roupa.choices = [(tipo.id, tipo.nome_tipo_roupa) for tipo in TiposRoupas.query.filter_by(situacao=1).all()]
    form.id_cor.choices = [(cor.id, cor.nome_cor) for cor in Cores.query.filter_by(situacao=1).all()]
    form.id_tamanho.choices = [(tamanho.id, tamanho.nome_tamanho) for tamanho in Tamanhos.query.filter_by(situacao=1).all()]
    form.id_marca.choices = [(marca.id, marca.nome_marca) for marca in Marcas.query.filter_by(situacao=1).all()]
    form.id_tipo_unidade.choices = [(tipo_unidade.id, tipo_unidade.nome_tipo_unidade) for tipo_unidade in TiposUnidades.query.filter_by(situacao=1).all()]
    if form.validate_on_submit():
        consulta = ItensEstoque.query.filter(ItensEstoque.codigo_item == form.codigo_item.data).first()
        if consulta:
            flash('Código do produto já existe em nosso banco de dados', 'alert-danger')
        else:
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
                                         valor_estoque_custo=vlr_estoque_custo,
                                         valor_unitario_venda=vlr_medio_venda,
                                         qtd_minima=string_to_float(form.qtd_minima.data),
                                         id_usuario_cadastro=current_user.id)

            database.session.add(itens_estoque)
            database.session.commit()
            item_estoque = ItensEstoque.query.filter_by(codigo_item=form.codigo_item.data).first()
            tipo_transacao = 5
            id_lote = busca_ultima_transacao_estoque()
            transacao_estoque = TransacoesEstoque(id_lote=int(id_lote),
                                                  tipo_transacao=int(tipo_transacao),
                                                  data_transacao=datetime.now(),
                                                  id_item=int(item_estoque.id),
                                                  qtd_transacao=int(form.qtd_inicial.data),
                                                  valor_total_transacao_custo=vlr_estoque_custo,
                                                  valor_total_transacao_venda=valor_total_medio_venda,
                                                  valor_unitario_medio_custo=valor_unitario_medio_custo,
                                                  valor_unitario_venda=vlr_medio_venda)
            database.session.add(transacao_estoque)
            database.session.commit()
            transacao_cadastrada = TransacoesEstoque.query.filter_by(id_lote=int(id_lote)).first()
            define_data_ultima_entrada_item_estoque(item_estoque, transacao_cadastrada)
            saldos_itens_estoque(item_estoque)
            flash(f"Cadastro concluído!", 'alert-success')
            return redirect(url_for('itens_estoque_', itens_estoque_id=item_estoque.id))
    return render_template('cadastro_itens_estoque.html', form=form)


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


@app.route('/estoque/itensestoque/<itens_estoque_id>/descricao', methods=['GET', 'POST'])
@login_required
def itens_estoque_(itens_estoque_id):
    descricao_item = False
    itens_estoque = ItensEstoque.query.get_or_404(itens_estoque_id)
    nome_roupa = cria_nome_item_estoque(itens_estoque)
    if not session.get('descricao_item') and not session.get('transacao_item'):
        descricao_item = 'active'
    elif session.get('descricao_item'):
        session.pop('descricao_item', None)
        descricao_item = 'active'
    elif session.get('transacao_item'):
        session.pop('transacao_item', None)
        return redirect(url_for('lista_transacoes_item', item_id=itens_estoque_id))
    return render_template('itens_estoque.html', descricao_item=descricao_item, itens_estoque_id=itens_estoque_id, itens_estoque=itens_estoque, nome_roupa=nome_roupa, transacao_item=False)


@app.route('/estoque/itensestoque/<item_estoque_id>/descricao/enc/<situacao>')
@login_required
def encaminha_item_estoque(item_estoque_id, situacao):
    if situacao == '1':
        session['descricao_item'] = True
    elif situacao == '2':
        session['transacao_item'] = True
    return redirect(url_for('itens_estoque_', itens_estoque_id=item_estoque_id))


@app.route('/estoque/itensestoque/<item_id>/transacoes')
@login_required
def lista_transacoes_item(item_id):
    todas_transacoes = False
    transacoes_entrada = False
    transacoes_saida = False
    transacao_item = 'active'
    itens_estoque_id = item_id
    if not session.get('todas_transacoes') and not session.get('transacoes_entrada') and not session.get('transacoes_saida'):
        todas_transacoes = 'active'
        transacoes = TransacoesEstoque.query.filter(TransacoesEstoque.id_item == item_id and TransacoesEstoque.situacao == 1).all()
    elif session.get('todas_transacoes'):
        session.pop('todas_transacoes', None)
        todas_transacoes = 'active'
        transacoes = TransacoesEstoque.query.filter(
            TransacoesEstoque.id_item == item_id and TransacoesEstoque.situacao == 1).all()
    elif session.get('transacoes_entrada'):
        session.pop('transacoes_entrada', None)
        transacoes_entrada = 'active'
        transacoes = TransacoesEstoque.query.filter(
            TransacoesEstoque.id_item == item_id,
            TransacoesEstoque.situacao == 1,
            TransacoesEstoque.tipo_transacao.in_([1, 3, 5])
        ).all()
    elif session.get('transacoes_saida'):
        session.pop('transacoes_saida', None)
        transacoes_saida = 'active'
        transacoes = TransacoesEstoque.query.filter(
            TransacoesEstoque.id_item == item_id,
            TransacoesEstoque.situacao == 1,
            TransacoesEstoque.tipo_transacao.in_([2, 4, 6])
        ).all()
    return render_template('lista_transacoes_estoque.html', itens_estoque_id=itens_estoque_id, item_id=item_id,transacoes=transacoes, transacao_item=transacao_item, todas_transacoes=todas_transacoes, transacoes_entrada=transacoes_entrada, transacoes_saida=transacoes_saida)


@app.route('/estoque/itensestoque/<item_id>/transacoes/enc/<situacao>')
@login_required
def encaminha_lista_transacoes_item(item_id, situacao):
    if situacao == '1':
        session['todas_transacoes'] = True
    elif situacao == '2':
        session['transacoes_entrada'] = True
    elif situacao == '3':
        session['transacoes_saida'] = True
    return redirect(url_for('lista_transacoes_item', item_id=item_id))


@app.route('/estoque/itensestoque/lista')
@login_required
def lista_itens_estoque():
    itens_estoque_ativo = False
    itens_estoque_inativo = False
    if not session.get('itens_estoque_ativo') and not session.get('itens_estoque_inativo'):
        itens_estoque_ativo = 'active'
        itens_estoque = ItensEstoque.query.filter_by(situacao=1).order_by(ItensEstoque.qtd.desc()).all()
    if session.get('itens_estoque_ativo'):
        itens_estoque_ativo = 'active'
        session.pop('itens_estoque_ativo', None)
        itens_estoque = ItensEstoque.query.filter_by(situacao=1).order_by(ItensEstoque.qtd.desc()).all()
    if session.get('itens_estoque_inativo'):
        itens_estoque_inativo = 'active'
        session.pop('itens_estoque_inativo', None)
        itens_estoque = ItensEstoque.query.filter_by(situacao=2).order_by(ItensEstoque.qtd.desc()).all()
    return render_template('lista_itens_estoque.html', str=str, itens_estoque_ativo=itens_estoque_ativo,
                           itens_estoque_inativo=itens_estoque_inativo, itens_estoque=itens_estoque, tipo_roupa=TiposRoupas,
                           tamanho=Tamanhos, marca=Marcas, cor=Cores, genero=GeneroRoupa)


@app.route('/estoque/itensestoque/lista/enc/<situacao>')
@login_required
def encaminha_lista_itens_estoque(situacao):
    if situacao == '1':
        session['itens_estoque_ativo'] = True
    elif situacao == '2':
        session['itens_estoque_inativo'] = True
    return redirect(url_for('lista_itens_estoque'))


@app.route('/estoque/itensestoque/<itens_estoque_id>/edicao', methods=['GET', 'POST'])
@login_required
def edicao_itens_estoque(itens_estoque_id):
    itens_estoque = ItensEstoque.query.get_or_404(itens_estoque_id)
    form = FormEditarItensEstoque(obj=itens_estoque)
    form.id_genero.choices = [(genero.id, genero.nome_genero) for genero in GeneroRoupa.query.all()]
    form.id_tipo_roupa.choices = [(tipo.id, tipo.nome_tipo_roupa) for tipo in TiposRoupas.query.all()]
    form.id_cor.choices = [(cor.id, cor.nome_cor) for cor in Cores.query.all()]
    form.id_marca.choices = [(marca.id, marca.nome_marca) for marca in Marcas.query.all()]
    form.id_tamanho.choices = [(tamanho.id, tamanho.nome_tamanho) for tamanho in Tamanhos.query.all()]
    form.id_tipo_unidade.choices = [(tipo.id, tipo.nome_tipo_unidade) for tipo in TiposUnidades.query.all()]
    form.situacao.choices = retorna_tupla_situacao()

    if form.validate_on_submit():
        form.populate_obj(itens_estoque)
        itens_estoque.valor_estoque_venda = float(form.valor_unitario_venda.data) * itens_estoque.qtd
        database.session.commit()
        flash("Edição concluída!", 'alert-success')
        return redirect(url_for('itens_estoque_', itens_estoque_id=itens_estoque.id))

    return render_template('edicao_itens_estoque.html', form=form, itens_estoque=itens_estoque.id)

# Financeiro

@app.route('/financeiro')
@login_required
def home_financeiro():
    cartoes = CartaoCredito.query.filter_by(situacao=1).all()
    for cartao in cartoes:
        verifica_fat_cartao(cartao.id)
    return render_template('home_financeiro.html')

# Atributos Financeiros

@app.route('/financeiro/atributosbancos')
@login_required
def home_atributos_bancos():
    return render_template('home_atributos_banco.html')


@app.route('/financeiro/atributosbancos/instituicoesbancarias')
@login_required
def home_bancos():
    return render_template('home_instituicao_bancaria.html')


@app.route('/financeiro/atributosbancos/instituicoesbancarias/cadastro', methods=['GET', 'POST'])
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
                           nome_banco=form.nome_banco.data,
                           data_cadastro=datetime.utcnow(),
                           id_usuario_cadastro=current_user.id)
            database.session.add(banco)
            database.session.commit()
            banco = Bancos.query.filter_by(cod_banco=form.cod_banco.data).first()
            flash("Cadastro concluído!", 'alert-success')
            return redirect(url_for('bancos', banco_id=banco.id))
    return render_template('cadastro_bancos.html', form=form)


@app.route('/financeiro/atributosbancos/instituicoesbancarias/<banco_id>', methods=['GET', 'POST'])
@login_required
def bancos(banco_id):
    banco = Bancos.query.filter_by(id=banco_id).first()
    return render_template('bancos.html', banco=banco)


@app.route('/financeiro/atributosbancos/instituicoesbancarias/lista')
@login_required
def lista_bancos():
    bancos_ativo = False
    bancos_inativo = False
    if not session.get('bancos_ativo') and not session.get('bancos_inativo'):
        bancos_ativo = 'active'
        bancos = Bancos.query.filter_by(situacao=1).order_by(Bancos.nome_banco).all()
    if session.get('bancos_ativo'):
        bancos_ativo = 'active'
        session.pop('bancos_ativo', None)
        bancos = Bancos.query.filter_by(situacao=1).order_by(Bancos.nome_banco).all()
    if session.get('bancos_inativo'):
        bancos_inativo = 'active'
        session.pop('bancos_inativo', None)
        bancos = Bancos.query.filter_by(situacao=2).order_by(Bancos.nome_banco).all()
    return render_template('lista_bancos.html', str=str, bancos_ativo=bancos_ativo,
                           bancos_inativo=bancos_inativo, bancos=bancos)


@app.route('/financeiro/atributosbancos/instituicoesbancarias/lista/enc/<situacao>')
@login_required
def encaminha_lista_bancos(situacao):
    if situacao == '1':
        session['bancos_ativo'] = True
    elif situacao == '2':
        session['bancos_inativo'] = True
    return redirect(url_for('lista_bancos'))


@app.route('/financeiro/bancos/<banco_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_bancos(banco_id):
    banco = Bancos.query.get_or_404(banco_id)
    form = FormEditarBancos(obj=banco)
    form.situacao.choices = retorna_tupla_situacao()
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
            banco.data_cadastro = datetime.utcnow()
            banco.id_usuario_cadastro = current_user.id
            database.session.commit()
            flash("Cadastro atualizado!", 'alert-success')
            return redirect(url_for('bancos', banco_id=banco.id))
    return render_template('editar_bancos.html', form=form)


@app.route('/financeiro/atributosbancos/agenciasbancarias')
@login_required
def home_agencias_bancarias():
    return render_template('home_agencias_bancarias.html')


@app.route('/financeiro/atributosbancos/agenciasbancarias/cadastro', methods=['GET', 'POST'])
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


@app.route('/financeiro/atributosbancos/agenciasbancarias/cadastro/<id_banco>', methods=['GET', 'POST'])
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
                                   apelido_agencia=session.get('apelido_agencia'),
                                   data_cadastro=datetime.utcnow(),
                                   id_usuario_cadastro=current_user.id)
            database.session.add(agencia)
            database.session.commit()
            flash("Agencia cadastrada com sucesso!", 'alert-success')
            return redirect(url_for('agencias_bancarias', id_agencia=agencia.id))
    return render_template('cadastro_fornecedor_selecionado_agencia.html', form_agencia=form_agencia)


@app.route('/financeiro/atributosbancos/agenciasbancarias/pesquisafornecedor', methods=['GET', 'POST'])
@login_required
def busca_fornecedor_banco():
    search = buscar_cliente_fornecedor_cnpj(session.get('pesquisa_bancos'))
    form_agencia = FormAgenciaBancoCadastro(agencia=session.get('agencia'),
                                            digito_agencia=session.get('digito_agencia'),
                                            id_banco=session.get('id_banco'),
                                            apelido_agencia=session.get('apelido_agencia'))
    form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in Bancos.query.all()]
    return render_template('pesquisa_fornecedor_banco.html', form_agencia=form_agencia, search=search)


@app.route('/financeiro/atributosbancos/agenciasbancarias/cadastro/cnpj', methods=['GET', 'POST'])
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
                                        apelido_agencia=form_agencia.apelido_agencia.data,
                                        data_cadastro=datetime.utcnow(),
                                        id_usuario_cadastro=current_user.id)
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
                                            id_usuario_cadastro=int(current_user.id),
                                            data_cadastro=datetime.utcnow())
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


@app.route('/financeiro/atributosbancos/agenciasbancarias/<id_agencia>')
@login_required
def agencias_bancarias(id_agencia):
    agencia = AgenciaBanco.query.get_or_404(id_agencia)
    banco = Bancos.query.get_or_404(agencia.id_banco)
    fornecedor = ClientesFornecedores.query.get_or_404(agencia.id_cliente)
    return render_template('agencia_bancaria.html', agencia=agencia, banco=banco, fornecedor=fornecedor)


@app.route('/financeiro/atributosbancos/agenciasbancarias/lista')
@login_required
def lista_agencias():
    agencia_ativo = False
    agencia_inativo = False
    if not session.get('agencia_ativo') and not session.get('agencia_inativo'):
        agencia_ativo = 'active'
        agencias = AgenciaBanco.query.filter_by(situacao=1).order_by(AgenciaBanco.apelido_agencia).all()
    if session.get('agencia_ativo'):
        agencia_ativo = 'active'
        session.pop('agencia_ativo', None)
        agencias = AgenciaBanco.query.filter_by(situacao=1).order_by(AgenciaBanco.apelido_agencia).all()
    if session.get('agencia_inativo'):
        agencia_inativo = 'active'
        session.pop('agencia_inativo', None)
        agencias = AgenciaBanco.query.filter_by(situacao=2).order_by(AgenciaBanco.apelido_agencia).all()
    return render_template('lista_agencia_bancaria.html', str=str, agencia_ativo_ativo=agencia_ativo,
                           agencia_inativo=agencia_inativo, agencias=agencias)


@app.route('/financeiro/atributosbancos/agenciasbancarias/lista/enc/<situacao>')
@login_required
def encaminha_lista_agencias(situacao):
    if situacao == '1':
        session['bancos_ativo'] = True
    elif situacao == '2':
        session['bancos_inativo'] = True
    return redirect(url_for('lista_bancos'))


@app.route('/financeiro/atributosbancos/agenciasbancarias/<id_agencia>/edicao', methods=['GET', 'POST'])
@login_required
def editar_agencias_bancarias(id_agencia):
    agencia = AgenciaBanco.query.get_or_404(id_agencia)
    form_agencia = FormAgenciaBancoEdicao(obj=agencia)
    form_agencia.id_cliente.choices = [(cnpj.id, cnpj.razao_social) for cnpj in ClientesFornecedores.query.filter(ClientesFornecedores.cnpj.isnot(None)).all()]
    form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in Bancos.query.all()]
    form_agencia.situacao.choices = retorna_tupla_situacao()
    if form_agencia.validate_on_submit():
        if 'finalizar' in request.form:
            form_agencia.populate_obj(agencia)
            agencia.id_cliente = form_agencia.id_cliente.data
            agencia.id_usuario_cadastro = datetime.utcnow()
            agencia.id_usuario_cadastro = current_user.id
            database.session.commit()
            flash("Agencia editada com sucesso!", 'alert-success')
            return redirect(url_for('agencias_bancarias', id_agencia=id_agencia))
    return render_template('edicao_agencias_bancos.html', form_agencia=form_agencia)


@app.route('/financeiro/atributosbancos/contasbancarias')
@login_required
def home_contas_bancarias():
    return render_template('home_contas_bancarias.html')


@app.route('/financeiro/atributosbancos/contasbancarias/cadastro', methods=['GET', 'POST'])
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


@app.route('/financeiro/atributosbancos/contasbancarias/buscatitularcpf', methods=['GET', 'POST'])
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


@app.route('/financeiro/atributosbancos/contasbancarias/buscatitularcnpj', methods=['GET', 'POST'])
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

@app.route('/financeiro/atributosbancos/contasbancarias/cadastro/<id_titular>', methods=['GET', 'POST'])
@login_required
def cadastro_titular_selecionado_conta(id_titular):
    titular = ClientesFornecedores.query.get_or_404(id_titular)
    form = FormContaBancariaCadastro2(id_agencia=session.get('id_agencia'),
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
                                         cheque_especial=string_to_float(form.cheque_especial.data))
        database.session.add(conta_bancaria)
        database.session.commit()
        conta_cadastrada = ContasBancarias.query.filter_by(id_agencia=form.id_agencia.data).first()
        transacao = TransacoesFinanceiras(id_categoria_financeira=1,
                                          tipo_lancamento=1,
                                          lote_transacao=busc_lote_transacao(),
                                          tipo_transacao=1,
                                          id_conta_bancaria=conta_cadastrada.id,
                                          valor_transacao=string_to_float(form.saldo_conta.data),
                                          data_pagamento=datetime.now(),
                                          situacao_transacao=3)
        database.session.add(transacao)
        database.session.commit()
        flash("Conta cadastrada com sucesso!", 'alert-success')
        return redirect(url_for('contas_bancarias', id_conta=conta_bancaria.id))
    return render_template('cadastro_titular_selecionado_conta.html', form=form)


@app.route('/financeiro/atributosbancos/contasbancarias/<id_conta>')
@login_required
def contas_bancarias(id_conta):
    conta = ContasBancarias.query.get_or_404(id_conta)
    titular = ClientesFornecedores.query.get_or_404(conta.id_titular)
    agencia = AgenciaBanco.query.get_or_404(conta.id_agencia)
    banco = Bancos.query.get_or_404(agencia.id_banco)
    fornecedor = ClientesFornecedores.query.get_or_404(agencia.id_cliente)
    return render_template('conta_bancaria.html', conta=conta, titular=titular, agencia=agencia, banco=banco, fornecedor=fornecedor)


@app.route('/financeiro/atributosbancos/contasbancarias/lista')
@login_required
def lista_contas():
    conta_ativo = False
    conta_inativo = False
    if not session.get('conta_ativo') and not session.get('conta_inativo'):
        conta_ativo = 'active'
        contas = ContasBancarias.query.filter_by(situacao=1).order_by(ContasBancarias.apelido_conta).all()
    if session.get('conta_ativo'):
        conta_ativo = 'active'
        session.pop('conta_ativo', None)
        contas = ContasBancarias.query.filter_by(situacao=1).order_by(ContasBancarias.apelido_conta).all()
    if session.get('conta_inativo'):
        conta_inativo = 'active'
        session.pop('conta_inativo', None)
        contas = ContasBancarias.query.filter_by(situacao=2).order_by(ContasBancarias.apelido_conta).all()
    return render_template('lista_contas_bancarias.html', str=str, conta_ativo=conta_ativo,
                           conta_inativo=conta_inativo, contas=contas)


@app.route('/financeiro/atributosbancos/contasbancarias/lista/enc/<situacao>')
@login_required
def encaminha_lista_contas(situacao):
    if situacao == '1':
        session['conta_ativo'] = True
    elif situacao == '2':
        session['conta_inativo'] = True
    return redirect(url_for('lista_contas'))


@app.route('/financeiro/atributosbancos/contasbancarias/<int:id_conta>/editar', methods=['GET', 'POST'])
@login_required
def editar_contas(id_conta):
    conta = ContasBancarias.query.get_or_404(id_conta)
    form = FormContaBancariaEdicao(obj=conta)
    form.situacao.choices = retorna_tupla_situacao()
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


@app.route('/financeiro/atributosbancos/cartoescredito')
@login_required
def home_cartao_credito():
    return render_template('home_cartao_credito.html')


@app.route('/financeiro/atributosbancos/cartoescredito/cadastrar', methods=['GET', 'POST'])
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
            id_conta_bancaria = int(form.id_conta_bancaria.data)
            conta_bancaria = ContasBancarias.query.get(id_conta_bancaria)

            if not conta_bancaria:
                flash('Conta bancária selecionada não existe', 'alert-danger')
            else:
                cartao = CartaoCredito(
                    id_conta_bancaria=id_conta_bancaria,
                    apelido_cartao=form.apelido_cartao.data,
                    dia_inicial=form.dia_inicial.data,
                    dia_final=form.dia_final.data,
                    dia_pgto=form.dia_pgto.data,
                    valor_limite=form.valor_limite.data,
                    valor_disponivel=form.valor_limite.data,
                    id_usuario_cadastro=current_user.id
                )
                database.session.add(cartao)
                database.session.commit()

                cartao2 = CartaoCredito.query.filter_by(apelido_cartao=form.apelido_cartao.data).first()
                data_ref = datetime.now()
                for i in range(24):
                    cod_fatura = gera_cod_fatura(cartao2, data_ref.month, data_ref.year)
                    pesquisa = FaturaCartaoCredito.query.filter_by(cod_fatura=cod_fatura).first()

                    if not pesquisa:
                        fatura = FaturaCartaoCredito(
                            cod_fatura=cod_fatura,
                            id_cartao_credito=cartao2.id,
                            id_usuario_cadastro=current_user.id
                        )
                        database.session.add(fatura)
                        database.session.commit()

                    data_ref = data_ref + timedelta(days=30)
                    validacao = ValidacaoFaturasCartaoCredito(id_cartao=cartao2.id)
                    database.session.add(validacao)
                    database.session.commit()

                flash('Cartão cadastrado com sucesso!', 'alert-success')
                return redirect(url_for('cartao_credito', id_cartao=cartao2.id))

    return render_template('cadastro_cartao_credito.html', form=form)


@app.route('/financeiro/atributosbancos/cartoescredito/<id_cartao>')
@login_required
def cartao_credito(id_cartao):
    cartao = CartaoCredito.query.get_or_404(id_cartao)
    conta = ContasBancarias.query.get_or_404(cartao.id_conta_bancaria)
    usuario = Usuarios.query.get_or_404(cartao.id_usuario_cadastro)
    return render_template('cartao_credito.html', cartao=cartao, conta=conta, usuario=usuario, dados_cadastro='active')


@app.route('/financeiro/atributosbancos/cartoescredito/<id_cartao>/faturas/lista')
@login_required
def lista_fatura_cartao_credito(id_cartao):
    faturas = FaturaCartaoCredito.query.filter_by(id_cartao_credito=int(id_cartao)).order_by(FaturaCartaoCredito.id).all()
    cartao = CartaoCredito.query.filter_by(id=int(id_cartao)).first()
    return render_template('lista_fat_cartao_credito.html', str=str, cartao=cartao, faturas=faturas, lista_faturas='active')


@app.route('/financeiro/atributosbancos/cartoescredito/<id_cartao>/faturas/<id_fatura>')
@login_required
def fatura_cartao_credito(id_cartao, id_fatura):
    faturas = FaturaCartaoCredito.query.filter(FaturaCartaoCredito.id_cartao_credito == int(id_cartao),
                                               FaturaCartaoCredito.id == int(id_fatura)).first()
    usuario = Usuarios.query.filter_by(id=faturas.id_usuario_cadastro).first()
    cartao = CartaoCredito.query.filter_by(id=int(id_cartao)).first()
    return render_template('fatura_cartao_credito.html', cartao=cartao, fatura=faturas, usuario=usuario, dados_fatura='active')


@app.route('/financeiro/atributosbancos/cartoescredito/<id_cartao>/faturas/<id_fatura>/lista')
@login_required
def lista_extrato_fatura_cartao_credito(id_cartao, id_fatura):
    transacoes = TransacoesFinanceiras.query.filter(
    TransacoesFinanceiras.id_fatura_cartao_credito == int(id_fatura),
    TransacoesFinanceiras.tipo_transacao == 2
).order_by(TransacoesFinanceiras.data_ocorrencia).all()
    cartao = CartaoCredito.query.filter_by(id=int(id_cartao)).first()
    fatura = FaturaCartaoCredito.query.filter_by(id=int(id_fatura)).first()
    categorias = CategoriasFinanceiras()
    return render_template('lista_extrato_fat_cartao_credito.html', categorias=categorias, fatura=fatura, str=str, cartao=cartao, transacoes=transacoes, extrato_fatura='active')


@app.route('/financeiro/atributosbancos/cartoescredito/<id_cartao>/faturas/<id_fatura>/editar', methods=['GET', 'POST'])
@login_required
def editar_fatura_cartao_credito(id_cartao, id_fatura):
    fatura = FaturaCartaoCredito.query.filter(FaturaCartaoCredito.id_cartao_credito==int(id_cartao), FaturaCartaoCredito.id==int(id_fatura)).first()
    form = FormEditarFaturaCartaoCredito(obj=fatura)
    if form.validate_on_submit():
        form.populate_obj(fatura)
        fatura.id_cadastro = current_user.id
        database.session.commit()
        flash('Fatura atualizada com sucesso', 'alert-success')
        return redirect(url_for('fatura_cartao_credito', id_cartao=id_cartao, id_fatura=id_fatura))
    return render_template('editar_fat_cartao_credito.html', form=form)


@app.route('/financeiro/atributosbancos/cartoescredito/<id_cartao>/faturas/<id_fatura>/pgto', methods=['GET','POST'])
@login_required
def alterar_pagamento_faturaa_cartao_credito(id_cartao, id_fatura):
    fatura = FaturaCartaoCredito.query.filter(FaturaCartaoCredito.id_cartao_credito == int(id_cartao),
                                              FaturaCartaoCredito.id == int(id_fatura)).first()
    form = FormAlterarPagamentoFaturaCartaoCredito(obj=fatura)
    if form.validate_on_submit():
        form.populate_obj(fatura)
        fatura.valor_pago = recebe_form_valor_monetario(form.valor_pago.data)
        fatura.id_cadastro = current_user.id
        database.session.commit()
        flash('Fatura atualizada com sucesso.', 'alert-success')
        return redirect(url_for('fatura_cartao_credito', id_cartao=id_cartao, id_fatura=id_fatura))
    return render_template('alterar_pagamento_fatura_cartao_credito.html', form=form)


@app.route('/financeiro/atributosbancos/cartoescredito/lista')
@login_required
def lista_cartao():
    cartao_ativo = False
    cartao_inativo = False
    if not session.get('cartao_ativo') and not session.get('cartao_inativo'):
        cartao_ativo = 'active'
        cartoes = CartaoCredito.query.filter_by(situacao=1).order_by(CartaoCredito.apelido_cartao).all()
    if session.get('cartao_ativo'):
        cartao_ativo = 'active'
        session.pop('cartao_ativo', None)
        cartoes = ContasBancarias.query.filter_by(situacao=1).order_by(ContasBancarias.apelido_conta).all()
    if session.get('cartao_inativo'):
        cartao_inativo = 'active'
        session.pop('cartao_inativo', None)
        cartoes = CartaoCredito.query.filter_by(situacao=2).order_by(CartaoCredito.apelido_cartao).all()
    return render_template('lista_cartao_credito.html', str=str, cartao_ativo=cartao_ativo,
                           cartao_inativo=cartao_inativo, cartoes=cartoes)


@app.route('/financeiro/atributosbancos/cartoescredito/lista/enc/<situacao>')
@login_required
def encaminha_lista_cartao(situacao):
    if situacao == '1':
        session['cartao_ativo'] = True
    elif situacao == '2':
        session['cartao_inativo'] = True
    return redirect(url_for('lista_cartao'))


@app.route('/financeiro/atributosbancos/cartoescredito/<id_cartao>/edicao', methods=['GET', 'POST'])
@login_required
def editar_cartao(id_cartao):
    cartao = CartaoCredito.query.get_or_404(id_cartao)
    form = FormEditarCartaoCredito(obj=cartao)
    form.id_conta_bancaria.choices = [(conta.id, conta.apelido_conta) for conta in ContasBancarias.query.all()]
    form.situacao.choices = retorna_tupla_situacao()
    if form.validate_on_submit():
        form.populate_obj(cartao)
        cartao.data_cadastro = datetime.utcnow()
        database.session.commit()
        flash('Cartão atualizado com sucesso!', 'alert-success')
        return redirect(url_for('cartao_credito', id_cartao=cartao.id))
    return render_template('editar_cartao_credito.html', form=form)

# Categorias Financeiras

@app.route('/financeiro/transacoesfinanceiras')
@login_required
def home_transacoes_financeiras():
    return render_template('home_transacoes_financeiras.html')

#1 - Receita 2 - Custo 3 - Despesa 4 - Transferência +, 5 - Transferência -
tipos_transacoes_financeiras = [(1, 'Receita'), (2, 'Custo'), (3, 'Despesa'), (4, 'Transferêncaia +'), (5, 'Transferêncaia -')]


@app.route('/financeiro/transacoesfinanceiras/categoriasfinanceiras/cadastrar', methods=['GET', 'POST'])
@login_required
def criar_categorias_financeiras():
    form = FormCategoriasFinanceiras()
    form.tipo_transacao_financeira.choices = [(tipo_id, tipo_nome) for tipo_id, tipo_nome in tipos_transacoes_financeiras]
    if form.validate_on_submit():
        categorias = CategoriasFinanceiras(nome_categoria=form.nome_categoria.data,
                                           tipo_transacao_financeira=form.tipo_transacao_financeira.data)
        database.session.add(categorias)
        database.session.commit()
        transacao = CategoriasFinanceiras.query.filter_by(nome_categoria=categorias.nome_categoria).first()
        flash('Categoria cadastrada com sucesso', 'alert-success')
        return redirect(url_for('categorias_financeiras', transacao_id=transacao.id))
    return render_template('cadastro_categorias_financeiras.html', form=form)


@app.route('/financeiro/transacoesfinanceiras/categoriasfinanceiras/<transacao_id>')
@login_required
def categorias_financeiras(transacao_id):
    categoria = CategoriasFinanceiras.query.get_or_404(transacao_id)
    return render_template('categorias_financeiras.html', categoria=categoria)


@app.route('/financeiro/transacoesfinanceiras/categoriasfinanceiras/lista')
@login_required
def lista_categoria_financeira():
    categoria_ativo = False
    categoria_inativo = False
    if not session.get('categoria_ativo') and not session.get('categoria_inativo'):
        categoria_ativo = 'active'
        categorias = CategoriasFinanceiras.query.filter_by(situacao=1).order_by(CategoriasFinanceiras.nome_categoria).all()
    if session.get('categoria_ativo'):
        categoria_ativo = 'active'
        session.pop('categoria_ativo', None)
        categorias = CategoriasFinanceiras.query.filter_by(situacao=1).order_by(CategoriasFinanceiras.nome_categoria).all()
    if session.get('categoria_inativo'):
        categoria_inativo = 'active'
        session.pop('categoria_inativo', None)
        categorias = CategoriasFinanceiras.query.filter_by(situacao=2).order_by(CategoriasFinanceiras.nome_categoria).all()
    return render_template('lista_categorias_financeiras.html', str=str, categoria_ativo=categoria_ativo,
                           categoria_inativo=categoria_inativo, categorias=categorias)


@app.route('/financeiro/transacoesfinanceiras/categoriasfinanceiras/lista/enc/<situacao>')
@login_required
def encaminha_lista_categoria_financeira(situacao):
    if situacao == '1':
        session['categoria_ativo'] = True
    elif situacao == '2':
        session['categoria_inativo'] = True
    return redirect(url_for('lista_categoria_financeira'))


@app.route('/financeiro/transacoesfinanceiras/categoriasfinanceiras/<transacao_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_categorias_financeiras(transacao_id):
    categoria = CategoriasFinanceiras.query.get_or_404(transacao_id)
    form = FormEditarCategoriasFinanceiras(obj=categoria)
    form.tipo_transacao_financeira.choices = [(tipo_id, tipo_nome) for tipo_id, tipo_nome in tipos_transacoes_financeiras]
    form.situacao.choices = retorna_tupla_situacao()
    if form.validate_on_submit():
        form.populate_obj(categoria)
        database.session.commit()
        flash('Edição realizada com sucesso.', 'alert-success')
        return redirect(url_for('categorias_financeiras', transacao_id=categoria.id))
    return render_template('editar_categorias_financeiras.html', form=form)


@app.route('/financeiro/lançamentosfinanceiros/criar', methods=['GET', 'POST'])
@login_required
def cadastro_custo_despesa():
    return render_template('cadastro_custo_despesa_financeira.html')


@app.route('/financeiro/lancamentosfinanceiros/despesa/cartaodecredito/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastro_despesa_cartao_credito():
    form = FormCadastroDespesaCartaoCredito()
    form.id_cartao_credito.choices = [(cartao.id, cartao.apelido_cartao) for cartao in CartaoCredito.query.filter_by(situacao=1).all()]
    form.id_categoria_financeira.choices = [(categoria.id, categoria.nome_categoria) for categoria in retorna_categorias_financeiras_custos_despesas()]
    form.fatura_cartao_credito.choices = retorna_fatura_cartao_credito()
    if form.validate_on_submit():
        fatura_seleciona = devolve_label_fatura(form.fatura_cartao_credito.data)
        cod_fat = gera_cod_fatura2(form.id_cartao_credito.data, fatura_seleciona[1][0:2], fatura_seleciona[1][3:])
        id_fat = FaturaCartaoCredito.query.filter_by(cod_fatura=cod_fat).first()
        lote_transacao = busc_lote_transacao()
        transacao = TransacoesFinanceiras(lote_transacao=lote_transacao,
                                          tipo_lancamento=2,
                                          tipo_transacao=2,
                                          id_categoria_financeira=int(form.id_categoria_financeira.data),
                                          id_cartao_credito=int(form.id_cartao_credito.data),
                                          id_fatura_cartao_credito=id_fat.id,
                                          valor_transacao=recebe_form_valor_monetario(form.valor_transacao.data),
                                          data_ocorrencia=form.data_ocorrencia.data,
                                          id_usuario_cadastro=current_user.id)
        database.session.add(transacao)
        database.session.commit()
        flash('Transação cadastrada com Sucesso.', 'alert-success')
        return redirect(url_for('home_transacoes_financeiras'))
    return render_template('cadastro_despesa_cartao_credito.html', form=form)


@app.route('/home/configuracoes')
@login_required
def home_configuracoes():
    return render_template('home_configuracoes.html')