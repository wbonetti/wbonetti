"""
Configuração pessoal do perfil. Edite este arquivo — os scripts leem tudo daqui.
"""
import os

# Seu usuário do GitHub. No GitHub Actions ele é preenchido sozinho
# (variável GITHUB_USER, vinda do dono do repositório).
USERNAME = os.environ.get("GITHUB_USER", "wbonetti")

# Nome que aparece no "prompt" do terminal: wbonetti@github ~ $
PROMPT_USER = "wbonetti"

# ---- Card estilo neofetch --------------------------------------------------
# Cada item é (rótulo, valor). O valor pode ser uma string ou uma lista de
# strings (cada string vira uma linha). Mantenha linhas com ~40 caracteres.
INFO = [
    ("Função",    "Sr .NET Dev · Full-Stack · IA"),
    ("Agora",     "Total Softwares · NF Avulsa SEF/SC"),
    ("Antes",     "DocPro · 7 anos de VB6 e VB.NET"),
    ("Código",    "desde 2013 · Florianópolis, SC"),
    ("Stack",     ["C# · .NET 8 · ASP.NET · EF · SQL Server",
                   "Python · YOLOv9 · PyQGIS",
                   "React · TypeScript · Supabase · n8n"]),
    ("Destaques", ["▸ Emissor fiscal: ~20 mil notas/dia",
                   "▸ YOLOv9 no QGIS: até -90% herbicida",
                   "▸ LigaPro: campeonatos em tempo real",
                   "▸ 10 entregas no portfólio"]),
    ("Web",       "portfolio.wbonetti.com.br"),
    ("Insta",     "@willbonetti"),
]

# ---- Retrato ASCII ---------------------------------------------------------
ASCII_COLS = 100            # largura do retrato em caracteres
ASCII_RAMP = " .`:-=+*cs#%@"  # do mais esparso ao mais denso
# True: partes claras da foto viram caracteres densos (fica certo no fundo escuro)
# False: mapeamento original do artigo (escuro = denso)
ASCII_INVERT = True
