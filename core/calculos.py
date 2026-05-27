"""
MÓDULO DE INTELIGÊNCIA DE CÁLCULO (CÉREBRO DO SISTEMA)
Este arquivo centraliza as regras de negócio e fórmulas de precificação da Logcare.
"""

def calcular_custo_por_posicao(valor_aluguel, valor_condominio, valor_utilidades, capacidade_posicoes):
    """
    PASSO 1: Descobre o custo fixo de uma única posição-palete no mês.
    """
    custo_fixo_total = valor_aluguel + valor_condominio + valor_utilidades
    
    if capacidade_posicoes == 0:
        return 0.0
        
    custo_por_posicao = custo_fixo_total / capacidade_posicoes
    return round(custo_por_posicao, 2)


def simular_lucro_proposta(custo_de_uma_posicao, quantidade_paletes_cliente, margem_lucro_desejada, aliquota_iss):
    """
    PASSO 2: Calcula o custo total do cliente e simula o preço de venda com base na margem e no ISS (Markup Multiplicador).
    """
    # 1. Descobre o custo seco que esse cliente específico vai gerar no galpão
    custo_total_cliente = custo_de_uma_posicao * quantidade_paletes_cliente
    
    # 2. Aplica a fórmula matemática de Markup considerando a margem E o imposto
    # Se a margem for 35% e o ISS for 2%, somamos ambos (37%) e dividimos o custo por (1 - 0.37 = 0.63)
    soma_deducoes = margem_lucro_desejada + aliquota_iss
    
    if soma_deducoes >= 100:
        soma_deducoes = 99  # Trava de segurança para não quebrar o cálculo
        
    fator_markup = 1 - (soma_deducoes / 100)
    preco_venda_final = custo_total_cliente / fator_markup
    
    # 3. Calcula o lucro líquido em Reais que vai sobrar (descontando o custo e o ISS)
    valor_iss_reais = preco_venda_final * (aliquota_iss / 100)
    lucro_em_reais = preco_venda_final - custo_total_cliente - valor_iss_reais
    
    return {
        "custo_total_cliente": round(custo_total_cliente, 2),
        "preco_venda_final": round(preco_venda_final, 2),
        "lucro_em_reais": round(lucro_em_reais, 2),
        "preco_por_palete_cliente": round(preco_venda_final / quantidade_paletes_cliente, 2) if quantidade_paletes_cliente > 0 else 0
    }