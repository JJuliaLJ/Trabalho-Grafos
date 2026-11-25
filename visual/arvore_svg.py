"""Desenho das árvores em SVG.

Cada nó é uma caixa. Nos nós da 2-3-4, cada chave ocupa uma célula da caixa,
então dá para ver quantas chaves cabem no nó.
"""

from html import escape

ALTURA_NO = 40
PASSO_NIVEL = 82
ESPACO = 12
LARGURA_CARACTERE = 7.2
LARGURA_MINIMA = 46
PADDING = 18
LARGURA_OCULTO = 16
MARGEM = 22
FONTE = "'Hanken Grotesk', 'Segoe UI', system-ui, -apple-system, Roboto, Arial, sans-serif"

# fundo, texto, borda
ESTILOS = {
    "vermelho": ("#c8102e", "#ffffff", "#8e0b20"),
    "preto": ("#1a272c", "#ffffff", "#0b1215"),
    "azul": ("#e2f1f2", "#0b3d44", "#0d7480"),
    "kd_x": ("#e2f1f2", "#0b3d44", "#0d7480"),
    "kd_y": ("#f3ecdf", "#5a3d0c", "#b98a3a"),
    "neutro": ("#f5f7f6", "#33413f", "#c4cfcc"),
}
DESTAQUES = {
    "novo": "#15803d",
    "alterado": "#d97706",
    "removido": "#dc2626",
    "caminho": "#2563eb",
    "achado": "#15803d",
}
NOMES_ESTILO = {
    "vermelho": "Nó vermelho",
    "preto": "Nó preto",
    "azul": "Nó com 1 a 3 chaves",
    "kd_x": "Corta em x",
    "kd_y": "Corta em y",
}
NOMES_DESTAQUE = {
    "novo": "Criado",
    "alterado": "Ajustado (cor, posição ou conteúdo)",
    "removido": "Removido",
    "caminho": "Visitado na busca",
    "achado": "Encontrado",
}
SELOS = {"novo": "NOVO", "removido": "SAIU", "achado": "ACHOU"}


def _largura_texto(rotulo):
    return max(len(linha) for linha in rotulo.split("\n")) * LARGURA_CARACTERE


def _largura(no):
    if no.get("oculto"):
        return LARGURA_OCULTO
    if no.get("celulas"):
        return sum(_largura_celula(c) for c in no["celulas"])
    return max(LARGURA_MINIMA, _largura_texto(no["rotulo"]) + PADDING)


def _largura_celula(texto):
    return max(LARGURA_MINIMA - 4, _largura_texto(texto) + 12)


def _posicionar(no, nivel, cursor):
    """Folhas ocupam sua largura em sequência; o pai fica centralizado sobre os filhos."""
    no["_y"] = nivel * PASSO_NIVEL
    no["_w"] = _largura(no)
    if not no["filhos"]:
        no["_x"] = cursor + no["_w"] / 2
        return cursor + no["_w"] + ESPACO
    inicio = cursor
    for filho in no["filhos"]:
        cursor = _posicionar(filho, nivel + 1, cursor)
    no["_x"] = (no["filhos"][0]["_x"] + no["filhos"][-1]["_x"]) / 2
    # Se a caixa do pai passa da faixa dos filhos, desloca ou alarga a faixa para não encostar no vizinho.
    sobra = inicio - (no["_x"] - no["_w"] / 2)
    if sobra > 0:
        _deslocar(no, sobra)
        cursor += sobra
    return max(cursor, no["_x"] + no["_w"] / 2 + ESPACO)


def _deslocar(no, dx):
    no["_x"] += dx
    for filho in no["filhos"]:
        _deslocar(filho, dx)


def _todos(no, saida):
    saida.append(no)
    for filho in no["filhos"]:
        _todos(filho, saida)
    return saida


def _ligacoes(no, saida):
    for filho in no["filhos"]:
        if not filho.get("oculto"):
            x1, y1 = no["_x"], no["_y"] + ALTURA_NO
            x2, y2 = filho["_x"], filho["_y"]
            m = (y2 - y1) / 2
            estado = filho.get("estado")
            cor = DESTAQUES[estado] if estado in DESTAQUES else "#9fafb5"
            largura = 2.6 if estado in DESTAQUES else 1.6
            nivel = filho["_y"] / PASSO_NIVEL
            saida.append(
                f'<path class="liga" style="--nivel:{nivel:.0f}" pathLength="1" d="M{x1:.1f},{y1:.1f} C{x1:.1f},{y1 + m:.1f} {x2:.1f},{y2 - m:.1f} '
                f'{x2:.1f},{y2:.1f}" fill="none" stroke="{cor}" stroke-width="{largura}"/>'
            )
        _ligacoes(filho, saida)
    return saida


def _texto(x, y, conteudo, tamanho, cor, peso, opacidade="1"):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONTE}" font-size="{tamanho}" '
        f'font-weight="{peso}" fill="{cor}" text-anchor="middle" dominant-baseline="central" '
        f'opacity="{opacidade}">{escape(conteudo)}</text>'
    )


def _rotulo(cx, cy, rotulo, cor, opacidade):
    linhas = rotulo.split("\n")
    if len(linhas) == 1:
        return _texto(cx, cy, linhas[0], 13, cor, 600, opacidade)
    return (
        _texto(cx, cy - 8, linhas[0], 12, cor, 600, opacidade)
        + _texto(cx, cy + 8, linhas[1], 11.5, cor, 500, opacidade)
    )


def _contador(x, y, quantidade):
    """Bolinha com o número de valores guardados na mesma chave."""
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#ffffff" stroke="#33413f" stroke-width="1.4"/>'
        + _texto(x, y, str(quantidade), 10.5, "#1b2423", 700)
    )


def _no(no):
    x, y, w = no["_x"] - no["_w"] / 2, no["_y"], no["_w"]
    fundo, texto, borda = ESTILOS.get(no["estilo"], ESTILOS["neutro"])
    estado = no.get("estado")
    opacidade = "0.5" if estado == "removido" else "1"
    partes = []
    if estado in DESTAQUES:
        cor = DESTAQUES[estado]
        traco = ' stroke-dasharray="6 4"' if estado == "removido" else ""
        partes.append(
            f'<rect x="{x - 5:.1f}" y="{y - 5:.1f}" width="{w + 10:.1f}" height="{ALTURA_NO + 10}" '
            f'rx="11" fill="{cor}" fill-opacity="0.14" stroke="{cor}" stroke-width="2.4"{traco}/>'
        )
    partes.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{ALTURA_NO}" rx="7" '
        f'fill="{fundo}" stroke="{borda}" stroke-width="1.4" opacity="{opacidade}"/>'
    )
    cy = y + ALTURA_NO / 2
    if no.get("celulas"):
        esquerda = x
        for i, celula in enumerate(no["celulas"]):
            largura = _largura_celula(celula)
            if i:
                partes.append(
                    f'<line x1="{esquerda:.1f}" y1="{y:.1f}" x2="{esquerda:.1f}" '
                    f'y2="{y + ALTURA_NO:.1f}" stroke="{borda}" stroke-width="1.2" opacity="{opacidade}"/>'
                )
            partes.append(_rotulo(esquerda + largura / 2, cy, celula, texto, opacidade))
            if no["quantidades"][i] > 1:
                partes.append(_contador(esquerda + largura - 6, y + ALTURA_NO, no["quantidades"][i]))
            esquerda += largura
    else:
        partes.append(_rotulo(x + w / 2, cy, no["rotulo"], texto, opacidade))
        if no.get("quantidade", 1) > 1:
            partes.append(_contador(x + w - 4, y + ALTURA_NO, no["quantidade"]))
    if estado in SELOS:
        cor, selo = DESTAQUES[estado], SELOS[estado]
        largura = len(selo) * 6.6 + 10
        partes.append(
            f'<rect x="{x + w / 2 - largura / 2:.1f}" y="{y - 14:.1f}" width="{largura:.1f}" '
            f'height="16" rx="4" fill="{cor}"/>'
            + _texto(x + w / 2, y - 6, selo, 9.5, "#ffffff", 700)
        )
    return f'<g class="no" style="--nivel:{no["_y"] / PASSO_NIVEL:.0f}">' + "".join(partes) + "</g>"


def arvore_svg(raiz, ajustar=True, quadro=True, animar=False):
    """Devolve o HTML (div com SVG) da árvore. Uma linha só, para o markdown do Streamlit.

    ajustar=True encaixa a árvore na largura da tela; False mantém o tamanho real, com rolagem.
    quadro=False devolve só o SVG. animar=True faz os níveis aparecerem de cima para baixo.
    """
    if raiz is None:
        return '<div class="arvore-vazia">A árvore está vazia.</div>'
    _posicionar(raiz, 0, 0)
    nos = _todos(raiz, [])
    minx = min(n["_x"] - n["_w"] / 2 for n in nos) - MARGEM
    maxx = max(n["_x"] + n["_w"] / 2 for n in nos) + MARGEM
    maxy = max(n["_y"] for n in nos) + ALTURA_NO + MARGEM
    largura, altura = maxx - minx, maxy + MARGEM
    corpo = "".join(_ligacoes(raiz, [])) + "".join(_no(n) for n in nos if not n.get("oculto"))
    minimo = 0 if ajustar else largura
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="{"animada" if animar else ""}" viewBox="{minx:.1f} {-MARGEM:.1f} {largura:.1f} {altura:.1f}" '
        f'style="width:100%;min-width:{minimo:.0f}px;max-width:{largura:.0f}px;'
        'height:auto;display:block;margin:0 auto">'
        + corpo + "</svg>"
    )
    return f'<div class="arvore-quadro">{svg}</div>' if quadro else svg


def _chip(fundo, borda, texto, tracejado=False):
    estilo_borda = "dashed" if tracejado else "solid"
    return (
        '<span class="chip">'
        f'<i style="background:{fundo};border:2px {estilo_borda} {borda}"></i>{escape(texto)}</span>'
    )


def legenda(estilos=(), destaques=()):
    partes = [_chip(ESTILOS[e][0], ESTILOS[e][2], NOMES_ESTILO[e]) for e in estilos]
    for chave in destaques:
        partes.append(_chip("#ffffff", DESTAQUES[chave], NOMES_DESTAQUE[chave], tracejado=chave == "removido"))
    return '<div class="legenda">' + "".join(partes) + "</div>"
