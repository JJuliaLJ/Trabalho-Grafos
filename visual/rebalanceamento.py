"""Compara a árvore antes e depois de uma operação e marca o que mudou.

Estados de cada nó:
  novo      -> não existia antes
  removido  -> deixou de existir (aparece só no 'antes')
  alterado  -> continua existindo, mas mudou de cor, de conteúdo ou de pai
               (é assim que rotações, recolorações, divisões e fusões aparecem)
"""

# Palavras que os eventos das árvores usam quando há rebalanceamento.
TIPOS_DE_AJUSTE = {
    "Rotação": "rotação",
    "Recoloração": "recoloração",
    "dividido": "divisão de nó",
    "Empréstimo": "empréstimo do irmão",
    "Fusão": "fusão de nós",
    "reconstruída": "reconstrução pela mediana",
}


def _indexar(raiz):
    nos, pais = {}, {}

    def visitar(no, pai):
        if no is None or no.get("oculto"):
            return
        nos[no["id"]] = no
        pais[no["id"]] = pai
        for filho in no["filhos"]:
            visitar(filho, no["id"])

    visitar(raiz, None)
    return nos, pais


def marcar(antes, depois):
    """Preenche o campo 'estado' dos nós das duas árvores."""
    nos_antes, pais_antes = _indexar(antes)
    nos_depois, pais_depois = _indexar(depois)

    for no in list(nos_antes.values()) + list(nos_depois.values()):
        no["estado"] = None

    for id_, no in nos_depois.items():
        if id_ not in nos_antes:
            no["estado"] = "novo"
            continue
        velho = nos_antes[id_]
        if (
            velho["estilo"] != no["estilo"]
            or velho["rotulo"] != no["rotulo"]
            or velho.get("quantidade") != no.get("quantidade")
            or velho.get("quantidades") != no.get("quantidades")
            or pais_antes.get(id_) != pais_depois.get(id_)
        ):
            velho["estado"] = "alterado"
            no["estado"] = "alterado"

    for id_, no in nos_antes.items():
        if id_ not in nos_depois:
            no["estado"] = "removido"


def marcar_caminho(retrato, visitados, achou):
    """Destaca no desenho os nós visitados por uma busca."""
    nos, _ = _indexar(retrato)
    for no in nos.values():
        no["estado"] = None
    for no in visitados:
        nos[id(no)]["estado"] = "caminho"
    if achou:
        nos[id(visitados[-1])]["estado"] = "achado"


def resumo_ajustes(eventos):
    """Conta os tipos de ajuste de balanceamento que aparecem nos eventos."""
    contagem = {}
    for evento in eventos:
        for palavra, nome in TIPOS_DE_AJUSTE.items():
            if palavra in evento:
                contagem[nome] = contagem.get(nome, 0) + 1
    return contagem


def descrever_ajustes(contagem):
    if not contagem:
        return ""
    partes = []
    for nome, n in contagem.items():
        if n == 1:
            partes.append(f"1 {nome}")
        else:
            plural = {"rotação": "rotações", "recoloração": "recolorações",
                      "divisão de nó": "divisões de nó", "empréstimo do irmão": "empréstimos do irmão",
                      "fusão de nós": "fusões de nós"}.get(nome, nome)
            partes.append(f"{n} {plural}")
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + " e " + partes[-1]
