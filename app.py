import streamlit as st
from core.documento import gerar_contrato_word
import os
from core.documento import converter_docx_para_pdf
from datetime import datetime
from core.calculos import calcular_custo_por_posicao, simular_lucro_proposta

# Configuração da página
st.set_page_config(page_title="Gerador de Propostas", layout="wide")

# Gerador de memória oficial para a chave do componente de armazenagem
if "val_armazenagem" not in st.session_state:
    st.session_state.val_armazenagem = 115.00

# --- ADICIONANDO A LOGO DA EMPRESA ---
caminho_logo = "templates/logo1.png"

if os.path.exists(caminho_logo):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(caminho_logo, width=150)
    with col2:
        st.title("Sistema de Propostas - Armazenagem")
else:
    st.title("📄 Sistema de Propostas - Armazenagem")

# Injeta a faixa colorida no topo
st.markdown(
    """
    <style>
    .faixa-topo {
        background-color: #008f84;
        height: 15px;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
    }
    </style>
    <div class="faixa-topo"></div>
    """,
    unsafe_allow_html=True
)

# --- CAPTURA DE IMPOSTOS SEGURA ---
if "iss_padrao" not in st.session_state:
    st.session_state.iss_padrao = 2.0

# ==============================================================================
# 1. CRIAÇÃO DAS ABAS UNIFICADAS NO TOPO DA TELA
# ==============================================================================
aba_custos, aba_proposta, aba_config = st.tabs([
    "⚙️ Custos do Galpão", 
    "📋 Preenchimento da Proposta", 
    "📊 Configurações Fiscais"
])

# ==============================================================================
# --- ABA 1: CUSTOS DO GALPÃO ---
# ==============================================================================
with aba_custos:
    st.subheader("⚙️ Configurações Ocupacionais do Galpão")
    st.markdown("Use esta aba para atualizar os custos fixos mensais da estrutura.")
    
    col_aluguel, col_cond, col_luz, col_vagas = st.columns(4)
    with col_aluguel:
        aluguel = st.number_input("Aluguel (Mês)", value=30000.0, step=1000.0)
    with col_cond:
        condominio = st.number_input("Condomínio", value=0.0, step=500.0)
    with col_luz:
        utilidades = st.number_input("Água/Luz/Outros", value=0.0, step=500.0)
    with col_vagas:
        posicoes_totais = st.number_input("Total de Posições (PP)", value=600, step=50)

    # Cálculo do custo base usando o cérebro do sistema
    custo_base_palete = calcular_custo_por_posicao(aluguel, condominio, utilidades, posicoes_totais)

    st.info(f"💡 **Custo Base da Operação:** Cada posição-palete custa hoje **R$ {custo_base_palete:.2f}** por mês para a empresa.")


# ==============================================================================
# --- ABA 2: PREENCHIMENTO DA PROPOSTA ---
# ==============================================================================
with aba_proposta:
    st.subheader("Dados Comerciais do Cliente")

    data_atual_sugestao = datetime.now().strftime("%Y%m%d")
    codigo_padrao = f"{data_atual_sugestao}-R0"

    col_cod, col_vazia = st.columns([1, 2])
    with col_cod:
        codigo_proposta = st.text_input(
            "Código de Controle da Proposta (Revisão)", 
            value=codigo_padrao,
            help="O sistema gera a data atual e a Revisão R0 automaticamente. Altere para R1, R2, etc., se for uma contraproposta."
        )

    col_empresa, col_cnpj = st.columns(2)
    with col_empresa:
        nome_cliente = st.text_input("Nome do Cliente / Razão Social", placeholder="Ex: Logística Brasil LTDA")
    with col_cnpj:
        cnpj_cliente = st.text_input("CNPJ", placeholder="00.000.000/0000-00")
        
    st.markdown("---")
    
    # --------------------------------------------------------------------------
    # NOVO SIMULADOR DE MARGEM (Dentro da aba de preenchimento)
    # --------------------------------------------------------------------------
    st.subheader("📊 Simulador de Negociação Estratégica")
    col_cliente, col_slider = st.columns([1, 2])

    with col_cliente:
        paletes_cliente = st.number_input("Quantidade de Paletes do Cliente", value=100, step=10)

    with col_slider:
        margem_desejada = st.slider(
            "Margem de Lucro Desejada (%)", 
            min_value=0, 
            max_value=90, 
            value=30, 
            step=5,
            help="Arraste para ajustar a porcentagem de lucro real calculada sobre a venda."
        )
        
    # Enviamos o iss_padrao como o quarto ingrediente do cálculo
    resultados = simular_lucro_proposta(custo_base_palete, paletes_cliente, margem_desejada, st.session_state.iss_padrao)
    
    # 2. Atualizamos a nossa caixinha de memória com o novo valor sugerido pelo simulador
    st.session_state.val_armazenagem = float(resultados['preco_por_palete_cliente'])

    st.markdown("### 📈 Resumo Comercial da Proposta")
    col_card1, col_card2, col_card3 = st.columns(3)

    with col_card1:
        st.metric(label="Custo Seco da Operação", value=f"R$ {resultados['custo_total_cliente']:.2f}")
    with col_card2:
        st.metric(label="Preço por Palete (Sugerido)", value=f"R$ {resultados['preco_por_palete_cliente']:.2f}")
    with col_card3:
        st.metric(
            label="Lucro Líquido Estimado", 
            value=f"R$ {resultados['lucro_em_reais']:.2f}",
            delta=f"Preço Total: R$ {resultados['preco_venda_final']:.2f}",
            delta_color="normal"
        )

    st.markdown("---")
    st.subheader("Tabela de Preços dos Serviços")
    st.write("Preencha os valores, bases e periodicidades combinados com o cliente.")
    
    opcoes_periodo = ["MENSAL", "Sob Demanda", "QUINZENAL", "DIÁRIO", "-"]

    # --- ITEM 2.1: ARMAZENAGEM ---
    st.markdown("### 2.1 Armazenagem")
    st.caption("A cobrança será realizada sobre o saldo anterior somando entradas do período e deduzindo as saídas...")
    
    col_v1, col_b1, col_p1 = st.columns(3)
    with col_v1:
        # Agora o campo usa a memória dinâmica (value=st.session_state.valor_calculado_armazenagem)
        valor_armazenagem = st.number_input(
            "Valor (R$)", 
            min_value=0.0, 
            step=0.50, 
            key="val_armazenagem"
        )
    with col_b1:
        base_armazenagem = st.selectbox("Base", ["Por Pallet.", "Por M²", "Por Posição Palete"], index=0, key="base_armazenagem")
    with col_p1:
        periodo_armazenagem = st.selectbox("Periodicidade", opcoes_periodo, index=0, key="per_armazenagem")
        
    # --- ITEM 2.2: MOVIMENTAÇÃO DE ENTRADA ---
    st.markdown("### 2.2 Movimentação de Entrada (Cross-docking)")
    st.caption("Desembarque, conferência, etiquetagem padrão WMS, input sistêmico, endereçamento, geração de relatórios.")
    col_v2, col_b2, col_p2 = st.columns(3)
    with col_v2:
        valor_entrada_cross = st.number_input("Valor (R$)", min_value=0.0, value=20.00, step=0.50, key="val_entrada_cross")
    with col_b2:
        base_entrada_cross = st.selectbox("Base", ["Por pallet", "Por Volume"], index=0, key="base_entrada_cross")
    with col_p2:
        periodo_entrada_cross = st.selectbox("Periodicidade", opcoes_periodo, index=0, key="per_entrada_cross")

    # --- ITEM 2.3: MOVIMENTAÇÃO DE ENTRADA (CONTAINER) ---
    st.markdown("### 2.3 Movimentação de Entrada (Desova de Container)")
    st.caption("Desembarque, Desova de container, conferência, etiquetagem padrão WMS, input sistêmico, endereçamento, geração de relatórios.")
    col_v3, col_b3, col_p3 = st.columns(3)
    with col_v3:
        valor_entrada_cont = st.number_input("Valor (R$)", min_value=0.0, value=0.50, step=0.05, key="val_entrada_cont")
    with col_b3:
        base_entrada_cont = st.selectbox("Base", ["Por Caixa MASTER", "Por Unidade"], index=0, key="base_entrada_cont")
    with col_p3:
        periodo_entrada_cont = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_entrada_cont")

    # --- ITEM 2.4: PALETIZAÇÃO RECEBIMENTO ---
    st.markdown("### 2.4 Paletização Recebimento (Incluso Stretch)")
    st.caption("Cenário de recebimento de carga batida ou fora do padrão de paletização. Neste cenário será cobrado PALETIZAÇÃO + MOVIMENTAÇÃO DE ENTRADA.")
    col_v4, col_b4, col_p4 = st.columns(3)
    with col_v4:
        valor_paletizacao = st.number_input("Valor (R$)", min_value=0.0, value=8.50, step=0.50, key="val_paletizacao")
    with col_b4:
        base_paletizacao = st.selectbox("Base", ["Por Pallet", "Por Volume"], index=0, key="base_paletizacao")
    with col_p4:
        periodo_paletizacao = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_paletizacao")

    # --- ITEM 2.5: FORRAÇÃO ---
    st.markdown("### 2.5 Forração (Folha de Papel Kraft)")
    st.caption("Especialmente utilizado em armazenamento de produtos alimentícios (por exigência da VIGILÂNCIA SANITÁRIA), serve para evitar o contato do produto diretamente com o pallet e evitar acúmulo de poeira na parte superior.")
    col_v5, col_b5, col_p5 = st.columns(3)
    with col_v5:
        valor_forracao = st.number_input("Valor (R$)", min_value=0.0, value=0.00, step=0.10, key="val_forracao")
    with col_b5:
        base_forracao = st.selectbox("Base", ["Por Folha", "Por Pallet"], index=0, key="base_forracao")
    with col_p5:
        periodo_forracao = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_forracao")

    # --- ITEM 2.6: MOVIMENTAÇÃO INTERNA ---
    st.markdown("### 2.6 Movimentação Interna")
    st.caption("Separação de pallet ou fração por solicitação do cliente seja por qualquer motivo, onde o produto retorne ao estoque.")
    col_v6, col_b6, col_p6 = st.columns(3)
    with col_v6:
        valor_mov_interna = st.number_input("Valor (R$)", min_value=0.0, value=0.00, step=1.00, key="val_mov_interna")
    with col_b6:
        base_mov_interna = st.selectbox("Base", ["Por NF", "Por Pallet"], index=0, key="base_mov_interna")
    with col_p6:
        periodo_mov_interna = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_mov_interna")

    # --- ITEM 2.7: INVENTÁRIOS ---
    st.markdown("### 2.7 Inventários")
    st.caption("Contagem geral ou cíclica de produtos por solicitação do cliente.")
    col_v7, col_b7, col_p7 = st.columns(3)
    with col_v7:
        valor_inventario = st.number_input("Valor (R$)", min_value=0.0, value=14.00, step=0.50, key="val_inventario")
    with col_b7:
        base_inventario = st.selectbox("Base", ["Por Pallet", "Por Item"], index=0, key="base_inventario")
    with col_p7:
        periodo_inventario = st.selectbox("Periodicidade", opcoes_periodo, index=0, key="per_inventario")

    # --- ITEM 2.8: PICKING EXPEDIÇÃO ---
    st.markdown("### 2.8 Picking Expedição (Fracionamento por Volume)")
    st.caption("Fracionamento por volume (cx máster) ou fração proporcional (unidades). Neste cenário será cobrado PICKING + MOVIMENTAÇÃO DE SAÍDA.")
    col_v8, col_b8, col_p8 = st.columns(3)
    with col_v8:
        valor_picking_nf = st.number_input("Valor (R$)", min_value=0.0, value=3.80, step=0.10, key="val_picking_nf")
    with col_b8:
        base_picking_nf = st.selectbox("Base", ["Por NF", "Por Volume"], index=0, key="base_picking_nf")
    with col_p8:
        periodo_picking_nf = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_picking_nf")

    # --- ITEM 2.9: PICKING EXPEDIÇÃO (POR PALLET) ---
    st.markdown("### 2.9 Picking Expedição (Por Pallet)")
    st.caption("Fracionamento por volume (cx máster) ou fração proporcional (unidades). Neste cenário será cobrado PICKING + MOVIMENTAÇÃO DE SAÍDA.")
    col_v9, col_b9, col_p9 = st.columns(3)
    with col_v9:
        valor_picking_plt = st.number_input("Valor (R$)", min_value=0.0, value=10.50, step=0.50, key="val_picking_plt")
    with col_b9:
        base_picking_plt = st.selectbox("Base", ["Por Pallet", "Por Volume"], index=0, key="base_picking_plt")
    with col_p9:
        periodo_picking_plt = st.selectbox("Periodicidade", opcoes_periodo, index=0, key="per_picking_plt")

    # --- ITEM 2.10: MOVIMENTAÇÃO DE SAÍDA ---
    st.markdown("### 2.10 Movimentação de Saída")
    st.caption("Separação, conferência, etiquetagem padrão WMS, emission de NF e embarque.")
    col_v10, col_b10, col_p10 = st.columns(3)
    with col_v10:
        valor_saida = st.number_input("Valor (R$)", min_value=0.0, value=0.90, step=0.05, key="val_saida")
    with col_b10:
        base_saida = st.selectbox("Base", ["Por VOLUME", "Por Pallet"], index=0, key="base_saida")
    with col_p10:
        periodo_saida = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_saida")

    # --- ITEM 2.11: LABELING ---
    st.markdown("### 2.11 Labeling (Impressão de Etiqueta)")
    st.caption("Quando o cliente solicita Impressão ETIQUETA PADRÃO WMS.")
    col_v11, col_b11, col_p11 = st.columns(3)
    with col_v11:
        valor_labeling = st.number_input("Valor (R$)", min_value=0.0, value=0.18, step=0.01, key="val_labeling")
    with col_b11:
        base_labeling = st.selectbox("Base", ["Por Etiqueta", "Por Pallet"], index=0, key="base_labeling")
    with col_p11:
        periodo_labeling = st.selectbox("Periodicidade", opcoes_periodo, index=0, key="per_labeling")

    # --- ITEM 2.12: PACKING PADRÃO ---
    st.markdown("### 2.12 Packing Padrão")
    st.caption("Embalagem dos kits com nossas caixas padrões.")
    col_v12, col_b12, col_p12 = st.columns(3)
    with col_v12:
        valor_packing_padrao = st.number_input("Valor (R$)", min_value=0.0, value=0.00, step=0.50, key="val_packing_padrao")
    with col_b12:
        base_packing_padrao = st.selectbox("Base", ["Sob Demanda", "Por Caixa"], index=0, key="base_packing_padrao")
    with col_p12:
        periodo_packing_padrao = st.selectbox("Periodicidade", opcoes_periodo, index=1, key="per_packing_padrao")

    # --- ITEM 2.13: PACKING ESPECIAL ---
    st.markdown("### 2.13 Packing Especial")
    st.caption("Embalagem dos kits que demandem utilização de embalagens fora dos nossos padrões de caixas.")
    col_v13, col_b13, col_p13 = st.columns(3)
    with col_v13:
        valor_packing_esp = st.number_input("Valor (R$)", min_value=0.0, value=0.00, step=0.50, key="val_packing_esp")
    with col_b13:
        base_packing_esp = st.selectbox("Base", ["Sob Demanda", "Por Caixa"], index=0, key="base_packing_esp")
    with col_p13:
        periodo_packing_esp = st.selectbox("Periodicidade", opcoes_periodo, index=1, key="per_packing_esp")

    # --- ITEM 2.14: ALUGUEL DE PALETE PBR ---
    st.markdown("### 2.14 Aluguel de Palete PBR")
    st.caption("Quando se utiliza pallets PBR para armazenagem.")
    col_v14, col_b14, col_p14 = st.columns(3)
    with col_v14:
        valor_aluguel_pbr = st.number_input("Valor (R$)", min_value=0.0, value=0.00, step=0.50, key="val_aluguel_pbr")
    with col_b14:
        base_aluguel_pbr = st.selectbox("Base", ["-", "Por Pallet"], index=0, key="base_aluguel_pbr")
    with col_p14:
        periodo_aluguel_pbr = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_aluguel_pbr")

    # --- ITEM 2.15: COMPRA DE PALETE PBR ---
    st.markdown("### 2.15 Compra de Palete PBR")
    st.caption("Quando da necessidade de embarque do nosso pallet PBR.")
    col_v15, col_b15, col_p15 = st.columns(3)
    with col_v15:
        valor_compra_pbr = st.number_input("Valor (R$)", min_value=0.0, value=41.00, step=1.00, key="val_compra_pbr")
    with col_b15:
        base_compra_pbr = st.selectbox("Base", ["Por Pallet", "-"], index=0, key="base_compra_pbr")
    with col_p15:
        periodo_compra_pbr = st.selectbox("Periodicidade", opcoes_periodo, index=0, key="per_compra_pbr")

    # --- ITEM 2.16: LABELING (MANUSEIO MONTAGEM KIT) ---
    st.markdown("### 2.16 Labeling (Manuseio e Montagem de Kit)")
    st.caption("Serviço de manuseio e etiquetagem especial para montagem de kits.")
    col_v16, col_b16, col_p16 = st.columns(3)
    with col_v16:
        valor_montagem_kit = st.number_input("Valor (R$)", min_value=0.0, value=3.90, step=0.10, key="val_montagem_kit")
    with col_b16:
        base_montagem_kit = st.selectbox("Base", ["Por unidade", "Por Kit"], index=0, key="base_montagem_kit")
    with col_p16:
        periodo_montagem_kit = st.selectbox("Periodicidade", opcoes_periodo, index=1, key="per_montagem_kit")

    # --- ITEM 2.17: SEGURO ARMAZENAGEM ---
    st.markdown("### 2.17 Seguro Armazenagem (Ad Valorem)")
    st.caption("Seguro cobrado com base no valor total da Nota Fiscal de entrada dos produtos.")
    col_v17, col_b17, col_p17 = st.columns(3)
    with col_v17:
        valor_seguro = st.number_input("Porcentagem (%)", min_value=0.0, max_value=100.0, value=0.19, step=0.01, key="val_seguro")
    with col_b17:
        base_seguro = st.selectbox("Base", ["Valor (R$) Nota fiscal de entrada dos produtos"], index=0, key="base_seguro")
    with col_p17:
        periodo_seguro = st.selectbox("Periodicidade", opcoes_periodo, index=0, key="per_seguro")

    # --- ITEM 2.18: DESOVA DE CARGA FRACIONADA ---
    st.markdown("### 2.18 Desova de Carga Fracionada")
    st.caption("Custos aplicados para a desova de veículos com carga fracionada.")
    col_v18, col_b18, col_p18 = st.columns(3)
    with col_v18:
        valor_desova_frac = st.number_input("Valor (R$)", min_value=0.0, value=500.00, step=50.00, key="val_desova_frac")
    with col_b18:
        base_desova_frac = st.selectbox("Base", ["Por Veículo", "Por Pallet"], index=0, key="base_desova_frac")
    with col_p18:
        periodo_desova_frac = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_desova_frac")

    # --- ITEM 2.19: DESOVA / CARREGAMENTO TRUCK ---
    st.markdown("### 2.19 Desova / Carregamento Truck ou Container 20'")
    st.caption("Operação Manual ou Mecânica por veículo do tipo Truck or Container de 20 pés.")
    col_v19, col_b19, col_p19 = st.columns(3)
    with col_v19:
        valor_desova_20 = st.number_input("Valor (R$)", min_value=0.0, value=850.00, step=50.00, key="val_desova_20")
    with col_b19:
        base_desova_20 = st.selectbox("Base", ["Por Veículo", "Por Contêiner"], index=0, key="base_desova_20")
    with col_p19:
        periodo_desova_20 = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_desova_20")

    # --- ITEM 2.20: DESOVA / CARREGAMENTO CARRETA ---
    st.markdown("### 2.20 Desova / Carregamento Carreta ou Container 40'")
    st.caption("Operação Manual ou Mecânica por veículo do tipo Carreta ou Container de 40 pés.")
    col_v20, col_b20, col_p20 = st.columns(3)
    with col_v20:
        valor_desova_40 = st.number_input("Valor (R$)", min_value=0.0, value=850.00, step=50.00, key="val_desova_40")
    with col_b20:
        base_desova_40 = st.selectbox("Base", ["Por Veículo", "Por Contêiner"], index=0, key="base_desova_40")
    with col_p20:
        periodo_desova_40 = st.selectbox("Periodicidade", opcoes_periodo, index=4, key="per_desova_40")

    # --- ITEM 2.21: HORA EXTRA OPERACIONAL ---
    st.markdown("### 2.21 Hora Extra por Equipe (Quando necessário e autorizado)")
    st.caption("Valor cobrado por hora de operação estendida fora do horário padrão da base.")
    col_v21, col_b21, col_p21 = st.columns(3)
    with col_v21:
        valor_hora_extra = st.number_input("Valor da Hora (R$)", min_value=0.0, value=50.00, step=5.00, key="val_hora_extra")
    with col_b21:
        base_hora_extra = st.selectbox("Condição", ["Dias úteis após o horário", "Sábados, Domingos e Feriados (Dobro)"], index=0, key="base_hora_extra")
    with col_p21:
        periodo_hora_extra = st.selectbox("Periodicidade", opcoes_periodo, index=1, key="per_hora_extra")

    st.markdown("---")
    
    # --------------------------------------------------------------------------
    # BOTÃO DE GERAR CONTRATO (Sempre na aba da proposta)
    # --------------------------------------------------------------------------
    if st.button("🚀 Gerar Proposta Comercial", use_container_width=True, type="primary"):
        if not nome_cliente or not cnpj_cliente:
            st.error("⚠️ Por favor, preencha o Nome do Cliente e o CNPJ antes de gerar a proposta.")
        else:
            st.success(f"Processando os dados para a empresa: {nome_cliente}...")
            
            def fmt_moeda(valor):
                return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            dados_da_proposta = {
                "{{NOME_CLIENTE}}": nome_cliente,
                "{{CNPJ_CLIENTE}}": cnpj_cliente,
                "{{CODIGO_PROPOSTA}}": codigo_proposta,
                
                # Itens 2.1 a 2.3
                "{{ITEM_1}}": "2.1", "{{VALOR_1}}": fmt_moeda(valor_armazenagem), "{{BASE_1}}": base_armazenagem, "{{PER_1}}": periodo_armazenagem,
                "{{ITEM_2}}": "2.2", "{{VALOR_2}}": fmt_moeda(valor_entrada_cross), "{{BASE_2}}": base_entrada_cross, "{{PER_2}}": periodo_entrada_cross,
                "{{ITEM_3}}": "2.3", "{{VALOR_3}}": fmt_moeda(valor_entrada_cont), "{{BASE_3}}": base_entrada_cont, "{{PER_3}}": periodo_entrada_cont,
                
                # Itens 2.4 a 2.7
                "{{ITEM_4}}": "2.4", "{{VALOR_4}}": fmt_moeda(valor_paletizacao), "{{BASE_4}}": base_paletizacao, "{{PER_4}}": periodo_paletizacao,
                "{{ITEM_5}}": "2.5", "{{VALOR_5}}": fmt_moeda(valor_forracao), "{{BASE_5}}": base_forracao, "{{PER_5}}": periodo_forracao,
                "{{ITEM_6}}": "2.6", "{{VALOR_6}}": fmt_moeda(valor_mov_interna), "{{BASE_6}}": base_mov_interna, "{{PER_6}}": periodo_mov_interna,
                "{{ITEM_7}}": "2.7", "{{VALOR_7}}": fmt_moeda(valor_inventario), "{{BASE_7}}": base_inventario, "{{PER_7}}": periodo_inventario,
                
                # Itens 2.8 a 2.11
                "{{ITEM_8}}": "2.8", "{{VALOR_8}}": fmt_moeda(valor_picking_nf), "{{BASE_8}}": base_picking_nf, "{{PER_8}}": periodo_picking_nf,
                "{{ITEM_9}}": "2.9", "{{VALOR_9}}": fmt_moeda(valor_picking_plt), "{{BASE_9}}": base_picking_plt, "{{PER_9}}": periodo_picking_plt,
                "{{ITEM_10}}": "2.10", "{{VALOR_10}}": fmt_moeda(valor_saida), "{{BASE_10}}": base_saida, "{{PER_10}}": periodo_saida,
                "{{ITEM_11}}": "2.11", "{{VALOR_11}}": fmt_moeda(valor_labeling), "{{BASE_11}}": base_labeling, "{{PER_11}}": periodo_labeling,
                
                # Itens 2.12 a 2.15
                "{{ITEM_12}}": "2.12", "{{VALOR_12}}": fmt_moeda(valor_packing_padrao), "{{BASE_12}}": base_packing_padrao, "{{PER_12}}": periodo_packing_padrao,
                "{{ITEM_13}}": "2.13", "{{VALOR_13}}": fmt_moeda(valor_packing_esp), "{{BASE_13}}": base_packing_esp, "{{PER_13}}": periodo_packing_esp,
                "{{ITEM_14}}": "2.14", "{{VALOR_14}}": fmt_moeda(valor_aluguel_pbr), "{{BASE_14}}": base_aluguel_pbr, "{{PER_14}}": periodo_aluguel_pbr,
                "{{ITEM_15}}": "2.15", "{{VALOR_15}}": fmt_moeda(valor_compra_pbr), "{{BASE_15}}": base_compra_pbr, "{{PER_15}}": periodo_compra_pbr,
                
                # Itens 2.16 a 2.17
                "{{ITEM_16}}": "2.16", "{{VALOR_16}}": f"{valor_seguro:.2f}%", "{{BASE_16}}": base_seguro, "{{PER_16}}": periodo_seguro,
                "{{ITEM_17}}": "2.17", "{{VALOR_17}}": fmt_moeda(valor_montagem_kit), "{{BASE_17}}": base_montagem_kit, "{{PER_17}}": periodo_montagem_kit,
                
                # Itens 2.18 a 2.20
                "{{ITEM_18}}": "2.18", "{{VALOR_18}}": fmt_moeda(valor_desova_frac), "{{BASE_18}}": base_desova_frac, "{{PER_18}}": periodo_desova_frac,
                "{{ITEM_19}}": "2.19", "{{VALOR_19}}": fmt_moeda(valor_desova_20), "{{BASE_19}}": base_desova_20, "{{PER_19}}": periodo_desova_20,
                "{{ITEM_20}}": "2.20", "{{VALOR_20}}": fmt_moeda(valor_desova_40), "{{BASE_20}}": base_desova_40, "{{PER_20}}": periodo_desova_40,
                
                "{{ITEM_21}}": "2.21"
            }
            
            caminho_do_modelo = "templates/modelo.docx"
            caminho_de_saida = f"templates/Proposta_{nome_cliente.replace(' ', '_')}.docx"
            
            try:
                with st.spinner("⚙️ Processando dados e gerando documentos..."):
                    gerar_contrato_word(caminho_do_modelo, caminho_de_saida, dados_da_proposta)
                    caminho_pdf = caminho_de_saida.replace(".docx", ".pdf")
                    
                    from core.documento import converter_docx_para_pdf
                    sucesso_pdf = converter_docx_para_pdf(caminho_de_saida, caminho_pdf)
                
                if sucesso_pdf and os.path.exists(caminho_pdf):
                    st.toast("Proposta gerada com sucesso!", icon="✅")
                    st.success("### 📄 Proposta Comercial Disponível para Download")
                    st.markdown("Os documentos foram gerados e revisados pelo sistema. Clique no botão abaixo para baixar o arquivo final em formato PDF.")
                    
                    with open(caminho_pdf, "rb") as f_pdf:
                        st.download_button(
                            label="📥 Baixar Proposta Comercial (PDF)",
                            data=f_pdf,
                            file_name=f"Proposta_{nome_cliente.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.warning("⚠️ O Word foi gerado, mas houve uma limitação ao converter para PDF localmente.")
                    
            except Exception as e:
                st.error(f"Erro ao gerar o arquivo: {e}")


# --- ABA 3: CONFIGURAÇÕES FISCAIS ---
# --- ABA 3: CONFIGURAÇÕES FISCAIS ---
with aba_config:
    st.subheader("Configurações de Impostos e Taxas")
    st.write("Altere as alíquotas padrão se houver mudanças na legislação.")
    
    # Usando a key="iss_padrao", o Streamlit vincula o campo diretamente com a memória do topo!
    st.number_input("Alíquota do ISS (%)", min_value=0.0, max_value=100.0, step=0.1, key="iss_padrao")