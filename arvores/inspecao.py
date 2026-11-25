"""Ajuda a mostrar a implementação interna: nós numerados e ponteiros entre eles."""

from collections import deque


def no_oculto():
    """Reserva o lugar de um filho ausente, para manter esquerda e direita no desenho."""
    return {"id": None, "rotulo": "", "estilo": "neutro", "filhos": [], "estado": None, "oculto": True}


def numerar(raiz, filhos):
    """Numera os nós por nível (N1, N2, ...).

    filhos(no) devolve a lista de filhos reais de um nó.
    Devolve (lista_de_nos_na_ordem, {id(no): 'N1', ...}).
    """
    if raiz is None:
        return [], {}
    ordem, ids, fila = [], {}, deque([raiz])
    while fila:
        no = fila.popleft()
        ids[id(no)] = f"N{len(ordem) + 1}"
        ordem.append(no)
        fila.extend(filhos(no))
    return ordem, ids


def esquema_texto(raiz, filhos, descricao):
    """Árvore em texto, com indentação, identificador e descrição de cada nó."""
    if raiz is None:
        return "(árvore vazia)"
    _, ids = numerar(raiz, filhos)
    linhas = []

    def visitar(no, prefixo_linha, prefixo_filhos):
        linhas.append(f"{prefixo_linha}{ids[id(no)]}  {descricao(no)}")
        lista = filhos(no)
        for i, filho in enumerate(lista):
            ultimo = i == len(lista) - 1
            visitar(
                filho,
                prefixo_filhos + ("└── " if ultimo else "├── "),
                prefixo_filhos + ("    " if ultimo else "│   "),
            )

    visitar(raiz, "", "")
    return "\n".join(linhas)
