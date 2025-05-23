import streamlit as st
import pandas as pd
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

# ======================
# CONFIGURAÇÕES
# ======================

SHAREPOINT_SITE_URL = "https://SEUDOMINIO.sharepoint.com/sites/NOMEDOSITE"
SHAREPOINT_LIST_NAME = "ProcessoRepasse"

# Substitua pelas credenciais do seu app no Azure
client_id = "SEU_CLIENT_ID"
client_secret = "SEU_CLIENT_SECRET"
tenant_id = "SEU_TENANT_ID"

ctx = ClientContext(SHAREPOINT_SITE_URL).with_credentials(
    ClientCredential(client_id, client_secret)
)

# ======================
# FUNÇÕES
# ======================

def carregar_dados():
    lista = ctx.web.lists.get_by_title(SHAREPOINT_LIST_NAME)
    items = lista.items.get().execute_query()
    data = []
    for item in items:
        data.append(item.properties)
    return pd.DataFrame(data)

def atualizar_status(item_id, campo, valor):
    lista = ctx.web.lists.get_by_title(SHAREPOINT_LIST_NAME)
    item = lista.get_item_by_id(item_id)
    item.set_property(campo, valor).update().execute_query()

# ======================
# STREAMLIT APP
# ======================

st.set_page_config(page_title="Processo de Repasse", layout="wide")
st.title("🏠 Painel de Repasse Imobiliário")

st.sidebar.title("🔐 Login Simples")
perfil = st.sidebar.selectbox("Selecione seu perfil:", ["Corretor", "CCA", "Crédito"])

# Carrega dados da lista
df = carregar_dados()

# Exibe os dados principais
st.subheader("📋 Processos em Andamento")
st.dataframe(df[["ID", "NomeCliente", "StatusAtual"]])

# Cards por cliente
for _, row in df.iterrows():
    with st.expander(f"Cliente: {row['NomeCliente']} | Status: {row['StatusAtual']}"):
        st.write("ID:", row["ID"])
        st.write("Observações:", row.get("Observacoes", ""))
        
        if perfil == "Corretor" and row["StatusAtual"] == "Início":
            if st.button(f"Enviar Documentos - ID {row['ID']}"):
                atualizar_status(row["ID"], "DocumentosOk", True)
                st.success("Documentos enviados.")
        
        if perfil == "CCA" and row["StatusAtual"] == "Em Andamento - Repasse":
            if st.button(f"Confirmar Assinatura Caixa - ID {row['ID']}"):
                atualizar_status(row["ID"], "AssinaturaCaixa", True)
                st.success("Assinatura confirmada.")

        if perfil == "Crédito":
            if row["StatusAtual"] == "Assinatura Caixa":
                if st.button(f"Confirmar Habite-se - ID {row['ID']}"):
                    atualizar_status(row["ID"], "HabiteSeOk", True)
                    st.success("Habite-se confirmado.")
            if row["StatusAtual"] == "Garantia Agehab":
                if st.button(f"Finalizar - ID {row['ID']}"):
                    atualizar_status(row["ID"], "DocsAgehabEnviados", True)
                    atualizar_status(row["ID"], "EtapaConcluida", True)
                    atualizar_status(row["ID"], "StatusAtual", "Finalizado")
                    st.success("Processo finalizado.")
