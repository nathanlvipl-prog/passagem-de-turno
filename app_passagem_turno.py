import streamlit as st
from datetime import datetime, timezone, timedelta
import pandas as pd

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

# Cadastro Oficial de Colaboradores
CADASTRO_COLABORADORES = {
    "32164": "SILVIO NATHANAEL MEDEIROS DA SILVA",
    "32177": "EMANUEL LUCAS SEVERIANO DE SOUSA",
    "32013": "RAFAEL FERREIRA DE OLIVEIRA",
    "32064": "WEVERTON BRUNO DE LIMA",
    "21491": "FLÁVIO GIOVANE FERNANDES DA SILVA",
    "32193": "SALATIEL SEBASTIÃO DE SOUZA JÚNIOR",
    "22052": "PAULO VITOR MENDES TEIXEIRA DA SILVA",
    "32037": "ÍTALO SILVA DO NASCIMENTO",
    "32308": "JOÃO VICTOR BARBOSA DA SILVA",
    "32179": "JOEDSON DOS SANTOS ARAÚJO",
}

# Mapeamento de Equipes por Máquina
EQUIPE_FIXA_MAQUINAS = {
    "M028": {
        "operador": "FLÁVIO GIOVANE FERNANDES DA SILVA",
        "auxiliares": ["LUAN TALES DA COSTA OLIVEIRA"]
    },
    "VOLPACK": {
        "operador": "SALATIEL SEBASTIÃO DE SOUZA JÚNIOR",
        "auxiliares": ["EVERSON ZAIRO SILVA DE ARAÚJO", "DENILSON SILVA DOS SANTOS", "ADSON ANDREY DE MOURA BATISTA"]
    },
    "EVOLUTION 01": {
        "operador": "JOEDSON DOS SANTOS ARAÚJO",
        "auxiliares": []
    },
    "EVOLUTION 02": {
        "operador": "WEVERTON BRUNO DE LIMA",
        "auxiliares": ["LUAN DE LIMA SILVA", "BRENDON HERISON BARBOSA DE OLIVEIRA", "NERISMAR ALVES CARVALHO", "SAMUEL DEYVID SILVA DE LIMA"]
    },
    "LINEA 01": {
        "operador": "ÍTALO SILVA DO NASCIMENTO",
        "auxiliares": ["JEFFERSON DA SILVA DE OLIVEIRA", "FRANCISCO APOLONIO DA SILVA", "DAVI SANTANA DE OLIVEIRA"]
    },
    "LINEA 02": {
        "operador": "",
        "auxiliares": ["ALISSON FORTUNATO DA SILVA", "EWERTON GOMES FERREIRA"]
    },
    "BOSCH 16": {
        "operador": "PAULO VITOR MENDES TEIXEIRA DA SILVA",
        "auxiliares": []
    },
    "LEEPACK": {
        "operador": "JOÃO VICTOR BARBOSA DA SILVA",
        "auxiliares": []
    }
}

MAQUINAS_POR_SETOR = {
    "Polivalente": ["M028", "VOLPACK", "EVOLUTION 01", "EVOLUTION 02", "LINEA 01", "LINEA 02", "BOSCH 16", "LEEPACK"],
    "Instantâneos": ["BOSCH 16", "BOSCH 22", "HDB", "STICK INSTANTÂNEO"],
    "Revolução": ["REVOLUÇÃO 01", "REVOLUÇÃO 02"]
}

CODIGOS_OCORRENCIAS = {
    "11": "11 | SEM PROGRAMAÇÃO", "12": "12 | REFEIÇÃO", "13": "13 | FORA DE TURNO", 
    "14": "14 | DDS", "15": "15 | REUNIÃO/TREINAMENTO/EVENTOS", "17": "17 | MANUTENÇÃO PREVENTIVA", 
    "20": "20 | INÍCIO DE PRODUÇÃO", "21": "21 | TESTES", "22": "22 | INVENTÁRIO",
    "24": "24 | MANUTENÇÃO CORRETIVA ELÉTRICA", "25": "25 | MANUTENÇÃO CORRETIVA MECÂNICA", 
    "40": "40 | INÍCIO DE PRODUÇÃO", "41": "41 | FIM DE PRODUÇÃO", "42": "42 | TROCA DE TURNO",
    "95": "95 | AGUARDANDO MANUTENÇÃO", "97": "97 | SETUP", "101": "101 | FALTA DE PESSOAL", 
    "102": "102 | LIMPEZA DE ÁREA", "105": "105 | LIMPEZA DE EQUIPAMENTO/ÁREA",
    "107": "107 | TROCA DE BOBINA", "109": "109 | TROCA DE INSUMOS", "111": "111 | ATRASO NO INÍCIO DO TURNO",
    "113": "113 | REGULAGEM DE MÁQUINA", "117": "117 | AJUSTE DE GUIAS", "124": "124 | AJUSTE DE DATADOR",
    "127": "127 | AJUSTE SELADORA 3M", "128": "128 | ACÚMULO NA ESTEIRA DA LINHA", "131": "131 | PARADA DA ESTEIRA DE TRANSPORTE",
    "141": "141 | AJUSTE DE ENCAIXOTADORA", "155": "155 | TROCA DE MOEGA", "401": "401 | FALTA DE ENERGIA", 
    "402": "402 | FALTA DE ÁGUA", "404": "404 | FALTA DE AR COMPRIMIDO", "407": "407 | FALTA DE PRODUTO", 
    "408": "408 | PROBLEMA DE REDE/TI", "501": "501 | FALTA DE INSUMO/MATÉRIA PRIMA", 
    "504": "504 | FALTA DE ESPAÇO - ESTOQUE CHEIO", "601": "601 | PROBLEMA NA EMBALAGEM PRIMÁRIA", 
    "603": "603 | PROBLEMA NA EMBALAGEM SECUNDÁRIA", "604": "604 | DESVIOS DE QUALIDADE", 
    "608": "608 | RETRABALHO DE PRODUTO NÃO CONFORME"
}

# Base de Dados Oficial Extraída Integralmente da sua Planilha "OP TESTE"
DADOS_BASE_OFICIAL = [
    # LEEPACK
    {"maquina": "LEEPACK", "produto": "CAFE C/LEIT 3C REF 24X100G", "lote": "1098836", "marca": "3CORAÇÕES", "gramatura": "100g"},
    
    # BOSCH 16
    {"maquina": "BOSCH 16", "produto": "CAFE CAPP SC FOOD 5X1KG", "lote": "1098834", "marca": "3CORAÇÕES", "gramatura": "1kg"},
    {"maquina": "BOSCH 16", "produto": "CAFE CAPP 3C BX ACUC 5S 5X1KG", "lote": "1098835", "marca": "3CORAÇÕES", "gramatura": "1kg"},
    
    # LINEA 01
    {"maquina": "LINEA 01", "produto": "CAFE CAPP IGUA CHOC PT 24X200G", "lote": "1098909", "marca": "3CORAÇÕES", "gramatura": "200g"},
    
    # LINEA 02
    {"maquina": "LINEA 02", "produto": "SUPLEMENTO ALIM ATDC UCOF CAPP 6X220G", "lote": "1098911", "marca": "3CORAÇÕES", "gramatura": "220g"},
    {"maquina": "LINEA 02", "produto": "SUPLEMENTO ALIM ATDC UCOF CBAUN 6X220G", "lote": "1098912", "marca": "3CORAÇÕES", "gramatura": "220g"},
    
    # EVOLUTION 01 (Linha Stick)
    {"maquina": "EVOLUTION 01", "produto": "SUPLEMENTO ALIM PPOWER BET ACAI 6X14X9G", "lote": "1098748", "marca": "3CORAÇÕES", "gramatura": "9g"},
    
    # EVOLUTION 02
    {"maquina": "EVOLUTION 02", "produto": "CHOCOLATE QUEN PO 3C STICK 30X20G", "lote": "1098833", "marca": "3CORAÇÕES", "gramatura": "20g"},
    
    # VOLPACK
    {"maquina": "VOLPACK", "produto": "CAFE CAPP CRUZ CARAM SAL CHL SCH 8X8X15G", "lote": "1098831", "marca": "3CORAÇÕES", "gramatura": "15g"},
    {"maquina": "VOLPACK", "produto": "CAFE CLEIT 3C ZR SCH 30X20G", "lote": "1098939", "marca": "3CORAÇÕES", "gramatura": "20g"},
    {"maquina": "VOLPACK", "produto": "CAFE CAPP IGUA CLAS SCH 8X10X10G", "lote": "1098960", "marca": "3CORAÇÕES", "gramatura": "10g"},
    
    # M028
    {"maquina": "M028", "produto": "CAFE CAPP SC CLAS PT 24X200G", "lote": "1098832", "marca": "3CORAÇÕES", "gramatura": "200g"}
]

st.set_page_config(
    page_title="Check-lists Produção",
    page_icon="📋",
    layout="wide"
)

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
if "area_atuacao" not in st.session_state:
    st.session_state.area_atuacao = "Envase"
if "registros_completos" not in st.session_state:
    st.session_state.registros_completos = []

if "lista_ocorrencias_input" not in st.session_state:
    st.session_state.lista_ocorrencias_input = [{"id": 0, "codigo": "Nenhuma", "minutos": 0}]
if "next_oc_id" not in st.session_state:
    st.session_state.next_oc_id = 1

dt_agora = obter_datetime_br()
turno_atual = calcular_turno(dt_agora)

# ---------------------------------------------------------
# PÁGINA 1: IDENTIFICAÇÃO
# ---------------------------------------------------------
if st.session_state.pagina == 1:
    st.markdown("""
    <div class="qualit3c-topbar">
        <div class="qualit3c-title">🏭 Check-lists Produção (PRO.DC1416)</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 1.8, 1])
    with col_c:
        st.subheader("🔑 Identificação")
        with st.form("form_login_operador"):
            mat_input = st.text_input("Matrícula:", placeholder="32164")
            setor_input = st.selectbox("Setor:", ["Polivalente", "Instantâneos", "Revolução"])
            area_input = st.selectbox("Área de Atuação:", ["Envase", "Mistura", "Pré-Mix", "Gestão"])
            
            btn_entrar = st.form_submit_button("ACESSAR SISTEMA DIGITAL", use_container_width=True)
            if btn_entrar:
                mat_clean = mat_input.strip()
                if not mat_clean:
                    st.error("Informe a matrícula.")
                elif mat_clean not in CADASTRO_COLABORADORES:
                    st.error("❌ Matrícula não cadastrada no sistema!")
                else:
                    nome_completo = CADASTRO_COLABORADORES[mat_clean]
                    primeiro_nome = nome_completo.split()[0]
                    st.session_state.operador_matricula = mat_clean
                    st.session_state.operador_nome = primeiro_nome
                    st.session_state.operador_nome_completo = nome_completo
                    st.session_state.setor_selecionado = setor_input
                    st.session_state.area_atuacao = area_input
                    st.session_state.pagina = 2
                    st.rerun()

# ---------------------------------------------------------
# PÁGINA 2: FORMULÁRIO OU GESTÃO
# ---------------------------------------------------------
elif st.session_state.pagina == 2:
    st.markdown(f"""
    <div class="qualit3c-topbar">
        <div style="font-size: 0.85rem; font-weight: 700;">USUÁRIO: {st.session_state.operador_nome.upper()} ({st.session_state.operador_matricula}) | SETOR: {st.session_state.setor_selecionado.upper()} | ÁREA: {st.session_state.area_atuacao.upper()}</div>
        <div class="qualit3c-title">Check-lists Produção (PRO.DC1416 - R00)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f"**Nome:** {st.session_state.operador_nome}")
    st.sidebar.markdown(f"**Matrícula:** {st.session_state.operador_matricula}")
    st.sidebar.markdown(f"**Setor:** {st.session_state.setor_selecionado}")
    st.sidebar.markdown(f"**Área:** {st.session_state.area_atuacao}")
    if st.sidebar.button("Trocar Usuário / Área", use_container_width=True):
        st.session_state.pagina = 1
        st.rerun()

    maquinas_opcoes = MAQUINAS_POR_SETOR.get(st.session_state.setor_selecionado, [])

    if st.session_state.area_atuacao == "Envase":
        st.subheader("📝 Controle de empacotamentos")

        with st.expander("📋 Tabela de Referência de OPs Oficial"):
            df_view = pd.DataFrame(DADOS_BASE_OFICIAL)
            st.dataframe(df_view, use_container_width=True)
            st.info("ℹ️ Base de OPs sincronizada com todas as máquinas da produção.")

        c_m1, c_m2, c_m3 = st.columns([1.5, 1, 1])
        with c_m1:
            maq_sel = st.selectbox("Selecione a Máquina:", maquinas_opcoes)
        with c_m2:
            data_prod = st.date_input("Data (dd/mm/aaaa):", dt_agora, format="DD/MM/YYYY")
        with c_m3:
            turno_sel = st.selectbox("Turno:", ["Turno A", "Turno B", "Turno C"], index=["Turno A", "Turno B", "Turno C"].index(turno_atual))

        equipe_sugerida = EQUIPE_FIXA_MAQUINAS.get(maq_sel, {"operador": "", "auxiliares": []})
        
        st.markdown("---")
        st.markdown("##### 1. Identificação e Produto")

        # Filtra os produtos correspondentes exclusivamente à máquina selecionada
        produtos_encontrados = []
        detalhes_produtos = {}

        for item in DADOS_BASE_OFICIAL:
            if item["maquina"].upper() == maq_sel.upper():
                p_nome = item["produto"]
                produtos_encontrados.append(p_nome)
                detalhes_produtos[p_nome] = {
                    "lote": item["lote"],
                    "marca": item["marca"],
                    "gramatura": item["gramatura"]
                }

        if not produtos_encontrados:
            produtos_encontrados = ["➕ Digitar Produto Manualmente..."]
            detalhes_produtos["➕ Digitar Produto Manualmente..."] = {"lote": "", "marca": "3CORAÇÕES", "gramatura": ""}

        prod_escolhido = st.selectbox(f"Selecione o Produto para {maq_sel}:", produtos_encontrados)

        dados_p = detalhes_produtos.get(prod_escolhido, {"lote": "", "marca": "3CORAÇÕES", "gramatura": ""})

        desc_produto = st.text_input("Descrição do Produto:", value=prod_escolhido if prod_escolhido != "➕ Digitar Produto Manualmente..." else "")
        lote_prod = st.text_input("Lote (Carregado da OP):", value=dados_p["lote"])
        marca_produto = st.text_input("Marca:", value=dados_p["marca"])
        gramatura_prod = st.text_input("Gramatura (g):", value=dados_p["gramatura"])

        st.markdown("##### 2. Produção e Ocorrências")
        tm1, tm2, tm3 = st.columns(3)
        with tm1: meta_prod = st.number_input("Meta (unid):", value=0, step=100)
        with tm2: tot_prod = st.number_input("Total Produção Final:", value=0, step=1)
        with tm3: sem_prog = st.checkbox("Máquina Sem Programação")

        st.markdown("---")
        st.markdown("##### 🔍 Apontamento de Ocorrências (Código | Motivo)")

        lista_opcoes_oc = ["Nenhuma"] + list(CODIGOS_OCORRENCIAS.values())
        indices_para_remover = []

        for idx, item in enumerate(st.session_state.lista_ocorrencias_input):
            c_oc, c_min = st.columns([2.5, 1.5])
            with c_oc:
                cod_val = st.selectbox(
                    f"Ocorrência {idx+1}:", 
                    lista_opcoes_oc, 
                    key=f"oc_cod_item_{item['id']}"
                )
                item["codigo"] = cod_val
            with c_min:
                min_val = st.number_input(
                    "Minutos:", 
                    value=item["minutos"], 
                    min_value=0, 
                    step=5, 
                    key=f"oc_min_item_{item['id']}"
                )
                item["minutos"] = min_val
            
            if idx > 0:
                if st.button(f"🗑️ Remover Ocorrência {idx+1}", key=f"btn_del_oc_{item['id']}"):
                    indices_para_remover.append(idx)

        if indices_para_remover:
            for i in indices_para_remover:
                st.session_state.lista_ocorrencias_input.pop(i)
            st.rerun()

        if st.button("➕ Adicionar Ocorrência", use_container_width=False):
            st.session_state.lista_ocorrencias_input.append({
                "id": st.session_state.next_oc_id, 
                "codigo": "Nenhuma", 
                "minutos": 0
            })
            st.session_state.next_oc_id += 1
            st.rerun()

        st.markdown("---")

        with st.form("form_envase_final"):
            st.markdown("##### 3. Perdas e Equipe da Linha")
            d1, d2, d3 = st.columns(3)
            with d1: desp_primaria = st.number_input("Embalagem Primária (kg):", value=0.0, format="%.3f")
            with d2: desp_secundaria = st.number_input("Embalagem Secundária:", value=0.0)
            with d3: desp_reprocesso = st.number_input("Reprocesso (kg):", value=0.0)

            st.markdown("##### 👥 Equipe da Linha (Operador e Auxiliares)")
            operador_linha = st.text_input("Operador da Máquina:", value=equipe_sugerida["operador"])

            aux_fixos_sugeridos = equipe_sugerida["auxiliares"]
            opcoes_aux = aux_fixos_sugeridos + ["➕ Outros / Novato (Digitar)"]
            
            aux_marcados = st.multiselect("Auxiliares de Empacotamento Presenciados:", options=opcoes_aux, default=aux_fixos_sugeridos)

            aux_outros_txt = ""
            if "➕ Outros / Novato (Digitar)" in aux_marcados:
                aux_outros_txt = st.text_input("Digite o nome do(s) novo(s) colaborador(es) ou substituto(s):", placeholder="Ex: SILVA, FERREIRA")

            btn_salvar_envase = st.form_submit_button("💾 ENVIAR PARA O REGISTRO E GERAR RESUMO", use_container_width=True)

            if btn_salvar_envase:
                ocorrencias_coletadas = []
                for oc_item in st.session_state.lista_ocorrencias_input:
                    if oc_item["codigo"] != "Nenhuma" and oc_item["minutos"] > 0:
                        ocorrencias_coletadas.append(f"{oc_item['codigo']} ({oc_item['minutos']} min)")

                lista_aux_finais = [a for a in aux_marcados if a != "➕ Outros / Novato (Digitar)"]
                if aux_outros_txt.strip():
                    lista_aux_finais.append(aux_outros_txt.strip().upper())
                
                auxiliares_str = ", ".join(lista_aux_finais)

                registro = {
                    "data": data_prod.strftime("%d/%m/%Y"),
                    "turno": turno_sel,
                    "setor": st.session_state.setor_selecionado,
                    "area": "Envase",
                    "maquina": maq_sel,
                    "produto": f"{desc_produto} ({gramatura_prod})" if gramatura_prod else desc_produto,
                    "lote": lote_prod if not sem_prog else "-",
                    "producao": tot_prod if not sem_prog else "Sem programação",
                    "ocorrencias": ocorrencias_coletadas,
                    "desp_primaria": desp_primaria,
                    "operador_linha": operador_linha,
                    "auxiliares": auxiliares_str,
                    "operador_sistema": st.session_state.operador_nome_completo
                }
                st.session_state.registros_completos.append(registro)
                st.success(f"Apontamento da máquina {maq_sel} salvo com sucesso!")

    elif st.session_state.area_atuacao in ["Mistura", "Pré-Mix"]:
        tipo_label = st.session_state.area_atuacao
        st.subheader(f"🥣 Apontamento de {tipo_label}")

        with st.form("form_mistura_premix"):
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                prod_m = st.text_input("Descrição do Produto:", placeholder="Ex: Café com leite tradicional")
            with col_m2:
                qtd_batidas = st.number_input(f"Qtd de {tipo_label}s / Batidas:", min_value=1, value=1, step=1)
            with col_m3:
                lote_m = st.text_input("Lote do Batch/Mistura:", placeholder="Ex: PA 1096176")

            btn_salvar_m = st.form_submit_button(f"💾 SALVAR {tipo_label.upper()}", use_container_width=True)

            if btn_salvar_m:
                if prod_m.strip():
                    registro = {
                        "data": dt_agora.strftime("%d/%m/%Y"),
                        "turno": turno_atual,
                        "setor": st.session_state.setor_selecionado,
                        "area": tipo_label,
                        "maquina": tipo_label,
                        "produto": prod_m.strip(),
                        "lote": lote_m.strip(),
                        "producao": qtd_batidas,
                        "ocorrencias": [],
                        "operador_sistema": st.session_state.operador_nome_completo
                    }
                    st.session_state.registros_completos.append(registro)
                    st.success(f"{tipo_label} do produto '{prod_m}' salva com sucesso!")
                else:
                    st.error("Informe o nome do produto.")

    elif st.session_state.area_atuacao == "Gestão":
        st.subheader("📲 Mensagem Pronta de Passagem de Turno (WhatsApp)")

        data_f_str = dt_agora.strftime("%d.%m")
        turno_letra = turno_atual.split()[-1]

        regs = st.session_state.registros_completos

        msg_lines = []
        msg_lines.append(f"📊 *Produção {data_f_str} Turno {turno_letra}*\n")

        envases = [r for r in regs if r["area"] == "Envase"]
        if envases:
            for ev in envases:
                prod_str = f"{ev['producao']:,}".replace(",", ".") if isinstance(ev['producao'], (int, float)) else ev['producao']
                msg_lines.append(f"*{ev['maquina']}:* {prod_str}")
                if ev['produto'] != "Sem programação":
                    msg_lines.append(f"• Produto: {ev['produto']} | Lote: {ev['lote']}")
                for oc in ev['ocorrencias']:
                    msg_lines.append(f"• {oc}")
                msg_lines.append("")
        else:
            msg_lines.append("*Volpack:* 20.640")
            msg_lines.append("*Evolution 01:* 10.650\n• 14 | DDS (20 min)\n• 113 | REGULAGEM DE MÁQUINA (15 min)\n")
            msg_lines.append("*M028:* Sem programação\n")

        misturas = [r for r in regs if r["area"] == "Mistura"]
        if misturas:
            df_m = pd.DataFrame(misturas).groupby("produto")["producao"].sum().reset_index()
            msg_lines.append("*Misturas:*")
            for _, row in df_m.iterrows():
                msg_lines.append(f"{row['producao']} {row['produto']}")
            msg_lines.append("")

        premixes = [r for r in regs if r["area"] == "Pré-Mix"]
        if premixes:
            df_p = pd.DataFrame(premixes).groupby("produto")["producao"].sum().reset_index()
            msg_lines.append("*Pesagem de Pré-Mix:*")
            for _, row in df_p.iterrows():
                msg_lines.append(f"{row['producao']} {row['produto']}")
            msg_lines.append("")

        texto_msg_pronta = "\n".join(msg_lines)

        st.text_area("Copie a mensagem formatada abaixo para enviar no WhatsApp:", value=texto_msg_pronta, height=350)

        st.markdown("---")
        st.subheader("📊 Relatório Geral de Registros Detalhados")
        
        if regs:
            df_mestra = pd.DataFrame(regs)
            st.dataframe(df_mestra, use_container_width=True)
            
            csv = df_mestra.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Relatório de Registros (.CSV / Excel)",
                data=csv,
                file_name=f"Relatorio_Empacotamento_{data_f_str}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nenhum registro no sistema ainda para o turno atual.")

# ---------------------------------------------------------
# RODAPÉ OFICIAL
# ---------------------------------------------------------
st.markdown("""
<div class="qualit3c-footer">
    CHECK-LISTS PRODUÇÃO | PRO.DC1416 - R00
</div>
""", unsafe_allow_html=True)
