# Sistema de Geração Automática de Certificados para Pareceristas

Este projeto contém um sistema completo e automatizado para a emissão de certificados para pareceristas *ad hoc* da revista acadêmica **História Revista**. A solução foi desenvolvida para substituir o processo manual de criação e envio de certificados, oferecendo uma ferramenta de autoatendimento para os colaboradores.

O sistema é uma solução híbrida que combina scripts locais em Python para processamento de dados pesados e o poder da nuvem do Google (Apps Script) para a automação da lógica de negócio e interação com o usuário.

## ✨ Funcionalidades

* **Portal de Autoatendimento:** Um Formulário Google permite que os pareceristas solicitem seus certificados 24/7.
* **Geração Automática de PDF:** O sistema cria um certificado personalizado em formato PDF a partir de um modelo no Google Docs.
* **Notificação por E-mail:** Envio automático do certificado em anexo para o e-mail do solicitante.
* **Notificações para Administrador:** O administrador do sistema é notificado sobre tentativas de geração com dados inválidos ou sobre falhas técnicas.
* **Ferramentas de Administração:** Scripts em Python para processar, limpar, analisar e remover duplicidades dos dados brutos exportados do sistema OJS.
* **Atualização Automatizada da Base de Dados:** Um script Python que utiliza a API do Google Sheets para atualizar a base de dados na nuvem, eliminando a necessidade de copiar e colar manualmente.

## 🏛️ Arquitetura do Sistema

Esta solução é dividida em dois ambientes que trabalham em conjunto:

1.  **Processamento de Dados (Ambiente Local - Python/Pandas):**
    * `processar_dados.py`: Lê a exportação bruta do OJS (`reviews-*.csv`), limpa os dados, remove duplicatas e gera o arquivo `dados_para_app.csv`.
    * `atualizar_planilha.py`: Envia os dados do `dados_para_app.csv` para a Planilha Google através da API do Google.
    * `analisar_datas.py`: Script auxiliar para analisar o intervalo de datas coberto pelo arquivo bruto.

2.  **Aplicação Principal (Ambiente de Nuvem - Google Workspace):**
    * **Google Form:** Interface de entrada de dados para o parecerista.
    * **Google Sheet:** Atua como o banco de dados principal, com uma aba para as solicitações (`Respostas`) e outra para a base de dados validada (`Dados Válidos`).
    * **Google Doc:** Serve como o modelo (template) do certificado.
    * **Google Apps Script (JavaScript):** O cérebro da automação. É acionado pelo envio do formulário, valida os dados, gera o PDF e dispara todos os e-mails.

## 🚀 Configuração e Instalação

Siga os passos abaixo para configurar o sistema do zero.

### Ambiente Local (Python)
1.  Clone este repositório para o seu computador.
2.  Instale Python (versão 3.8 ou superior).
3.  No seu terminal, navegue até a pasta do projeto e instale as dependências:
    ```bash
    pip install pandas gspread google-auth-oauthlib
    ```
4.  Configure o arquivo `credentials.json` seguindo o guia para criar uma **Conta de Serviço** no Google Cloud e habilite as APIs do **Google Drive** e **Google Sheets**.
5.  Compartilhe a Planilha Google (criada no passo seguinte) com o e-mail da Conta de Serviço (encontrado no `credentials.json`), dando permissão de **"Editor"**.

### Ambiente Google (Nuvem)
1.  **Planilha Google:** Crie uma planilha (ex: "Controle de Certificados") com duas abas: `Respostas` e `Dados Válidos`.
2.  **Documento Google:** Crie um documento para ser o template, usando os placeholders `{{nome_completo}}`, `{{codigo_artigo}}`, e `{{data_emissao}}`.
3.  **Formulário Google:** Crie um formulário com os campos necessários e vincule-o à aba `Respostas` da sua planilha. Ative a coleta de e-mails nas configurações.
4.  **Apps Script:** Na planilha, vá em `Extensões > Apps Script`. Cole o código do arquivo `google_apps_script.js`. Preencha as constantes no topo (IDs do template, da pasta de PDFs e e-mail do admin). Crie um acionador (trigger) do tipo "Ao enviar formulário" para a função `gerarCertificado`.

## 🔧 Como Usar

### Atualizando a Base de Dados (Rotina do Administrador)
1.  Exporte o novo arquivo de avaliações (`reviews-AAAAMMDD.csv`) do OJS e coloque na pasta do projeto no seu computador.
2.  No seu terminal, dentro da pasta, execute `python processar_dados.py`.
3.  Em seguida, execute `python atualizar_planilha.py`.

### Gerando um Certificado (Usuário Final)
1.  O administrador compartilha o link do Formulário Google com os pareceristas.
2.  O parecerista preenche o formulário e envia.
3.  O certificado é recebido por e-mail momentos depois.

## 📄 Licença

Este projeto está licenciado sob os termos da **Licença Pública Geral GNU v3.0]**. Veja o arquivo `LICENSE` para mais detalhes.

---
