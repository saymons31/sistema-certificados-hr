/**
 * =================================================================
 * Sistema de Geração de Certificados - Aplicação Principal
 * =================================================================
 * Módulo:      Google Apps Script (Code.gs)
 * Descrição:   Este é o script central da aplicação de certificados, 
 * operando inteiramente no ambiente Google Workspace. Anexado
 * a uma Planilha Google, ele é ativado automaticamente 
 * quando um parecerista submete uma solicitação via 
 * Google Form. Suas principais responsabilidades incluem 
 * a validação dos dados do parecerista contra a base de 
 * dados, a geração dinâmica de um certificado em PDF a 
 * partir de um template no Google Docs, e o envio 
 * automatizado do documento final por e-mail. O script 
 * também gerencia as notificações de sucesso, erro de 
 * validação e falhas técnicas para garantir a robustez 
 * e a manutenibilidade do sistema.
 * * Autor:       Saymon Siqueira
 * Revisão: Gem Parceiro de Programação (IA Gemini 2.5 Pro)
 * Data da Versão: 18 de junho de 2025
 * =================================================================
 */

// --- 1. CONFIGURAÇÕES OBRIGATÓRIAS ---
// Cole aqui o ID do seu documento Google Docs que serve como modelo.
const ID_TEMPLATE_CERTIFICADO = "COLE_O_ID_DO_SEU_GOOGLE_DOC_AQUI";

// Cole aqui o ID da pasta no Google Drive onde os PDFs serão salvos.
const ID_PASTA_PDFS = "COLE_O_ID_DA_PASTA_DO_GOOGLE_DRIVE_AQUI";

// E-mail do administrador para receber notificações de erro.
const EMAIL_ADMIN = "seu_email_de_admin@provedor.com";


/**
 * Função principal que é acionada quando um formulário é enviado.
 * Ela gera o certificado e envia por e-mail.
 */
function gerarCertificado(e) {
  // Pega os dados que o usuário enviou pelo formulário
  const respostas = e.values;
  const emailParecerista = respostas[1].trim();
  const username = respostas[2].trim();
  const codigoArtigo = respostas[3].trim();

  // Acessa a planilha com a lista de dados válidos
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  const abaDadosValidos = planilha.getSheetByName("Dados Válidos");
  const todosOsDados = abaDadosValidos.getDataRange().getValues();

  // Valida os dados enviados e busca o nome completo do parecerista
  let nomeCompleto = "";
  let dadosEncontrados = false;
  
  // Loop para procurar uma correspondência na planilha
  for (let i = 1; i < todosOsDados.length; i++) { // Começa em 1 para pular o cabeçalho
    const linha = todosOsDados[i];
    const usernamePlanilha = String(linha[0]).trim();     // Coluna A: Username (Avaliador)
    const codigoArtigoPlanilha = String(linha[1]).trim(); // Coluna B: ID da Submissão
    const nomeCompletoPlanilha = String(linha[2]).trim(); // Coluna C: Nome Completo
    
    // Compara os dados do formulário (em minúsculas) com os da planilha
    if (username.toLowerCase() === usernamePlanilha.toLowerCase() && codigoArtigo === codigoArtigoPlanilha) {
      nomeCompleto = nomeCompletoPlanilha;
      dadosEncontrados = true;
      break; // Para o loop assim que encontrar
    }
  }

 // Se, após o loop, não encontrar os dados, notifica ambos e encerra.
if (!dadosEncontrados) {
  // Envia o e-mail de erro para o parecerista
  enviarEmailDeErro(emailParecerista, username, codigoArtigo);

  // Envia um e-mail de AVISO para o administrador
  notificarAdminSobreFalhaDeValidacao(username, codigoArtigo, emailParecerista);

  return; // Encerra a execução
}

  // Se encontrou, tenta criar o PDF e enviar o e-mail de sucesso.
  try {
    const dataHoje = new Date().toLocaleDateString("pt-BR", { day: '2-digit', month: 'long', year: 'numeric' });
    const nomeArquivo = `Certificado - ${nomeCompleto}.pdf`;
    
    // Acessa a pasta de destino e o arquivo de modelo
    const pastaDestino = DriveApp.getFolderById(ID_PASTA_PDFS);
    const template = DriveApp.getFileById(ID_TEMPLATE_CERTIFICADO);
    
    // Cria uma cópia temporária do modelo para preencher
    const novoArquivoTemporario = template.makeCopy(`${nomeCompleto}_temp_`, pastaDestino);
    const doc = DocumentApp.openById(novoArquivoTemporario.getId());
    const body = doc.getBody();
    
    // Substitui os placeholders pelos dados reais
    body.replaceText("{{nome_completo}}", nomeCompleto);
    body.replaceText("{{codigo_artigo}}", codigoArtigo);
    body.replaceText("{{data_emissao}}", dataHoje);
    
    doc.saveAndClose(); // Salva e fecha o documento temporário
    
    // Cria o arquivo PDF final
    const pdfBlob = novoArquivoTemporario.getAs('application/pdf');
    pdfBlob.setName(nomeArquivo);
    const arquivoPdfFinal = pastaDestino.createFile(pdfBlob);
    
    // Apaga a cópia temporária do Google Docs
    DriveApp.getFileById(novoArquivoTemporario.getId()).setTrashed(true);
    
    // Envia o e-mail de sucesso com o PDF em anexo
    enviarEmailDeSucesso(emailParecerista, nomeCompleto, arquivoPdfFinal);

  } catch (err) {
    // Se ocorrer um erro técnico, envia um e-mail de falha para o parecerista.
    enviarEmailDeErroTecnico(emailParecerista, err.message);
    
    // E também envia uma notificação detalhada para o administrador.
    notificarAdminSobreFalha(username, codigoArtigo, err, emailParecerista);
  }
}

/**
 * Função auxiliar para enviar o e-mail de sucesso
 */
function enviarEmailDeSucesso(destinatario, nome, anexo) {
  const assunto = "Seu Certificado de Parecerista - História Revista";
  
  // MODIFICADO: O corpo é construído em HTML para permitir formatação.
  // Usamos <p> para parágrafos, <br> para quebra de linha e <i> para itálico.
  const corpoHtml = `
    <p>Prezado(a) ${nome},</p>
    <p>É com grande satisfação que enviamos seu certificado de parecerista <i>ad hoc</i> para a História Revista.</p>
    <p>O documento está em anexo neste e-mail.</p>
    <p>Agradecemos imensamente sua valiosa contribuição.</p>
    <br>
    <p>Atenciosamente,<br>Equipe da História Revista.</p>
  `;
  
  // MODIFICADO: Usamos a opção 'htmlBody' para enviar o e-mail formatado.
  GmailApp.sendEmail(destinatario, assunto, "", {
    attachments: [anexo],
    htmlBody: corpoHtml 
  });
}

/**
 * Função auxiliar para enviar o e-mail de dados não encontrados
 */
function enviarEmailDeErro(destinatario, username, codigoArtigo) {
  const assunto = "Erro ao Gerar seu Certificado da História Revista";
  const corpoHtml = `
    <p>Prezado(a) parecerista,</p>
    <p>Não foi possível gerar seu certificado. Os dados fornecidos (Usuário: ${username}, Código do Artigo: ${codigoArtigo}) não foram encontrados em nossos registros de avaliações concluídas.</p>
    <p>Por favor, verifique os dados e tente novamente. Se o erro persistir, entre em contato com a equipe editorial.</p>
    <p><b>Lembrete:</b> a atualização da base de dados é mensal. Se sua colaboração foi muito recente, provavelmente será integrada no próximo ciclo.</p>
    <br>
    <p>Atenciosamente,<br>Equipe da História Revista.</p>
  `;
  GmailApp.sendEmail(destinatario, assunto, "", { htmlBody: corpoHtml });
}

/**
 * Função auxiliar para enviar o e-mail de erro técnico
 */
function enviarEmailDeErroTecnico(destinatario, erro) {
  const assunto = "Erro Técnico ao Gerar Certificado";
  const corpo = `Prezado(a) parecerista,\n\nOcorreu um erro técnico inesperado ao tentar gerar o seu certificado. Nossa equipe já foi notificada.\n\nDetalhes do erro: ${erro}\n\nPor favor, aguarde e tente novamente mais tarde, ou entre em contato com a equipe editorial.\n\nAtenciosamente,\nEquipe da História Revista.`;
  GmailApp.sendEmail(destinatario, assunto, corpo);
}

/**
 * Função para notificar o administrador sobre uma falha técnica
 */
function notificarAdminSobreFalha(username, codigoArtigo, erro, emailParecerista) {
  const assunto = "[Alerta Urgente] Falha na Geração de Certificado - História Revista";
  const corpo = `
    Olá, Admin,

    O sistema de geração de certificados encontrou um erro técnico e não pôde concluir uma solicitação.

    Detalhes da Solicitação:
    - E-mail do Parecerista: ${emailParecerista}
    - Username Inserido: ${username}
    - Código do Artigo Inserido: ${codigoArtigo}

    Detalhes do Erro:
    - Mensagem: ${erro.message}
    - Linha do Erro: ${erro.lineNumber}
    - Arquivo: ${erro.fileName}

    Stack Trace (para depuração avançada):
    ${erro.stack}

    O parecerista foi notificado com uma mensagem de erro genérica.
  `;
  GmailApp.sendEmail(EMAIL_ADMIN, assunto, corpo);
}