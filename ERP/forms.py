from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ERP.models import Usuarios
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome Usuário:', validators=[DataRequired(), Length(5, 100)])
    senha = PasswordField('Senha:', validators=[DataRequired(), Length(8, 100)])
    confirmacao_senha = PasswordField('Confirme sua senha:', validators=[DataRequired(), EqualTo('senha')])
    tipo_usuario = SelectField('Tipo Usuario:')
    botao_submit_criar_conta = SubmitField('Criar conta')


    def validate_username(self, username):
        usuario = Usuarios.query.filter_by(username=username.data).first()
        if usuario:
            raise ValidationError('Usuário já cadastrado.')


class FormLogin(FlaskForm):
    username = StringField('Usuário:', validators=[DataRequired()])
    senha = PasswordField('Senha:', validators=[DataRequired(), Length(8, 100)])
    lembrar_dados = BooleanField("Manter logado")
    botao_submit_login = SubmitField('Fazer login')


class FormCadastroCNPJ(FlaskForm):
    nome_fantasia = StringField('Nome Fantasia:', validators=[DataRequired('Favor incluir um nome fantasia')])
    razao_social = StringField('Razão Social:', validators=[DataRequired('Favor incluir a Razão Social')])
    cnpj = StringField('CNPJ:', validators=[DataRequired('Favor incluir um CNPJ'), Length(14,18)])
    rua = StringField('Rua:', validators=[DataRequired('Favor incluir uma rua')])
    complemento = StringField('Complemento:')
    nro = StringField('Nº:', validators=[DataRequired('Favor incluir um nro residencial')])
    bairro = StringField('Bairro:', validators=[DataRequired('Favor incluir um bairro')])
    cidade = StringField('Cidade:', validators=[DataRequired('Favor incluir uma cidade')])
    uf = StringField('UF:', validators=[DataRequired('Favor incluir uma UF')])
    cep = StringField('CEP:', validators=[DataRequired('Favor incluir um CEP')])
    data_fundacao = DateField('Data Fundação Empresa:')
    telefone = StringField('Telefone:', validators=[DataRequired(message='Favor incluir pelo menos um telefone')])
    telefone2 = StringField('Telefone 2:')
    telefone3 = StringField('Telefone 3:')
    email = StringField('E-mail:', validators=[DataRequired(message='Favor incluir e-mail'), Email()])
    obs = StringField('Observações:')
    tipo_cadastro = SelectField('Tipo Cadastro:')
    botao_submit = SubmitField('Cadastrar', name='cadastro_cnpj')


class FormCadastroCPF(FlaskForm):
    nome_completo = StringField('Nome Completo:', validators=[DataRequired()])
    cpf = StringField('CPF:', validators=[DataRequired(), Length(11, 15)])
    rua = StringField('Rua:', validators=[DataRequired()])
    complemento = StringField('Complemento:')
    nro = StringField('Nº:', validators=[DataRequired()])
    bairro = StringField('Bairro:', validators=[DataRequired()])
    uf = StringField('UF:', validators=[DataRequired()])
    cidade = StringField('Cidade:', validators=[DataRequired()])
    cep = StringField('CEP:', validators=[DataRequired()])
    data_aniversario = DateField('Aniversário:', validators=[DataRequired()])
    telefone = StringField('Telefone:', validators=[DataRequired()])
    telefone2 = StringField('Telefone 2:')
    telefone3 = StringField('Telefone 3:')
    email = StringField('E-mail:', validators=[DataRequired(), Email()])
    obs = StringField('Observações:')
    tipo_cadastro = SelectField('Tipo Cadastro:')
    botao_submit = SubmitField('Cadastrar')


class FormCadastroEmpresa(FlaskForm):
    nome_empresa = StringField('Nome empresa:', validators=[DataRequired()])
    email_responsavel = StringField('E-mail:', validators=[DataRequired(), Email()])
    botao_submit = SubmitField('Cadastrar')


class FormCadastroCompraEstoque(FlaskForm):
    id_documento_fiscal = SelectField('Tipo Documento Fiscal:')
    tipo_fornecedor = SelectField('Fornecedor CPF/CNPJ')
    pesquisa_fornecedor = SelectField('Fornecedor:')
    nro_documento_fiscal = StringField('Nro. Documento Fiscal:')
    emissao_documento_fiscal = DateField('Data Emissão Documento Fiscal:', validators=[DataRequired(message='Favor inserir data.')])
    data_chegada = DateField('Data chegada:', validators=[DataRequired(message='Favor inserir data.')])
    data_prazo = DateField('Data Prazo:', validators=[DataRequired(message='Favor inserir data.')])
    valor_desconto = StringField('Valor Desconto:')
    valor_acrescimo = StringField('Valor Acréscimo:')
    parcelas = StringField('Qtd. Parcelas:')
    id_forma_pagamento = SelectField('Forma de Pagamento:')
    pesquisa_item = StringField('Produto:')
    valor_item = StringField('Valor Compra')
    qtd_item = StringField('Qtd. Itens')
    situacao = SelectField('Situação Ticket:')
    botao_pesquisar_item = SubmitField('Pesquisar Item', name='pesquisar_item')
    botao_pesquisar_fornecedor = SubmitField('Pesquisar Fornecedor', name='pesquisar_fornecedor')
    botao_finalizar = SubmitField('Finalizar', name='finalizar')


class FormCadastroVendaMercadoria(FlaskForm):
    tipo_fornecedor = SelectField('Fornecedor CPF/CNPJ')
    pesquisa_fornecedor = SelectField('Fornecedor:')
    valor_desconto = StringField('Valor Desconto:')
    valor_acrescimo = StringField('Valor Acréscimo:')
    parcelas = StringField('Qtd. Parcelas:')
    id_forma_pagamento = SelectField('Forma de Pagamento:')
    pesquisa_item = StringField('Produto:')
    qtd_item = StringField('Qtd. Itens')
    situacao = SelectField('Situação Ticket:')
    botao_pesquisar_item = SubmitField('Pesquisar Item', name='pesquisar_item')
    botao_pesquisar_fornecedor = SubmitField('Pesquisar Fornecedor', name='pesquisar_fornecedor')
    botao_inserir_pagamento = SubmitField('Inserir Pagamento', name='inserir_pagamento')
    botao_finalizar = SubmitField('Finalizar', name='finalizar')


class FormRegistraTrocoVenda(FlaskForm):
    valor_recebido = StringField('Valor Recebido')
    botao_calcular = SubmitField('Calcular troco.', name='calcular')
    botao_finalizar = SubmitField('Finalizar Venda', name='finalizar')


class FormParcelamentoProprio(FlaskForm):
    pesquisa_fornecedor = SelectField('Cliente:')
    valor_a_parcelar = StringField('Valor Parcelamento:')
    qtd_parcelas = StringField('Qtd. Parcelas:')
    botao_calcular = SubmitField('Calcular Parcelas', name='calcular')
    botao_cadastrar = SubmitField('Cadastrar Parcelamento', name='cadastrar')


class FormVendaCartaoCreditoAVista(FlaskForm):
    pesquisa_fornecedor = SelectField('Cliente')
    maquina_cartao = SelectField('Máquina de Cartão')
    valor_compra = StringField('Valor Venda')
    botao_submit = SubmitField('Cadastrar Pagamento')


class FormVendaCartaoCreditoParcelado(FlaskForm):
    pesquisa_fornecedor = SelectField('Cliente')
    maquina_cartao = SelectField('Máquina de Cartão')
    qtd_parcelas = StringField('Parcelas')
    valor_compra = StringField('Valor Venda')
    botao_submit = SubmitField('Cadastrar Pagamento')



class FormTiposRoupas(FlaskForm):
    nome_tipo_roupa = StringField('Tipo Roupa:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormEditarTiposRoupas(FlaskForm):
    nome_tipo_roupa = StringField('Tipo Roupa:', validators=[DataRequired()])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormCores(FlaskForm):
    nome_cor = StringField('Cor:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormEditarCores(FlaskForm):
    nome_cor = StringField('Cor:', validators=[DataRequired()])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormTamanhos(FlaskForm):
    tamanho = StringField('Tamanho:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormEditarTamanhos(FlaskForm):
    nome_tamanho = StringField('Tamanho:', validators=[DataRequired()])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormMarcas(FlaskForm):
    nome_marca = StringField('Marca:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormEditarMarcas(FlaskForm):
    nome_marca = StringField('Marca:', validators=[DataRequired()])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormGeneros(FlaskForm):
    nome_genero = StringField('Genero:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormEditarGeneros(FlaskForm):
    nome_genero = StringField('Genero:', validators=[DataRequired()])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormTiposUnidades(FlaskForm):
    nome_tipo_unidade = StringField('Tipo unidade:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormEditarTiposUnidades(FlaskForm):
    nome_tipo_unidade = StringField('Tipo unidade:', validators=[DataRequired()])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormItensEstoque(FlaskForm):
    id_tipo_roupa = SelectField('Tipo Roupa')
    id_genero = SelectField('Genero')
    id_cor = SelectField('Cor')
    id_marca = SelectField('Marca')
    id_tamanho = SelectField('Tamanho')
    id_tipo_unidade = SelectField('Tipo Unidade')
    codigo_item = StringField('Código de Barras:', validators=[DataRequired(message='Código Item requerido')])
    valor_total_custo = StringField('Valor total: (custo)')
    valor_unitario_venda = StringField('Valor unitário: (venda)')
    qtd_minima = StringField('Quantidade mínima:')
    qtd_inicial = IntegerField('Quantidade Inicial:')
    botao_submit = SubmitField('Cadastrar')


class FormItensNaoEncontrados(FlaskForm):
    id_tipo_roupa = SelectField('Tipo Roupa')
    id_genero = SelectField('Genero')
    id_cor = SelectField('Cor')
    id_marca = SelectField('Marca')
    id_tamanho = SelectField('Tamanho')
    id_tipo_unidade = SelectField('Tipo Unidade')
    codigo_item = StringField('Código de Barras:', validators=[DataRequired(message='Código Item requerido')])
    valor_total_custo = StringField('Valor total: (custo)')
    valor_unitario_venda = StringField('Valor unitário: (venda)')
    qtd_minima = StringField('Quantidade mínima:')
    botao_submit = SubmitField('Cadastrar')


class FormEditarItensEstoque(FlaskForm):
    id_tipo_roupa = SelectField('Tipo Roupa')
    id_genero = SelectField('Genero')
    id_cor = SelectField('Cor')
    id_marca = SelectField('Marca')
    id_tamanho = SelectField('Tamanho')
    id_tipo_unidade = SelectField('Tipo Unidade')
    codigo_item = StringField('Código de Barras:', validators=[DataRequired(message='Código Item requerido')])
    valor_unitario_venda = StringField('Valor unitário: (venda)')
    qtd_minima = StringField('Quantidade mínima:')
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormBancos(FlaskForm):
    cod_banco = StringField('Código Banco', validators=[DataRequired(message='Favor incluir código banco')])
    nome_banco = StringField('Nome Banco', validators=[DataRequired(message='Favor incluir nome banco')])
    botao_submit = SubmitField('Cadastrar')


class FormEditarBancos(FlaskForm):
    cod_banco = StringField('Código Banco', validators=[DataRequired(message='Favor incluir código banco')])
    nome_banco = StringField('Nome Banco', validators=[DataRequired(message='Favor incluir nome banco')])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormAgenciaBancoCadastro(FlaskForm):
    agencia = StringField('Agência Banco', validators=[DataRequired(message='Favor incluir código agencia')])
    digito_agencia = StringField('Dígito agência', validators=[DataRequired(message='Favor incluir dígito agencia')])
    id_banco = SelectField('Banco')
    apelido_agencia = StringField('Apelido agência', validators=[DataRequired(message='Favor incluir apelido agencia')])
    campo_pesquisa = StringField('Nome fornecedor a pesquisar')
    botao_pesquisar = SubmitField('Pesquisar cliente/fornecedor banco', name='pesquisar')
    botao_cadastrar = SubmitField('Cadastrar cliente/fornecedor banco', name='cadastrar')
    botao_finalizar = SubmitField('Finalizar cadastro', name='finalizar')


class FormAgenciaBancoEdicao(FlaskForm):
    agencia = StringField('Agência Banco', validators=[DataRequired(message='Favor incluir código agencia')])
    digito_agencia = StringField('Dígito agência', validators=[DataRequired(message='Favor incluir dígito agencia')])
    id_banco = SelectField('Banco')
    apelido_agencia = StringField('Apelido agência', validators=[DataRequired(message='Favor incluir apelido agencia')])
    id_cliente = SelectField('Cliente/Fornecedor Banco')  # Adicionando o campo id_cliente
    campo_pesquisa = StringField('Nome fornecedor a pesquisar')
    botao_pesquisar = SubmitField('Pesquisar cliente/fornecedor banco', name='pesquisar')
    botao_cadastrar = SubmitField('Cadastrar cliente/fornecedor banco', name='cadastrar')
    situacao = SelectField('Situação')
    botao_finalizar = SubmitField('Finalizar cadastro', name='finalizar')


class FormContaBancariaCadastro(FlaskForm):
    id_agencia = SelectField('Agência')
    id_tipo_conta = SelectField('Tipo Conta')
    apelido_conta = StringField('Apelido conta', validators=[DataRequired(message='Favor incluir apelido conta')])
    nro_conta = StringField('Número conta', validators=[DataRequired(message='Favor incluir número conta')])
    digito_conta = StringField('Dígito conta', validators=[DataRequired(message='Favor incluir dígito conta')])
    campo_pesquisa = StringField('Nome titular conta a pesquisar')
    cheque_especial = StringField('Valor cheque especial')
    saldo_conta = StringField('Saldo inicial conta', validators=[DataRequired(message='Favor incluir saldo inicial da conta')])
    botao_pesquisar_cpf = SubmitField('Pesquisar CPF', name='cpf')
    botao_pesquisar_cnpj = SubmitField('Pesquisar CNPJ', name='cnpj')


class FormContaBancariaCadastro2(FlaskForm):
    id_agencia = SelectField('Agência')
    id_tipo_conta = SelectField('Tipo Conta')
    apelido_conta = StringField('Apelido conta', validators=[DataRequired(message='Favor incluir apelido conta')])
    nro_conta = StringField('Número conta', validators=[DataRequired(message='Favor incluir número conta')])
    digito_conta = StringField('Dígito conta', validators=[DataRequired(message='Favor incluir dígito conta')])
    id_titular = SelectField('Titular')
    cheque_especial = StringField('Valor cheque especial')
    saldo_conta = StringField('Saldo inicial conta', validators=[DataRequired(message='Favor incluir saldo inicial da conta')])
    botao_finalizar = SubmitField('Cadastrar', name='finalizar')


class FormContaBancariaEdicao(FlaskForm):
    id_agencia = SelectField('Agência')
    apelido_conta = StringField('Apelido conta', validators=[DataRequired(message='Favor incluir apelido conta')])
    nro_conta = StringField('Número conta', validators=[DataRequired(message='Favor incluir número conta')])
    digito_conta = StringField('Dígito conta', validators=[DataRequired(message='Favor incluir dígito conta')])
    id_titular = SelectField('Titular')
    cheque_especial = StringField('Valor cheque especial')
    saldo_conta = StringField('Saldo inicial conta', validators=[DataRequired(message='Favor incluir saldo inicial da conta')])
    situacao = SelectField('Situação')
    botao_finalizar = SubmitField('Cadastrar', name='finalizar')


class FormChequesPropriosCadastro(FlaskForm):
    id_conta = SelectField('Conta Bancaria:')
    comp = StringField('Comp:')
    banco = StringField('Banco:')
    agencia = StringField('Agência:')
    conta = StringField('Conta:')
    serie = StringField('Série:')
    nro_cheque = StringField('Nº Cheque:')
    valor_cheque = StringField('Valor Cheque:')
    bom_para = DateField('Bom para:')
    data_emissao = DateField('Data Emissão')
    botao_submit = SubmitField('Cadastrar')


class FormChequesTerceirosCadastro(FlaskForm):
    id_cliente = SelectField('Cliente:')
    comp = StringField('Comp:')
    banco = StringField('Banco:')
    agencia = StringField('Agência:')
    conta = StringField('Conta:')
    serie = StringField('Série:')
    nro_cheque = StringField('Nº Cheque:')
    valor_cheque = StringField('Valor Cheque:')
    bom_para = DateField('Bom para:')
    data_emissao = DateField('Data Emissão')
    botao_submit = SubmitField('Cadastrar')


class FormEditarChequesPropriosCadastro(FlaskForm):
    id_conta = SelectField('Conta Bancaria:')
    comp = StringField('Comp:')
    banco = StringField('Banco:')
    agencia = StringField('Agência:')
    conta = StringField('Conta:')
    serie = StringField('Série:')
    nro_cheque = StringField('Nº Cheque:')
    valor_cheque = StringField('Valor Cheque:')
    bom_para = DateField('Bom para:')
    data_emissao = DateField('Data Emissão')
    situacao_cheque = SelectField('Situação Cheque:')
    botao_submit = SubmitField('Cadastrar')


class FormEditarChequesTerceirosCadastro(FlaskForm):
    id_titular_cheque = SelectField('Cliente:')
    comp = StringField('Comp:')
    banco = StringField('Banco:')
    agencia = StringField('Agência:')
    conta = StringField('Conta:')
    serie = StringField('Série:')
    nro_cheque = StringField('Nº Cheque:')
    valor_cheque = StringField('Valor Cheque:')
    bom_para = DateField('Bom para:')
    data_emissao = DateField('Data Emissão')
    situacao_cheque = SelectField('Situação Cheque:')
    botao_submit = SubmitField('Cadastrar')


class FormCartaoCredito(FlaskForm):
    id_conta_bancaria = SelectField('Conta bancária')
    apelido_cartao = StringField('Apelido cartão de crédito', validators=[DataRequired(message='Favor incluir apelido cartão de crédito')])
    dia_inicial = IntegerField('Dia inicial fatura', validators=[DataRequired(message='Favor incluir dia inicial fatura')])
    dia_final = IntegerField('Dia final fatura', validators=[DataRequired(message='Favor incluir dia final fatura')])
    dia_pgto = IntegerField('Dia de vencimento da fatura', validators=[DataRequired(message='Favor incluir dia de vencimento da fatura')])
    valor_limite = StringField('Limite cartão de crédito', validators=[DataRequired(message='Favor incluir o valor limite de seu cartão de crédito')])
    botao_submit = SubmitField('Cadastrar')


class FormEditarCartaoCredito(FlaskForm):
    id_conta_bancaria = SelectField('Conta bancária')
    apelido_cartao = StringField('Apelido cartão de crédito', validators=[DataRequired(message='Favor incluir apelido cartão de crédito')])
    dia_inicial = IntegerField('Dia inicial fatura', validators=[DataRequired(message='Favor incluir dia inicial fatura')])
    dia_final = IntegerField('Dia final fatura', validators=[DataRequired(message='Favor incluir dia final fatura')])
    dia_pgto = IntegerField('Dia de vencimento da fatura', validators=[DataRequired(message='Favor incluir dia de vencimento da fatura')])
    valor_limite = StringField('Limite cartão de crédito', validators=[DataRequired(message='Favor incluir o valor limite de seu cartão de crédito')])
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormEditarFaturaCartaoCredito(FlaskForm):
    data_inicial = DateField('Data Inicial')
    data_final = DateField('Data Final')
    data_vcto = DateField('Data Vencimento')
    botao_submit = SubmitField('Cadastrar')


class FormAlterarPagamentoFaturaCartaoCredito(FlaskForm):
    data_pagamento = DateField('Data Pagamento')
    valor_pago = StringField('Valor Pago')
    botao_submit = SubmitField('Cadastrar')


class FormCategoriasFinanceiras(FlaskForm):
    nome_categoria = StringField('Nome Categoria', validators=[DataRequired(message='Favor inserir categoria')])
    tipo_transacao_financeira = SelectField('Tipo transação')
    botao_submit = SubmitField('Cadastrar')


class FormEditarCategoriasFinanceiras(FlaskForm):
    nome_categoria = StringField('Nome Categoria', validators=[DataRequired(message='Favor inserir categoria')])
    tipo_transacao_financeira = SelectField('Tipo transação')
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormCadastroCustoDespesa(FlaskForm):
    pass


class FormCadastroDespesaCartaoCredito(FlaskForm):
    id_categoria_financeira = SelectField('Categoria Financeira')
    id_cartao_credito = SelectField('Cartão de Crédito')
    fatura_cartao_credito = SelectField('Fatura')
    valor_transacao = StringField('Valor Transação')
    data_ocorrencia = DateField('Data Ocorrência')
    botao_submit = SubmitField('Cadastrar')


class FormEditarUsuario(FlaskForm):
    tipo_usuario = SelectField('Tipo Usuário')
    situacao = SelectField('Situação')
    botao_submit = SubmitField('Cadastrar')


class FormEditarSenha(FlaskForm):
    senha_antiga = PasswordField('Senha Antiga')
    nova_senha = PasswordField('Nova Senha')
    confirmar_nova_senha = PasswordField('Confirmar Nova Senha')
    botao_submit = SubmitField('Cadastrar')


class FormRedefinirSenha(FlaskForm):
    nova_senha = PasswordField('Nova Senha')
    confirmar_nova_senha = PasswordField('Confirmar Nova Senha')
    botao_submit = SubmitField('Cadastrar')