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
#TODO: tabela acesso
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
    fundacao = DateField('Data Fundação Empresa:')
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
    aniversario = DateField('Aniversário:', validators=[DataRequired()])
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


class FormTiposRoupas(FlaskForm):
    nome_tipo_roupa = StringField('Tipo Roupa:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormCores(FlaskForm):
    nome_cor = StringField('Cor:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormTamanhos(FlaskForm):
    tamanho = StringField('Tamanho:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormMarcas(FlaskForm):
    nome_marca = StringField('Marca:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormTiposUnidades(FlaskForm):
    tipo_unidade = StringField('Tipo unidade:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')


class FormItensEstoque(FlaskForm):
    id_tipo_roupa = SelectField('Tipo Roupa')
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


class FormBancos(FlaskForm):
    cod_banco = StringField('Código Banco', validators=[DataRequired(message='Favor incluir código banco')])
    nome_banco = StringField('Nome Banco', validators=[DataRequired(message='Favor incluir nome banco')])
    botao_submit = SubmitField('Cadastrar')

class FormAgenciaBanco(FlaskForm):
    agencia = StringField('Agência Banco', validators=[DataRequired(message='Favor incluir código agencia')])
    digito_agencia = StringField('Dígito agência', validators=[DataRequired(message='Favor incluir dígito agencia')])
    id_banco = SelectField('Banco')
    id_fornecedor = SelectField('Fornecedor')
    apelido_agencia = StringField('Apelido agência', validators=[DataRequired(message='Favor incluir apelido agencia')])
    id_cliente = IntegerField('Cadastro Banco')
    campo_pesquisa = StringField('Nome fornecedor a pesquisar')
    botao_pesquisar = SubmitField('Pesquisar cliente/fornecedor banco', name='pesquisar')
    botao_cadastrar = SubmitField('Cadastrar cliente/fornecedor banco', name='cadastrar')
    botao_finalizar = SubmitField('Finalizar cadastro', name='finalizar')

class FormContaBancaria(FlaskForm):
    id_agencia = SelectField('Agência')
    apelido_conta = StringField('Apelido conta', validators=[DataRequired(message='Favor incluir apelido conta')])
    nro_conta = StringField('Número conta', validators=[DataRequired(message='Favor incluir número conta')])
    digito_conta = StringField('Dígito conta', validators=[DataRequired(message='Favor incluir dígito conta')])
    id_titular_conta = SelectField('Titular conta')
    cheque_especial = StringField('Valor cheque especial')
    saldo_conta = StringField('Saldo inicial conta', validators=[DataRequired(message='Favor incluir saldo inicial da conta')])
    botao_submit = SubmitField('Cadastrar')


class FormCartaoCredito(FlaskForm):
    id_conta_bancaria = SelectField('Conta bancária')
    apelido_cartao = StringField('Apelido cartão de crédito', validators=[DataRequired(message='Favor incluir apelido cartão de crédito')])
    dia_inicial = IntegerField('Dia inicial fatura', validators=[DataRequired(message='Favor incluir dia inicial fatura')])
    dia_final = IntegerField('Dia final fatura', validators=[DataRequired(message='Favor incluir dia final fatura')])
    dia_pgto = IntegerField('Dia de vencimento da fatura', validators=[DataRequired(message='Favor incluir dia de vencimento da fatura')])
    valor_limite = StringField('Limite cartão de crédito', validators=[DataRequired(message='Favor incluir o valor limite de seu cartão de crédito')])
    botao_submit = SubmitField('Cadastrar')
