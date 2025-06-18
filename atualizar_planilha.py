# -*- coding: utf-8 -*-
"""
==============================================================================
 Sistema de Geração de Certificados - Ferramenta de Administração
==============================================================================
 Módulo: atualizar_planilha.py
  Descrição: Esta ferramenta serve como a ponte entre o processamento de 
            dados local e a aplicação na nuvem. O script se autentica 
            na API do Google, lê o arquivo de dados limpo 
            ('dados_para_app.csv') e atualiza automaticamente a aba 
            'Dados Válidos' na Planilha Google 'Controle de Certificados'.
            Ele apaga os dados antigos e insere os novos, garantindo 
            que a base de dados online esteja sempre sincronizada com o 
            processamento mais recente.
 
 Autor: Saymon Siqueira
 Revisão: Gem Parceiro de Programação (IA Gemini 2.5 Pro)
 Data da Versão: 18 de junho de 2025
==============================================================================
"""

# --- atualizar_planilha.py ---
# Este script envia os dados do CSV local limpo para a Planilha Google na nuvem.
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- CONFIGURAÇÕES ---
# O nome do arquivo CSV local que será enviado
ARQUIVO_LOCAL_LIMPO = "dados_para_app.csv"
# O nome exato da sua Planilha Google no seu Drive
NOME_DA_PLANILHA_GOOGLE = "NOME_DA_SUA_PLANILHA_GOOGLE_AQUI"
# O nome da aba que será atualizada
NOME_DA_ABA = "Dados Válidos"
# Arquivo de credenciais JSON
ARQUIVO_DE_CREDENCIAS = "credentials.json"
# Escopos de permissão necessários
ESCOPOS = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
# ---------------------

print(f"Iniciando a atualização da planilha '{NOME_DA_PLANILHA_GOOGLE}'...")

try:
    # Autenticação com a Conta de Serviço do Google
    creds = Credentials.from_service_account_file(ARQUIVO_DE_CREDENCIAS, scopes=ESCOPOS)
    client = gspread.authorize(creds)

    # Abre a planilha e a aba de destino
    sheet = client.open(NOME_DA_PLANILHA_GOOGLE).worksheet(NOME_DA_ABA)
    print("Conexão com a Planilha Google estabelecida com sucesso.")

    # Lê os dados do arquivo CSV local e limpo
    df = pd.read_csv(ARQUIVO_LOCAL_LIMPO)
    # Garante que não há valores nulos que possam causar problemas
    df = df.fillna('')
    
    # Limpa a aba inteira antes de inserir os novos dados
    print("Limpando dados antigos da planilha...")
    sheet.clear()

    # Atualiza a planilha com os novos dados
    print(f"Enviando {len(df)} novos registros para a nuvem...")
    # Converte o dataframe para uma lista de listas (incluindo o cabeçalho)
    dados_para_enviar = [df.columns.values.tolist()] + df.values.tolist()
    sheet.update(dados_para_enviar, 'A1')

    print("\n✅ Sucesso! A aba 'Dados Válidos' foi atualizada com os dados mais recentes.")

except FileNotFoundError:
    print(f"❌ ERRO: O arquivo '{ARQUIVO_LOCAL_LIMPO}' não foi encontrado. Você já rodou o script 'processar_dados.py' primeiro?")
except Exception as e:
    print(f"❌ Ocorreu um erro: {e}")