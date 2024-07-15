import time
from flask import render_template, redirect, url_for, flash, request, session
from ERP import app, database, bcrypt, login_manager
from ERP.forms import FormCriarConta, FormLogin, FormCadastroCNPJ, FormCadastroEmpresa, FormCadastroCPF
from ERP.forms import FormTiposRoupas, FormCores, FormMarcas, FormTamanhos, FormTiposUnidades, FormEditarItensEstoque
from ERP.forms import FormItensEstoque, FormBancos, FormAgenciaBancoCadastro, FormAgenciaBancoEdicao, FormAlterarPagamentoFaturaCartaoCredito
from ERP.forms import FormEditarBancos, FormEditarCartaoCredito, FormContaBancariaCadastro2, FormEditarCategoriasFinanceiras
from ERP.forms import FormContaBancariaCadastro, FormContaBancariaEdicao, FormGeneros, FormRedefinirSenha, FormEditarFaturaCartaoCredito
from ERP.forms import FormCartaoCredito, FormCategoriasFinanceiras, FormEditarUsuario, FormEditarSenha, FormEditarTiposUnidades
from ERP.forms import FormEditarTiposRoupas, FormEditarCores, FormEditarMarcas, FormEditarTamanhos, FormEditarGeneros
from ERP.forms import FormCadastroDespesaCartaoCredito, FormCadastroCompraEstoque, FormRegistraTrocoVenda
from ERP.forms import FormCadastroVendaMercadoria, FormItensNaoEncontrados, FormParcelamentoProprio
from ERP.forms import FormVendaCartaoCreditoAVista, FormVendaCartaoCreditoParcelado
from ERP.models import Usuarios, CadastroEmpresa, TiposCadastros, ClientesFornecedores, TiposUsuarios, TransacoesFinanceiras
from ERP.models import TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, ItensEstoque, SituacoesUsuarios
from ERP.models import TransacoesEstoque, TiposTransacoesEstoque, Bancos, AgenciaBanco, ContasBancarias
from ERP.models import CartaoCredito, GeneroRoupa, CategoriasFinanceiras, ValidacaoFaturasCartaoCredito, FaturaCartaoCredito
from ERP.models import Conferencias, TicketsComerciais, DocumentosFiscais, FormasPagamento, FormasParcelamento
from ERP.models import TemporariaCompraEstoque, ItensTicketsComerciais
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, desc, func


def atualizacao_geral_financeiro(conta=False, situacao=True):
    ajusta_saldo_contas(conta=conta, tipo=6)
    if situacao:
        atualiza_cartao()
        vincula_fat_cartao_credito_transacao_financeira()


def retorna_total_faturas_ticket_venda(id_ticket):
    total_pagamentos = database.session.query(
        func.coalesce(func.sum(TransacoesFinanceiras.valor_transacao), 0)
    ).filter(
        TransacoesFinanceiras.situacao == 1,
        TransacoesFinanceiras.id_ticket == id_ticket
    ).scalar()
    return total_pagamentos


def retorna_situacoes_tickets():
    situacoes = {0: 'Ticket não finalizado',
                 1: 'Em condicional',
                 2: 'Devolvido',
                 3: 'Convertido a compra',
                 4: 'Compra não recebida',
                 5: 'Compra Recebida',
                 6: 'Enviado ao Financeiro',
                 7: 'Pagamento em Aberto',
                 8: 'Pagamento em atraso',
                 9: 'Pagamento parcial realizado em atraso',
                10: 'Pagamento parcial realizado',
                11: 'Pagamento realizado em atraso',
                12: 'Pagamento realizado',
                13: 'Cancelado',
                14: 'Devolução parcial',
                15: 'Devolução completa',
                16: 'Finalizado'}
    return situacoes


def rateia_valores_adicionais(ticket, itens_ticket):
    valor_ratear = ticket.valor_acrescimo - ticket.valor_desconto
    for item in itens_ticket:
        perc = item.valor_item / ticket.valor_ticket
        item.valor_item_rateio = item.valor_item + (valor_ratear * perc)
    database.session.commit()


def calcula_valor_parcelado(valor, parcelas):
    divisao = round(valor / parcelas, 2)
    total_arredondado = divisao * parcelas
    diferenca = valor - total_arredondado

    retorno = []
    for i in range(parcelas):
        if i == 0:
            retorno.append(round(divisao, 2) + round(diferenca, 2))
        else:
            retorno.append(round(divisao, 2))

    return retorno


def cria_transacao_estoque(itens, ticket, situacao):
    #  1 - Entrada Estoque Compra Mercadoria
    #  2 - Edição Ticket - INATIVA TRANSAÇÕES ANTIGAS
    #  3 -  Saída Estoque Venda Mercadoria
    if situacao == 2:
        transacoes = TransacoesEstoque.query.filter_by(id_ticket=ticket.id).all()
        for tran in transacoes:
            tran.situacao = 2
            database.session.commit()

    elif situacao == 1:
        lote = busca_ultima_transacao_estoque()
        for item in itens:
            id_item = ItensEstoque.query.filter_by(codigo_item=item.codigo_item).first()
            if id_item:
                transacao = TransacoesEstoque(
                    tipo_transacao=1,
                    id_lote=lote,
                    id_ticket=item.id_ticket_comercial,
                    data_registro_transacao=datetime.now(),
                    data_transacao=ticket.data_chegada,
                    id_item=id_item.id,
                    qtd_transacao=item.qtd,
                    valor_total_transacao_custo=item.valor_item_rateio * item.qtd,
                    valor_unitario_medio_custo=item.valor_item_rateio / item.qtd
                )
                database.session.add(transacao)
                database.session.commit()

                transacao_cadastrada = TransacoesEstoque.query.filter_by(id_lote=lote).order_by(
                    TransacoesEstoque.id.desc()).first()
                define_data_ultima_entrada_item_estoque(id_item, transacao_cadastrada)
                saldos_itens_estoque(id_item)

    elif situacao == 3:
        lote = busca_ultima_transacao_estoque()
        for item in itens:
            id_item = ItensEstoque.query.filter_by(codigo_item=item.codigo_item).first()
            if id_item:
                transacao = TransacoesEstoque(
                    tipo_transacao=2,
                    id_lote=lote,
                    id_ticket=item.id_ticket_comercial,
                    data_registro_transacao=datetime.now(),
                    data_transacao=ticket.data_cadastro,
                    id_item=id_item.id,
                    qtd_transacao=item.qtd,
                    valor_total_transacao_venda=item.valor_item_rateio,
                    valor_unitario_venda=item.valor_item_rateio / item.qtd
                )
                database.session.add(transacao)
                database.session.commit()

                transacao_cadastrada = TransacoesEstoque.query.filter_by(id_lote=lote).order_by(
                    TransacoesEstoque.id.desc()).first()
                define_data_ultima_entrada_item_estoque(id_item, transacao_cadastrada)
                saldos_itens_estoque(id_item)
            else:
                flash('Entre em contato com o suporte.', 'alert-danger')


def retorn_lista_itens_tickets_comercial_compras(id_ticket, situacao):
    # 1 - Somente ativos
    if situacao == 1:
        retorno = ItensTicketsComerciais.query.filter(ItensTicketsComerciais.id_ticket_comercial == id_ticket,
                                                         ItensTicketsComerciais.situacao_item_ticket.in_([0,1])).order_by(ItensTicketsComerciais.id).all()
    return retorno


def cria_fatura_ticket(ticket, situacao, valor_parcial=False, conta_bancaria=False):
        #  0 - Inativa Transações Financeiras
        # CADA TIPO TICKET TEM SUA LISTA DE SITUACOES PROPRIA
        # SITUACOES COMPRA - 2
        #  1 - PRIMEIRO CADASTRO FATURAS COMPRA MERCADORIAS



        # SITUACOES VENDA - 3
        #  1 - CADASTRO PARCELAMENTO PROPRIO
        #  2 - CARTÃO CREDITO, PIX
        #  3 - DINHEIRO A VISTA
        #  4 - CARTAO CREDITO PARCELADO
        #  5 - PERMUTA

    if situacao == 0:
        faturas = TransacoesFinanceiras.query.filter_by(id_ticket=ticket.id).all()
        for fat in faturas:
            fat.situacao = 2
            database.session.commit()

    if ticket.id_tipo_ticket == 2:


        if situacao == 1:
            forma_pagamento = FormasPagamento.query.filter_by(id=ticket.id_forma_pagamento).first()
            if forma_pagamento.parcelado == 0:
                transacao = TransacoesFinanceiras(tipo_lancamento=1,
                                                  lote_transacao=busc_lote_transacao(),
                                                  tipo_transacao=3,
                                                  id_categoria_financeira=5,
                                                  id_forma_pagamento=ticket.id_forma_pagamento,
                                                  id_ticket=ticket.id,
                                                  nro_total_parcelas=1,
                                                  nro_parcela_atual=1,
                                                  valor_transacao=ticket.valor_final,
                                                  data_ocorrencia=ticket.emissao_documento_fiscal,
                                                  situacao_transacao=1,
                                                  id_usuario_cadastro=current_user.id)
                database.session.add(transacao)
                database.session.commit()
            else:
                lote = busc_lote_transacao()
                valor_transacao = calcula_valor_parcelado(ticket.valor_final, ticket.parcelas)
                for i in range(ticket.parcelas):
                    transacao = TransacoesFinanceiras(tipo_lancamento=1,
                                                      lote_transacao=lote,
                                                      tipo_transacao=3,
                                                      id_categoria_financeira=5,
                                                      id_forma_pagamento=ticket.id_forma_pagamento,
                                                      id_ticket=ticket.id,
                                                      nro_total_parcelas=ticket.parcelas,
                                                      nro_parcela_atual=i+1,
                                                      valor_transacao=valor_transacao[i],
                                                      data_ocorrencia=ticket.emissao_documento_fiscal,
                                                      situacao_transacao=1,
                                                      id_usuario_cadastro=current_user.id)
                    database.session.add(transacao)
                    database.session.commit()

    elif ticket.id_tipo_ticket == 3:

        if situacao == 1:
            # PARCELAMENTO PROPRIO
            lote = busc_lote_transacao()
            valor_transacao = calcula_valor_parcelado(valor_parcial, ticket.parcelas)
            data_vcto = datetime.now() + timedelta(days=30)
            for i in range(ticket.parcelas):
                transacao = TransacoesFinanceiras(
                    tipo_lancamento=1,
                    lote_transacao=lote,
                    tipo_transacao=3,
                    id_conta_bancaria=1,
                    id_categoria_financeira=5,
                    id_forma_pagamento=ticket.id_forma_pagamento,
                    id_ticket=ticket.id,
                    nro_total_parcelas=ticket.parcelas,
                    nro_parcela_atual=i + 1,
                    valor_transacao=valor_transacao[i],
                    data_ocorrencia=ticket.data_abertura,
                    data_vencimento=data_vcto,
                    situacao_transacao=1,
                    id_usuario_cadastro=current_user.id)
                database.session.add(transacao)
                database.session.commit()
                data_vcto = data_vcto + timedelta(days=30)
                conta = ContasBancarias.query.filter_by(id=1).first()
                atualizacao_geral_financeiro(conta=conta, situacao=False)
        elif situacao == 2:
            # CARTAO CREDITO, PIX
            transacao = TransacoesFinanceiras(
                tipo_lancamento=1,
                lote_transacao=busc_lote_transacao(),
                tipo_transacao=1,
                id_categoria_financeira=6,
                id_conta_bancaria=conta_bancaria,
                id_forma_pagamento=ticket.id_forma_pagamento,
                id_ticket=ticket.id,
                nro_total_parcelas=1,
                nro_parcela_atual=1,
                valor_transacao=valor_parcial,
                data_ocorrencia=ticket.data_abertura,
                situacao_transacao=3,
                id_usuario_cadastro=current_user.id)
            database.session.add(transacao)
            database.session.commit()
            conta = ContasBancarias.query.filter_by(id=conta_bancaria).first()
            atualizacao_geral_financeiro(conta=conta, situacao=False)
        elif situacao == 3:
            # DINHEIRO A VISTA
            transacao = TransacoesFinanceiras(
                tipo_lancamento=1,
                lote_transacao=busc_lote_transacao(),
                tipo_transacao=1,
                id_categoria_financeira=6,
                id_conta_bancaria=1,
                id_forma_pagamento=ticket.id_forma_pagamento,
                id_ticket=ticket.id,
                nro_total_parcelas=1,
                nro_parcela_atual=1,
                valor_transacao=valor_parcial,
                data_ocorrencia=ticket.data_abertura,
                situacao_transacao=1,
                id_usuario_cadastro=current_user.id)
            database.session.add(transacao)
            database.session.commit()
            conta = ContasBancarias.query.filter_by(id=1).first()
            atualizacao_geral_financeiro(conta=conta, situacao=False)

        elif situacao == 4:
            # CARTAO CREDITO PARCELADO
            lote = busc_lote_transacao()
            valor_transacao = calcula_valor_parcelado(valor_parcial, ticket.parcelas)
            data_vcto = datetime.now() + timedelta(days=30)
            for i in range(ticket.parcelas):
                transacao = TransacoesFinanceiras(
                    tipo_lancamento=1,
                    lote_transacao=lote,
                    tipo_transacao=3,
                    id_conta_bancaria=conta_bancaria,
                    id_categoria_financeira=5,
                    id_forma_pagamento=ticket.id_forma_pagamento,
                    id_ticket=ticket.id,
                    nro_total_parcelas=ticket.parcelas,
                    nro_parcela_atual=i + 1,
                    valor_transacao=valor_transacao[i],
                    data_ocorrencia=ticket.data_abertura,
                    data_vencimento=data_vcto,
                    situacao_transacao=3,
                    id_usuario_cadastro=current_user.id)
                database.session.add(transacao)
                database.session.commit()
                data_vcto = data_vcto + timedelta(days=30)
                conta = ContasBancarias.query.filter_by(id=1).first()
                atualizacao_geral_financeiro(conta=conta, situacao=False)

        elif situacao == 5:
            # Permuta
            transacao = TransacoesFinanceiras(
                tipo_lancamento=1,
                lote_transacao=busc_lote_transacao(),
                tipo_transacao=1,
                id_categoria_financeira=6,
                id_forma_pagamento=ticket.id_forma_pagamento,
                id_ticket=ticket.id,
                nro_total_parcelas=1,
                nro_parcela_atual=1,
                valor_transacao=valor_parcial,
                data_ocorrencia=ticket.data_abertura,
                situacao_transacao=1,
                id_usuario_cadastro=current_user.id)
            database.session.add(transacao)
            database.session.commit()
            conta = ContasBancarias.query.filter_by(id=1).first()
            atualizacao_geral_financeiro(conta=conta, situacao=False)

    elif ticket.id_tipo_ticket == 1:
        pass
    else:
        pass


def retorna_situacoes_ticket_venda():
    situacoes = [(6, 'Venda não finalizada'), (7, 'Venda finalizada')]
    return situacoes


def retorna_situacoes_ticket_compra():
    situacoes = [(0, 'Ticket não finalizado'), (4, 'Compra não recebida'), (5, 'Compra Recebida')]
    return situacoes


def recebe_form_valor_monetario(valor):
    if valor:
        valor = valor.strip()  # Remove espaços em branco no início e fim
        valor = valor.replace(',', '.')  # Substitui vírgulas por pontos
        valor = valor.replace('R$', '').replace('$', '')  # Remove símbolos de moeda
        valor = valor.replace(' ', '')  # Remove espaços adicionais
    else:
        valor = '0'  # Define como string '0' para conversão correta
    try:
        return float(valor)
    except ValueError:
        return 0.0  # Em caso de erro, retorna 0.0


def calcular_soma_valor_item(id_ticket_comercial=False):
    if id_ticket_comercial:
        situacoes = [0, 1]  # Situações desejadas

        # Consulta para calcular a soma
        soma = database.session.query(database.func.sum(ItensTicketsComerciais.valor_item)) \
                        .filter(ItensTicketsComerciais.id_ticket_comercial == id_ticket_comercial) \
                        .filter(ItensTicketsComerciais.situacao_item_ticket.in_(situacoes)) \
                        .scalar()


        return soma if soma is not None else 0.0
    else:
        return 0.0


def calcula_valor_final_compra_estoque(valor_ticket, acrescimo, desconto):
    valor_total = valor_ticket + acrescimo - desconto
    return valor_total


def verifica_valor(campo_form):
    if campo_form == '':
        return None
    else:
        return campo_form


def retorna_sit_ticket(sit):
    if sit == 0 or sit == 1 or sit == 4 or sit == 5:
        retorno = 0
    elif sit == 2:
        retorno = 4
    elif sit == 3:
        retorno = 5
    elif sit == 6:
        retorno = 6
    elif sit == 7:
        retorno = 7
    return retorno


def popula_ticket(ticket, form, situacao, id_ticket=False):
    # SITUACOES:
    ## COMPRA ESTOQUE ##
    #  0 - PRIMEIRO CADASTRO COMPRA ESTOQUE
    #  1 - CADASTRO EM ANDAMENTO, SALVANDO APENAS POR SEGURANÇA COMPRA ESTOQUE
    #  2 - CADASTRO TICKET COM STATUS 4 - COMPRA NÃO RECEBIDA
    #  3 - CADASTRO TICKET COM STATUS 5 - COMPRA RECEBIDA
    ## VENDA MERCADORIA ##
    #  4 - PRIMEIRO CADASTRO VENDA MERCADORIA
    #  5 - CADASTRO EM ANDAMENTO, SALVANDO APENAS POR SEGURANÇA VENDA MERCADORIA
    #  6 - CADASTRO TICKET COM STATUS 6 - VENDA NÃO FINALIZADA
    #  7 - CADASTRO TICKET COM STATUS 7 - VENDA FINALIZADA
    if situacao == 0:
        ticket.data_abertura = datetime.now()


    elif situacao in [0, 1, 2, 3]:
        sit_ticket = retorna_sit_ticket(situacao)
        ticket.id_tipo_ticket = 2
        ticket.id_documento_fiscal = int(form.id_documento_fiscal.data)
        ticket.id_fornecedor = int(form.pesquisa_fornecedor.data)
        ticket.nro_documento_fiscal = verifica_valor(form.nro_documento_fiscal.data)
        ticket.emissao_documento_fiscal = form.emissao_documento_fiscal.data
        ticket.valor_ticket = calcular_soma_valor_item(id_ticket)
        ticket.valor_desconto = recebe_form_valor_monetario(form.valor_desconto.data)
        ticket.valor_acrescimo = recebe_form_valor_monetario(form.valor_acrescimo.data)
        ticket.valor_final = calcula_valor_final_compra_estoque(ticket.valor_ticket, ticket.valor_acrescimo,
                                                                ticket.valor_desconto)
        ticket.parcelas = int(form.parcelas.data) if form.parcelas.data else 1
        ticket.id_forma_pagamento = int(form.id_forma_pagamento.data)
        ticket.data_chegada = form.data_chegada.data
        ticket.data_prazo = form.data_prazo.data
        ticket.situacao = sit_ticket
        ticket.id_usuario_cadastro = current_user.id


        database.session.commit()

        if situacao == 3:
            return ticket

    elif situacao == 4:
        ticket.data_abertura = datetime.now()

    elif situacao in [4, 5, 6, 7]:
        sit_ticket = retorna_sit_ticket(situacao)
        ticket.id_tipo_ticket = 3
        ticket.id_cliente = int(form.pesquisa_fornecedor.data)
        ticket.valor_ticket = calcular_soma_valor_item(id_ticket)
        ticket.valor_desconto = recebe_form_valor_monetario(form.valor_desconto.data)
        ticket.valor_acrescimo = recebe_form_valor_monetario(form.valor_acrescimo.data)
        ticket.valor_final = calcula_valor_final_compra_estoque(ticket.valor_ticket, ticket.valor_acrescimo,
                                                                ticket.valor_desconto)
        ticket.parcelas = int(form.parcelas.data) if form.parcelas.data else 1
        ticket.id_forma_pagamento = int(form.id_forma_pagamento.data)
        ticket.situacao = sit_ticket
        ticket.id_usuario_cadastro = current_user.id

        database.session.commit()

        if situacao == 7:
            return ticket


def converte_str_datetime_select_field(data):
    if data:
        retorno = datetime.strptime(data, "%a, %d %b %Y %H:%M:%S %Z")
    else:
        retorno = datetime.now()
    return retorno


def clear_sessions_tickets_compra(sit=1):
    # 1 - Venda, 2 - Compra
    if sit == 1:
        session_keys = [
            'parcelado',
            'pagamento',
            'situacao',
            'data_chegada',
            'data_prazo',
            'valor_item',
            'id_ticket',
            'recarregar',
            'id_documento_fiscal',
            'tipo_fornecedor',
            'pesquisa_fornecedor',
            'nro_documento_fiscal',
            'emissao_documento_fiscal',
            'valor_desconto',
            'valor_acrescimo',
            'parcelas',
            'id_forma_pagamento',
            'pesquisa_item',
            'registra_troco_venda',
            'valor_parcelar',
            'parcelas_'
        ]
    else:
        session_keys = [
            'id_ticket_compra',
            'situacao',
            'data_chegada',
            'data_prazo',
            'valor_item',
            'recarregar',
            'id_documento_fiscal',
            'tipo_fornecedor',
            'pesquisa_fornecedor',
            'nro_documento_fiscal',
            'emissao_documento_fiscal',
            'valor_desconto',
            'valor_acrescimo',
            'parcelas',
            'id_forma_pagamento',
            'pesquisa_item'
        ]

    for key in session_keys:
        session.pop(key, None)


def retorna_clientes_fornecedores(tipo):
    if tipo == 1:
        retorno = ClientesFornecedores.query.filter(ClientesFornecedores.tipo_cadastro.in_([1, 3]),
                                                    ClientesFornecedores.cpf.isnot(None),
                                                    ClientesFornecedores.situacao == 1).all()
    else:
        retorno = ClientesFornecedores.query.filter(ClientesFornecedores.tipo_cadastro.in_([2, 3]),
                                                    ClientesFornecedores.cnpj.isnot(None),
                                                    ClientesFornecedores.situacao == 1).all()
    return retorno


def retorna_tipo_conta_bancaria():
    return [(1, 'Conta Caixa'), (2, 'Conta Bancária'), (3, 'Conta Máquina Cartão')]


def retorna_tipo_fornecedor():
    retorno = [(1, 'CPF'), (2, 'CNPJ')]
    return retorno


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


def verifica_fat_cartao_credito_transacao_financeira(fatura):
    verifica_transacao = TransacoesFinanceiras.query.filter(TransacoesFinanceiras.tipo_lancamento == 1,
                                                            TransacoesFinanceiras.id_categoria_financeira == 2,
                                                            TransacoesFinanceiras.tipo_transacao == 1,
                                                            TransacoesFinanceiras.id_fatura_cartao_credito == fatura.id).first()
    cartao = CartaoCredito.query.filter_by(id=fatura.id_cartao_credito).first()

    if verifica_transacao:
        verifica_transacao.valor_transacao = fatura.valor_fatura
        verifica_transacao.valor_pago = fatura.valor_pago
        verifica_transacao.data_vencimento = fatura.data_vcto
        verifica_transacao.tipo_lancamento = 1
        verifica_transacao.id_usuario_cadastro = current_user.id
        verifica_transacao.id_cartao_credito = fatura.id_cartao_credito
        verifica_transacao.data_pagamento = fatura.data_pagamento
        verifica_transacao.id_conta_bancaria = cartao.id_conta_bancaria
        database.session.commit()

    else:
        nova_transacao = TransacoesFinanceiras(tipo_transacao=1,
                                               tipo_lancamento=1,
                                               id_categoria_financeira=2,
                                               id_fatura_cartao_credito=fatura.id,
                                               data_vencimento=fatura.data_vcto,
                                               id_usuario_cadastro=current_user.id,
                                               lote_transacao=busc_lote_transacao(),
                                               valor_pago=fatura.valor_pago,
                                               valor_transacao=fatura.valor_fatura,
                                               id_cartao_credito=fatura.id_cartao_credito,
                                               data_pagamento=fatura.data_pagamento,
                                               id_conta_bancaria=cartao.id_conta_bancaria,
                                               id_forma_pagamento=1,
                                               situacao_transacao=1,
                                               situacao=1,
                                               data_ocorrencia=fatura.data_vcto)
        database.session.add(nova_transacao)
        database.session.commit()


def vincula_fat_cartao_credito_transacao_financeira(fatura=False):
    if fatura:
        verifica_fat_cartao_credito_transacao_financeira(fatura)
    else:
        faturas = FaturaCartaoCredito.query.filter(or_(
            FaturaCartaoCredito.situacao_fatura == 0,
            FaturaCartaoCredito.situacao_fatura == 2)).all()
        for fatura in faturas:
            verifica_fat_cartao_credito_transacao_financeira(fatura)


def calcula_valor_utilizado_cartao(credito, tipo=11):
    valor_utilizado = database.session.query(
        func.coalesce(func.sum(FaturaCartaoCredito.valor_fatura), 0)
    ).filter(
        FaturaCartaoCredito.id_cartao_credito == credito.id,
        or_(
            FaturaCartaoCredito.situacao_fatura == 0,
            FaturaCartaoCredito.situacao_fatura == 2
        )
    ).scalar()
    valor_disponivel = credito.valor_limite - valor_utilizado
    credito.valor_gasto = valor_utilizado
    credito.valor_disponivel = valor_disponivel
    conferencia = Conferencias(id_cartao=credito.id,
                               id_funcao=tipo)
    database.session.add(conferencia)
    database.session.commit()


def calcula_gastos_fatura_cartao(fatura):
    gastos = database.session.query(
        func.coalesce(func.sum(TransacoesFinanceiras.valor_transacao), 0)
    ).join(CategoriasFinanceiras, CategoriasFinanceiras.id == TransacoesFinanceiras.id_categoria_financeira
    ).filter(
        TransacoesFinanceiras.id_fatura_cartao_credito == fatura.id,
        CategoriasFinanceiras.tipo_transacao_financeira.in_([2, 3, 5])
    ).scalar()
    return gastos


def calcula_abatimentos_fatura_cartao(fatura):
    abatimentos = database.session.query(
        func.coalesce(func.sum(TransacoesFinanceiras.valor_transacao), 0)
    ).join(CategoriasFinanceiras, CategoriasFinanceiras.id == TransacoesFinanceiras.id_categoria_financeira
    ).filter(
        TransacoesFinanceiras.id_fatura_cartao_credito == fatura.id,
        CategoriasFinanceiras.tipo_transacao_financeira.in_([1, 4])
    ).scalar()
    return abatimentos


def atualiza_valores_faturas(fatura, tipo=9):
    gastos = calcula_gastos_fatura_cartao(fatura)
    abatimentos = calcula_abatimentos_fatura_cartao(fatura)
    fatura.valor_fatura = gastos - abatimentos
    conferencia = Conferencias(id_fatura=fatura.id,
                               id_funcao=tipo)
    database.session.add(conferencia)
    database.session.commit()


def atualiza_cartao(cartao=False):
    if cartao:
        for fatura in FaturaCartaoCredito.query.filter(
                and_(
                    FaturaCartaoCredito.id_cartao_credito == cartao.id,
                    or_(
                        FaturaCartaoCredito.situacao_fatura == 0,
                        FaturaCartaoCredito.situacao_fatura == 2
                    )
                )
        ).all():
            atualiza_valores_faturas(fatura)
            vincula_fat_cartao_credito_transacao_financeira(fatura)
        calcula_valor_utilizado_cartao(cartao)
    else:
        for cartao in CartaoCredito.query.filter_by(situacao=1).all():
            for fatura in FaturaCartaoCredito.query.filter(
                    and_(
                        FaturaCartaoCredito.id_cartao_credito == cartao.id,
                        or_(
                            FaturaCartaoCredito.situacao_fatura == 0,
                            FaturaCartaoCredito.situacao_fatura == 2
                        )
                    )
            ).all():
                atualiza_valores_faturas(fatura, tipo=8)
                vincula_fat_cartao_credito_transacao_financeira(fatura)
            calcula_valor_utilizado_cartao(cartao, tipo=10)


def calcula_entradas(conta):
    entradas = database.session.query(
        func.coalesce(func.sum(TransacoesFinanceiras.valor_transacao), 0)
    ).join(CategoriasFinanceiras, CategoriasFinanceiras.id == TransacoesFinanceiras.id_categoria_financeira
    ).filter(
        TransacoesFinanceiras.id_conta_bancaria == conta.id,
        CategoriasFinanceiras.tipo_transacao_financeira.in_([1, 4]),
        TransacoesFinanceiras.tipo_lancamento == 1
    ).scalar()

    return entradas


def calcula_saidas(conta):
    saidas = database.session.query(
        func.coalesce(func.sum(TransacoesFinanceiras.valor_transacao), 0)
    ).join(CategoriasFinanceiras, CategoriasFinanceiras.id == TransacoesFinanceiras.id_categoria_financeira
    ).filter(
        TransacoesFinanceiras.id_conta_bancaria == conta.id,
        CategoriasFinanceiras.tipo_transacao_financeira.in_([2, 3, 5]),
        TransacoesFinanceiras.tipo_lancamento == 1
    ).scalar()
    return saidas


def ajusta_saldo_contas(conta=False, tipo=7):
    if conta:
        entradas = calcula_entradas(conta)
        saidas = calcula_saidas(conta)
        saldo = entradas - saidas
        conta.saldo_conta = saldo
        if conta.saldo_conta < 0:
            conta.cheque_especial_utilizado = saldo
            conta.cheque_especial_disponivel = conta.cheque_especial - saldo
        else:
            conta.cheque_especial_utilizado = 0
            conta.cheque_especial_disponivel = conta.cheque_especial
        conferencia = Conferencias(id_conta=conta.id,
                                   id_funcao=tipo)
        database.session.add(conferencia)
        database.session.commit()
    else:
        for conta in ContasBancarias.query.filter_by(situacao=1).all():
            entradas = calcula_entradas(conta)
            saidas = calcula_saidas(conta)
            saldo = entradas - saidas
            conta.saldo_conta = saldo
            if conta.saldo_conta < 0:
                conta.cheque_especial_utilizado = saldo
                conta.cheque_especial_disponivel = conta.cheque_especial + saldo
            else:
                conta.cheque_especial_utilizado = 0
                conta.cheque_especial_disponivel = conta.cheque_especial
            conferencia = Conferencias(id_conta=conta.id,
                                       id_funcao=tipo)
            database.session.add(conferencia)
            database.session.commit()


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
    qtd_final = qtd_entradas - qtd_saidas

    try:
        custo_final = (database.session.query(
            func.coalesce(func.sum(TransacoesEstoque.valor_unitario_medio_custo), 0)
        ).filter(
            TransacoesEstoque.id_item == item.id,
            TransacoesEstoque.tipo_transacao.in_([1, 3, 5, 7])
        ).scalar()) * qtd_final
    except:
        custo_final = 0

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


def calcular_soma_qtd_item(id_ticket_comercial=False):
    if id_ticket_comercial:
        situacoes = [0, 1]  # Situações desejadas

        # Consulta para calcular a soma
        soma_qtd = database.session.query(database.func.sum(ItensTicketsComerciais.qtd)) \
            .filter(ItensTicketsComerciais.id_ticket_comercial == id_ticket_comercial) \
            .filter(ItensTicketsComerciais.situacao_item_ticket.in_(situacoes)) \
            .scalar()

        return int(soma_qtd) if soma_qtd is not None else 0
    else:
        return 0


app.add_template_global(calcular_soma_qtd_item, 'calcular_soma_qtd_item')


def cria_nome_item_estoque(itens_estoque_id):
    if itens_estoque_id:
        itens_estoque = ItensEstoque.query.filter_by(id=itens_estoque_id).first()
        tipo_roupa = TiposRoupas.query.filter_by(id=itens_estoque.id_tipo_roupa ).first()
        tamanho = Tamanhos.query.filter_by(id=itens_estoque.id_tamanho).first()
        marca = Marcas.query.filter_by(id=itens_estoque.id_marca).first()
        genero = GeneroRoupa.query.filter_by(id=itens_estoque.id_genero).first()
        cor = Cores.query.filter_by(id=itens_estoque.id_cor).first()
        nome_produto = tipo_roupa.nome_tipo_roupa + ' ' + genero.nome_genero + ' ' + cor.nome_cor + ' ' + marca.nome_marca + ' ' + tamanho.nome_tamanho
        return nome_produto


app.add_template_global(cria_nome_item_estoque, 'cria_nome_item_estoque')


def retorna_item_estoque(id_item):
    if id_item:
        item = ItensEstoque.query.filter_by(codigo_item=id_item).first()
        return item


app.add_template_global(retorna_item_estoque, 'retorna_item_estoque')


def retorno_situacao_fatura(sit):
    if sit == 1:
        return 'em aberto'
    if sit == 2:
        return 'vencida'
    if sit == 3:
        return 'paga'
    if sit == 4:
        return 'paga em atraso'
    if sit == 5:
        return 'paga adiantado'


app.add_template_global(retorno_situacao_fatura, 'retorno_situacao_fatura')


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
            nome=form.nome_fantasia.data,
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
            cliente_fornecedor.nome = form.nome_fantasia.data
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

# TICKETS COMPRA ESTOQUE

@app.route('/comercial/comprasestoque')
@login_required
def home_compra_estoque():
    return render_template('home_compras_estoque.html')


@app.route('/comercial/compraestoque/cadastraitem', methods=['GET', 'POST'])
@login_required
def cadastra_item_nao_encontrado():
    form = FormItensNaoEncontrados()
    form.id_genero.choices = [(genero.id, genero.nome_genero) for genero in
                              GeneroRoupa.query.filter_by(situacao=1).all()]
    form.id_tipo_roupa.choices = [(tipo.id, tipo.nome_tipo_roupa) for tipo in
                                  TiposRoupas.query.filter_by(situacao=1).all()]
    form.id_cor.choices = [(cor.id, cor.nome_cor) for cor in Cores.query.filter_by(situacao=1).all()]
    form.id_tamanho.choices = [(tamanho.id, tamanho.nome_tamanho) for tamanho in
                               Tamanhos.query.filter_by(situacao=1).all()]
    form.id_marca.choices = [(marca.id, marca.nome_marca) for marca in Marcas.query.filter_by(situacao=1).all()]
    form.id_tipo_unidade.choices = [(tipo_unidade.id, tipo_unidade.nome_tipo_unidade) for tipo_unidade in
                                    TiposUnidades.query.filter_by(situacao=1).all()]
    if form.validate_on_submit():
        consulta = ItensEstoque.query.filter(ItensEstoque.codigo_item == form.codigo_item.data).first()
        if consulta:
            flash('Código do produto já existe em nosso banco de dados', 'alert-danger')
        else:
            vlr_estoque_custo = string_to_float(form.valor_total_custo.data)
            vlr_medio_venda = string_to_float(form.valor_unitario_venda.data)
            try:
                valor_unitario_medio_custo = string_to_float(form.valor_total_custo.data) / string_to_float(
                    form.qtd_inicial.data)
            except:
                valor_unitario_medio_custo = float(0)
            try:
                valor_total_medio_venda = string_to_float(form.valor_unitario_venda.data) * string_to_float(
                    form.qtd_inicial.data)
            except:
                valor_total_medio_venda = float(0)
            itens_estoque = ItensEstoque(id_tipo_roupa=int(form.id_tipo_roupa.data),
                                         id_tamanho=int(form.id_tamanho.data),
                                         id_genero=int(form.id_genero.data),
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
                                                  qtd_transacao=0,
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
            if session.get('compra_estoque'):
                session.pop('compra_estoque', None)
                return redirect(url_for('cadastra_compra'))
            else:
                return redirect(url_for('cadastra_venda'))
    return render_template('cadastro_itens_nao_encontrados.html', form=form)


@app.route('/comercial/comprasestoque/cadastrar/itenstickets/<id>/<tipo_ticket>/cancelar')
@login_required
def altera_status_item(id, tipo_ticket):
    item = ItensTicketsComerciais.query.filter_by(id=int(id)).first()
    item.situacao_item_ticket = 2
    database.session.commit()
    ticket = TicketsComerciais.query.filter_by(id=item.id_ticket_comercial).first()
    ticket.valor_ticket = calcular_soma_valor_item(item.id_ticket_comercial)
    ticket.valor_final = calcula_valor_final_compra_estoque(ticket.valor_ticket, ticket.valor_acrescimo,
                                       ticket.valor_desconto)
    database.session.commit()
    if tipo_ticket == '2':
        return redirect(url_for('cadastra_compra'))
    elif tipo_ticket == '3':
        return redirect(url_for('cadastra_venda'))


@app.route('/comercial/comprasestoque/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastra_compra():
    if 'id_ticket_compra' in session:
        ticket_atual = TicketsComerciais.query.filter_by(id=int(session['id_ticket_compra'])).first()
        if not session.get('valor_acrescimo'):
            session['valor_acrescimo'] = ticket_atual.valor_acrescimo
        if not session.get('valor_desconto'):
            session['valor_desconto'] = ticket_atual.valor_desconto

        if not session.get('tipo_fornecedor'):
            if ticket_atual.id_fornecedor:
                fornecedor = ClientesFornecedores.query.filter_by(id=ticket_atual.id_fornecedor).first()
                if fornecedor.cpf:
                    tipo_fornecedor = 1
                elif fornecedor.cnpj:
                    tipo_fornecedor = 2
                else:
                    tipo_fornecedor = 2
            else:
                tipo_fornecedor = 2
        else:
            tipo_fornecedor = int(session.get('tipo_fornecedor'))

        if not session.get('parcelas'):
            session['parcelas'] = 1

        if not session.get('nro_documento_fiscal'):
            session['nro_documento_fiscal'] = ticket_atual.nro_documento_fiscal

        if not session.get('situacao'):
            session['situacao'] = ticket_atual.situacao

        temporario = TemporariaCompraEstoque(id_documento_fiscal=session.get('id_documento_fiscal'),
                                             tipo_fornecedor=tipo_fornecedor,
                                             nro_documento_fiscal=session.get('nro_documento_fiscal'),
                                             emissao_documento_fiscal=converte_str_datetime_select_field(session.get('emissao_documento_fiscal')),
                                             valor_desconto=session.get('valor_desconto'),
                                             valor_acrescimo=session.get('valor_acrescimo'),
                                             parcelas=session.get('parcelas'),
                                             id_forma_pagamento=session.get('id_forma_pagamento'),
                                             data_chegada=converte_str_datetime_select_field(session.get('data_chegada')),
                                             data_prazo=converte_str_datetime_select_field(session.get('data_prazo')),
                                             situacao=session.get('situacao'))
        form = FormCadastroCompraEstoque(obj=temporario)
    else:
        data_atual = datetime.now()

        abertura = TemporariaCompraEstoque(tipo_fornecedor=2,
                                           emissao_documento_fiscal=data_atual,
                                           data_prazo=data_atual,
                                           data_chegada=data_atual,
                                           parcelas=1,
                                           valor_desconto='0,0',
                                           valor_acrescimo='0,0')
        form = FormCadastroCompraEstoque(obj=abertura)

        cadastrar_ticket = TicketsComerciais()
        popula_ticket(cadastrar_ticket, form, 0)
        cadastrar_ticket.valor_desconto = recebe_form_valor_monetario(cadastrar_ticket.valor_desconto) or 0.0
        cadastrar_ticket.valor_acrescimo = recebe_form_valor_monetario(cadastrar_ticket.valor_acrescimo) or 0.0

        database.session.add(cadastrar_ticket)
        database.session.commit()
        ticket_atual = cadastrar_ticket

    if session.get('pesquisa_cpf'):
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome) for fornecedor in retorna_clientes_fornecedores(1)]
        session.pop('pesquisa_cpf', None)
    elif session.get('pesquisa_cnpj'):
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome_fantasia) for fornecedor in retorna_clientes_fornecedores(2)]
        session.pop('pesquisa_cnpj', None)
    else:
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome) for fornecedor in
                                            retorna_clientes_fornecedores(int(form.tipo_fornecedor.data))]

    lista_compras = retorn_lista_itens_tickets_comercial_compras(ticket_atual.id, 1)

    form.id_documento_fiscal.choices = [(documento.id, documento.nome_documento) for documento in DocumentosFiscais.query.filter_by(situacao=1).order_by(DocumentosFiscais.id).all()]
    form.tipo_fornecedor.choices = retorna_tipo_fornecedor()
    form.id_forma_pagamento.choices = [(forma.id, forma.nome_forma_pagamento) for forma in
                                       FormasPagamento.query.filter(FormasPagamento.id_tipo_transacao.in_([1, 3]),
                                       FormasPagamento.situacao == 1).all()]
    form.situacao.choices = retorna_situacoes_ticket_compra()

    clear_sessions_tickets_compra(0)

    # definição de id_ticket DEVE ser antes do submit
    session['id_ticket_compra'] = ticket_atual.id

    if form.validate_on_submit():
        session['id_documento_fiscal'] = form.id_documento_fiscal.data
        session['tipo_fornecedor'] = form.tipo_fornecedor.data
        session['pesquisa_fornecedor'] = form.pesquisa_fornecedor.data
        session['nro_documento_fiscal'] = form.nro_documento_fiscal.data
        session['emissao_documento_fiscal'] = form.emissao_documento_fiscal.data
        session['valor_desconto'] = form.valor_desconto.data or '0,0'
        session['valor_acrescimo'] = form.valor_acrescimo.data or '0,0'
        session['parcelas'] = form.parcelas.data
        session['id_forma_pagamento'] = form.id_forma_pagamento.data
        session['pesquisa_item'] = form.pesquisa_item.data
        session['valor_item'] = form.valor_item.data
        session['data_chegada'] = form.data_chegada.data
        session['data_prazo'] = form.data_prazo.data
        session['situacao'] = form.situacao.data

        popula_ticket(ticket_atual, form, 1, ticket_atual.id)

        if 'pesquisar_fornecedor' in request.form:
            if form.tipo_fornecedor.data == '1':
                session['pesquisa_cpf'] = True
            else:
                session['pesquisa_cnpj'] = True

            return redirect(url_for('cadastra_compra'))

        elif 'finalizar' in request.form:
            if form.id_documento_fiscal.data != '6' and not form.nro_documento_fiscal.data:
                flash('Favor incluir número do documento ou informar "-" para tipo de documento fiscal', 'alert-danger')
                return redirect(url_for('cadastra_compra'))

            if form.situacao.data == '0':
                popula_ticket(ticket_atual, form, 1, ticket_atual.id)
                clear_sessions_tickets_compra(0)
                flash('Compra salva com sucesso.', 'alert-success')
                return redirect(url_for('home_compra_estoque'))

            elif form.situacao.data == '4':
                popula_ticket(ticket_atual, form, 2, ticket_atual.id)
                clear_sessions_tickets_compra(0)
                flash('Compra salva com sucesso.', 'alert-success')
                return redirect(url_for('home_compra_estoque'))

            elif form.situacao.data == '5':
                forma_pagamento = FormasPagamento.query.filter_by(id=int(form.id_forma_pagamento.data)).first()
                if forma_pagamento.parcelado == 0 and form.parcelas.data != '1':
                    flash('Favor verificar forma de pagamento e número de parcelas, foi selecionado forma de pagamento à vista e múltiplas parcelas.', 'alert-warning')
                    return redirect(url_for('cadastra_compra'))

                if forma_pagamento.parcelado == 1 and form.parcelas.data == '1':
                    flash('Favor verificar forma de pagamento e número de parcelas, foi selecionado forma de pagamento parcelado e parcela única.', 'alert-warning')
                    return redirect(url_for('cadastra_compra'))

                ticket_atual = popula_ticket(ticket_atual, form, 3, ticket_atual.id)

                faturas = TransacoesFinanceiras.query.filter(TransacoesFinanceiras.id_ticket == ticket_atual.id).first()
                if faturas:
                    cria_fatura_ticket(ticket_atual, 0)
                    cria_fatura_ticket(ticket_atual, 1)
                else:
                    cria_fatura_ticket(ticket_atual, 1)

                itens = ItensTicketsComerciais.query.filter(ItensTicketsComerciais.id_ticket_comercial == ticket_atual.id,
                                                            ItensTicketsComerciais.situacao_item_ticket.in_([0,1])).all()

                rateia_valores_adicionais(ticket_atual, itens)
                if itens:
                    for item in itens:
                        if item.situacao_item_ticket == 0:
                            item.situacao_item_ticket = 1
                    database.session.commit()

                # Consulta para buscar transações
                transacoes = TransacoesEstoque.query.filter(TransacoesEstoque.id_ticket == ticket_atual.id,
                                                            TransacoesEstoque.situacao == 1).first()

                if transacoes:
                    cria_transacao_estoque(itens, ticket_atual, 2)
                    cria_transacao_estoque(itens, ticket_atual, 1)
                else:
                    cria_transacao_estoque(itens, ticket_atual, 1)
                clear_sessions_tickets_compra(0)
                flash('Compra salva com sucesso.', 'alert-success')
                return redirect(url_for('home_compra_estoque'))

        elif 'pesquisar_item' in request.form:
            if form.valor_item.data == '':
                flash('Favor inserir valor', 'alert-warning')
                return redirect(url_for('cadastra_compra'))
            if form.pesquisa_item.data == '':
                flash('Favor inserir Código Item', 'alert-warning')
                return redirect(url_for('cadastra_compra'))
            item = ItensEstoque.query.filter_by(codigo_item=form.pesquisa_item.data).first()
            if item:
                cadastro = ItensTicketsComerciais(id_ticket_comercial=ticket_atual.id,
                                                  codigo_item=item.codigo_item,
                                                  situacao_item_ticket=0,
                                                  id_usuario_cadastro=current_user.id,
                                                  qtd=int(form.qtd_item.data),
                                                  valor_item=string_to_float(form.valor_item.data) * int(form.qtd_item.data))
                database.session.add(cadastro)
                database.session.commit()

                ticket_atual.valor_ticket = calcular_soma_valor_item(ticket_atual.id)
                ticket_atual.valor_final = calcular_soma_valor_item(ticket_atual.id) - ticket_atual.valor_desconto + ticket_atual.valor_acrescimo

                database.session.commit()
            else:
                flash('Código não encontrado, favor cadastre o item e após você será redirecionado para a página anterior.', 'alert-danger')
                session['compra_estoque'] = True
                return redirect(url_for('cadastra_item_nao_encontrado'))

            return redirect(url_for('cadastra_compra'))

    return render_template('cadastro_compra_estoque.html', ticket_atual=ticket_atual, len=len, enumerate=enumerate, float=float, form=form, lista_compras=lista_compras)


@app.route('/comercial/comprasestoque/lista')
@login_required
def lista_tickets_compras():
    tickets_nao_finalizados = False
    tickets_compras_nao_recebidas = False
    tickets_compras_recebidas = False
    if not session.get('tickets_nao_finalizados') and not session.get('tickets_compras_nao_recebidas') and not session.get('tickets_compras_recebidas'):
        tickets_nao_finalizados = 'active'
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2, TicketsComerciais.situacao == 0).order_by(TicketsComerciais.id.desc()).all()
    if session.get('tickets_nao_finalizados'):
        tickets_nao_finalizados = 'active'
        session.pop('tickets_nao_finalizados', None)
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2,
                                                 TicketsComerciais.situacao == 0).order_by(
            TicketsComerciais.id.desc()).all()
    if session.get('tickets_compras_nao_recebidas'):
        tickets_compras_nao_recebidas = 'active'
        session.pop('tickets_compras_nao_recebidas', None)
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2,
                                                 TicketsComerciais.situacao == 4).order_by(
            TicketsComerciais.id.desc()).all()
    if session.get('tickets_compras_recebidas'):
        tickets_compras_recebidas = 'active'
        session.pop('tickets_compras_recebidas', None)
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2,
                                                 TicketsComerciais.situacao >= 5).order_by(
            TicketsComerciais.id.desc()).all()
    return render_template('lista_tickets_compras.html', str=str, tickets_nao_finalizados=tickets_nao_finalizados,
                           tickets_compras_nao_recebidas=tickets_compras_nao_recebidas, tickets_compras_recebidas=tickets_compras_recebidas, tickets=tickets,
                           fornecedores=ClientesFornecedores, tipos_doc=DocumentosFiscais, situacoes=retorna_situacoes_tickets(), forma_pagamento=FormasPagamento)


@app.route('/comercial/comprasestoque/lista/enc/<situacao>')
@login_required
def encaminha_lista_tickets_compras(situacao):
    if situacao == '1':
        session['tickets_nao_finalizados'] = True
    elif situacao == '2':
        session['tickets_compras_nao_recebidas'] = True
    elif situacao == '3':
        session['tickets_compras_recebidas'] = True
    return redirect(url_for('lista_tickets_compras'))


@app.route('/comercial/comprasestoque/<id_ticket>')
@login_required
def ticket_compra_estoque(id_ticket):
    if session.get('faturas_ticket'):
        session.pop('faturas_ticket', None)
        return redirect(url_for('faturas_ticket_compra', id_ticket=id_ticket))
    else:
        #TODO: por encaminhamento para outras paginas quando não for ticket compra estoque
        ticket = TicketsComerciais.query.filter_by(id=int(id_ticket)).first()
        forncedor = ClientesFornecedores.query.filter_by(id=ticket.id_fornecedor).first()
        if forncedor.cpf:
            nome_fornecedor = forncedor.nome
        else:
            nome_fornecedor = forncedor.nome_fantasia

        itens = ItensTicketsComerciais.query.filter(ItensTicketsComerciais.id_ticket_comercial == ticket.id,
                                                    ItensTicketsComerciais.situacao_item_ticket.in_([0,1])).all()
        return render_template('ticket_compra_estoque.html', ticket=ticket, situacoes=retorna_situacoes_tickets(), nome_fornecedor=nome_fornecedor,
                           tipos_doc=DocumentosFiscais, fornecedor=forncedor, forma_pagamento=FormasPagamento, dados_ticket='active', lista_faturas=False, itens=itens, estoque=ItensEstoque)


@app.route('/comercial/compraestoque/<id_ticket>/enc/faturas')
@login_required
def encaminha_faturas_ticket_compra(id_ticket):
    session['faturas_ticket'] = True
    return redirect(url_for('ticket_compra_estoque', id_ticket=id_ticket))

@app.route('/comercial/compraestoque/<id_ticket>/faturas')
@login_required
def faturas_ticket_compra(id_ticket):
    faturas = TransacoesFinanceiras.query.filter(TransacoesFinanceiras.id_ticket == int(id_ticket),
                                                 TransacoesFinanceiras.situacao == 1).all()

    ticket = TicketsComerciais.query.filter_by(id=int(id_ticket)).first()
    return render_template('faturas_ticket_compra.html', faturas=faturas, dados_ticket=False, lista_faturas='active',
                           ticket=ticket, categorias=CategoriasFinanceiras, contas=ContasBancarias, cartoes=CartaoCredito, faturass=FaturaCartaoCredito)


@app.route('/comercial/compraestoque/<id_ticket>/enc/editar')
@login_required
def editar_ticket_compra(id_ticket):
    ticket = TicketsComerciais.query.filter_by(id=int(id_ticket)).first()
    if ticket.situacao not in [0, 4, 5, 6]:
        flash('Ticket já possui faturas lançadas, favor falar com o financeiro', 'alert-danger')
        return redirect(url_for('ticket_compra_estoque', id_ticket=id_ticket))
    session['id_ticket_compra'] = int(id_ticket)
    return redirect(url_for('cadastra_compra'))

# TICKETS VENDAS

@app.route('/comercial/vendamercadoria')
@login_required
def home_venda_mercadoria():
    return render_template('home_vendas_mercadoria.html')


@app.route('/comercial/vendamercadoria/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastra_venda():
    pagamento_concluido = False
    if 'id_ticket' in session:
        ticket_atual = TicketsComerciais.query.filter_by(id=int(session['id_ticket'])).first()
        if not session.get('valor_acrescimo'):
            session['valor_acrescimo'] = ticket_atual.valor_acrescimo
        if not session.get('valor_desconto'):
            session['valor_desconto'] = ticket_atual.valor_desconto

        pagamentos = retorna_total_faturas_ticket_venda(ticket_atual.id)

        restante = ticket_atual.valor_final - pagamentos

        pagamento_concluido = pagamentos == ticket_atual.valor_final

        if not session.get('tipo_fornecedor'):
            if ticket_atual.id_fornecedor:
                fornecedor = ClientesFornecedores.query.filter_by(id=ticket_atual.id_fornecedor).first()
                if fornecedor.cpf:
                    tipo_fornecedor = 1
                elif fornecedor.cnpj:
                    tipo_fornecedor = 2
                else:
                    tipo_fornecedor = 1
            else:
                tipo_fornecedor = 1
        else:
            tipo_fornecedor = int(session.get('tipo_fornecedor'))

        if not session.get('parcelas'):
            session['parcelas'] = 1

        if not session.get('nro_documento_fiscal'):
            session['nro_documento_fiscal'] = ticket_atual.nro_documento_fiscal

        if not session.get('situacao'):
            session['situacao'] = ticket_atual.situacao

        temporario = TemporariaCompraEstoque(id_documento_fiscal=session.get('id_documento_fiscal'),
                                             tipo_fornecedor=tipo_fornecedor,
                                             nro_documento_fiscal=session.get('nro_documento_fiscal'),
                                             emissao_documento_fiscal=converte_str_datetime_select_field(session.get('emissao_documento_fiscal')),
                                             valor_desconto=session.get('valor_desconto'),
                                             valor_acrescimo=session.get('valor_acrescimo'),
                                             pesquisa_fornecedor=session.get('pesquisa_fornecedor'),
                                             parcelas=session.get('parcelas'),
                                             id_forma_pagamento=session.get('id_forma_pagamento'),
                                             data_chegada=converte_str_datetime_select_field(session.get('data_chegada')),
                                             data_prazo=converte_str_datetime_select_field(session.get('data_prazo')),
                                             situacao=session.get('situacao'))
        form = FormCadastroVendaMercadoria(obj=temporario)
    else:
        data_atual = datetime.now()

        pagamentos = 0

        restante = 0

        abertura = TemporariaCompraEstoque(tipo_fornecedor=2,
                                           emissao_documento_fiscal=data_atual,
                                           data_prazo=data_atual,
                                           data_chegada=data_atual,
                                           parcelas=1,
                                           valor_desconto='0,0',
                                           valor_acrescimo='0,0')
        form = FormCadastroVendaMercadoria(obj=abertura)

        cadastrar_ticket = TicketsComerciais()
        popula_ticket(cadastrar_ticket, form, 4)
        cadastrar_ticket.valor_desconto = recebe_form_valor_monetario(cadastrar_ticket.valor_desconto) or 0.0
        cadastrar_ticket.valor_acrescimo = recebe_form_valor_monetario(cadastrar_ticket.valor_acrescimo) or 0.0

        database.session.add(cadastrar_ticket)
        database.session.commit()
        ticket_atual = cadastrar_ticket

    if session.get('pesquisa_cpf'):
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome) for fornecedor in retorna_clientes_fornecedores(1)]
        session.pop('pesquisa_cpf', None)
    elif session.get('pesquisa_cnpj'):
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome_fantasia) for fornecedor in retorna_clientes_fornecedores(2)]
        session.pop('pesquisa_cnpj', None)
    else:
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome) for fornecedor in
                                            retorna_clientes_fornecedores(int(form.tipo_fornecedor.data))]

    lista_compras = retorn_lista_itens_tickets_comercial_compras(ticket_atual.id, 1)

    form.tipo_fornecedor.choices = retorna_tipo_fornecedor()
    form.id_forma_pagamento.choices = [(forma.id, forma.nome_forma_pagamento) for forma in FormasPagamento.query.filter(FormasPagamento.id_tipo_transacao.in_([2,3]),
                                                                                                                        FormasPagamento.situacao == 1).all()]
    form.situacao.choices = retorna_situacoes_ticket_venda()

    clear_sessions_tickets_compra()

    # definição de id_ticket DEVE ser antes do submit
    session['id_ticket'] = ticket_atual.id

    if form.validate_on_submit():
        session['tipo_fornecedor'] = form.tipo_fornecedor.data
        session['pesquisa_fornecedor'] = form.pesquisa_fornecedor.data
        session['valor_desconto'] = form.valor_desconto.data or '0,0'
        session['valor_acrescimo'] = form.valor_acrescimo.data or '0,0'
        session['parcelas'] = form.parcelas.data
        session['id_forma_pagamento'] = form.id_forma_pagamento.data
        session['pesquisa_item'] = form.pesquisa_item.data
        session['situacao'] = form.situacao.data

        popula_ticket(ticket_atual, form, 5, ticket_atual.id)

        if 'pesquisar_fornecedor' in request.form:
            if form.tipo_fornecedor.data == '1':
                session['pesquisa_cpf'] = True
            else:
                session['pesquisa_cnpj'] = True

            return redirect(url_for('cadastra_venda'))

        elif 'inserir_pagamento' in request.form:
            # forma_pagamento = FormasPagamento.query.filter_by(id=int(form.id_forma_pagamento.data)).first()
            # if forma_pagamento.parcelado == 0 and form.parcelas.data != '1':
            #     flash(
            #         'Favor verificar forma de pagamento e número de parcelas, foi selecionado forma de pagamento à vista e múltiplas parcelas.',
            #         'alert-warning')
            #     return redirect(url_for('cadastra_venda'))
            #
            # if forma_pagamento.parcelado == 1 and form.parcelas.data == '1':
            #     flash(
            #         'Favor verificar forma de pagamento e número de parcelas, foi selecionado forma de pagamento parcelado e parcela única.',
            #         'alert-warning')
            #     return redirect(url_for('cadastra_venda'))



            if form.id_forma_pagamento.data == '1':
                ticket_atual = popula_ticket(ticket_atual, form, 7, ticket_atual.id)
                return redirect(url_for('registra_troco_venda'))

            elif form.id_forma_pagamento.data == '2':
                if form.pesquisa_fornecedor.data == '2':
                    flash('Favor escolher um cliente ou fornecedor cadastrado para compra de parcelamento próprio.', 'alert-warning')
                    return redirect(url_for('cadastra_venda'))
                else:
                    ticket_atual = popula_ticket(ticket_atual, form, 7, ticket_atual.id)
                    return redirect(url_for('registra_pagamento_parcelamento_proprio'))

            elif form.id_forma_pagamento.data in ['7', '8', '9', '10']:
                if form.id_forma_pagamento.data in ['8', '10']:
                    session['parcelado'] = True
                ticket_atual = popula_ticket(ticket_atual, form, 7, ticket_atual.id)
                return redirect(url_for('registra_pagamento_cartao_credito'))

            elif form.id_forma_pagamento.data == '11':
                ticket_atual = popula_ticket(ticket_atual, form, 7, ticket_atual.id)
                session['pagamento'] = 'pix'
                return redirect(url_for('registra_pagamento_cartao_credito'))

            elif form.id_forma_pagamento.data == '12':
                ticket_atual = popula_ticket(ticket_atual, form, 7, ticket_atual.id)
                session['permuta'] = 'permuta'
                return redirect(url_for('registra_troco_venda'))

        elif 'finalizar' in request.form:
            # Itens Estoque
            # itens = ItensTicketsComerciais.query.filter(
            #     ItensTicketsComerciais.id_ticket_comercial == ticket_atual.id,
            #     ItensTicketsComerciais.situacao_item_ticket.in_([0, 1])).all()
            # rateia_valores_adicionais(ticket_atual, itens)
            # if itens:
            #     for item in itens:
            #         if item.situacao_item_ticket == 0:
            #             item.situacao_item_ticket = 1
            #     database.session.commit()
            #
            # transacoes = TransacoesEstoque.query.filter(TransacoesEstoque.id_ticket == ticket_atual.id,
            #                                             TransacoesEstoque.situacao == 1).first()
            #
            # if transacoes:
            #     cria_transacao_estoque(itens, ticket_atual, 2)
            # cria_transacao_estoque(itens, ticket_atual, 3)
            # pass
            clear_sessions_tickets_compra()
            return redirect(url_for('home_venda_mercadoria'))

        elif 'pesquisar_item' in request.form:
            if form.pesquisa_item.data == '':
                flash('Favor inserir Código Item', 'alert-warning')
                return redirect(url_for('cadastra_compra'))
            item = ItensEstoque.query.filter_by(codigo_item=form.pesquisa_item.data).first()
            if item:
                cadastro = ItensTicketsComerciais(id_ticket_comercial=ticket_atual.id,
                                                  codigo_item=item.codigo_item,
                                                  situacao_item_ticket=0,
                                                  id_usuario_cadastro=current_user.id,
                                                  qtd=int(form.qtd_item.data),
                                                  valor_item=item.valor_unitario_venda * int(form.qtd_item.data))
                database.session.add(cadastro)
                database.session.commit()

                ticket_atual.valor_ticket = calcular_soma_valor_item(ticket_atual.id)
                ticket_atual.valor_final = calcular_soma_valor_item(ticket_atual.id) - ticket_atual.valor_desconto + ticket_atual.valor_acrescimo

                database.session.commit()
            else:
                flash('Código não encontrado, favor cadastre o item e após você será redirecionado para a página anterior.', 'alert-danger')
                return redirect(url_for('cadastra_item_nao_encontrado'))

            return redirect(url_for('cadastra_venda'))

    return render_template('cadastro_venda_mercadoria.html', ticket_atual=ticket_atual, len=len, enumerate=enumerate, float=float,
                           form=form, lista_compras=lista_compras, pagamento_concluido=pagamento_concluido, pagamentos=pagamentos, restante=restante)


@app.route('/comercial/vendamercadoria/cadastrar/cartaocredito/avista', methods=['GET', 'POST'])
@login_required
def registra_pagamento_cartao_credito():
    ticket = TicketsComerciais.query.filter_by(id=int(session.get('id_ticket'))).first()
    temporario = TemporariaCompraEstoque(pesquisa_fornecedor=int(session.get('pesquisa_fornecedor')))

    parcelado = session.get('parcelado')

    if parcelado:
        form = FormVendaCartaoCreditoParcelado(obj=temporario)
    else:
        parcelado = False
        form = FormVendaCartaoCreditoAVista(obj=temporario)
    cliente = ClientesFornecedores.query.filter_by(id=ticket.id_cliente).first()
    if cliente.cpf:
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome) for fornecedor in
                                            retorna_clientes_fornecedores(1)]
    else:
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome_fantasia) for fornecedor in
                                            retorna_clientes_fornecedores(2)]

    valor_pago = retorna_total_faturas_ticket_venda(ticket.id)

    if session.get('pagamento') == 'pix':
        form.maquina_cartao.choices = [(maq.id, maq.apelido_conta) for maq in ContasBancarias.query.filter(ContasBancarias.id_tipo_conta.in_([2, 3]),
                                                                                                           ContasBancarias.situacao == 1).all()]
    else:
        form.maquina_cartao.choices = [(maq.id, maq.apelido_conta) for maq in
                                       ContasBancarias.query.filter(ContasBancarias.id_tipo_conta == 3,
                                                                    ContasBancarias.situacao == 1).all()]
    if form.validate_on_submit():
        if parcelado:
            ticket.parcelas = int(form.qtd_parcelas.data)
            database.session.commit()
            cria_fatura_ticket(ticket, 4, valor_parcial=recebe_form_valor_monetario(form.valor_compra.data),
                               conta_bancaria=int(form.maquina_cartao.data))
        else:
            cria_fatura_ticket(ticket, 2, valor_parcial=recebe_form_valor_monetario(form.valor_compra.data), conta_bancaria=int(form.maquina_cartao.data))
        clear_sessions_tickets_compra()
        session['id_ticket'] = ticket.id
        return redirect(url_for('cadastra_venda'))
    return render_template('cadastro_cartao_credito_avista.html', form=form, valor_pago=valor_pago, ticket=ticket,
                           enumerate=enumerate, parcelado=parcelado)


@app.route('/comercial/vendamercadoria/cadastrar/parcelamentoproprio', methods=['GET', 'POST'])
@login_required
def registra_pagamento_parcelamento_proprio():
    ticket = TicketsComerciais.query.filter_by(id=int(session.get('id_ticket'))).first()
    temporario = TemporariaCompraEstoque(pesquisa_fornecedor=int(session.get('pesquisa_fornecedor')))
    form = FormParcelamentoProprio(obj=temporario)
    cliente = ClientesFornecedores.query.filter_by(id=ticket.id_cliente).first()
    if cliente.cpf:
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome) for fornecedor in retorna_clientes_fornecedores(1)]
    else:
        form.pesquisa_fornecedor.choices = [(fornecedor.id, fornecedor.nome_fantasia) for fornecedor in retorna_clientes_fornecedores(2)]

    valor_pago = retorna_total_faturas_ticket_venda(ticket.id)

    if session.get('parcelas_'):
        parcelas = session.get('parcelas_')
    else:
        parcelas = []
    if form.validate_on_submit():
        if 'calcular' in request.form:
            parcelas = calcula_valor_parcelado(recebe_form_valor_monetario(form.valor_a_parcelar.data), int(form.qtd_parcelas.data))
            session['parcelas_'] = parcelas
        else:
            ticket.parcelas = int(form.qtd_parcelas.data)
            cria_fatura_ticket(ticket, 1, valor_parcial=recebe_form_valor_monetario(form.valor_a_parcelar.data))
            ticket.id_cliente = int(form.pesquisa_fornecedor.data)
            database.session.commit()
            clear_sessions_tickets_compra()
            session['id_ticket'] = ticket.id
            return redirect(url_for('cadastra_venda'))
    return render_template('parcelamento_proprio.html', form=form, ticket=ticket, valor_pago=valor_pago, parcelas=parcelas,
                           enumerate=enumerate)


@app.route('/comercial/vendamercadoria/cadastrar/troco', methods=['GET', 'POST'])
@login_required
def registra_troco_venda():
    ticket = TicketsComerciais.query.filter_by(id=int(session.get('id_ticket'))).first()

    form = FormRegistraTrocoVenda(obj=ticket)
    valor_pago = retorna_total_faturas_ticket_venda(ticket.id)
    if session.get('calculo'):
        session.pop('calculo', None)
        valor_troco = recebe_form_valor_monetario(session.get('valor')) - ticket.valor_final
        session.pop('valor', None)
    else:
        valor_troco = 0.0

    valor_venda = ticket.valor_final

    if form.validate_on_submit():
        if 'calcular' in request.form:
            session['calculo'] = True
            session['valor'] = form.valor_recebido.data
            return redirect(url_for('registra_troco_venda'))
        elif 'finalizar' in request.form:
            valor_pago = retorna_total_faturas_ticket_venda(ticket.id)
            valor_pago_total = valor_pago + recebe_form_valor_monetario(form.valor_recebido.data)
            if valor_pago_total > ticket.valor_final:
                flash(f'Valor ultrapassa total do Ticket. Valor restante a pagar é de R$ {{}}')
            clear_sessions_tickets_compra()
            if session.get('permuta') == 'permuta':
                cria_fatura_ticket(ticket, 5, recebe_form_valor_monetario(form.valor_recebido.data))
            else:
                cria_fatura_ticket(ticket, 3, recebe_form_valor_monetario(form.valor_recebido.data))
            session['id_ticket'] = ticket.id
            return redirect(url_for('cadastra_venda'))  # Redirecione para a próxima view apropriada

    return render_template('registra_troco.html', form=form, valor_venda=valor_venda, valor_pago=valor_pago, valor_troco=valor_troco, ticket=ticket)


@app.route('/comercial/vendamercadoria/lista')
@login_required
def lista_tickets_vendas():
    tickets_nao_finalizados = False
    tickets_compras_nao_recebidas = False
    tickets_compras_recebidas = False
    if not session.get('tickets_nao_finalizados') and not session.get('tickets_compras_nao_recebidas') and not session.get('tickets_compras_recebidas'):
        tickets_nao_finalizados = 'active'
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2, TicketsComerciais.situacao == 0).order_by(TicketsComerciais.id.desc()).all()
    if session.get('tickets_nao_finalizados'):
        tickets_nao_finalizados = 'active'
        session.pop('tickets_nao_finalizados', None)
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2,
                                                 TicketsComerciais.situacao == 0).order_by(
            TicketsComerciais.id.desc()).all()
    if session.get('tickets_compras_nao_recebidas'):
        tickets_compras_nao_recebidas = 'active'
        session.pop('tickets_compras_nao_recebidas', None)
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2,
                                                 TicketsComerciais.situacao == 4).order_by(
            TicketsComerciais.id.desc()).all()
    if session.get('tickets_compras_recebidas'):
        tickets_compras_recebidas = 'active'
        session.pop('tickets_compras_recebidas', None)
        tickets = TicketsComerciais.query.filter(TicketsComerciais.id_tipo_ticket == 2,
                                                 TicketsComerciais.situacao >= 5).order_by(
            TicketsComerciais.id.desc()).all()
    return render_template('lista_tickets_compras.html', str=str, tickets_nao_finalizados=tickets_nao_finalizados,
                           tickets_compras_nao_recebidas=tickets_compras_nao_recebidas, tickets_compras_recebidas=tickets_compras_recebidas, tickets=tickets,
                           fornecedores=ClientesFornecedores, tipos_doc=DocumentosFiscais, situacoes=retorna_situacoes_tickets(), forma_pagamento=FormasPagamento)


@app.route('/comercial/vendamercadoria/lista/enc/<situacao>')
@login_required
def encaminha_lista_tickets_vendas(situacao):
    if situacao == '1':
        session['tickets_nao_finalizados'] = True
    elif situacao == '2':
        session['tickets_compras_nao_recebidas'] = True
    elif situacao == '3':
        session['tickets_compras_recebidas'] = True
    return redirect(url_for('lista_tickets_compras'))


@app.route('/comercial/vendamercadoria/<id_ticket>')
@login_required
def ticket_venda_mercadoria(id_ticket):
    if session.get('faturas_ticket'):
        session.pop('faturas_ticket', None)
        return redirect(url_for('faturas_ticket_compra', id_ticket=id_ticket))
    else:
        #TODO: por encaminhamento para outras paginas quando não for ticket compra estoque
        ticket = TicketsComerciais.query.filter_by(id=int(id_ticket)).first()
        forncedor = ClientesFornecedores.query.filter_by(id=ticket.id_fornecedor).first()
        if forncedor.cpf:
            nome_fornecedor = forncedor.nome
        else:
            nome_fornecedor = forncedor.nome_fantasia

        itens = ItensTicketsComerciais.query.filter(ItensTicketsComerciais.id_ticket_comercial == ticket.id,
                                                    ItensTicketsComerciais.situacao_item_ticket.in_([0,1])).all()
        return render_template('ticket_compra_estoque.html', ticket=ticket, situacoes=retorna_situacoes_tickets(), nome_fornecedor=nome_fornecedor,
                           tipos_doc=DocumentosFiscais, fornecedor=forncedor, forma_pagamento=FormasPagamento, dados_ticket='active', lista_faturas=False, itens=itens, estoque=ItensEstoque)


@app.route('/comercial/vendamercadoria/<id_ticket>/enc/faturas')
@login_required
def encaminha_faturas_ticket_venda(id_ticket):
    session['faturas_ticket'] = True
    return redirect(url_for('ticket_compra_estoque', id_ticket=id_ticket))

@app.route('/comercial/vendamercadoria/<id_ticket>/faturas')
@login_required
def faturas_ticket_venda(id_ticket):
    faturas = TransacoesFinanceiras.query.filter(TransacoesFinanceiras.id_ticket == int(id_ticket),
                                                 TransacoesFinanceiras.situacao == 1).all()

    ticket = TicketsComerciais.query.filter_by(id=int(id_ticket)).first()
    return render_template('faturas_ticket_compra.html', faturas=faturas, dados_ticket=False, lista_faturas='active',
                           ticket=ticket, categorias=CategoriasFinanceiras, contas=ContasBancarias, cartoes=CartaoCredito, faturass=FaturaCartaoCredito)


@app.route('/comercial/compraestoque/<id_ticket>/enc/editar')
@login_required
def editar_ticket_venda(id_ticket):
    ticket = TicketsComerciais.query.filter_by(id=int(id_ticket)).first()
    if ticket.situacao not in [0, 4, 5, 6]:
        flash('Ticket já possui faturas lançadas, favor falar com o financeiro', 'alert-danger')
        return redirect(url_for('ticket_compra_estoque', id_ticket=id_ticket))
    session['id_ticket'] = int(id_ticket)
    return redirect(url_for('cadastra_compra'))

# TICKETS CONDICIONAIS

@app.route('/comercial/condicionais')
@login_required
def home_tickets_condicionais():
    return render_template('home_tickets_condicionais.html')

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
                                         valor_estoque_venda=vlr_estoque_custo * string_to_float(form.qtd_inicial.data),
                                         valor_unitario_venda=vlr_medio_venda,
                                         qtd_minima=string_to_float(form.qtd_minima.data),
                                         id_usuario_cadastro=current_user.id)

            database.session.add(itens_estoque)
            database.session.commit()
            item_estoque = ItensEstoque.query.filter_by(codigo_item=form.codigo_item.data).first()
            tipo_transacao = 7
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
    nome_roupa = cria_nome_item_estoque(itens_estoque.id)
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
        transacoes = TransacoesEstoque.query.filter(TransacoesEstoque.id_item == item_id, TransacoesEstoque.situacao == 1).all()
    elif session.get('todas_transacoes'):
        session.pop('todas_transacoes', None)
        todas_transacoes = 'active'
        transacoes = TransacoesEstoque.query.filter(
            TransacoesEstoque.id_item == item_id, TransacoesEstoque.situacao == 1).all()
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
    return render_template('lista_transacoes_estoque.html', itens_estoque_id=itens_estoque_id, item_id=item_id,transacoes=transacoes,
                           transacao_item=transacao_item, todas_transacoes=todas_transacoes, transacoes_entrada=transacoes_entrada,
                           transacoes_saida=transacoes_saida, usuarios=Usuarios)


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
        itens_estoque.valor_estoque_venda = recebe_form_valor_monetario(form.valor_unitario_venda.data) * itens_estoque.qtd
        itens_estoque.valor_unitario_venda = recebe_form_valor_monetario(form.valor_unitario_venda.data)
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
                                          id_banco=int(session.get('id_banco')),
                                          id_cliente=id_banco,
                                          apelido_agencia=session.get('apelido_agencia'))

    bancos = Bancos.query.all()
    if bancos:
        form_agencia.id_banco.choices = [(banco.id, banco.nome_banco) for banco in bancos]
    else:
        form_agencia.id_banco.choices = ['']

    fornecedores = buscar_cliente_fornecedor_cnpj(session.get('pesquisa_bancos'))
    if fornecedores:
        form_agencia.id_cliente.choices = [(fornecedor.id, fornecedor.razao_social) for fornecedor in fornecedores]
    else:
        form_agencia.id_cliente.choices = ['']

    form_agencia.situacao.choices = [(1, 'Ativo'), (2, 'Inativo')]
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
    form.id_tipo_conta.choices = retorna_tipo_conta_bancaria()
    if form.validate_on_submit():
        session['id_agencia'] = form.id_agencia.data
        session['apelido_conta'] = form.apelido_conta.data
        session['nro_conta'] = form.nro_conta.data
        session['digito_conta'] = form.digito_conta.data
        session['campo_pesquisa'] = form.campo_pesquisa.data
        session['cheque_especial'] = form.cheque_especial.data
        session['saldo_conta'] = form.saldo_conta.data
        session['id_tipo_conta'] = form.id_tipo_conta.data
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
                                     id_tipo_conta=session.get('id_tipo_conta'),
                                     apelido_conta=session.get('apelido_conta'),
                                     nro_conta=session.get('nro_conta'),
                                     digito_conta=session.get('digito_conta'),
                                     campo_pesquisa=session.get('campo_pesquisa'),
                                     cheque_especial=session.get('cheque_especial'),
                                     saldo_conta=session.get('saldo_conta'))
    form.id_agencia.choices = [(agencia.id, agencia.apelido_agencia) for agencia in AgenciaBanco.query.all()]
    form.id_tipo_conta.choices = retorna_tipo_conta_bancaria()
    return render_template('pesquisa_titular_conta_cpf.html', form=form, search=search)


@app.route('/financeiro/atributosbancos/contasbancarias/buscatitularcnpj', methods=['GET', 'POST'])
@login_required
def busca_titular_conta_cnpj():
    search = buscar_cliente_fornecedor_cnpj(session.get('campo_pesquisa'))
    form = FormContaBancariaCadastro(id_agencia=session.get('id_agencia'),
                                     id_tipo_conta=session.get('id_tipo_conta'),
                                     apelido_conta=session.get('apelido_conta'),
                                     nro_conta=session.get('nro_conta'),
                                     digito_conta=session.get('digito_conta'),
                                     campo_pesquisa=session.get('campo_pesquisa'),
                                     cheque_especial=session.get('cheque_especial'),
                                     saldo_conta=session.get('saldo_conta'))
    form.id_tipo_conta.choices = retorna_tipo_conta_bancaria()
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
                                      id_tipo_conta=session.get('id_tipo_conta'),
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
    form.id_tipo_conta.choices = retorna_tipo_conta_bancaria()
    if form.validate_on_submit():
        conta_bancaria = ContasBancarias(id_agencia=int(form.id_agencia.data),
                                         id_tipo_conta=int(form.id_tipo_conta.data),
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

        ajusta_saldo_contas(conta_cadastrada)

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


@app.route('/financeiro/atributosbancos/contasbancarias/recalculo')
@login_required
def recalcula_contas_bancarias():
    atualizacao_geral_financeiro()
    return redirect(url_for('home_contas_bancarias'))


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
            conta_bancaria = ContasBancarias.query.filter_by(id=id_conta_bancaria).first()

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
                        pesq_fat = FaturaCartaoCredito.query.filter_by(cod_fatura=fatura.cod_fatura).first()
                        vincula_fat_cartao_credito_transacao_financeira(pesq_fat)

                    else:
                        vincula_fat_cartao_credito_transacao_financeira()

                    data_ref = data_ref + timedelta(days=30)
                    validacao = ValidacaoFaturasCartaoCredito(id_cartao=cartao2.id)
                    database.session.add(validacao)
                    database.session.commit()

                time.sleep(0.5)
                atualiza_cartao(cartao2)
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
    faturas = FaturaCartaoCredito.query.filter_by(id=int(id_fatura)).first()
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
        ajusta_saldo_contas(tipo=6)
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
        cartao = CartaoCredito.query.filter_by(id=id_fat.id_cartao_credito).first()
        atualiza_cartao(cartao)
        flash('Transação cadastrada com Sucesso.', 'alert-success')
        return redirect(url_for('home_transacoes_financeiras'))
    return render_template('cadastro_despesa_cartao_credito.html', form=form)


@app.route('/home/configuracoes')
@login_required
def home_configuracoes():
    return render_template('home_configuracoes.html')
