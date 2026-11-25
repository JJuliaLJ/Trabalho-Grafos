"""Aparência do site: CSS e pequenos componentes em HTML.

Um só sistema, com a paleta "Frost and slate": branco frio, ardósia nos textos e um
único verde-azulado nas ações. Cantos 8/12/20, linhas de 1px e nenhuma sombra em repouso.
A fonte é a Hanken Grotesk; sem internet, entra a fonte do sistema.
"""

from html import escape

CSS = """
<style>
:root {
  --tinta:#1f3038; --suave:#56656c; --linha:rgba(31,48,56,.13); --fundo:#f7f9fa; --degrau:#ecf0f2;
  --papel:#ffffff; --marca:#0d7480; --marca-escura:#0a5a64; --marca-clara:#e2f1f2; --noite:#10262d;
  --alerta:#fff5e0; --alerta-linha:#dca84a;
  --r-sm:8px; --r-md:12px; --r-lg:20px;
  --curva:cubic-bezier(.2,.8,.2,1); --entrada:cubic-bezier(.22,1,.36,1);
  --fonte:"Hanken Grotesk","Segoe UI",system-ui,-apple-system,Roboto,Arial,sans-serif;
}
html, body, [data-testid="stAppViewContainer"], button, input, textarea, select {font-family:var(--fonte);}
#MainMenu, footer {visibility:hidden;}
[data-testid="stHeader"] {background:transparent;}
.block-container {padding:32px 40px 64px; max-width:1440px;}
*:focus-visible {outline-color:var(--marca);}

/* Barra lateral */
[data-testid="stSidebar"] {background:var(--papel); border-right:1px solid var(--linha);}
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stRadio"]),
[data-testid="stSidebar"] [data-testid="stRadio"], [data-testid="stSidebar"] [role="radiogroup"] {width:100% !important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  width:100%; min-height:44px; align-items:center; padding:8px 12px; margin:1px 0; border-radius:var(--r-sm);
  transition:background 150ms var(--curva);}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:var(--degrau);}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {background:var(--noite);}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {color:#fff; font-weight:600;}
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {display:none;}
[data-testid="stSidebar"] [data-testid="stRadio"] label p {font-size:16px;}
.marca {display:flex; align-items:center; gap:12px; margin:0 0 16px 2px;}
.marca svg {width:40px; height:40px; flex:none;}
.marca b {display:block; font-size:20px; font-weight:600; letter-spacing:-.02em; color:var(--tinta); line-height:1.2;}

/* Abertura da página inicial */
.st-key-abertura {background:var(--noite); border-radius:var(--r-lg); padding:48px 0 0 48px; overflow:hidden;}
.st-key-abertura_texto {padding:8px 0 48px;}
.abertura h1 {font-size:clamp(34px,3.3vw,50px); font-weight:600; letter-spacing:-.035em; line-height:1.06;
  color:#fff; margin:0 0 16px; padding:0; text-wrap:balance;}
.abertura p {font-size:18px; line-height:1.55; color:#c8d6da; margin:0 0 12px; max-width:44ch;}
.abertura h1, .abertura p, .st-key-abertura .stButton {animation:sobe 700ms var(--entrada) both;}
.abertura p {animation-delay:90ms;}
.st-key-abertura .stButton {animation-delay:180ms;}
.st-key-abertura button {min-height:48px; padding:0 20px; border:1px solid rgba(255,255,255,.28);
  background:transparent; color:#fff;}
.st-key-abertura button p {font-size:16px;}
.st-key-abertura button:hover {background:rgba(255,255,255,.10); border-color:rgba(255,255,255,.5); color:#fff;}
.st-key-abertura button[kind="primary"] {background:#fff; border-color:#fff; color:var(--tinta);}
.st-key-abertura button[kind="primary"]:hover {background:#dcebed; color:var(--tinta);}
.tela {background:var(--fundo); border-radius:var(--r-md) 0 0 0; padding:20px 20px 8px; height:388px; overflow:hidden;
  animation:sobe 900ms var(--entrada) 120ms both;}
.tela .barra {display:flex; justify-content:space-between; gap:16px; font-size:14px; color:var(--suave);
  border-bottom:1px solid var(--linha); padding-bottom:12px; margin-bottom:16px; white-space:nowrap;}
.tela .barra b {color:var(--tinta); font-weight:600;}
.tela svg {overflow:visible;}
.animada .no {opacity:0; animation:aparece 420ms var(--entrada) forwards; animation-delay:calc(450ms + var(--nivel)*190ms);}
.animada .liga {stroke-dasharray:1; stroke-dashoffset:1; animation:traca 420ms var(--curva) forwards;
  animation-delay:calc(330ms + var(--nivel)*190ms);}
@keyframes sobe {from {opacity:0; transform:translateY(14px);} to {opacity:1; transform:none;}}
@keyframes aparece {from {opacity:0; transform:translateY(-8px);} to {opacity:1; transform:none;}}
@keyframes traca {to {stroke-dashoffset:0;}}

/* Cartões da página inicial: cartão, painel com a tela de verdade e o atalho no cartão inteiro */
[class*="st-key-cartao_"] {position:relative; background:var(--papel); border:1px solid var(--linha);
  border-radius:var(--r-lg); padding:28px 28px 0; overflow:hidden;
  transition:transform 150ms var(--curva), box-shadow 150ms var(--curva), border-color 150ms;}
[class*="st-key-cartao_"]:hover {transform:translateY(-2px); border-color:rgba(31,48,56,.24);
  box-shadow:0 10px 28px rgba(16,38,45,.08);}
.resumo h3 {font-size:22px; font-weight:600; letter-spacing:-.02em; color:var(--tinta); margin:0 0 8px; padding:0;}
.resumo p {font-size:16px; line-height:1.5; color:var(--tinta); margin:0; min-height:48px; max-width:46ch;}
[class*="st-key-cartao_"] [data-testid="stElementContainer"], [class*="st-key-cartao_"] .stButton {position:static !important;}
[class*="st-key-cartao_"] .stButton button {position:static; border:0; background:none; padding:0; min-height:32px;
  color:var(--marca); font-weight:600;}
[class*="st-key-cartao_"] .stButton button:hover {background:none; color:var(--marca-escura); transform:none;}
[class*="st-key-cartao_"] .stButton button::after {content:""; position:absolute; inset:0; z-index:2; border-radius:var(--r-lg);}
.previa {height:196px; overflow:hidden; background:var(--degrau); border-radius:var(--r-md) var(--r-md) 0 0; padding:20px 20px 0;}
.previa .folha {background:var(--papel); border:1px solid var(--linha); border-bottom:0; border-radius:var(--r-md) var(--r-md) 0 0;
  padding:14px 16px 0; height:100%; overflow:hidden;}
.previa .folha svg {max-height:150px;}
.previa .linha {display:flex; gap:14px; align-items:baseline; padding:9px 0; border-bottom:1px solid var(--linha); font-size:15px; color:var(--tinta);}
.previa .linha b {font-weight:600; color:var(--marca); font-variant-numeric:tabular-nums; min-width:46px;}
.previa .linha span {margin-left:auto; color:var(--suave); font-size:14px;}
.previa.mapa-previa {padding:0;} .previa.mapa-previa svg {max-width:none !important; width:100%; margin-top:-34%;}
.barra-h {display:grid; grid-template-columns:104px 1fr 76px; gap:12px; align-items:center; padding:9px 0; font-size:15px; color:var(--tinta);}
.barra-h i {display:block; height:22px; border-radius:0 4px 4px 0; background:var(--marca);}
.barra-h i.neutra {background:#b3c1c6;}

/* Cabeçalho das páginas */
.topo {display:flex; align-items:flex-end; justify-content:space-between; gap:24px; flex-wrap:wrap; padding-bottom:8px;}
.topo h1 {font-size:38px; font-weight:600; letter-spacing:-.03em; color:var(--tinta); margin:0; padding:0; line-height:1.1;}
.topo p {margin:8px 0 0; font-size:17px; line-height:1.5; color:var(--suave); max-width:62ch;}
.topo .estrutura {display:inline-flex; align-items:center; gap:8px; white-space:nowrap; font-size:15px; font-weight:600;
  color:var(--tinta); border:1px solid var(--linha); background:var(--papel); padding:8px 14px; border-radius:var(--r-sm);}
.topo .estrutura svg {width:18px; height:18px;}

/* Painéis e campos */
[class*="st-key-painel_"] {background:var(--papel); border:1px solid var(--linha) !important; border-radius:var(--r-lg) !important; padding:28px !important;}
[data-testid="stHeading"] h3 {font-size:22px; font-weight:600; letter-spacing:-.02em; padding-top:0;}
[data-testid="stWidgetLabel"] p {font-size:15px; font-weight:500; color:var(--tinta);}
[data-baseweb="input"], [data-baseweb="select"] > div, [data-testid="stNumberInputContainer"] {min-height:46px;}
[data-baseweb="input"] input, [data-baseweb="select"] {font-size:16px;}
.stTabs [data-baseweb="tab-list"] {gap:4px;}
.stTabs [data-baseweb="tab"] {padding:12px 16px;}
.stTabs [data-baseweb="tab"] p {font-size:16px; font-weight:600;}
.stButton > button, [data-testid="stPopover"] button {border-radius:var(--r-sm); min-height:46px; font-weight:600;
  transition:transform 150ms var(--curva), background 150ms, border-color 150ms;}
.stButton > button p {font-size:16px;}
.stButton > button:hover:not(:disabled) {transform:translateY(-1px);}
.stButton > button:active:not(:disabled) {transform:translateY(1px) scale(.985); transition-duration:90ms;}
[data-testid="stExpander"] details {border-radius:var(--r-lg); background:var(--papel); border-color:var(--linha);}
[data-testid="stCaptionContainer"] p {font-size:15px; color:var(--suave);}

/* Lista de consultas */
.consulta {display:flex; align-items:center; gap:16px; min-height:48px;}
.consulta .hora {font-weight:600; font-size:18px; color:var(--marca); min-width:58px; font-variant-numeric:tabular-nums;}
.consulta .nome {font-weight:600; font-size:16px; color:var(--tinta); line-height:1.3;}
.consulta .info {font-size:14px; color:var(--suave);}

/* Resultado das unidades */
.unidade {display:flex; align-items:center; gap:14px; border-top:1px solid var(--linha); padding:13px 0; font-size:16px;}
.unidade .pos {width:30px; height:30px; border-radius:var(--r-sm); display:grid; place-items:center; flex:none;
  background:var(--degrau); color:var(--suave); font-weight:600;}
.unidade.melhor .pos {background:var(--marca); color:#fff;}
.unidade .nome {font-weight:600; color:var(--tinta);}
.unidade .dist {margin-left:auto; font-weight:600; color:var(--tinta); font-variant-numeric:tabular-nums;}

/* Árvore */
.arvore-quadro {background:var(--papel); border:1px solid var(--linha); border-radius:var(--r-lg); padding:16px; overflow-x:auto;}
.arvore-vazia {background:var(--papel); border:1px dashed #aebbc0; border-radius:var(--r-lg);
  padding:40px; text-align:center; color:var(--suave); font-size:16px;}
.legenda {display:flex; gap:8px 20px; flex-wrap:wrap; margin:4px 0 8px;}
.chip {display:inline-flex; align-items:center; gap:8px; font-size:15px; color:var(--tinta);}
.chip i {display:inline-block; width:16px; height:16px; border-radius:4px;}
.rotulo-fase {font-weight:600; font-size:20px; letter-spacing:-.02em; color:var(--tinta); margin:16px 0 8px;}
.operacao {border-radius:var(--r-md); padding:16px 20px; margin:4px 0 8px; border:1px solid var(--linha); background:var(--papel);}
.operacao.ajuste {background:var(--alerta); border-color:var(--alerta-linha);}
.operacao b {font-size:18px; font-weight:600; letter-spacing:-.01em; color:var(--tinta);}
.operacao .sub {font-size:15px; color:var(--suave); margin-top:4px;}
.passos {padding:0 0 0 24px; margin:0 0 8px; columns:2; column-gap:48px;}
.passos.curto {columns:1;}
.passos li {padding:4px 0 4px 4px; font-size:16px; color:var(--tinta); break-inside:avoid;}
.passos li::marker {color:var(--suave); font-weight:600;}
.passos li.ajuste {font-weight:600; color:#7d4a00;}
.aviso-arvore {background:var(--marca-clara); color:var(--tinta); border-radius:var(--r-md);
  padding:14px 18px; font-size:16px; margin:8px 0;}
.mapa svg {border-radius:var(--r-lg); border:1px solid var(--linha);}

@media (max-width:900px) {
  .passos {columns:1;} .block-container {padding:16px 16px 48px;}
  .st-key-abertura {padding:28px 0 0 24px;} .st-key-abertura_texto {padding:0 24px 24px 0;} .tela {height:260px;}
  .topo h1 {font-size:30px;}
}
@media (prefers-reduced-motion:reduce) {
  *, *::before, *::after {animation:none !important; transition:none !important;}
  .animada .no {opacity:1;} .animada .liga {stroke-dashoffset:0;}
}
</style>
"""

# Símbolo de árvore: um nó com dois filhos, o mesmo desenho na marca e nas páginas.
_GALHOS = '<path d="M12 8v3M12 11H6v4M12 11h6v4" fill="none" stroke="{cor}" stroke-width="1.8"/>'
_NOS = '<circle cx="12" cy="5.4" r="2.9" fill="{raiz}"/><circle cx="6" cy="18" r="2.9" fill="{cor}"/><circle cx="18" cy="18" r="2.9" fill="{cor}"/>'


def _simbolo(cor, raiz):
    return _GALHOS.format(cor=cor) + _NOS.format(cor=cor, raiz=raiz)


def topo(titulo, texto, estrutura=""):
    selo = ""
    if estrutura:
        selo = (
            '<div class="estrutura"><svg viewBox="0 0 24 24" aria-hidden="true">'
            f'{_simbolo("#1f3038", "#0d7480")}</svg>{escape(estrutura)}</div>'
        )
    return f'<div class="topo"><div><h1>{escape(titulo)}</h1><p>{escape(texto)}</p></div>{selo}</div>'


def abertura(titulo, texto):
    return f'<div class="abertura"><h1>{escape(titulo)}</h1><p>{escape(texto)}</p></div>'


def tela(titulo, detalhe, desenho):
    """Moldura da árvore na abertura, cortada pela borda."""
    return (
        f'<div class="tela"><div class="barra"><b>{escape(titulo)}</b><span>{escape(detalhe)}</span></div>'
        f"{desenho}</div>"
    )


def resumo(titulo, texto):
    return f'<div class="resumo"><h3>{escape(titulo)}</h3><p>{escape(texto)}</p></div>'


def previa_desenho(svg):
    return f'<div class="previa"><div class="folha">{svg}</div></div>'


def previa_mapa(svg):
    return f'<div class="previa mapa-previa">{svg}</div>'


def previa_lista(itens):
    """itens: lista de (hora, nome, dia)."""
    linhas = "".join(
        f'<div class="linha"><b>{escape(h)}</b>{escape(n)}<span>{escape(d)}</span></div>' for h, n, d in itens
    )
    return f'<div class="previa"><div class="folha">{linhas}</div></div>'


def previa_barras(itens):
    """itens: lista de (nome, valor, é neutra). As barras são proporcionais ao maior valor."""
    maior = max(v for _, v, _ in itens)
    linhas = "".join(
        f'<div class="barra-h">{escape(n)}<i class="{"neutra" if neutra else ""}" '
        f'style="width:{100 * v / maior:.1f}%"></i><span>{v} níveis</span></div>'
        for n, v, neutra in itens
    )
    return f'<div class="previa"><div class="folha">{linhas}</div></div>'


def consulta(hora, nome, info):
    return (
        f'<div class="consulta"><div class="hora">{escape(hora)}</div>'
        f'<div><div class="nome">{escape(nome)}</div><div class="info">{escape(info)}</div></div></div>'
    )


def unidade(posicao, nome, distancia, melhor):
    classe = "unidade melhor" if melhor else "unidade"
    km = f"{distancia:.1f}".replace(".", ",")
    return (
        f'<div class="{classe}"><div class="pos">{posicao}</div>'
        f'<div class="nome">{escape(nome)}</div><div class="dist">{km} km</div></div>'
    )


def operacao(titulo, detalhe, ajuste):
    classe = "operacao ajuste" if ajuste else "operacao"
    return f'<div class="{classe}"><b>{escape(titulo)}</b><div class="sub">{escape(detalhe)}</div></div>'


def passos(itens, destacados=()):
    """Lista numerada de passos; os destacados são os de rebalanceamento."""
    classe = "passos" if len(itens) > 4 else "passos curto"
    linhas = "".join(
        f'<li class="{"ajuste" if i in destacados else ""}">{escape(t)}</li>' for i, t in enumerate(itens)
    )
    return f'<ol class="{classe}">{linhas}</ol>'


def marca():
    return (
        '<div class="marca"><svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="#10262d"/>'
        f'<g transform="translate(6.4 6) scale(1.13)">{_simbolo("#ffffff", "#5fc3cd")}</g></svg><b>Agenda UBS</b></div>'
    )
