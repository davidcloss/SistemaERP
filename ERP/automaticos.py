from ERP import database, create_app
from ERP.models import CartaoCredito, FaturaCartaoCredito
from datetime import datetime, timedelta
from calendar import monthrange


app = create_app()
app.app_context().push()


def gera_cod_fatura(id_cartao, data_inicial, data_final, data_pgto):
    cod_fatura = f'C{id_cartao}DI{data_inicial}DF{data_final}DP{data_pgto}'
    return cod_fatura


def cria_data_inicial(dia_inicial, data_referencia):
    try:
        if dia_inicial > data_referencia.day:
            mes_anterior = data_referencia.month - 1
            ano_anterior = data_referencia.year - 1
            if mes_anterior == 0:
                mes_anterior = 12
                data_inicial = datetime.strptime(f'{dia_inicial}/{mes_anterior}/{ano_anterior}', '%d/%m/%Y')
                return data_inicial
            else:
                data_inicial = datetime.strptime(f'{dia_inicial}/{mes_anterior}/{data_referencia.year}', '%d/%m/%Y')
                return data_inicial
        else:
            data_inicial = datetime.strptime(f'{dia_inicial}/{data_referencia.month}/{data_referencia.year}', '%d/%m/%Y')
            return data_inicial
    except:
        data_inicial = f'01/{data_referencia.month}/{data_referencia.year}'
        data_inicial = datetime.strptime(data_inicial, '%d/%m/%Y')
        return data_inicial


def cria_data_final(dia_final, data_referencia):
    try:
        data_final = datetime.strptime(f'{dia_final}/{data_referencia.month}/{data_referencia.year}', '%d/%m/%Y')
        if data_final >= data_referencia:
            return data_final
        else:
            proximo_mes = data_referencia.month + 1
            proximo_ano = data_referencia.year + 1
            if proximo_mes == 1:
                data_final = datetime.strptime(f'{dia_final}/{proximo_mes}/{proximo_ano}', '%d/%m/%Y')
                return data_final
            else:
                data_final = datetime.strptime(f'{dia_final}/{proximo_mes}/{data_referencia.year}', '%d/%m/%Y')
                return data_final
    except:
        data_final = data_referencia.replace(day=monthrange(data_referencia.year, data_referencia.month)[1])
        return data_final


def cria_data_pgto(dia_vcto, data_final, data_referencia):
    try:
        print('1')
        data_vcto = datetime.strptime(f'{dia_vcto}/{data_referencia.month}/{data_referencia.year}', '%d/%m/%Y')
    except:
        print('2')
        proximo_mes = data_referencia.month + 1
        if proximo_mes == 13:
            print('2.1')
            proximo_mes = 1
            ano = data_referencia.year + 1
        else:
            print('2.2')
            ano = data_referencia.year
        data_vcto = datetime.strptime(f'{1}/{proximo_mes}/{ano}', '%d/%m/%Y')
    if data_final < data_vcto:
        print('3')
        return data_vcto
    else:
        print('4')
        proximo_mes = data_referencia.month + 1
        proximo_ano = data_referencia.year + 1
        if proximo_mes == 13:
            print('4.1')
            proximo_mes = 1
            if proximo_mes == 1:
                print('4.1.2')
                data_vcto = datetime.strptime(f'{dia_vcto}/{proximo_mes}/{proximo_ano}', '%d/%m/%Y')
                return data_vcto
        else:
            print('4.2')
            try:
                print('4.2.1')
                data_vcto = datetime.strptime(f'{dia_vcto}/{proximo_mes}/{data_referencia.year}', '%d/%m/%Y')
                return data_vcto
            except:
                print('4.2.2')
                prox_mes = datetime.strptime(f'01/{proximo_mes}/{data_referencia.year}', '%d/%m/%Y')
                dia_final = prox_mes.replace(day=monthrange(data_referencia.year, proximo_mes)[1])
                data_vcto = dia_final + timedelta(days=1)
                return data_vcto


def ajusta_data(data):
    data = data.replace(hour=0, minute=0, second=0, microsecond=0)
    return data


def calcula_datas_fatura(cartao, data_referencia):
    data_inicial = ajusta_data(cria_data_inicial(cartao.dia_inicial, data_referencia))
    data_final = ajusta_data(cria_data_final(cartao.dia_final, data_referencia))
    data_pgto = ajusta_data(cria_data_pgto(cartao.dia_pgto, data_final, data_referencia))
    cod_fatura = gera_cod_fatura(cartao.id, data_inicial, data_final, data_pgto)
    fatura_cartao = FaturaCartaoCredito.query.filter_by(cod_fatura=cod_fatura).first()
    try:
        if fatura_cartao.id:
            pass
    except:
        fatura = FaturaCartaoCredito(cod_fatura=cod_fatura,
                                     id_cartao_credito=cartao.id,
                                     data_inicial=data_inicial,
                                     data_final=data_final,
                                     data_vcto=data_pgto,
                                     id_usuario_cadastro=1)
        database.session.add(fatura)
        database.session.commit()


def gera_faturas_cartao():
    cartoes = CartaoCredito.query.filter_by(situacao_cartao=1).all()
    for cartao in cartoes:
        data_referencia = ajusta_data(datetime.utcnow())
        for i in range(15):
            calcula_datas_fatura(cartao, data_referencia)
            data_referencia = data_referencia + timedelta(days=30)


if __name__ == "__main__":
    gera_faturas_cartao()