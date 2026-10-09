import streamlit as st
from datetime import datetime, timezone, timedelta
import pandas as pd
import requests

# ---------------------------------------------------------
# CONFIGURAÇÕES GERAIS E FUSO HORÁRIO BRASIL (UTC-3)
# ---------------------------------------------------------
FUSO_BR = timezone(timedelta(hours=-3))

def obter_datetime_br():
    return datetime.now(FUSO_BR)

def calcular_turno(dt=None):
    if dt is None:
        dt = obter_datetime_br()
    minutos_totais = dt.hour * 60 + dt.minute
    if 340 <= minutos_totais < 840:    # 05:40 - 14:00
        return "Turno A"
    elif 840 <= minutos_totais < 1340:  # 14:00 - 22:20
        return "Turno B"
    else:                              # 22:20 - 05:40
        return "Turno C"

st.set_page_config(
    page_title="Qualit3c | Passagem de Turno da Produção",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS (Padrão Qualit3c)
# ---------------------------------------------------------
st.markdown("""
<style>
    .qualit3c-topbar {
        background: linear-gradient(90deg, #d35400 0%, #e67e22 100%);
        color: #ffffff;
        padding: 14px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .qualit3c-title {
        font-size: 1.4rem;
        font-weight: 800;
        margin: 0;
    }
    .stButton > button {
        background-color: #e67e22 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
    }
    .stButton > button:hover {
        background-color: #d35400 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CABEÇALHO
# ---------------------------------------------------------
dt_hoje = obter_datetime_br()
turno_sugerido = calcular_turno(dt_hoje)

st.markdown(f"""
<div class="qualit3c-topbar">
    <div class="qualit3c-title">📋 Qualit3c — Relatório de Passagem de Turno da Produção</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR / PARÂMETROS
# ---------------------------------------------------------
st.sidebar.header("⚙️ Parâmetros do Relatório")
data_relatorio = st.sidebar.date_input("Data da Produção", dt_hoje)
turno_selecionado = st.sidebar.selectbox("Turno", ["Turno A", "Turno B", "Turno C"], index=["Turno A", "Turno B", "Turno C"].index(turno_sugerido))
supervisor_nome = st.sidebar.text_input("Supervisor Responsável", value="Nathanael")

# Lista das Máquinas Padrão da Fábrica
MAQUINAS_LISTA = [
    "Volpack", "Evolution 1", "Leepack", "Bosch 16", 
    "Linea 1", "Linea 2", "Stick 01", "Stick 02", "M028"
]

# ---------------------------------------------------------
# ABAS DO APLICATIVO
# ---------------------------------------------------------
aba1, aba2, aba3, aba4 = st.tabs([
    "⚙️ Produção por Máquina", 
    "🥣 Misturas e Pré-Mix", 
    "🔄 Cenário e Transição de Turnos", 
    "📄 Gerar Relatório Final"
])

# ---------------------------------------------------------
# ABA 1: PRODUÇÃO E OCORRÊNCIAS POR MÁQUINA
# ---------------------------------------------------------
with aba1:
    st.subheader("📊 Produção Final e Ocorrências das Máquinas")
    st.caption("Insira a produção física confirmada e as observações operacionais de cada linha.")
    
    dados_maquinas = {}
    
    col_a, col_b = st.columns(2)
    
    for idx, maq in enumerate(MAQUINAS_LISTA):
        col_alvo = col_a if idx % 2 == 0 else col_b
        
        with col_alvo:
            with st.expander(f"🔹 **{maq}**", expanded=True):
                sem_prog = st.checkbox(f"Sem Programação ({maq})", key=f"sp_{maq}")
                
                if sem_prog:
                    dados_maquinas[maq] = {
                        "producao": "Sem programação",
                        "ocorrencias": [],
                        "produto": "-",
                        "lote": "-"
                    }
                else:
                    prod = st.number_input(f"Produção Final (unid):", min_value=0, value=0, step=100, key=f"prod_{maq}")
                    produto_desc = st.text_input("Produto / Descrição:", key=f"prod_desc_{maq}")
                    lote_num = st.text_input("Lote:", key=f"lote_{maq}")
                    
                    ocorrencias_raw = st.text_area(
                        "Ocorrências / Regulagens (uma por linha):", 
                        placeholder="Ex:\nTroca de bobina\nRegulagem operacional\nEsteira travando", 
                        key=f"ocor_{maq}",
                        height=100
                    )
                    
                    lista_ocor = [o.strip() for o in ocorrencias_raw.split("\n") if o.strip()]
                    
                    dados_maquinas[maq] = {
                        "producao": f"{prod:,}".replace(",", "."),
                        "produto": produto_desc,
                        "lote": lote_num,
                        "ocorrencias": lista_ocor
                    }

# ---------------------------------------------------------
# ABA 2: MISTURAS E PRÉ-MIX
# ---------------------------------------------------------
with aba2:
    st.subheader("🥣 Controles de Mistura e Pré-Mix")
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        st.markdown("### ☕ Misturas Realizadas")
        misturas_txt = st.text_area(
            "Liste as misturas (Ex: 4 café com leite tradicional):",
            placeholder="4 café com leite tradicional\n4 capp classic food\n2 capp santa clara",
            height=150
        )
        
    with col_m2:
        st.markdown("### ⚖️ Pesagem de Pré-Mix")
        premix_txt = st.text_area(
            "Liste a pesagem de pré-mix:",
            placeholder="7 chocolate quente Lugano\n5 capp classic nova fórmula",
            height=150
        )
        
    st.markdown("### 📦 Cenário Atual de Pré-Mix (Estoque em Linha)")
    cenario_premix_txt = st.text_area(
        "Cenário atual de Pré-mix preparado:",
        placeholder="1 Ultra coffe double shot\n3 Ultra coffee caramelo\n1 Capp Iguaçu tradicional 300kg exportação",
        height=200
    )

# ---------------------------------------------------------
# ABA 3: TRANSIÇÃO DE TURNOS (RECEBIDO E ENTREGUE)
# ---------------------------------------------------------
with aba3:
    st.subheader("🔄 Cenário de Posição de Máquinas (Reserva / Na Linha)")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.markdown("### 📥 Cenário Recebido do Turno Anterior")
        cenario_recebido = st.text_area(
            "Situação recebida:",
            value="028: 1 na linha e 1 reserva\nVolpack: meia na linha e 1 reserva\nLinea 1: 1 na linha e 2 reserva\nLinea 2: \nStick 01: 1 na linha\nStick 02: 1 na linha\nBosch: 1 na linha e 3 reserva\nLeepack: 3 reserva",
            height=250
        )
        
    with col_t2:
        st.markdown("### 📤 Cenário Entregue para o Próximo Turno")
        cenario_entregue = st.text_area(
            "Situação para o próximo turno:",
            value="028: 1 na linha e 1 reserva\nVolpack: 1 na linha\nLinea 1: 1 na linha e 1 reserva\nLinea 2: \nStick 01: 1 na linha\nStick 02: 1 na linha\nBosh 16: 1 na linha e 3 reserva\nLeepack: 1 na linha e 1 reserva",
            height=250
        )

# ---------------------------------------------------------
# ABA 4: GERAÇÃO E FORMATAÇÃO DO RELATÓRIO
# ---------------------------------------------------------
with aba4:
    st.subheader("📄 Relatório Consolidado de Passagem de Turno")
    
    data_str = data_relatorio.strftime("%d.%m")
    turno_letra = turno_selecionado.split()[-1]
    
    # Construção do Relatório em Texto Padronizado
    relatorio_linhas = []
    relatorio_linhas.append(f"📊 *Produção {data_str} Turno {turno_letra}*\n")
    
    for maq, info in dados_maquinas.items():
        relatorio_linhas.append(f"*{maq}:* {info['producao']}")
        if info['produto'] and info['produto'] != "-":
            relatorio_linhas.append(f"• Produto: {info['produto']} | Lote: {info['lote']}")
        for oc in info['ocorrencias']:
            relatorio_linhas.append(f"• {oc}")
        relatorio_linhas.append("")
        
    if misturas_txt.strip():
        relatorio_linhas.append("*Misturas:*")
        relatorio_linhas.append(misturas_txt.strip())
        relatorio_linhas.append("\n")
        
    if premix_txt.strip():
        relatorio_linhas.append("*Pesagem de Pré-Mix:*")
        relatorio_linhas.append(premix_txt.strip())
        relatorio_linhas.append("\n")
        
    if cenario_premix_txt.strip():
        relatorio_linhas.append("*Cenário atual de Pré-mix:*")
        for linha in cenario_premix_txt.strip().split("\n"):
            relatorio_linhas.append(f"• {linha.strip()}" if not linha.startswith("•") else linha)
        relatorio_linhas.append("\n")
        
    if cenario_recebido.strip():
        relatorio_linhas.append(f"*Cenário que recebemos:*")
        relatorio_linhas.append(cenario_recebido.strip())
        relatorio_linhas.append("\n")
        
    if cenario_entregue.strip():
        relatorio_linhas.append(f"*Cenário para o próximo turno:*")
        relatorio_linhas.append(cenario_entregue.strip())
        
    texto_relatorio_final = "\n".join(relatorio_linhas)
    
    st.text_area("Cópia rápida para WhatsApp / e-mail:", value=texto_relatorio_final, height=450)
    
    st.download_button(
        label="📥 Baixar Relatório (.txt)",
        data=texto_relatorio_final,
        file_name=f"Relatorio_Passagem_Turno_{turno_letra}_{data_str}.txt",
        mime="text/plain"
    )
