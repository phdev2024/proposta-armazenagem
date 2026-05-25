from docx import Document

def gerar_contrato_word(caminho_modelo, caminho_saida, dados):
    """
    Função responsável por abrir o modelo Word, substituir as tags nos parágrafos
    e nas tabelas pelos valores da tela, e salvar o arquivo final.
    """
    doc = Document(caminho_modelo)
    
    # 1. Substituição nos parágrafos comuns (Texto livre, assinaturas, etc.)
    for paragrafo in doc.paragraphs:
        for tag, valor in dados.items():
            if tag in paragrafo.text:
                paragrafo.text = paragrafo.text.replace(tag, str(valor))
                
    # 2. Substituição dentro das Tabelas do documento
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for tag, valor in dados.items():
                    if tag in celula.text:
                        celula.text = celula.text.replace(tag, str(valor))
                        
    # 3. Salva o documento preenchido
    doc.save(caminho_saida)