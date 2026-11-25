"""Mapa 2D estilizado da cidade fictícia, gerado como SVG.

A cidade ocupa 0..20 km nos dois eixos. Os quarteirões, prédios e parques são
sorteados com semente fixa, então o mapa é sempre o mesmo.
"""

import random
from html import escape

TAMANHO = 20.0
MARGEM = 0.6
RUAS = [0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0]
TELHADOS = ["#e4dccb", "#d8cfbb", "#cbbfa6", "#e9e2d2", "#d9d3c2"]
COR_CHAO = "#e6e0d1"
COR_RUA = "#fbf8f1"
COR_BORDA_RUA = "#cfc6b3"
COR_SOMBRA = "#8e8470"
COR_PARQUE = "#cfe3b0"
COR_ARVORE = "#86b56a"
COR_ARVORE_BORDA = "#5f8f4c"


def _y(y):
    """Converte y (cresce para cima) para o sistema do SVG (cresce para baixo)."""
    return TAMANHO - y


def _retangulo(x, y, w, h, fill, extra=""):
    return f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{fill}" {extra}/>'


def _predio(rnd, x, y, w, h):
    bw = w * rnd.uniform(0.55, 0.85)
    bh = h * rnd.uniform(0.55, 0.85)
    bx = x + (w - bw) / 2 + rnd.uniform(-0.05, 0.05)
    by = y + (h - bh) / 2 + rnd.uniform(-0.05, 0.05)
    telhado = rnd.choice(TELHADOS)
    partes = [
        _retangulo(bx + 0.09, _y(by + bh) + 0.09, bw, bh, COR_SOMBRA, 'fill-opacity="0.45"'),
        _retangulo(bx, _y(by + bh), bw, bh, telhado, 'stroke="#b5ab95" stroke-width="0.04"'),
        _retangulo(bx + 0.14, _y(by + bh) + 0.14, bw - 0.28, bh - 0.28, "#f1ece0",
                   'fill-opacity="0.55"'),
    ]
    return "".join(partes)


def _parque(rnd, x0, y0, x1, y1):
    partes = [_retangulo(x0, _y(y1), x1 - x0, y1 - y0, COR_PARQUE,
                         'stroke="#b5d18f" stroke-width="0.05"')]
    for _ in range(rnd.randint(3, 6)):
        cx = rnd.uniform(x0 + 0.3, x1 - 0.3)
        cy = rnd.uniform(y0 + 0.3, y1 - 0.3)
        r = rnd.uniform(0.14, 0.22)
        partes.append(
            f'<circle cx="{cx:.3f}" cy="{_y(cy):.3f}" r="{r:.3f}" fill="{COR_ARVORE}" '
            f'stroke="{COR_ARVORE_BORDA}" stroke-width="0.03"/>'
        )
    return "".join(partes)


def _quarteiroes(rnd):
    partes = []
    for i in range(len(RUAS) - 1):
        for j in range(len(RUAS) - 1):
            x0, x1 = RUAS[i] + 0.35, RUAS[i + 1] - 0.35
            y0, y1 = RUAS[j] + 0.35, RUAS[j + 1] - 0.35
            if rnd.random() < 0.12:
                partes.append(_parque(rnd, x0, y0, x1, y1))
                continue
            lw, lh = (x1 - x0) / 2, (y1 - y0) / 2
            for a in range(2):
                for b in range(2):
                    if rnd.random() < 0.15:
                        continue
                    partes.append(_predio(rnd, x0 + a * lw, y0 + b * lh, lw, lh))
    return "".join(partes)


def _ruas():
    partes = []
    for r in RUAS:
        partes.append(_retangulo(r - 0.42, -MARGEM, 0.84, TAMANHO + 2 * MARGEM, COR_BORDA_RUA))
        partes.append(_retangulo(_x_inicio(), _y(r) - 0.42, TAMANHO + 2 * MARGEM, 0.84, COR_BORDA_RUA))
    for r in RUAS:
        partes.append(_retangulo(r - 0.34, -MARGEM, 0.68, TAMANHO + 2 * MARGEM, COR_RUA))
        partes.append(_retangulo(_x_inicio(), _y(r) - 0.34, TAMANHO + 2 * MARGEM, 0.68, COR_RUA))
    for r in RUAS:
        partes.append(
            f'<line x1="{r:.3f}" y1="{-MARGEM:.3f}" x2="{r:.3f}" y2="{TAMANHO + MARGEM:.3f}" '
            'stroke="#e0d3a8" stroke-width="0.05" stroke-dasharray="0.45 0.45"/>'
        )
        partes.append(
            f'<line x1="{-MARGEM:.3f}" y1="{_y(r):.3f}" x2="{TAMANHO + MARGEM:.3f}" y2="{_y(r):.3f}" '
            'stroke="#e0d3a8" stroke-width="0.05" stroke-dasharray="0.45 0.45"/>'
        )
    return "".join(partes)


def _x_inicio():
    return -MARGEM


def _largura_etiqueta(texto):
    return len(texto) * 0.22 + 0.5


def _etiqueta(x, y, texto):
    largura = _largura_etiqueta(texto)
    return (
        f'<rect x="{x - largura / 2:.3f}" y="{y - 0.24:.3f}" width="{largura:.3f}" height="0.48" '
        'rx="0.24" fill="#ffffff" fill-opacity="0.92" stroke="#cbd5e1" stroke-width="0.03"/>'
        f'<text x="{x:.3f}" y="{y:.3f}" font-family="Arial, sans-serif" font-size="0.38" '
        'font-weight="700" fill="#0f172a" text-anchor="middle" dominant-baseline="middle">'
        f"{escape(texto)}</text>"
    )


def _ubs(x, y, nome, distancia=None):
    """As unidades destacadas mostram o nome; nas outras, ele aparece ao passar o mouse."""
    cx, cy = x, _y(y)
    destaque = distancia is not None
    s = 0.42 if destaque else 0.34
    partes = [f"<g><title>{escape(nome)} ({x:g}, {y:g})</title>"]
    if destaque:
        partes.append(
            f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="0.78" fill="#dcfce7" fill-opacity="0.8" '
            'stroke="#16a34a" stroke-width="0.09"/>'
        )
    partes.append(
        f'<rect x="{cx - s:.3f}" y="{cy - s:.3f}" width="{2 * s:.3f}" height="{2 * s:.3f}" '
        'rx="0.16" fill="#2563eb" stroke="#ffffff" stroke-width="0.08"/>'
    )
    partes.append(_retangulo(cx - 0.07, cy - 0.27, 0.14, 0.54, "#ffffff"))
    partes.append(_retangulo(cx - 0.27, cy - 0.07, 0.54, 0.14, "#ffffff"))
    partes.append("</g>")
    return "".join(partes)


def _nomes_das_unidades(itens, ocupados):
    """Escreve o nome das unidades destacadas sem um ficar por cima do outro.

    itens: (texto, x, y no SVG). ocupados: retângulos (x0, y0, x1, y1) já usados.
    """
    partes = []
    for texto, x, y in itens:
        meia = _largura_etiqueta(texto) / 2
        # Mantém a etiqueta dentro do mapa.
        x = min(max(x, meia - MARGEM), TAMANHO + MARGEM - meia)
        for dy in (-1.05, 1.1, -1.65, 1.7, -2.25, 2.3):
            caixa = (x - meia, y + dy - 0.28, x + meia, y + dy + 0.28)
            livre = all(caixa[2] <= o[0] or caixa[0] >= o[2] or caixa[3] <= o[1] or caixa[1] >= o[3]
                        for o in ocupados)
            if livre and -MARGEM <= caixa[1] and caixa[3] <= TAMANHO + MARGEM:
                break
        ocupados.append(caixa)
        partes.append(_etiqueta(x, y + dy, texto))
    return "".join(partes)


def _paciente(x, y, destaque):
    cx, cy = x, _y(y)
    if destaque:
        return (
            f'<ellipse cx="{cx:.3f}" cy="{cy + 0.3:.3f}" rx="0.28" ry="0.1" fill="#000000" fill-opacity="0.22"/>'
            f'<circle cx="{cx:.3f}" cy="{cy - 0.2:.3f}" r="0.34" fill="#dc2626" '
            'stroke="#ffffff" stroke-width="0.08"/>'
            f'<circle cx="{cx:.3f}" cy="{cy - 0.2:.3f}" r="0.12" fill="#ffffff"/>'
            + _etiqueta(cx, cy + 0.85, "Paciente")
        )
    return (
        f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="0.13" fill="#475569" fill-opacity="0.75" '
        'stroke="#ffffff" stroke-width="0.04"/>'
    )


def _rota(origem, destino):
    ax, ay = origem
    bx, by = destino
    return (
        f'<line x1="{ax:.3f}" y1="{_y(ay):.3f}" x2="{bx:.3f}" y2="{_y(by):.3f}" '
        'stroke="#16a34a" stroke-width="0.16" stroke-linecap="round" '
        'stroke-dasharray="0.4 0.3"/>'
    )


def cidade_svg(unidades, paciente=None, rotas=(), pacientes=()):
    """Gera o SVG do mapa.

    unidades: lista de (nome, (x, y)) das UBS.
    paciente: (x, y) do paciente selecionado, ou None.
    rotas: lista de (distância, nome, (x, y)) das unidades destacadas.
    pacientes: lista de (x, y) de todos os pacientes, para os pontos de fundo.
    """
    rnd = random.Random(3)
    distancias = {nome: distancia for distancia, nome, _ in rotas}

    corpo = [
        _retangulo(-MARGEM, -MARGEM, TAMANHO + 2 * MARGEM, TAMANHO + 2 * MARGEM, COR_CHAO),
        _quarteiroes(rnd),
        _ruas(),
    ]
    for x, y in pacientes:
        if paciente is None or (x, y) != tuple(paciente):
            corpo.append(_paciente(x, y, destaque=False))
    for _, _, ponto in rotas:
        if paciente is not None:
            corpo.append(_rota(paciente, ponto))
    # As destacadas vão por último, para o nome não ficar atrás de outra unidade.
    for nome, (x, y) in sorted(unidades, key=lambda u: u[0] in distancias):
        corpo.append(_ubs(x, y, nome, distancias.get(nome)))
    if paciente is not None:
        corpo.append(_paciente(paciente[0], paciente[1], destaque=True))

    ocupados = [(x - 0.8, _y(y) - 0.8, x + 0.8, _y(y) + 0.8) for _, _, (x, y) in rotas]
    if paciente is not None:
        px, py = paciente[0], _y(paciente[1])
        ocupados += [(px - 0.5, py - 0.7, px + 0.5, py + 0.4), (px - 1.2, py + 0.55, px + 1.2, py + 1.15)]
    corpo.append(_nomes_das_unidades(
        [(f"{nome}, {distancia:.1f} km".replace(".", ","), x, _y(y)) for distancia, nome, (x, y) in rotas],
        ocupados,
    ))

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.6 -0.6 21.2 21.2" '
        'width="100%" style="display:block;max-width:max(420px, calc(100vh - 220px))">'
        + "".join(corpo)
        + "</svg>"
    )


def legenda_html():
    item = (
        '<span style="display:inline-flex;align-items:center;gap:7px">{}{}</span>'
    )
    quadrado = '<span style="width:14px;height:14px;border-radius:4px;background:#2563eb;display:inline-block"></span>'
    vermelho = '<span style="width:14px;height:14px;border-radius:50%;background:#dc2626;display:inline-block"></span>'
    cinza = '<span style="width:10px;height:10px;border-radius:50%;background:#475569;display:inline-block"></span>'
    verde = '<span style="width:24px;height:0;border-top:3px dashed #16a34a;display:inline-block"></span>'
    return (
        '<div style="display:flex;gap:20px;flex-wrap:wrap;font-size:13px;color:#334155;margin-top:10px">'
        + item.format(quadrado, "Unidade de saúde (passe o mouse para ver o nome)")
        + item.format(vermelho, "Paciente selecionado")
        + item.format(cinza, "Outros pacientes")
        + item.format(verde, "Distância em linha reta")
        + "</div>"
    )
