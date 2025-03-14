import io
import pandas as pd
import streamlit as st
from funcoes import saldo, saldo_mes

# Menu
st.title('Relatório de uso da plataforma')

# Abrindo arquivo
arquivo = st.file_uploader(
    'Escolha um arquivo .xlsx ou .xls ', type=['xlsx', 'xls'])

if arquivo is None:
    st.write('Selecione um arquivo')
else:
    nome_arquivo = arquivo.name

    # Sempre lê a primeira aba (mudar mediante necessidade)
    sheet_arquivo = pd.ExcelFile(arquivo).sheet_names[0]

    # Criando DataFrame
    df = pd.read_excel(arquivo, sheet_name=sheet_arquivo)

    # Empresas
    empresas = list(set(df['Empresa']))

    # Tabelas disponíveis
    empresas_box = empresas.copy()
    empresas_box.insert(0, 'Selecionar tudo')
    empresa_escolhida = st.multiselect(
        'Empresa', empresas_box, placeholder='Escolha uma opção:')

    # Ajustar seleção para "Selecionar tudo"
    if 'Selecionar tudo' in empresa_escolhida:
        empresa_escolhida = empresas  # Seleciona todas as empresas

    # Status ativos/inativos
    df_ativos = df[df['Usou a Plataforma?'] == 'Sim']
    df_inativos = df[df['Usou a Plataforma?'] == 'Não']

    # Selecionando status disponíveis
    opcoes = ['Todos', 'Ativos', 'Inativos']
    opcao_escolhida = st.selectbox(
        'Status', opcoes, placeholder='Escolha uma opção:')

    # Inicializando variáveis
    tabela = None
    saldo_tot = 0
    saldo_esperado = saldo_tot

    # Verificar se uma opção foi escolhida
    if empresa_escolhida != [] and opcao_escolhida != 'Escolha uma opção:':

        # Determinar a tabela com base no status escolhido
        if opcao_escolhida == 'Todos':
            tabela = df
        elif opcao_escolhida == 'Ativos':
            tabela = df_ativos
        elif opcao_escolhida == 'Inativos':
            tabela = df_inativos

        # Filtrar a tabela pela empresa escolhida, se aplicável
        if tabela is not None:
            if 'Selecionar tudo' not in empresa_escolhida:  # Caso não seja "Selecionar tudo"
                tabela = tabela[tabela['Empresa'].isin(empresa_escolhida)]

            # Exibir a tabela
            st.dataframe(tabela, width=700)

            # Cálculo de Saldo
            st.subheader('Dados:')

            # Saldo antecipado
            saldo_ante = st.text_input(
                'Saldo antecipado/retroativo', placeholder='ex: 200').replace(',', '.')
            if saldo_ante:
                try:
                    saldo_ante = float(saldo_ante.replace(',', '.').strip())
                except ValueError:
                    st.error('Valor inválido')

            # Visualização de saldos

            # Total
            try:
                if isinstance(saldo_ante, (int, float)):
                    saldo_tot = saldo(tabela) + saldo_ante
                else:
                    saldo_tot = saldo(tabela)

                st.info(f'Saldo Total: R${saldo_tot:.2f}')

                # Situação
                if isinstance(saldo_ante, (int, float)):
                    saldo_esperado = saldo_mes(
                        tabela, saldo_ante, ver_esperado=True)

                    saldo_mensal = saldo_mes(
                        tabela, saldo_ante, ver_mensal=True)

                    # Antecipado
                    if saldo_tot > saldo_esperado:
                        st.success(f'Antecipado: R${saldo_ante}')
                        st.success(f'Saldo (em meses): {saldo_mensal} mês' if saldo_mensal ==
                                   1 else f'Saldo (em meses): {saldo_mensal} meses')

                    # Retroativo
                    elif saldo_tot < saldo_esperado:
                        st.error(f'Retroativo: R${saldo_ante}')
                        st.error(f'Saldo (em meses): {saldo_mensal} mês' if saldo_mensal == -
                                 1 else f'Saldo (em meses): {saldo_mensal} meses')
                    # Regular
                    else:
                        st.info('Saldo Regular')

                    # Esperado
                    ver_saldo_esperado = st.checkbox('Detalhes')
                    if ver_saldo_esperado:
                        st.info(f'Saldo Esperado: R${saldo_esperado}')
            except ZeroDivisionError:
                st.error('Operação inválida')
            else:
                if isinstance(saldo_ante, (int, float)):
                    # Coluna nova para armazenar valores
                    valor_usuario = []

                    for sts in tabela['Usou a Plataforma?']:
                        if sts == 'Sim':
                            valor_usuario.append(-20)
                        else:
                            valor_usuario.append(-5)

                    tabela['Valor (Usuário)'] = valor_usuario
                    

                    # Agrupamentos
                    grupo_esperado = tabela.groupby('Empresa')['Valor (Usuário)'].sum()

                    grupo_tot = grupo_esperado + saldo_ante

                    # Tabela final para arquivo
                    tabela_final = pd.DataFrame({'Empresa(s)': empresa_escolhida})

                    if saldo_esperado != 0:
                        tabela_final['Saldo Esperado'] = grupo_esperado.values

                    if saldo_ante:
                        tabela_final['Saldo Extra'] = saldo_ante

                    tabela_final['Saldo Total'] = grupo_tot.values

                    tabela_final['Saldo (em meses)'] = saldo_mensal

                    if ver_saldo_esperado:
                        st.dataframe(tabela_final)

                        # # Gerar relatório
                        buffer_2 = io.BytesIO()
                        with pd.ExcelWriter(buffer_2, engine='openpyxl') as writer:
                            tabela_final.to_excel(writer, sheet_name='Resumo', index=False)
                        buffer_2.seek(0)

                        st.download_button(
                            label='Gerar Resumo',
                            data=buffer_2,
                            file_name='Relatório_Resumo.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )

        # Gerar relatório
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            tabela.to_excel(writer, sheet_name='Usuários', index=False)
        buffer.seek(0)

        st.download_button(
            label='Gerar Relatório',
            data=buffer,
            file_name='Relatório_Usuários.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    else:
        st.write("Selecione uma empresa e um status para exibir os dados.")
