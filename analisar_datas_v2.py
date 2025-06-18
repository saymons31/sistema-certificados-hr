# -*- coding: utf-8 -*-
"""
==============================================================================
 Sistema de Geração de Certificados - Ferramenta de Administração
==============================================================================
 Módulo: analisar_datas_v2.py
 Descrição: Script de diagnóstico para analisar o arquivo de exportação                         de avaliações do OJS (reviews-*.csv). Ele identifica dinamicamente o                 arquivo mais recente na pasta, utiliza um motor de leitura robusto para              lidar com a formatação inconsistente dos dados, e reporta a data de                  conclusão de parecer mais antiga e a mais recente encontradas no                     conjunto de dados, junto com seus respectivos IDs de submissão para                  referência.
 
 Autor: Saymon Siqueira
 Revisão: Gem Parceiro de Programação (IA Gemini 2.5 Pro)
 Data da Versão: 18 de junho de 2025
==============================================================================
"""

import pandas as pd
import glob
import os
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    print("Locale pt_BR não encontrado.")

print("Analisando o arquivo de dados...")

# Lógica para encontrar o arquivo dinamicamente
padrao_arquivo = 'reviews-*.csv'
print(f"Procurando por arquivos que correspondem ao padrão: {padrao_arquivo}")
lista_de_arquivos = glob.glob(padrao_arquivo)
if not lista_de_arquivos:
    print(f"❌ ERRO: Nenhum arquivo correspondendo ao padrão '{padrao_arquivo}' foi encontrado.")
    exit()
arquivo_a_processar = max(lista_de_arquivos, key=os.path.getmtime)
print(f"Selecionando o arquivo mais recente para processar: {arquivo_a_processar}")

try:
    # Método de leitura
    df_completo = pd.read_csv(
        arquivo_a_processar, 
        sep=',', 
        encoding='utf-8-sig', 
        engine='python',
        on_bad_lines='warn'
    )
    print("Arquivo lido com sucesso usando o método robusto.")
    
    # Constantes
    COLUNA_CONCLUSAO = "Conclusão"
    COLUNA_ID_ARTIGO = "ID da submissão"
    
    # Limpeza dos nomes das colunas
    df_completo.columns = df_completo.columns.str.replace('"', '', regex=False)

    # Lógica de processamento de datas
    df_com_data = df_completo.dropna(subset=[COLUNA_CONCLUSAO]).copy()
    datas_limpas = df_com_data[COLUNA_CONCLUSAO].str.replace('""', '', regex=False)
    df_com_data['data_formatada'] = pd.to_datetime(
        datas_limpas,
        format='%Y-%m-%d %H:%M:%S',
        errors='coerce'
    )
    df_com_data = df_com_data.dropna(subset=['data_formatada'])

    if not df_com_data.empty:
        data_minima = df_com_data['data_formatada'].min()
        data_maxima = df_com_data['data_formatada'].max()

        id_submissao_min = df_com_data.loc[df_com_data['data_formatada'] == data_minima, COLUNA_ID_ARTIGO].iloc[0]
        id_submissao_max = df_com_data.loc[df_com_data['data_formatada'] == data_maxima, COLUNA_ID_ARTIGO].iloc[0]
        
        # Verificação inteligente do formato do ID
        id_min_formatado = str(id_submissao_min) if str(id_submissao_min).isdigit() else "(ID textual/inválido)"
        id_max_formatado = str(id_submissao_max) if str(id_submissao_max).isdigit() else "(ID textual/inválido)"

        print("\n--- ANÁLISE CONCLUÍDA ---")
        print(f"🗓️ Data mais antiga encontrada: {data_minima.strftime('%d de %B de %Y')} (Submissão ID: {id_min_formatado})")
        print(f"🗓️ Data mais recente encontrada: {data_maxima.strftime('%d de %B de %Y')} (Submissão ID: {id_max_formatado})")
    else:
        print("\n--- ANÁLISE CONCLUÍDA ---")
        print("❌ Nenhuma data válida foi encontrada na coluna 'Conclusão'.")

except Exception as e:
    print(f"❌ Ocorreu um erro durante a análise: {e}")
    import traceback
    traceback.print_exc()