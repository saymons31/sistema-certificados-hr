# -*- coding: utf-8 -*-
"""
==============================================================================
 Sistema de Geração de Certificados - Ferramenta de Administração
==============================================================================
 Módulo: analisar_datas_v2.py
 Descrição: Este script é o principal motor de processamento de dados do 
            sistema. Ele localiza o arquivo de exportação de avaliações mais 
            recente do OJS (reviews-*.csv), lê seu conteúdo usando um 
            método robusto para lidar com formatação inconsistente, e 
            realiza uma limpeza completa. O processo inclui: filtrar 
            apenas pareceres concluídos, criar um campo de nome completo, 
            remover dados duplicados e, finalmente, salvar um arquivo 
            'dados_para_app.csv' limpo e enxuto, pronto para ser 
            enviado para a nuvem.
 
 Autor: Saymon Siqueira
 Revisão: Gem Parceiro de Programação (IA Gemini 2.5 Pro)
 Data da Versão: 18 de junho de 2025
==============================================================================
"""

# --- processar_dados.py (Versão final, robusta e simplificada) ---
import pandas as pd
import glob
import os

print("Iniciando o processamento de dados...")

# Lógica para encontrar o arquivo
padrao_arquivo = 'reviews-*.csv'
print(f"Procurando por arquivos que correspondem ao padrão: {padrao_arquivo}")
lista_de_arquivos = glob.glob(padrao_arquivo)
if not lista_de_arquivos:
    print(f"❌ ERRO: Nenhum arquivo correspondendo ao padrão '{padrao_arquivo}' foi encontrado.")
    exit()
arquivo_a_processar = max(lista_de_arquivos, key=os.path.getmtime)
print(f"Selecionando o arquivo mais recente para processar: {arquivo_a_processar}")


# --- INÍCIO DA NOVA LÓGICA DE LEITURA ---
try:
    # Usamos o leitor avançado do pandas (engine='python') que lida melhor com arquivos malformatados.
    # O separador é a vírgula, e a codificação 'utf-8-sig' lida com os caracteres especiais do início.
    # O parâmetro 'on_bad_lines' avisa sobre linhas problemáticas em vez de quebrar.
    df_completo = pd.read_csv(
        arquivo_a_processar, 
        sep=',', 
        encoding='utf-8-sig', 
        engine='python',
        on_bad_lines='warn'
    )
    print("Arquivo lido com sucesso usando o método robusto.")

    # --- FIM DA NOVA LÓGICA DE LEITURA ---

    # O resto do script de limpeza e processamento
    ARQUIVO_LIMPO_SAIDA = "dados_para_app.csv"
    COLUNA_ID_ARTIGO = "ID da submissão"
    COLUNA_NOME_PROPRIO = "Nome Próprio"
    COLUNA_SOBRENOME = "Sobrenome"
    COLUNA_CONCLUSAO = "Conclusão"
    COLUNA_USERNAME = "Avaliador"
    
    # Limpa os nomes das colunas, removendo aspas que possam ter sido lidas
    df_completo.columns = df_completo.columns.str.replace('"', '', regex=False)

    df_concluidas = df_completo.dropna(subset=[COLUNA_CONCLUSAO]).copy()
    
    # Adicionamos .astype(str) para garantir que nomes e sobrenomes sejam tratados como texto
    df_concluidas['Nome Completo'] = (df_concluidas[COLUNA_NOME_PROPRIO].astype(str).str.replace('"', '', regex=False) + ' ' + 
                                      df_concluidas[COLUNA_SOBRENOME].astype(str).str.replace('"', '', regex=False))
    
    colunas_essenciais = [COLUNA_USERNAME, COLUNA_ID_ARTIGO, 'Nome Completo']
    df_com_colunas_finais = df_concluidas[colunas_essenciais]
    df_limpo = df_com_colunas_finais.dropna()
    df_sem_duplicatas = df_limpo.drop_duplicates(subset=[COLUNA_USERNAME, COLUNA_ID_ARTIGO], keep='first')
    
    df_sem_duplicatas.to_csv(ARQUIVO_LIMPO_SAIDA, index=False)

    print(f"\n✅ Sucesso! O arquivo '{ARQUIVO_LIMPO_SAIDA}' foi criado/atualizado.")
    print(f"De {len(df_completo)} registros, foram mantidos {len(df_sem_duplicatas)} registros válidos e únicos.")

except Exception as e:
    print(f"❌ Ocorreu um erro durante o processamento: {e}")
    # Para depuração, imprimir o traceback completo
    import traceback
    traceback.print_exc()