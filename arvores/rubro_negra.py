"""Árvore Rubro-Negra implementada com nós e ponteiros.

Propriedades:
  1. A raiz é preta.
  2. Um nó vermelho nunca tem filho vermelho.
  3. Todo caminho da raiz até uma folha vazia tem o mesmo número de nós pretos.

Chaves repetidas (método adotado no projeto):
  Cada nó guarda uma lista de valores, chamada balde. Inserir uma chave que já
  existe só acrescenta um valor ao balde: a estrutura não muda e não há
  rebalanceamento. A chave só sai da árvore quando o balde fica vazio.
"""

from .inspecao import esquema_texto, no_oculto, numerar

VERMELHO = "vermelho"
PRETO = "preto"


class No:
    __slots__ = ("chave", "valores", "cor", "esq", "dir", "pai")

    def __init__(self, chave, valores, cor, sentinela):
        self.chave = chave
        self.valores = valores
        self.cor = cor
        self.esq = sentinela
        self.dir = sentinela
        self.pai = sentinela


class ArvoreRubroNegra:
    def __init__(self):
        # Nó sentinela NIL: representa todas as folhas vazias, sempre preto.
        self.nil = No(None, [], PRETO, None)
        self.nil.esq = self.nil.dir = self.nil.pai = self.nil
        self.raiz = self.nil
        self._nos = 0
        self.eventos = []

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def __len__(self):
        """Número de nós, ou seja, de chaves distintas."""
        return self._nos

    def total_valores(self):
        return sum(len(no.valores) for no in self._percorrer())

    def _registrar(self, mensagem):
        self.eventos.append(mensagem)

    def limpar_eventos(self):
        self.eventos = []

    def _pintar(self, no, cor):
        """Muda a cor de um nó e registra a recoloração, se a cor mudou."""
        if no.cor == cor:
            return
        no.cor = cor
        self._registrar(f"Recoloração: {no.chave} vira {cor}")

    def _percorrer(self):
        """Percorre os nós reais em ordem crescente de chave."""
        pilha = []
        atual = self.raiz
        while pilha or atual is not self.nil:
            while atual is not self.nil:
                pilha.append(atual)
                atual = atual.esq
            atual = pilha.pop()
            yield atual
            atual = atual.dir

    def em_ordem(self):
        return [(no.chave, list(no.valores)) for no in self._percorrer()]

    def altura(self):
        def h(no):
            return 0 if no is self.nil else 1 + max(h(no.esq), h(no.dir))
        return h(self.raiz)

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------
    def _localizar(self, chave):
        atual = self.raiz
        while atual is not self.nil:
            if chave == atual.chave:
                return atual
            atual = atual.esq if chave < atual.chave else atual.dir
        return None

    def buscar(self, chave):
        """Devolve a lista de valores da chave, ou None se não existir."""
        no = self._localizar(chave)
        return list(no.valores) if no is not None else None

    def passos_busca(self, chave, formatar=str):
        """Caminho da busca: (nós visitados, explicação de cada passo, achou?)."""
        visitados, passos = [], []
        atual = self.raiz
        while atual is not self.nil:
            visitados.append(atual)
            if chave == atual.chave:
                passos.append(f"{formatar(chave)} encontrado")
                return visitados, passos, True
            menor = chave < atual.chave
            passos.append(
                f"{formatar(chave)} é {'menor' if menor else 'maior'} que {formatar(atual.chave)}: "
                f"segue para a {'esquerda' if menor else 'direita'}"
            )
            atual = atual.esq if menor else atual.dir
        passos.append(f"Chegou a uma folha vazia: {formatar(chave)} não está na árvore")
        return visitados, passos, False

    def intervalo(self, inicio, fim):
        """Todas as chaves entre inicio e fim (inclusive), em ordem.

        Poda os ramos que não podem conter nenhuma chave do intervalo.
        """
        resultado = []

        def visitar(no):
            if no is self.nil:
                return
            if inicio < no.chave:
                visitar(no.esq)
            if inicio <= no.chave <= fim:
                resultado.append((no.chave, list(no.valores)))
            if fim > no.chave:
                visitar(no.dir)

        visitar(self.raiz)
        return resultado

    # ------------------------------------------------------------------
    # Rotações
    # ------------------------------------------------------------------
    def _rotacionar_esquerda(self, x):
        y = x.dir
        x.dir = y.esq
        if y.esq is not self.nil:
            y.esq.pai = x
        y.pai = x.pai
        if x.pai is self.nil:
            self.raiz = y
        elif x is x.pai.esq:
            x.pai.esq = y
        else:
            x.pai.dir = y
        y.esq = x
        x.pai = y
        self._registrar(f"Rotação à esquerda em {x.chave}")

    def _rotacionar_direita(self, x):
        y = x.esq
        x.esq = y.dir
        if y.dir is not self.nil:
            y.dir.pai = x
        y.pai = x.pai
        if x.pai is self.nil:
            self.raiz = y
        elif x is x.pai.dir:
            x.pai.dir = y
        else:
            x.pai.esq = y
        y.dir = x
        x.pai = y
        self._registrar(f"Rotação à direita em {x.chave}")

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, chave, valor):
        existente = self._localizar(chave)
        if existente is not None:
            existente.valores.append(valor)
            self._registrar(
                f"Chave {chave} já existe: o valor entrou no balde, sem rebalancear"
            )
            return

        novo = No(chave, [valor], VERMELHO, self.nil)
        pai = self.nil
        atual = self.raiz
        while atual is not self.nil:
            pai = atual
            atual = atual.esq if chave < atual.chave else atual.dir

        novo.pai = pai
        if pai is self.nil:
            self.raiz = novo
        elif chave < pai.chave:
            pai.esq = novo
        else:
            pai.dir = novo

        self._nos += 1
        self._registrar(f"Inserido {chave} como vermelho")
        self._corrigir_insercao(novo)

    def _corrigir_insercao(self, z):
        while z.pai.cor == VERMELHO:
            avo = z.pai.pai
            if z.pai is avo.esq:
                tio = avo.dir
                if tio.cor == VERMELHO:
                    self._registrar(
                        f"Recoloração: pai {z.pai.chave} e tio {tio.chave} viram pretos; "
                        f"avô {avo.chave} vira vermelho"
                    )
                    z.pai.cor = PRETO
                    tio.cor = PRETO
                    avo.cor = VERMELHO
                    z = avo
                else:
                    if z is z.pai.dir:
                        z = z.pai
                        self._rotacionar_esquerda(z)
                    self._pintar(z.pai, PRETO)
                    self._pintar(z.pai.pai, VERMELHO)
                    self._rotacionar_direita(z.pai.pai)
            else:
                tio = avo.esq
                if tio.cor == VERMELHO:
                    self._registrar(
                        f"Recoloração: pai {z.pai.chave} e tio {tio.chave} viram pretos; "
                        f"avô {avo.chave} vira vermelho"
                    )
                    z.pai.cor = PRETO
                    tio.cor = PRETO
                    avo.cor = VERMELHO
                    z = avo
                else:
                    if z is z.pai.esq:
                        z = z.pai
                        self._rotacionar_direita(z)
                    self._pintar(z.pai, PRETO)
                    self._pintar(z.pai.pai, VERMELHO)
                    self._rotacionar_esquerda(z.pai.pai)
        self._pintar(self.raiz, PRETO)

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover(self, chave):
        """Remove a chave inteira, com todo o balde. Devolve True se achou."""
        z = self._localizar(chave)
        if z is None:
            return False
        self._registrar(f"Removido {chave}")
        self._remover_no(z)
        self._nos -= 1
        return True

    def remover_valor(self, chave, valor):
        """Remove um valor do balde. Se o balde ficar vazio, remove o nó."""
        no = self._localizar(chave)
        if no is None or valor not in no.valores:
            return False
        if len(no.valores) > 1:
            no.valores.remove(valor)
            self._registrar(f"Valor removido do balde da chave {chave}; estrutura não muda")
            return True
        return self.remover(chave)

    def _transplantar(self, u, v):
        if u.pai is self.nil:
            self.raiz = v
        elif u is u.pai.esq:
            u.pai.esq = v
        else:
            u.pai.dir = v
        v.pai = u.pai

    def _minimo(self, x):
        while x.esq is not self.nil:
            x = x.esq
        return x

    def _remover_no(self, z):
        y = z
        cor_original = y.cor
        if z.esq is self.nil:
            x = z.dir
            self._transplantar(z, z.dir)
        elif z.dir is self.nil:
            x = z.esq
            self._transplantar(z, z.esq)
        else:
            y = self._minimo(z.dir)
            cor_original = y.cor
            self._registrar(
                f"{z.chave} tem dois filhos: o sucessor {y.chave} ocupa o lugar e a cor dele"
            )
            x = y.dir
            if y.pai is z:
                x.pai = y
            else:
                self._transplantar(y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            self._transplantar(z, y)
            y.esq = z.esq
            y.esq.pai = y
            y.cor = z.cor

        if cor_original == PRETO:
            self._corrigir_remocao(x)

    def _corrigir_remocao(self, x):
        while x is not self.raiz and x.cor == PRETO:
            if x is x.pai.esq:
                w = x.pai.dir
                if w.cor == VERMELHO:
                    self._pintar(w, PRETO)
                    self._pintar(x.pai, VERMELHO)
                    self._rotacionar_esquerda(x.pai)
                    w = x.pai.dir
                if w.esq.cor == PRETO and w.dir.cor == PRETO:
                    self._pintar(w, VERMELHO)
                    x = x.pai
                else:
                    if w.dir.cor == PRETO:
                        self._pintar(w.esq, PRETO)
                        self._pintar(w, VERMELHO)
                        self._rotacionar_direita(w)
                        w = x.pai.dir
                    self._pintar(w, x.pai.cor)
                    self._pintar(x.pai, PRETO)
                    self._pintar(w.dir, PRETO)
                    self._rotacionar_esquerda(x.pai)
                    x = self.raiz
            else:
                w = x.pai.esq
                if w.cor == VERMELHO:
                    self._pintar(w, PRETO)
                    self._pintar(x.pai, VERMELHO)
                    self._rotacionar_direita(x.pai)
                    w = x.pai.esq
                if w.dir.cor == PRETO and w.esq.cor == PRETO:
                    self._pintar(w, VERMELHO)
                    x = x.pai
                else:
                    if w.esq.cor == PRETO:
                        self._pintar(w.dir, PRETO)
                        self._pintar(w, VERMELHO)
                        self._rotacionar_esquerda(w)
                        w = x.pai.esq
                    self._pintar(w, x.pai.cor)
                    self._pintar(x.pai, PRETO)
                    self._pintar(w.esq, PRETO)
                    self._rotacionar_direita(x.pai)
                    x = self.raiz
        self._pintar(x, PRETO)

    # ------------------------------------------------------------------
    # Validação e visualização
    # ------------------------------------------------------------------
    def validar(self):
        """Confere as propriedades da Rubro-Negra. Devolve (ok, lista_de_erros)."""
        erros = []
        contagem = 0

        if self.raiz is not self.nil and self.raiz.cor != PRETO:
            erros.append("a raiz não é preta")

        def visitar(no, minimo, maximo):
            nonlocal contagem
            if no is self.nil:
                return 1
            contagem += 1
            if minimo is not None and no.chave <= minimo:
                erros.append(f"ordem violada em {no.chave}")
            if maximo is not None and no.chave >= maximo:
                erros.append(f"ordem violada em {no.chave}")
            for filho in (no.esq, no.dir):
                if filho is not self.nil and filho.pai is not no:
                    erros.append(f"ponteiro do pai incorreto em {filho.chave}")
            if no.cor == VERMELHO and (no.esq.cor == VERMELHO or no.dir.cor == VERMELHO):
                erros.append(f"vermelho com filho vermelho em {no.chave}")
            esquerda = visitar(no.esq, minimo, no.chave)
            direita = visitar(no.dir, no.chave, maximo)
            if esquerda != direita:
                erros.append(f"altura negra diferente em {no.chave}")
            return esquerda + (1 if no.cor == PRETO else 0)

        visitar(self.raiz, None, None)
        if contagem != self._nos:
            erros.append("contador de nós inconsistente")
        return len(erros) == 0, erros

    # ------------------------------------------------------------------
    # Interface comum com a 2-3-4 (usada pela troca de estrutura na agenda)
    # ------------------------------------------------------------------
    def adicionar(self, chave, valor):
        """Acrescenta um valor à chave (balde). Mesma regra de inserir."""
        self.inserir(chave, valor)

    def _filhos_reais(self, no):
        return [f for f in (no.esq, no.dir) if f is not self.nil]

    def implementacao(self, formatar=str):
        """Uma linha por nó, com cor e ponteiros (esquerdo, direito e pai)."""
        raiz = None if self.raiz is self.nil else self.raiz
        ordem, ids = numerar(raiz, self._filhos_reais)

        def ponteiro(no):
            return ids.get(id(no), "—")

        return [
            {
                "nó": ids[id(no)],
                "chave": formatar(no.chave),
                "cor": no.cor,
                "valores no balde": len(no.valores),
                "ponteiro esquerdo": ponteiro(no.esq),
                "ponteiro direito": ponteiro(no.dir),
                "ponteiro pai": ponteiro(no.pai),
            }
            for no in ordem
        ]

    def snapshot(self, formatar=str):
        """Retrato da árvore para desenho e comparação (antes/depois)."""
        if self.raiz is self.nil:
            return None

        def conv(no):
            rotulo = formatar(no.chave)
            filhos = []
            if no.esq is not self.nil or no.dir is not self.nil:
                filhos = [
                    conv(no.esq) if no.esq is not self.nil else no_oculto(),
                    conv(no.dir) if no.dir is not self.nil else no_oculto(),
                ]
            return {
                "id": id(no),
                "_ref": no,
                "rotulo": rotulo,
                "quantidade": len(no.valores),
                "estilo": "vermelho" if no.cor == VERMELHO else "preto",
                "filhos": filhos,
                "estado": None,
            }

        return conv(self.raiz)

    def esquema(self, formatar=str):
        raiz = None if self.raiz is self.nil else self.raiz

        def descricao(no):
            extra = f" ×{len(no.valores)}" if len(no.valores) > 1 else ""
            return f"{formatar(no.chave)} ({no.cor}){extra}"

        return esquema_texto(raiz, self._filhos_reais, descricao)
