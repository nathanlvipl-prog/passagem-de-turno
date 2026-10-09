import streamlit as st
from datetime import datetime, timezone, timedelta
import pandas as pd
import requests

# ---------------------------------------------------------
# CONFIGURAÇÕES DE FUSO HORÁRIO BRASIL (UTC-3) E TURNO
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

# Cadastro de Colaboradores
CADASTRO_COLABORADORES = {
    "32164": "SILVIO NATHANAEL MEDEIROS DA SILVA",
    "32177": "EMANUEL LUCAS SEVERIANO DE SOUSA",
}

# Mapeamento de Máquinas por Setor
MAQUINAS_POR_SETOR = {
    "Polivalente": ["LEEPACK", "VOLPACK", "EVOLUTION 1", "LINEA 1", "LINEA 2", "STICK 01", "STICK 02", "M028"],
    "Instantâneos": ["BOSCH 16", "BOSCH 22", "HDB", "STICK INSTANTÂNEO"],
    "Revolução": ["REVOLUÇÃO 01", "REVOLUÇÃO 02"]
}

# Dicionário de Códigos de Ocorrências da Ficha PRO.DC1416
CODIGOS_OCORRENCIAS = {
    "11": "SEM PROGRAMAÇÃO", "12": "REFEIÇÃO", "14": "DDS", "15": "REUNIÃO/TREINAMENTOS/FESTAS",
    "17": "MANUTENÇÃO PREVENTIVA", "20": "INÍCIO/FIM DE PRODUÇÃO", "21": "TESTES", "22": "INVENTÁRIO",
    "24": "MANUTENÇÃO CORRETIVA ELÉTRICA", "25": "MANUTENÇÃO CORRETIVA MECÂNICA", "95": "AGUARDANDO MANUTENÇÃO",
    "97": "SETUP", "101": "FALTA DE PESSOAL", "102": "LIMPEZA DE ÁREA", "105": "LIMPEZA DE EQUIPAMENTO/ÁREA",
    "107": "TROCA DE BOBINA", "109": "TROCA DE INSUMOS", "111": "ATRASO NO INÍCIO DO TURNO",
    "113": "REGULAGEM DE MÁQUINA", "117": "AJUSTE DE GUIAS", "124": "AJUSTE DE DATADOR",
    "127": "AJUSTE SELADORA 3M", "128": "ACÚMULO NA ESTEIRA DA LINHA", "131": "PARADA DA ESTEIRA DE TRANSPORTE",
    "141": "AJUSTE DE ENCAIXOTADORA", "155": "TROCA DE MOEGA", "401": "FALTA DE ENERGIA", "402": "FALTA DE ÁGUA",
    "404": "FALTA DE AR COMPRIMIDO", "407": "FALTA DE PRODUTO", "408": "PROBLEMA DE REDE/TI",
    "501": "FALTA DE INSUMO/MATÉRIA PRIMA", "504": "FALTA DE ESPAÇO - ESTOQUE CHEIO",
    "601": "PROBLEMA NA EMBALAGEM PRIMÁRIA", "603": "PROBLEMA NA EMBALAGEM SECUNDÁRIA",
    "604": "DESVIOS DE QUALIDADE", "608": "RETRABALHO DE PRODUTO NÃO CONFORME"
}

st.set_page_config(
    page_title="Qualit3c | PRO.DC1416 Digital",
    page_icon="📋",
    layout="wide"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS
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
        font-size: 1.3rem;
        font-weight: 800;
        margin: 0;
    }
    .qualit3c-footer {
        text-align: center;
        color: #7f8c8d;
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 30px;
        padding: 10px;
        border-top: 1px solid #dcdfe6;
    }
    .stButton > button {
        background-color: #e67e22 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

if "pagina" not in st.session_state:
    st.session_state.pagina = 1
if "operador_matricula" not in st.session_state:
    st.session_state.operador_matricula = ""
if "operador_nome" not in st.session_state:
    st.session_state.operador_nome = ""
if "setor_selecionado" not in st.session_state:
    st.session_state.setor_selecionado = "Polivalente"

dt_agora = obter_datetime_br()
turno_atual = calcular_turno(dt_agora)

# ---------------------------------------------------------
# PÁGINA 1: IDENTIFICAÇÃO DO OPERADOR E SETOR
# ---------------------------------------------------------
if st.session_state.pagina == 1:
    st.markdown("""
    <div class="qualit3c-topbar">
        <div class="qualit3c-title">🏭 Qualit3c — Controle de Empacotamento por Equipamento (PRO.DC1416)</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 1.8, 1])
    with col_c:
        st.subheader("🔑 Login do Operador")
        with st.form("form_login_operador"):
            mat_input = st.text_input("Matrícula do Operador:", placeholder="Ex: 32164")
            setor_input = st.selectbox("Setor de Atuação:", ["Polivalente", "Instantâneos", "Revolução"])
            
            btn_entrar = st.form_submit_button("INICIAR REGISTRO DIGITAL", use_container_width=True)
            if btn_entrar:
                mat_clean = mat_input.strip()
                if not mat_clean:
                    st.error("Informe a matrícula.")
                else:
                    nome_encontrado = CADASTRO_COLABORADORES.get(mat_clean, f"OPERADOR ({mat_clean})")
                    st.session_state.operador_matricula = mat_clean
                    st.session_state.operador_nome = nome_encontrado
                    st.session_state.setor_selecionado = setor_input
                    st.session_state.pagina = 2
                    st.rerun()

# ---------------------------------------------------------
# PÁGINA 2: FORMULÁRIO COMPLETO DA FICHA PRO.DC1416
# ---------------------------------------------------------
elif st.session_state.pagina == 2:
    st.markdown(f"""
    <div class="qualit3c-topbar">
        <div style="font-size: 0.85rem; font-weight: 700;">OPERADOR: {st.session_state.operador_nome.upper()} ({st.session_state.operador_matricula}) | SETOR: {st.session_state.setor_selecionado.upper()}</div>
        <div class="qualit3c-title">Controle de Empacotamento por Equipamento (PRO.DC1416 - R00)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"**Operador:** {st.session_state.operador_nome}")
    st.sidebar.markdown(f"**Matrícula:** {st.session_state.operador_matricula}")
    st.sidebar.markdown(f"**Setor:** {st.session_state.setor_selecionado}")
    if st.sidebar.button("Trocar Operador / Setor", use_container_width=True):
        st.session_state.pagina = 1
        st.rerun()

    maquinas_opcoes = MAQUINAS_POR_SETOR.get(st.session_state.setor_selecionado, [])

    aba_ficha, aba_misturas, aba_relatorio = st.tabs([
        "📝 Ficha da Máquina (PRO.DC1416)", 
        "🥣 Misturas e Pré-Mix", 
        "📄 Relatório Final / Passagem de Turno"
    ])

    with aba_ficha:
        st.subheader("1. Cabeçalho e Identificação da Máquina")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            maq_sel = st.selectbox("Máquina:", maquinas_opcoes)
        with c2:
            data_prod = st.date_input("Data:", dt_agora)
        with c3:
            turno_sel = st.selectbox("Turno:", ["Turno A", "Turno B", "Turno C"], index=["Turno A", "Turno B", "Turno C"].index(turno_atual))
        with c4:
            lote_prod = st.text_input("Lote:", placeholder="Ex: 1096176")

        c_p1, c_p2, c_p3, c_p4 = st.columns([2, 1, 1, 1])
        with c_p1:
            desc_produto = st.text_input("Descrição do Produto:", placeholder="Ex: CAP. CLASSIC")
        with c_p2:
            marca_produto = st.text_input("Marca:", placeholder="Ex: 3CORAÇÕES")
        with c_p3:
            gramatura_prod = st.text_input("Gramatura (g):", placeholder="Ex: 100")
        with c_p4:
            alergenico_sel = st.selectbox("Alergênico:", ["Leite e Soja", "Castanha", "Não Contém"])

        st.subheader("2. Tempos, Metas e Produção Final")
        tm1, tm2, tm3, tm4, tm5, tm6 = st.columns(6)
        with tm1:
            meta_prod = st.number_input("Meta (unid):", value=0, step=100)
        with tm2:
            tot_prod = st.number_input("Total Produção:", value=0, step=1)
        with tm3:
            hora_ini = st.time_input("Hora Início:", value=None)
        with tm4:
            tempo_desp = st.number_input("Tempo Desperdício (min):", value=0)
        with tm5:
            hora_fim = st.time_input("Hora Término:", value=None)
        with tm6:
            horas_trab = st.number_input("Horas Trabalhadas (min):", value=0)

        st.subheader("3. Desperdício e Perdas")
        d1, d2, d3, d4, d5 = st.columns(5)
        with d1:
            desp_primaria = st.number_input("Embalagem Primária (kg):", value=0.0, format="%.3f")
        with d2:
            desp_secundaria = st.number_input("Embalagem Secundária:", value=0.0)
        with d3:
            desp_terciaria = st.number_input("Embalagem Terciária:", value=0.0)
        with d4:
            desp_reprocesso = st.number_input("Reprocesso (kg):", value=0.0)
        with d5:
            desp_varricao = st.number_input("Varrição (kg):", value=0.0)

        st.subheader("4. Apontamento de Ocorrências (Códigos da Ficha)")
        st.caption("Selecione os códigos de paradas/ocorrências e informe o tempo em minutos.")
        
        lista_opcoes_oc = ["Nenhuma"] + [f"{k} - {v}" for k,v in CODIGOS_OCORRENCIAS.items()]
        
        c_oc1, c_oc2 = st.columns(2)
        with c_oc1:
            oc_cod1 = st.selectbox("Ocorrência 1:", lista_opcoes_oc, index=0)
            oc_min1 = st.number_input("Minutos Ocorrência 1:", value=0)
            
            oc_cod2 = st.selectbox("Ocorrência 2:", lista_opcoes_oc, index=0)
            oc_min2 = st.number_input("Minutos Ocorrência 2:", value=0)

        with c_oc2:
            oc_cod3 = st.selectbox("Ocorrência 3:", lista_opcoes_oc, index=0)
            oc_min3 = st.number_input("Minutos Ocorrência 3:", value=0)
            
            oc_cod4 = st.selectbox("Ocorrência 4:", lista_opcoes_oc, index=0)
            oc_min4 = st.number_input("Minutos Ocorrência 4:", value=0)

        st.subheader("5. Equipe Auxiliar e Observações")
        e1, e2 = st.columns(2)
        with e1:
            aux_empacotamento = st.text_input("Auxiliar Empacotamento:", placeholder="Ex: AUDACIR")
            operador_linha = st.text_input("Operador da Máquina:", placeholder="Ex: GILVAN")
        with e2:
            obs_gerais = st.text_area("Observações Gerais da Ficha:", placeholder="Informe observações adicionais da rodagem...")

    with aba_misturas:
        st.subheader("Controles de Misturas e Pré-Mix do Turno")
        cm1, cm2 = st.columns(2)
        with cm1:
            misturas_txt = st.text_area("Misturas Realizadas:", placeholder="Ex:\n4 café com leite tradicional\n4 capp classic food", height=140)
        with cm2:
            premix_txt = st.text_area("Pesagem de Pré-Mix:", placeholder="Ex:\n7 chocolate quente Lugano\n5 capp classic nova fórmula", height=140)
        cenario_premix_txt
