import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA WEB (Tema Amplo e Responsivo)
# =============================================================================
st.set_page_config(
    page_title="GRPRISM2D — Painel de Modelagem",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para emular a identidade escura e profissional
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #f8fafc; font-family: 'Helvetica', sans-serif; }
    .stNumberInput label { color: #94a3b8 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 1. FUNÇÕES DE MODELAGEM FÍSICA (MOTOR GEOMETRADO DE PRISMAS)
# =============================================================================

def gvertical(vecx, R, xq, z1, z2, t):
    G_const = 6.672e-11
    gz = np.zeros(len(vecx))
    for i in range(len(vecx)):
        dx = vecx[i] - xq
        gz[i] = (2 * G_const * R) * (1.0 / (1.0 + (dx**2 + ((z1+z2)/2)**2)/1e6))
    return gz

def curva_gv_automatica(densidades, vecx, xq, z1, z2, t):
    curva_final = np.zeros(len(vecx), dtype=float)
    prismas_por_camada = len(xq) 
    contador = 0 
    for d in densidades:
        for i, j in enumerate(d):
            idx_camada = contador // prismas_por_camada
            if idx_camada >= len(z1):
                break
            curva_final += gvertical(vecx, j, xq[i], z1[idx_camada], z2[idx_camada], t)
            contador += 1
    return curva_final / (10**(-5))

# =============================================================================
# 2. INTERFACE CONFIGURADORA LATERAL (SIDEBAR)
# =============================================================================

st.sidebar.markdown("# 🌌 GRPRISM2D")
st.sidebar.markdown("### Parâmetros Físicos")

comp_km = st.sidebar.number_input("Comprimento útil da área (km):", min_value=0.1, value=1.5, step=0.1)
prof_km = st.sidebar.number_input("Profundidade máxima (km):", min_value=0.1, value=1.0, step=0.1)
dist_m = st.sidebar.number_input("Distância entre as estações (m):", min_value=1.0, value=100.0, step=10.0)

comprimento_total = comp_km * 1000.0
profundidade_max = prof_km * 1000.0

st.sidebar.markdown("---")
st.sidebar.markdown("### Resolução da Malha")

opcoes_malha = {
    "Malha 5x19  —  Centro Útil 5x5": 1,
    "Malha 6x16  —  Centro Útil 6x6": 2,
    "Malha 7x17  —  Centro Útil 7x7": 3,
    "Malha 8x18  —  Centro Útil 8x8": 4,
    "Malha 9x19  —  Centro Útil 9x9": 5,
    "Malha 10x20 —  Centro Útil 10x10": 6
}
selecao_malha = st.sidebar.selectbox("Configuração de Resolução:", list(opcoes_malha.keys()))
opcao_idx = opcoes_malha[selecao_malha]

# --- EQUACIONAMENTO GEOMÉTRICO ADAPTATIVO ---
mapa_linhas = {1: 5, 2: 6, 3: 7, 4: 8, 5: 9, 6: 10}
n_prismas_z = mapa_linhas[opcao_idx]

limite_esquerda = 5
colunas_brancas_centro = n_prismas_z  
limite_direita = limite_esquerda + colunas_brancas_centro
n_prismas_x = limite_direita + 5  

xq = np.array([i * dist_m for i in range(n_prismas_x)])
vecx = xq + (dist_m / 2.0)

espessura_camada = profundidade_max / n_prismas_z
z1 = np.array([i * espessura_camada for i in range(n_prismas_z)])
z2 = z1 + espessura_camada

# --- IMPORTADOR DINÂMICO DE DADOS OBSERVADOS DE CAMPO ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Importação de Arquivos")
arquivo_carregado = st.sidebar.file_uploader("Carregar arquivo de dados (.TXT)", type=["txt"])

dado_observado = None

if arquivo_carregado is not None:
    try:
        linhas_texto = arquivo_carregado.read().decode("utf-8").splitlines()
        linhas_corrigidas = [linha.replace(',', '.') for r in linhas_texto if (linha := r.strip()) and not linha.startswith('#')]
        dados_brutos = np.loadtxt(linhas_corrigidas)
        
        if dados_brutos.ndim > 1:
            dados_brutos = dados_brutos[:, -1]
            
        dist_dados = np.linspace(vecx[0], vecx[-1], len(dados_brutos))
        dado_observado = np.interp(vecx, dist_dados, dados_brutos)
        st.sidebar.success("✓ Dados de campo injetados com sucesso")
    except Exception as e:
        st.sidebar.error(f"Erro ao processar o arquivo: {e}")

# Caso nenhum arquivo tenha sido carregado, constrói a resposta do corpo retangular sintético alvo
if dado_observado is None:
    matriz_sintetica_alvo = np.zeros((n_prismas_z, n_prismas_x))
    linha_centro = n_prismas_z // 2
    coluna_centro = limite_esquerda + (colunas_brancas_centro // 2)
    matriz_sintetica_alvo[linha_centro, coluna_centro] = 100.0
    matriz_sintetica_alvo[linha_centro, coluna_centro - 1] = 100.0
    dado_observado = curva_gv_automatica(matriz_sintetica_alvo, vecx, xq, z1, z2, dist_m)

# =============================================================================
# 3. INTERFACE PRINCIPAL E MATRIX EDITOR INTERATIVO
# =============================================================================

st.title("Painel de Modelagem Prismática Gravimétrica 2D")
st.markdown(f"**Configuração Ativa:** Centro Útil de `{colunas_brancas_centro}x{colunas_brancas_centro}` blocos editáveis flanqueados por zonas de transição (padding).")

st.markdown("### 🎛️ Matrix Editor — Contrastes de Densidade ($g/cm^3$)")
st.caption("Células pretas representam as bordas travadas em 0.0. Insira os valores nas caixas de input livres no centro.")

# Mantém a matriz de dados na memória do cache de sessão da página para evitar resets ao digitar
if "matriz_residente" not in st.session_state or st.session_state.get("malha_anterior_idx") != opcao_idx:
    st.session_state.matriz_residente = np.zeros((n_prismas_z, colunas_brancas_centro))
    st.session_state.malha_anterior_idx = opcao_idx

matriz_densidades = np.zeros((n_prismas_z, n_prismas_x))

# Renderização do grid numérico usando containers dinâmicos horizontais
for r in range(n_prismas_z):
    colunas_grid_web = st.columns(n_prismas_x)
    for c in range(n_prismas_x):
        if c < limite_esquerda or c >= limite_direita:
            # Renderiza as bordas pretas estáticas (padding)
            colunas_grid_web[c].markdown(
                "<div style='background-color:#000000; color:#475569; text-align:center; "
                "border: 1px solid #1e293b; border-radius:3px; padding:2px; font-size:11px; font-weight:bold;'>0.0</div>", 
                unsafe_allow_html=True
            )
        else:
            # Renderiza os inputs numéricos centrais editáveis
            c_centro = c - limite_esquerda
            valor_celula_atual = float(st.session_state.matriz_residente[r, c_centro])
            
            novo_valor_celula = colunas_grid_web[c].number_input(
                f"R{r}C{c}", label_visibility="collapsed",
                value=valor_celula_atual, key=f"input_celula_{r}_{c}", step=10.0
            )
            st.session_state.matriz_residente[r, c_centro] = novo_valor_celula
            matriz_densidades[r, c] = novo_valor_celula

# =============================================================================
# 4. PROCESSAMENTO GRÁFICO (MATPLOTLIB)
# =============================================================================

dado_calculado = curva_gv_automatica(matriz_densidades, vecx, xq, z1, z2, dist_m)
erro_residuo = dado_observado - dado_calculado
erro_rms = np.sqrt(np.mean(erro_residuo ** 2))

# Criação das figuras com dimensões otimizadas para páginas web
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 5.5))

# Plot Superior: Anomalia Gravimétrica e Ajuste de Três Sinais
ax1.plot(vecx / 1000, dado_observado, 'ko', label='Dado Observado', markersize=4)
ax1.plot(vecx / 1000, dado_calculado, 'k-', label='Dado Calculado', linewidth=1.5)
ax1.plot(vecx / 1000, erro_residuo, 'r--', label='Erro Residual (Ponto a Ponto)', linewidth=1.0)
ax1.set_title(f"Ajuste de Curvas Gravimétricas (Erro RMS Total = {erro_rms:.3f} mGal)", fontsize=10, fontweight="bold")
ax1.set_ylabel("g_z (mGal)", fontsize=9)
ax1.grid(True, linestyle=":")
ax1.legend(loc='upper right', fontsize=8)

# Plot Inferior: Seção Geológica Cruzada
im = ax2.imshow(matriz_densidades, cmap='jet', aspect='auto', extent=[0, (n_prismas_x * dist_m) / 1000, profundidade_max / 1000, 0])
ax2.set_title("Seção do Modelo de Contrastes de Densidade", fontsize=10, fontweight="bold")
ax2.set_xlabel("Distância (km)", fontsize=9)
ax2.set_ylabel("Profundidade (km)", fontsize=9)

# Barra de Cores Adaptativa com Divisor Rígido
divider = make_axes_locatable(ax2)
cax = divider.append_axes("right", size="2%", pad=0.12)
cbar = fig.colorbar(im, cax=cax, orientation='vertical')
cbar.set_label('Contraste de Densidade (g/cm³)', fontsize=8)

# Gerenciamento da dinâmica de contrastes positivos e negativos na Colorbar
min_c, max_c = np.min(matriz_densidades), np.max(matriz_densidades)
if min_c == 0.0 and max_c == 0.0:
    im.set_clim(vmin=-10.0, vmax=100.0)
else:
    im.set_clim(vmin=min_c, vmax=max_c)

fig.subplots_adjust(left=0.06, right=0.93, top=0.92, bottom=0.12, hspace=0.45)

# Renderização do painel no Streamlit de forma nativa e síncrona
st.markdown("---")
st.markdown("### 📊 Painel de Visualização Física (Atualização Automática)")
st.pyplot(fig)

# Métricas rápidas de rodapé para acompanhamento numérico estável
col_m1, col_m2 = st.columns(2)
col_m1.metric(label="Ajuste Estatístico (Erro RMS)", value=f"{erro_rms:.4f} mGal")
col_m2.metric(label="Contraste de Densidade Máximo Registrado", value=f"{max_c:.1f} g/cm³")