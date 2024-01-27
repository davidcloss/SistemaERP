from ERP import database, create_app
from ERP.models import CartaoCredito, FaturaCartaoCredito
from datetime import datetime
from calendar import monthrange


app = create_app()

app.app_context().push()
def gera_cod_fatura(id_cartao, data_inicial, data_final, data_pgto):
    cod_fatura = f'C{id_cartao}DI{data_inicial}DF{data_final}DP{data_pgto}'
    return cod_fatura


def ajuste_datas(dia, data_referencia):
    print('1.1.1.3')
    mes_referencia = data_referencia.month
    ano_referencia = data_referencia.year
    if data_referencia.day <= dia:
        print('1.1.1.3.1')
        ultimo_dia_mes_referencia = data_referencia.replace(
            day=monthrange(data_referencia.year, data_referencia.month)[1])
        if dia <= ultimo_dia_mes_referencia.day:
            print('1.1.1.3.1.1')
            data = datetime.strptime(f'{dia}/{mes_referencia}/{ano_referencia}', '%d/%m/%Y')
        else:
            print('1.1.1.3.1.2')
            mes_referencia += 1
            if mes_referencia <= 12:
                print('1.1.1.3.1.2.1')
                data = datetime.strptime(f'1/{mes_referencia}/{ano_referencia}')
            else:
                print('1.1.1.3.1.2.2')
                mes_referencia = 1
                ano_referencia += 1
                data = datetime.strptime(f'1/{mes_referencia}/{ano_referencia}')
    else:
        print('1.1.1.3.2')
        mes_referencia -= 1
        if mes_referencia >= 1:
            print('1.1.1.3.2.1')
            data = datetime.strptime(f'{dia}/{mes_referencia}/{ano_referencia}')
        else:
            print('1.1.1.3.2.2')
            mes_referencia = 12
            ano_referencia -= 1
            data = datetime.strptime(f'{dia}/{mes_referencia}/{ano_referencia}', '%d/%m/%Y')
    return data


def calcula_datas_fatura(cartao):
    print('1.1.1')
    data_atual = datetime.utcnow()
    print('1.1.1')
    data_atual.replace(hour=0, minute=0, second=0)
    data_inicial = ajuste_datas(cartao.dia_inicial, data_atual)
    data_final = ajuste_datas(cartao.dia_final, data_atual)
    data_pgto = ajuste_datas(cartao.dia_pgto, data_atual)
    cod_fatura = gera_cod_fatura(cartao.id, data_inicial, data_final, data_pgto)
    print(cod_fatura)
    fatura_cartao = FaturaCartaoCredito.query.filter_by(cod_fatura=cod_fatura).first()
    try:
        if fatura_cartao.id:
            print('1.1.1.1')
            pass
    except:
        print('1.1.1.2')
        fatura = FaturaCartaoCredito(cod_fatura=cod_fatura,
                                     id_cartao_credito=cartao.id,
                                     data_inicial=data_inicial,
                                     data_final=data_final,
                                     data_vcto=data_pgto,
                                     id_usuario_cadastro=1)
        database.session.add(fatura)
        database.session.commit()


def gera_faturas_cartao():
    print('1')
    cartoes = CartaoCredito.query.filter_by(situacao_cartao=1).all()
    for cartao in cartoes:
        print('1.1')
        calcula_datas_fatura(cartao)

if __name__ == "__main__":
    gera_faturas_cartao()