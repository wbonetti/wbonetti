# Como publicar este perfil

Baseado no tutorial de Avi Vashishta ("How I Built an Animated GitHub Profile README"),
adaptado para português. Tudo é SVG animado gerado por Python — sem token, sem
serviço de terceiros, sem JavaScript.

## 1. Crie o repositório especial

O repositório precisa ter **exatamente o nome do seu usuário** (no seu caso, `wbonetti/wbonetti`).
O `README.md` dele aparece no topo do seu perfil.

```bash
gh repo create wbonetti --public --clone
cd wbonetti
# copie para cá todo o conteúdo desta pasta (inclusive a pasta oculta .github)
```

## 2. Personalize

| O quê | Onde |
|---|---|
| Nome do prompt (`wbonetti@github`), cargo, stack, destaques, contato | `scripts/config.py` |
| Links de contato | final do `README.md` |

Depois de editar o `config.py`, regenere o card:

```bash
python scripts/make_info_card.py
```

## 3. Publique

```bash
git add . && git commit -m "perfil animado" && git push
```

O push dispara o workflow, que baixa suas contribuições reais e substitui o
heatmap de demonstração. Para rodar manualmente: aba **Actions** →
**Atualizar arte do perfil** → **Run workflow**. Depois disso ele roda sozinho
todo dia por volta das 06h17 (horário de Brasília).

> Se o workflow falhar com erro de permissão no push: **Settings → Actions →
> General → Workflow permissions → Read and write permissions**.

## Trocar a foto

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements-portrait.txt
python scripts/prep_photo.py minha-foto.jpg   # remove fundo + contraste
python scripts/make_ascii_svg.py              # gera portrait-ascii.svg
```

Ajustes em `scripts/config.py`: `ASCII_COLS` (resolução) e `ASCII_INVERT`
(`True` = rosto claro em caracteres densos, ideal no fundo escuro).

## Arquivos

```
README.md                      layout do perfil (estilo terminal)
portrait-ascii.svg             retrato ASCII que se "digita"
info-card.svg                  card estilo neofetch
contrib-heatmap.svg            calendário de contribuições (atualizado todo dia)
data/contributions.json        dados brutos + estatísticas
scripts/                       geradores (Python)
.github/workflows/             automação diária
```

## Dicas do GitHub Markdown

- `style="..."` inline é removido; para espaço vertical, só `<br>`.
- `<h1>`/`<h2>` desenham uma linha embaixo; use `<h3>` para títulos sem linha.
- Sem JavaScript: toda animação precisa estar dentro do próprio SVG.
