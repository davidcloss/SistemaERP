CREATE TABLE auditoria (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(300) NOT NULL,
    data_cadastro TIMESTAMP,
    situacao INTEGER DEFAULT 1,
    tipo_usuario INTEGER NOT NULL,
    FOREIGN KEY (situacao) REFERENCES situacoes_usuarios(id),
    FOREIGN KEY (tipo_usuario) REFERENCES tipos_usuarios(id)
);


CREATE TABLE situacoes_usuarios (
    id SERIAL PRIMARY KEY,
    nome_situacao VARCHAR(70),
    data_cadastro TIMESTAMP
);



CREATE TABLE clientes_fornecedores (
    id SERIAL PRIMARY KEY,
    nome_fantasia VARCHAR(500),
    razao_social VARCHAR(500),
    cnpj VARCHAR(20) UNIQUE,
    rua VARCHAR(100),
    complemento VARCHAR(70),
    nro VARCHAR(20),
    bairro VARCHAR(70),
    cidade VARCHAR(70),
    uf VARCHAR(2),
    cep VARCHAR(15),
    data_fundacao TIMESTAMP,
    cpf VARCHAR(20) UNIQUE,
    nome VARCHAR(100),
    telefone VARCHAR(20),
    telefone2 VARCHAR(20),
    telefone3 VARCHAR(20),
    email VARCHAR(100),
    data_aniversario TIMESTAMP,
    obs TEXT,
    data_cadastro TIMESTAMP,
    tipo_cadastro INTEGER,
    id_usuario_cadastro INTEGER,
    FOREIGN KEY (tipo_cadastro) REFERENCES tipos_cadastro(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);



CREATE TABLE tipos_cadastro (
    id SERIAL PRIMARY KEY,
    nome_tipo VARCHAR(70) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);


CREATE TABLE tipos_usuarios (
    id SERIAL PRIMARY KEY,
    nome_tipo VARCHAR(70) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP
);


CREATE TABLE cadastro_empresa (
    id SERIAL PRIMARY KEY,
    nome_empresa VARCHAR(100) NOT NULL,
    email_verificacao VARCHAR(100) NOT NULL,
    situacao CHAR(1) DEFAULT 'A',
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);


CREATE TABLE genero_roupa (
    id SERIAL PRIMARY KEY,
    nome_genero VARCHAR(255) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE tipos_roupas (
    id SERIAL PRIMARY KEY,
    nome_tipo_roupa VARCHAR(100) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE cores (
    id SERIAL PRIMARY KEY,
    nome_cor VARCHAR(255) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);


CREATE TABLE tamanhos (
    id SERIAL PRIMARY KEY,
    nome_tamanho VARCHAR(255) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE marcas (
    id SERIAL PRIMARY KEY,
    nome_marca VARCHAR(255) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE tipos_unidades (
    id SERIAL PRIMARY KEY,
    nome_tipo_unidade VARCHAR(255) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE itens_estoque (
    id SERIAL PRIMARY KEY,
    id_tipo_roupa INTEGER NOT NULL,
    id_tamanho INTEGER NOT NULL,
    id_marca INTEGER NOT NULL,
    id_cor INTEGER NOT NULL,
    id_genero INTEGER NOT NULL,
    codigo_item VARCHAR(100) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    data_ultima_entrada TIMESTAMP,
    data_ultima_saida TIMESTAMP,
    id_tipo_unidade INTEGER NOT NULL,
    qtd FLOAT,
    valor_estoque_custo FLOAT,
    valor_unitario_medio_custo FLOAT,
    valor_estoque_venda FLOAT,
    valor_unitario_medio_venda FLOAT,
    qtd_minima FLOAT,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_tipo_roupa) REFERENCES tipos_roupas(id),
    FOREIGN KEY (id_tamanho) REFERENCES tamanhos(id),
    FOREIGN KEY (id_marca) REFERENCES marcas(id),
    FOREIGN KEY (id_cor) REFERENCES cores(id),
    FOREIGN KEY (id_genero) REFERENCES genero_roupa(id),
    FOREIGN KEY (id_tipo_unidade) REFERENCES tipos_unidades(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE tipos_transacoes (
    id SERIAL PRIMARY KEY,
    nome_tipo_transacao VARCHAR(255) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE transacoes_estoque (
    id SERIAL PRIMARY KEY,
    id_lote INTEGER,
    tipo_transacao INTEGER NOT NULL,
    data_transacao TIMESTAMP,
    data_registro_transacao TIMESTAMP,
    id_item INTEGER,
    qtd_transacao INTEGER NOT NULL,
    valor_unitario_medio_custo FLOAT NOT NULL,
    valor_total_transacao_custo FLOAT NOT NULL,
    valor_unitario_medio_venda FLOAT NOT NULL,
    valor_total_transacao_venda FLOAT NOT NULL,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (tipo_transacao) REFERENCES tipos_transacoes(id),
    FOREIGN KEY (id_item) REFERENCES itens_estoque(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE bancos (
    id SERIAL PRIMARY KEY,
    cod_banco INTEGER NOT NULL UNIQUE,
    nome_banco VARCHAR(255) NOT NULL UNIQUE,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE agencia_bancos (
    id SERIAL PRIMARY KEY,
    agencia VARCHAR(255),
    digito_agencia VARCHAR(10),
    id_banco INTEGER NOT NULL,
    apelido_agencia VARCHAR(255) UNIQUE,
    id_cliente INTEGER,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_banco) REFERENCES bancos(id),
    FOREIGN KEY (id_cliente) REFERENCES clientes_fornecedores(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE contas_bancarias (
    id SERIAL PRIMARY KEY,
    id_agencia INTEGER NOT NULL,
    apelido_conta VARCHAR(255) UNIQUE,
    nro_conta VARCHAR(255),
    digito_conta VARCHAR(10),
    id_titular INTEGER NOT NULL,
    cheque_especial FLOAT DEFAULT 0,
    cheque_especial_utilizado FLOAT DEFAULT 0,
    cheque_especial_disponivel FLOAT DEFAULT 0,
    saldo_conta FLOAT DEFAULT 0,
    situacao_conta INTEGER DEFAULT 1, -- 1: Ativo, 2: Arquivada
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_agencia) REFERENCES agencia_bancos(id),
    FOREIGN KEY (id_titular) REFERENCES agencia_bancos(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE cartao_credito (
    id SERIAL PRIMARY KEY,
    id_conta_bancaria INTEGER NOT NULL,
    apelido_cartao VARCHAR(255) UNIQUE,
    dia_inicial INTEGER NOT NULL,
    dia_final INTEGER NOT NULL,
    dia_pgto INTEGER NOT NULL,
    valor_limite FLOAT NOT NULL,
    valor_gasto FLOAT DEFAULT 0,
    valor_disponivel FLOAT,
    situacao_cartao INTEGER DEFAULT 1, -- 1: Ativo, 2: Bloqueado, 3: Temporariamente Bloqueado
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_conta_bancaria) REFERENCES agencia_bancos(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE fatura_cartao_credito (
    id SERIAL PRIMARY KEY,
    cod_fatura VARCHAR(255) UNIQUE NOT NULL,
    id_cartao_credito INTEGER NOT NULL,
    valor_fatura FLOAT DEFAULT 0,
    data_inicial TIMESTAMP,
    data_final TIMESTAMP,
    data_vcto TIMESTAMP,
    data_pgto TIMESTAMP,
    descontos_recebidos FLOAT DEFAULT 0,
    juros_pagos FLOAT DEFAULT 0,
    valor_pago FLOAT,
    situacao_fatura INTEGER DEFAULT 0, -- 0: Em aberto, 1: Pago, 2: Em atraso, 3: Pago em atraso
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_cartao_credito) REFERENCES cartao_credito(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE fatura_cartao_credito (
    id SERIAL PRIMARY KEY,
    cod_fatura VARCHAR(255) UNIQUE NOT NULL,
    id_cartao_credito INTEGER NOT NULL,
    valor_fatura FLOAT DEFAULT 0,
    data_inicial TIMESTAMP,
    data_final TIMESTAMP,
    data_vcto TIMESTAMP,
    data_pgto TIMESTAMP,
    descontos_recebidos FLOAT DEFAULT 0,
    juros_pagos FLOAT DEFAULT 0,
    valor_pago FLOAT,
    situacao_fatura INTEGER DEFAULT 0,
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_cartao_credito) REFERENCES cartao_credito(id),
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

CREATE TABLE categorias_financeiras (
    id SERIAL PRIMARY KEY,
    nome_categoria VARCHAR(50) UNIQUE NOT NULL,
    tipo_transacao INTEGER NOT NULL, -- 1: ativo, 2: inativo, 3: transferencia
    situacao INTEGER DEFAULT 1, -- 1: ativo, 2: inativo
    data_cadastro TIMESTAMP,
    id_usuario_cadastro INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario_cadastro) REFERENCES usuarios(id)
);

