def saldo(tabela):
    '''
    Calcula o saldo a partir dos funcionários ativos/inativos
    :param tabela: recebe um dataframe
    :param for funcionario...: itera e verifica o status dos funcionários
    :param
    '''
    valor = 0
    for funcionario in tabela['Usou a Plataforma?']:
        if funcionario == 'Sim':
            valor -= 20
        else:
            valor -= 5
    return valor


def saldo_mes(tabela, extra=0, ver_valor=False, ver_esperado=False, ver_mensal=False):
    '''
    Calcula o valor total, valor esperado e/ou saldo em meses

    :param tabela: recebe um dataframe
    :param extra: recebe o valor antecipado ou retroativo
    :param ver_...: seleciona o tipo de operação que será feita
    '''
    valor = saldo(tabela) + extra
    esperado = (valor) - extra
    if esperado != 0:
        mensal = int(extra / esperado) * -1
    else:
        mensal = 0

    if ver_valor:
        return valor
    if ver_esperado:
        return esperado
    if ver_mensal:
        return mensal
    else:
        return None
