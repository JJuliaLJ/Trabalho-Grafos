"""Árvore binária de busca SEM balanceamento.

Serve apenas para comparação. Com chaves inseridas em ordem crescente,
ela vira praticamente uma lista e a altura cresce junto com o número de chaves.
"""


class NoBinario:
    __slots__ = ("chave", "esq", "dir")

    def __init__(self, chave):
        self.chave = chave
        self.esq = None
        self.dir = None


class ArvoreBinariaSimples:
    def __init__(self):
        self.raiz = None
        self._nos = 0

    def __len__(self):
        return self._nos

    def inserir(self, chave):
        if self.raiz is None:
            self.raiz = NoBinario(chave)
            self._nos += 1
            return
        atual = self.raiz
        while True:
            if chave == atual.chave:
                return
            if chave < atual.chave:
                if atual.esq is None:
                    atual.esq = NoBinario(chave)
                    self._nos += 1
                    return
                atual = atual.esq
            else:
                if atual.dir is None:
                    atual.dir = NoBinario(chave)
                    self._nos += 1
                    return
                atual = atual.dir

    def altura(self):
        def h(no):
            return 0 if no is None else 1 + max(h(no.esq), h(no.dir))
        return h(self.raiz)
