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
    nome_fantasia = StringField('Nome Fantasia:', validators=[DataRequired()])
    razao_social = StringField('Razão Social:', validators=[DataRequired()])
    cnpj = StringField('CNPJ:', validators=[DataRequired(), Length(14,18)])
    rua = StringField('Rua:', validators=[DataRequired()])
    complemento = StringField('Complemento:')
    nro = StringField('Nº:', validators=[DataRequired()])
    bairro = StringField('Bairro:', validators=[DataRequired()])
    cidade = StringField('Cidade:', validators=[DataRequired()])
    uf = StringField('UF:', validators=[DataRequired()])
    cep = StringField('CEP:', validators=[DataRequired()])
    fundacao = DateField('Data Fundação Empresa:')
    telefone = StringField('Telefone:', validators=[DataRequired()])
    telefone2 = StringField('Telefone 2:')
    telefone3 = StringField('Telefone 3:')
    email = StringField('E-mail:', validators=[DataRequired(), Email()])
    obs = StringField('Observações:')
    tipo_cadastro = SelectField('Tipo Cadastro:')
    botao_submit = SubmitField('Cadastrar')


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
    codigo_item = StringField('Código de Barras:', validators=[DataRequired()])
    qtd_inicial = IntegerField('Quantidade Inicial:', validators=[DataRequired()])
    valor_total_custo = StringField('Valor total: (custo)', validators=[DataRequired()])
    valor_unitario_venda = StringField('Valor unitário: (venda)', validators=[DataRequired()])
    qtd_minima = IntegerField('Quantidade mínima:', validators=[DataRequired()])
    botao_submit = SubmitField('Cadastrar')
