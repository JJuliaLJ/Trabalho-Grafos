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


def _indexar(raiz, por_conteudo=False):
    """Indexa os nós do retrato.

    por_conteudo=True usa o campo 'chave' quando existe (na k-D, a unidade), em vez da caixa:
    numa reconstrução ou remoção as unidades mudam de caixa, mas não saem da árvore.
    """
    nos, pais = {}, {}

    def ident(no):
        return no.get("chave", no["id"]) if por_conteudo else no["id"]

    def visitar(no, pai):
        if no is None or no.get("oculto"):
            return
        nos[ident(no)] = no
        pais[ident(no)] = pai
        for filho in no["filhos"]:
            visitar(filho, ident(no))

    visitar(raiz, None)
    return nos, pais


def _marcar_por_chaves(nos_antes, nos_depois):
    """2-3-4: compara chaves, não caixas.

    Numa fusão ou divisão as chaves trocam de nó, e as caixas antigas deixam de existir.
    Comparar caixas marcaria como removidas chaves que continuam na árvore. Aqui:
      - a chave que saiu de fato fica vermelha, e a que entrou fica verde (estado por célula);
      - um nó fica laranja só se o seu conjunto de chaves mudou.
    """
    def conteudo(no):
        return tuple(zip(no["celulas"], no["quantidades"]))

    def chaves(nos):
        return {c for no in nos.values() for c in no["celulas"]}

    def conjuntos(nos):
        return {conteudo(no) for no in nos.values()}

    chaves_antes, chaves_depois = chaves(nos_antes), chaves(nos_depois)
    for nos, outras_chaves, outros_nos, marca in ((nos_antes, chaves_depois, conjuntos(nos_depois), "removido"),
                                                  (nos_depois, chaves_antes, conjuntos(nos_antes), "novo")):
        for no in nos.values():
            no["celulas_estado"] = [None if c in outras_chaves else marca for c in no["celulas"]]
            if all(no["celulas_estado"]):
                no["estado"] = marca
            elif conteudo(no) not in outros_nos:
                no["estado"] = "alterado"
            else:
                no["estado"] = None


def marcar(antes, depois):
    """Preenche o campo 'estado' dos nós das duas árvores."""
    nos_antes, pais_antes = _indexar(antes, por_conteudo=True)
    nos_depois, pais_depois = _indexar(depois, por_conteudo=True)
    if any(no.get("celulas") for no in list(nos_antes.values()) + list(nos_depois.values())):
        _marcar_por_chaves(nos_antes, nos_depois)
        return

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
