"""Árvore k-D (k = 2) implementada com nós ligados nos dois sentidos (filhos e pai).

Cada nível divide o plano por uma coordenada: o eixo alterna entre x e y.
O vizinho mais próximo usa poda: um ramo só é visitado se ainda puder
conter um ponto mais perto que o melhor já encontrado.

Pontos repetidos (método adotado no projeto):
  Se o ponto já existe, o novo registro vai para a subárvore DIREITA
  (critério "maior ou igual"), e a busca segue o mesmo critério. Não há fusão:
  os dois registros continuam na árvore. A remoção recebe também os dados do
  registro, para tirar o certo entre os repetidos.

A inserção não balanceia sozinha (como a k-D clássica).
construir_balanceada() reconstrói a árvore pela mediana de cada eixo.
"""

import math

from .inspecao import esquema_texto, no_oculto, numerar


class NoKD:
    __slots__ = ("ponto", "dados", "eixo", "esq", "dir", "pai")

    def __init__(self, ponto, dados, eixo, pai=None):
        self.ponto = ponto
        self.dados = dados
        self.eixo = eixo
        self.esq = None
        self.dir = None
        self.pai = pai


def _normalizar(ponto):
    return (float(ponto[0]), float(ponto[1]))


def _trocar(par, eixo, valor):
    return (valor, par[1]) if eixo == 0 else (par[0], valor)


def _dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


class ArvoreKD:
    def __init__(self):
        self.raiz = None
        self._quantidade = 0
        self.eventos = []

    def __len__(self):
        return self._quantidade

    def _registrar(self, mensagem):
        self.eventos.append(mensagem)

    def limpar_eventos(self):
        self.eventos = []

    def todos(self):
        saida = []

        def visitar(no):
            if no is None:
                return
            saida.append(no)
            visitar(no.esq)
            visitar(no.dir)

        visitar(self.raiz)
        return saida

    def altura(self):
        def h(no):
            return 0 if no is None else 1 + max(h(no.esq), h(no.dir))
        return h(self.raiz)

    # ------------------------------------------------------------------
    # Inserção e busca
    # ------------------------------------------------------------------
    def inserir(self, ponto, dados=None):
        ponto = _normalizar(ponto)
        repetido = self.buscar(ponto) is not None

        if self.raiz is None:
            self.raiz = NoKD(ponto, dados, 0)
        else:
            no = self.raiz
            while True:
                if ponto[no.eixo] < no.ponto[no.eixo]:
                    if no.esq is None:
                        no.esq = NoKD(ponto, dados, 1 - no.eixo, no)
                        break
                    no = no.esq
                else:
                    if no.dir is None:
                        no.dir = NoKD(ponto, dados, 1 - no.eixo, no)
                        break
                    no = no.dir

        self._quantidade += 1
        nome = dados if dados else str(ponto)
        if repetido:
            self._registrar(f"{nome} está no mesmo ponto de outro registro: foi para a direita")
        else:
            self._registrar(f"{nome} inserido em {ponto}")

    def _localizar(self, ponto, dados=None):
        no = self.raiz
        while no is not None:
            if no.ponto == ponto and (dados is None or no.dados == dados):
                return no
            no = no.esq if ponto[no.eixo] < no.ponto[no.eixo] else no.dir
        return None

    def buscar(self, ponto):
        """Devolve o nó com exatamente esse ponto, ou None."""
        return self._localizar(_normalizar(ponto))

    def passos_busca(self, ponto, dados=None):
        """Caminho da busca: (nós visitados, explicação de cada passo, achou?)."""
        ponto = _normalizar(ponto)
        visitados, passos = [], []
        no = self.raiz
        while no is not None:
            visitados.append(no)
            if no.ponto == ponto and (dados is None or no.dados == dados):
                passos.append(f"{no.dados or no.ponto} encontrado")
                return visitados, passos, True
            eixo = "x" if no.eixo == 0 else "y"
            a, b = ponto[no.eixo], no.ponto[no.eixo]
            lado, sinal = ("esquerda", "<") if a < b else ("direita", "≥")
            passos.append(
                f"{no.dados or no.ponto} corta em {eixo}: {a:g} {sinal} {b:g}, segue para a {lado}"
            )
            no = no.esq if a < b else no.dir
        passos.append("Chegou ao fim: o ponto não está na árvore")
        return visitados, passos, False

    # ------------------------------------------------------------------
    # Consultas espaciais
    # ------------------------------------------------------------------
    def mais_proximo(self, alvo):
        """Devolve (nó, distância) do ponto mais próximo do alvo."""
        alvo = _normalizar(alvo)
        melhor = [None, math.inf]

        def visitar(no):
            if no is None:
                return
            d2 = _dist2(no.ponto, alvo)
            if d2 < melhor[1]:
                melhor[0], melhor[1] = no, d2
            diff = alvo[no.eixo] - no.ponto[no.eixo]
            perto, longe = (no.esq, no.dir) if diff < 0 else (no.dir, no.esq)
            visitar(perto)
            if diff * diff < melhor[1]:
                visitar(longe)

        visitar(self.raiz)
        if melhor[0] is None:
            return None, None
        return melhor[0], math.sqrt(melhor[1])

    def k_mais_proximos(self, alvo, k):
        """Lista de (distância, nó) com os k pontos mais próximos, do mais perto ao mais longe.

        Mantém uma lista ordenada com no máximo k candidatos (k é pequeno no projeto).
        """
        alvo = _normalizar(alvo)
        melhores = []  # pares (distância², nó), sempre em ordem crescente

        def visitar(no):
            if no is None:
                return
            d2 = _dist2(no.ponto, alvo)
            if len(melhores) < k or d2 < melhores[-1][0]:
                posicao = 0
                while posicao < len(melhores) and melhores[posicao][0] <= d2:
                    posicao += 1
                melhores.insert(posicao, (d2, no))
                del melhores[k:]
            diff = alvo[no.eixo] - no.ponto[no.eixo]
            perto, longe = (no.esq, no.dir) if diff < 0 else (no.dir, no.esq)
            visitar(perto)
            pior = melhores[-1][0] if len(melhores) == k else math.inf
            if diff * diff < pior:
                visitar(longe)

        visitar(self.raiz)
        return [(math.sqrt(d2), no) for d2, no in melhores]

    def dentro_do_raio(self, alvo, raio):
        """Lista de (distância, nó) de todos os pontos a até 'raio' do alvo."""
        alvo = _normalizar(alvo)
        r2 = raio * raio
        achados = []

        def visitar(no):
            if no is None:
                return
            d2 = _dist2(no.ponto, alvo)
            if d2 <= r2:
                achados.append((math.sqrt(d2), no))
            diff = alvo[no.eixo] - no.ponto[no.eixo]
            if diff < 0:
                visitar(no.esq)
                if diff * diff <= r2:
                    visitar(no.dir)
            else:
                visitar(no.dir)
                if diff * diff <= r2:
                    visitar(no.esq)

        visitar(self.raiz)
        return sorted(achados, key=lambda par: par[0])

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover(self, ponto, dados=None):
        """Remove um registro. Com 'dados', escolhe o certo entre pontos repetidos."""
        no = self._localizar(_normalizar(ponto), dados)
        if no is None:
            return False
        nome = no.dados or no.ponto
        self._remover_no(no)
        self._quantidade -= 1
        self._registrar(f"{nome} removido")
        return True

    def _minimo_no(self, no, eixo):
        """Nó com menor coordenada no eixo dentro da subárvore de 'no'."""
        melhor = no
        # Se o nó corta no mesmo eixo, o menor só pode estar à esquerda.
        filhos = (no.esq,) if no.eixo == eixo else (no.esq, no.dir)
        for filho in filhos:
            if filho is not None:
                candidato = self._minimo_no(filho, eixo)
                if candidato.ponto[eixo] < melhor.ponto[eixo]:
                    melhor = candidato
        return melhor

    def _remover_no(self, no):
        """Troca o conteúdo pelo menor do lado direito e remove o nó que ficou sobrando.

        Sem lado direito, usa o menor da esquerda, e o resto da esquerda passa
        para a direita (todos são maiores ou iguais ao novo valor do nó).
        """
        if no.dir is not None:
            self._copiar_e_remover(no, self._minimo_no(no.dir, no.eixo))
        elif no.esq is not None:
            self._copiar_e_remover(no, self._minimo_no(no.esq, no.eixo))
            no.dir, no.esq = no.esq, None
        elif no.pai is None:
            self.raiz = None
        elif no.pai.esq is no:
            no.pai.esq = None
        else:
            no.pai.dir = None

    def _copiar_e_remover(self, no, substituto):
        self._registrar(
            f"{substituto.dados or substituto.ponto} ocupa o lugar de {no.dados or no.ponto}"
        )
        no.ponto, no.dados = substituto.ponto, substituto.dados
        self._remover_no(substituto)

    # ------------------------------------------------------------------
    # Balanceamento, validação e desenho
    # ------------------------------------------------------------------
    def snapshot(self):
        """Retrato da árvore para desenho e comparação (antes/depois)."""
        def conv(no):
            x, y = no.ponto
            eixo = "x" if no.eixo == 0 else "y"
            nome = no.dados or "Ponto"
            filhos = []
            if no.esq is not None or no.dir is not None:
                filhos = [
                    conv(no.esq) if no.esq is not None else no_oculto(),
                    conv(no.dir) if no.dir is not None else no_oculto(),
                ]
            return {
                "id": id(no),
                "chave": (no.ponto, no.dados),
                "_ref": no,
                "rotulo": f"{nome}\n({x:g}, {y:g})",
                "estilo": f"kd_{eixo}",
                "filhos": filhos,
                "estado": None,
            }

        return conv(self.raiz) if self.raiz is not None else None

    def construir_balanceada(self, itens):
        """Reconstrói a árvore com a mediana de cada eixo. itens: lista de (ponto, dados)."""
        itens = [(_normalizar(p), d) for p, d in itens]
        altura_antes = self.altura()

        def construir(lista, profundidade, pai=None):
            if not lista:
                return None
            eixo = profundidade % 2
            lista = sorted(lista, key=lambda item: item[0][eixo])
            meio = len(lista) // 2
            # Com coordenadas iguais, recua até a primeira: os iguais ficam à direita.
            while meio > 0 and lista[meio - 1][0][eixo] == lista[meio][0][eixo]:
                meio -= 1
            ponto, dados = lista[meio]
            no = NoKD(ponto, dados, eixo, pai)
            no.esq = construir(lista[:meio], profundidade + 1, no)
            no.dir = construir(lista[meio + 1:], profundidade + 1, no)
            return no

        self.raiz = construir(itens, 0)
        self._quantidade = len(itens)
        self._registrar(
            f"Árvore reconstruída pela mediana: altura {altura_antes} → {self.altura()} "
            f"com {len(itens)} pontos"
        )

    def validar(self):
        """Confere a regra de partição: esquerda < valor do nó <= direita."""
        erros = []

        def visitar(no, pai, minimo, maximo):
            """minimo (inclusivo) e maximo (exclusivo) são pares (x, y)."""
            if no is None:
                return
            if no.pai is not pai:
                erros.append(f"ponteiro do pai incorreto em {no.ponto}")
            if any(not (minimo[e] <= no.ponto[e] < maximo[e]) for e in (0, 1)):
                erros.append(f"ponto {no.ponto} fora da região do seu ramo")
            corte = no.ponto[no.eixo]
            visitar(no.esq, no, minimo, _trocar(maximo, no.eixo, corte))
            visitar(no.dir, no, _trocar(minimo, no.eixo, corte), maximo)

        visitar(self.raiz, None, (-math.inf, -math.inf), (math.inf, math.inf))
        if len(self.todos()) != self._quantidade:
            erros.append("contador de pontos inconsistente")
        return len(erros) == 0, erros

    def regioes(self, x0, x1, y0, y1):
        """Cortes do plano para desenho: (eixo, valor, início, fim, ponto)."""
        cortes = []

        def visitar(no, x0, x1, y0, y1):
            if no is None:
                return
            x, y = no.ponto
            if no.eixo == 0:
                cortes.append(("x", x, y0, y1, no.ponto))
                visitar(no.esq, x0, x, y0, y1)
                visitar(no.dir, x, x1, y0, y1)
            else:
                cortes.append(("y", y, x0, x1, no.ponto))
                visitar(no.esq, x0, x1, y0, y)
                visitar(no.dir, x0, x1, y, y1)

        visitar(self.raiz, x0, x1, y0, y1)
        return cortes


def _filhos_kd(no):
    return [f for f in (no.esq, no.dir) if f is not None]


def _descricao_kd(no):
    x, y = no.ponto
    eixo = "x" if no.eixo == 0 else "y"
    nome = f"{no.dados}  " if no.dados else ""
    return f"{nome}({x:g}, {y:g}) corte em {eixo}"


def implementacao_kd(arvore):
    """Uma linha por nó, com ponto, eixo de corte e ponteiros."""
    ordem, ids = numerar(arvore.raiz, _filhos_kd)

    def ponteiro(no):
        return ids.get(id(no), "—") if no is not None else "—"

    return [
        {
            "nó": ids[id(no)],
            "ponto": f"({no.ponto[0]:g}, {no.ponto[1]:g})",
            "eixo de corte": "x" if no.eixo == 0 else "y",
            "ponteiro esquerdo": ponteiro(no.esq),
            "ponteiro direito": ponteiro(no.dir),
            "ponteiro pai": ponteiro(no.pai),
            "dados": str(no.dados or ""),
        }
        for no in ordem
    ]


def esquema_kd(arvore):
    return esquema_texto(arvore.raiz, _filhos_kd, _descricao_kd)

