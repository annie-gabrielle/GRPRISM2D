import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA WEB
# =============================================================================
st.set_page_config(
    page_title="GRPRISM2D — Painel de Modelagem / Modeling Panel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para manter o visual profissional
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    h1 { color: #f8fafc; font-family: 'Helvetica', sans-serif; margin-bottom: 0; }
    .stNumberInput label { color: #94a3b8 !important; font-weight: bold; font-size: 10px; }
    div[data-testid="column"] { padding: 0px 1px !important; }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 0. DICIONÁRIO DE TRADUÇÃO (SISTEMA BILÍNGUE)
# =============================================================================
if "idioma" not in st.session_state:
    st.session_state.idioma = "PT"

# Seletor de idioma no topo da barra lateral
idioma_selecionado = st.sidebar.radio("🌐 Language / Idioma:", ["Português", "English"], horizontal=True)
st.session_state.idioma = "PT" if idioma_selecionado == "Português" else "EN"

# Mapa de textos para alternância dinâmica
t = {
    "PT": {
        "params": "### Parâmetros Físicos",
        "comp": "Comprimento útil da área (km):",
        "prof": "Profundidade máxima (km):",
        "dist": "Distância entre estações (m):",
        "resolucao": "### Resolução da Malha",
        "config_res": "Configuração de Resolução:",
        "campo": "### Dados de Campo",
        "carregar": "Carregar arquivo de dados (.TXT)",
        "sucesso": "✓ Dados carregados com sucesso",
        "titulo": "Painel de Modelagem Gravimétrica 2D",
        "config_ativa": "**Configuração Ativa:** Centro Útil de `{}` blocos editáveis flanqueados por zonas de transição (padding).",
        "editor_titulo": "🎛️ Matrix Editor — Entrada de Contrastes ($g/cm^3$)",
        "editor_caption": "As bordas pretas são zonas de padding (0.0). Edite os valores nas colunas centrais brancas.",
        "graficos_titulo": "📊 Painel de Visualização Física (Atualização Automática)",
        "eixo_y_gz": "g_z (mGal)",
        "eixo_x_dist": "Distância (km)",
        "eixo_y_prof": "Profundidade (km)",
        "obs": "Dado Observado",
        "calc": "Dado Calculado",
        "res": "Erro Residual",
        "cbar_label": "Contraste de Densidade (g/cm³)",
        "erro_rms": "Erro RMS Total",
        "erro_rms_curva": "Ajuste de Curvas (Erro RMS = {:.4f} mGal)",
        "secao_titulo": "Seção do Modelo de Contrastes de Densidade",
        "met_rms": "Erro RMS",
        "met_max": "Contraste Máx",
    },
    "EN": {
        "params": "### Physical Parameters",
        "comp": "Useful area length (km):",
        "prof": "Maximum depth (km):",
        "dist": "Distance between stations (m):",
        "resolucao": "### Mesh Resolution",
        "config_res": "Resolution Configuration:",
        "campo": "### Field Data",
        "carregar": "Load data file (.TXT)",
        "sucesso": "✓ Data loaded successfully",
        "titulo": "2D Gravimetric Modeling Panel",
        "config_ativa": "**Active Configuration:** Useful Center of `{}` editable blocks flanked by transition zones (padding).",
        "editor_titulo": "🎛️ Matrix Editor — Density Contrast Input ($g/cm^3$)",
        "editor_caption": "Black borders are padding zones (0.0). Edit values in the white central columns.",
        "graficos_titulo": "📊 Physical Visualization Panel (Automatic Update)",
        "eixo_y_gz": "g_z (mGal)",
        "eixo_x_dist": "Distance (km)",
        "eixo_y_prof": "Depth (km)",
        "obs": "Observed Data",
        "calc": "Calculated Data",
        "res": "Residual Error",
        "cbar_label": "Density Contrast (g/cm³)",
        "erro_rms": "Total RMS Error",
        "erro_rms_curva": "Curve Fitting (RMS Error = {:.4f} mGal)",
        "secao_titulo": "Density Contrast Model Section",
        "met_rms": "RMS Error",
        "met_max": "Max Contrast",
    }
}[st.session_state.idioma]

# =============================================================================
# 1. MOTOR DE MODELAGEM FÍSICA
# =============================================================================

def gvertical(vecx, R, xq, z1, z2, t_val):
    G_const = 6.672e-11
    gz = np.zeros(len(vecx))
    for i in range(len(vecx)):
        dx = vecx[i] - xq
        gz[i] = (2 * G_const * R) * (1.0 / (1.0 + (dx**2 + ((z1+z2)/2)**2)/1e6))
    return gz

def curva_gv_automatica(densidades, vecx, xq, z1, z2, t_val):
    curva_final = np.zeros(len(vecx), dtype=float)
    prismas_por_camada = len(xq) 
    contador = 0 
    for d in densidades:
        for i, j in enumerate(d):
            idx_camada = contador // prismas_por_camada
            if idx_camada >= len(z1):
                break
            curva_final += gvertical(vecx, j, xq[i], z1[idx_camada], z2[idx_camada], t_val)
            contador += 1
    return curva_final / (10**(-5))

# =============================================================================
# 2. CONTINUAÇÃO DA BARRA LATERAL (SETUP TRADUZIDO)
# =============================================================================

st.sidebar.markdown(t["params"])
comp_km = st.sidebar.number_input(t["comp"], min_value=0.1, value=1.5, step=0.1)
prof_km = st.sidebar.number_input(t["prof"], min_value=0.1, value=1.0, step=0.1)
dist_m = st.sidebar.number_input(t["dist"], min_value=1.0, value=100.0, step=10.0)

comprimento_total = comp_km * 1000.0
profundidade_max = prof_km * 1000.0

st.sidebar.markdown("---")
st.sidebar.markdown(t["resolucao"])

opcoes_malha = {
    "Malha 5x19  —  Centro Útil 5x5" if st.session_state.idioma == "PT" else "Mesh 5x19  —  Useful Center 5x5": 1,
    "Malha 6x16  —  Centro Útil 6x6" if st.session_state.idioma == "PT" else "Mesh 6x16  —  Useful Center 6x6": 2,
    "Malha 7x17  —  Centro Útil 7x7" if st.session_state.idioma == "PT" else "Mesh 7x17  —  Useful Center 7x7": 3,
    "Malha 8x18  —  Centro Útil 8x8" if st.session_state.idioma == "PT" else "Mesh 8x18  —  Useful Center 8x8": 4,
    "Malha 9x19  —  Centro Útil 9x9" if st.session_state.idioma == "PT" else "Mesh 9x19  —  Useful Center 9x9": 5,
    "Malha 10x20 —  Centro Útil 10x10" if st.session_state.idioma == "PT" else "Mesh 10x20 —  Useful Center 10x10": 6
}
selecao_malha = st.sidebar.selectbox(t["config_res"], list(opcoes_malha.keys()))
opcao_idx = opcoes_malha[selecao_malha]

# Geometria adaptativa
mapa_linhas = {1: 5, 2: 6, 3: 7, 4: 8, 5: 9, 6: 10}
n_prismas_z = mapa_linhas[opcao_idx]
limite_esquerda, colunas_brancas_centro = 5, n_prismas_z  
limite_direita = limite_esquerda + colunas_brancas_centro
n_prismas_x = limite_direita + 5  

xq = np.array([i * dist_m for i in range(n_prismas_x)])
vecx = xq + (dist_m / 2.0)
espessura_camada = profundidade_max / n_prismas_z
z1 = np.array([i * espessura_camada for i in range(n_prismas_z)])
z2 = z1 + espessura_camada

# Importação de arquivos
st.sidebar.markdown("---")
st.sidebar.markdown(t["campo"])
arquivo_carregado = st.sidebar.file_uploader(t["carregar"], type=["txt"])

dado_observado = None
if arquivo_carregado is not None:
    try:
        linhas_texto = arquivo_carregado.read().decode("utf-8").splitlines()
        linhas_corrigidas = [linha.replace(',', '.') for r in linhas_texto if (linha := r.strip()) and not linha.startswith('#')]
        dados_brutos = np.loadtxt(linhas_corrigidas)
        if dados_brutos.ndim > 1: dados_brutos = dados_brutos[:, -1]
        dist_dados = np.linspace(vecx[0], vecx[-1], len(dados_brutos))
        dado_observado = np.interp(vecx, dist_dados, dados_brutos)
        st.sidebar.success(t["sucesso"])
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

if dado_observado is None:
    matriz_alvo = np.zeros((n_prismas_z, n_prismas_x))
    l_c, c_c = n_prismas_z // 2, limite_esquerda + (colunas_brancas_centro // 2)
    matriz_alvo[l_c, c_c] = 100.0; matriz_alvo[l_c, c_c-1] = 100.0
    dado_observado = curva_gv_automatica(matriz_alvo, vecx, xq, z1, z2, dist_m)

# Sincronização do Estado da Malha
if "matriz_residente" not in st.session_state or st.session_state.get("malha_anterior_idx") != opcao_idx:
    st.session_state.matriz_residente = np.zeros((n_prismas_z, colunas_brancas_centro))
    st.session_state.malha_anterior_idx = opcao_idx

# =============================================================================
# 4. PAINEL SUPERIOR: VISUALIZAÇÃO GRÁFICA (TRADUZIDO)
# =============================================================================

st.title(t["titulo"])
st.markdown(t["config_ativa"].format(f"{colunas_brancas_centro}x{colunas_brancas_centro}"))
st.markdown("---")

matriz_para_calculo = np.zeros((n_prismas_z, n_prismas_x))
for r in range(n_prismas_z):
    for c_centro in range(colunas_brancas_centro):
        matriz_para_calculo[r, limite_esquerda + c_centro] = st.session_state.matriz_residente[r, c_centro]

dado_calculado = curva_gv_automatica(matriz_para_calculo, vecx, xq, z1, z2, dist_m)
erro_residuo = dado_observado - dado_calculado
erro_rms = np.sqrt(np.mean(erro_residuo ** 2))

# Configuração e estilo dos Plots no Matplotlib
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 5.2))
plt.style.use('dark_background')
fig.patch.set_facecolor('#0e1117')
ax1.set_facecolor('#0e1117')
ax2.set_facecolor('#0e1117')

# Sinal Superior
ax1.plot(vecx / 1000, dado_observado, 'wo', label=t["obs"], markersize=4, alpha=0.8)
ax1.plot(vecx / 1000, dado_calculado, '#38bdf8', label=t["calc"], linewidth=2)
ax1.plot(vecx / 1000, erro_residuo, '#ef4444', label=t["res"], linewidth=1, linestyle='--')
ax1.set_title(t["erro_rms_curva"].format(erro_rms), color='white', fontsize=10)
ax1.set_ylabel(t["eixo_y_gz"], fontsize=8)
ax1.grid(True, alpha=0.2)
ax1.legend(fontsize=7)

# Seção Geológica Inferior
im = ax2.imshow(matriz_para_calculo, cmap='jet', aspect='auto', extent=[0, (n_prismas_x * dist_m)/1000, profundidade_max/1000, 0])
ax2.set_title(t["secao_titulo"], color='white', fontsize=10)
ax2.set_xlabel(t["eixo_x_dist"], fontsize=8)
ax2.set_ylabel(t["eixo_y_prof"], fontsize=8)

divider = make_axes_locatable(ax2)
cax = divider.append_axes("right", size="1.5%", pad=0.1)
cbar = fig.colorbar(im, cax=cax)
cbar.set_label(t["cbar_label"], fontsize=8)
cbar.ax.tick_params(labelsize=7)

min_c, max_c = np.min(matriz_para_calculo), np.max(matriz_para_calculo)
im.set_clim(vmin=min_c if min_c < 0 else 0, vmax=max(100.0, max_c))

fig.subplots_adjust(left=0.06, right=0.94, top=0.92, bottom=0.12, hspace=0.4)
st.pyplot(fig)

# =============================================================================
# 5. PAINEL INFERIOR: MATRIX EDITOR (TRADUZIDO)
# =============================================================================

st.markdown(f"### {t['editor_titulo']}")
st.caption(t["editor_caption"])

for r in range(n_prismas_z):
    colunas_ui = st.columns(n_prismas_x)
    for c in range(n_prismas_x):
        if c < limite_esquerda or c >= limite_direita:
            colunas_ui[c].markdown(
                "<div style='background-color:#1e293b; color:#475569; text-align:center; "
                "border-radius:2px; padding:3px; font-size:10px; margin-top:5px;'>0.0</div>", 
                unsafe_allow_html=True
            )
        else:
            c_idx = c - limite_esquerda
            val_ini = float(st.session_state.matriz_residente[r, c_idx])
            
            novo_val = colunas_ui[c].number_input(
                f"R{r}C{c}", label_visibility="collapsed",
                value=val_ini, key=f"in_{r}_{c}", step=10.0
            )
            st.session_state.matriz_residente[r, c_idx] = novo_val

# Métricas de rodapé estáveis
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric(t["met_rms"], f"{erro_rms:.4f} mGal")
c2.metric(t["met_max"], f"{max_c:.1f} g/cm³")
c3.metric("Depth" if st.session_state.idioma == "EN" else "Profundidade", f"{prof_km} km")