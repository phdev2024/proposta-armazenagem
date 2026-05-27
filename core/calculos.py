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


def simular_lucro_proposta(custo_de_uma_posicao, quantidade_paletes_cliente, margem_lucro_desejada):
    """
    PASSO 2: Calcula o custo total do cliente e simula o preço de venda com base na margem (Markup).
    """
    custo_total_cliente = custo_de_uma_posicao * quantidade_paletes_cliente
    
    if margem_lucro_desejada >= 100:
        margem_lucro_desejada = 99  
        
    fator_markup = 1 - (margem_lucro_desejada / 100)
    preco_venda_final = custo_total_cliente / fator_markup
    lucro_em_reais = preco_venda_final - custo_total_cliente
    
    return {
        "custo_total_cliente": round(custo_total_cliente, 2),
        "preco_venda_final": round(preco_venda_final, 2),
        "lucro_em_reais": round(lucro_em_reais, 2),
        "preco_por_palete_cliente": round(preco_venda_final / quantidade_paletes_cliente, 2) if quantidade_paletes_cliente > 0 else 0
    }