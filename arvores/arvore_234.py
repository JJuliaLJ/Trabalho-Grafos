"""Árvore 2-3-4 (não binária) implementada com nós ligados nos dois sentidos:
cada nó aponta para os filhos e para o pai.

Cada nó tem 1, 2 ou 3 chaves e, se não for folha, 2, 3 ou 4 filhos.
Todas as folhas ficam no mesmo nível.

Inserção: divide preventivamente os nós cheios (com 3 chaves) durante a descida.
Remoção: a descida garante que todo nó visitado tenha pelo menos 2 chaves,
usando empréstimo de irmão ou fusão. Assim a remoção também mantém o balanceamento.

Chaves repetidas (método adotado no projeto):
  Não existem duas entradas com a mesma chave. Inserir uma chave que já existe
  substitui o valor guardado (o cadastro é atualizado). A estrutura não muda.
"""

from bisect import bisect_left

from .inspecao import esquema_texto, numerar


class No:
    __slots__ = ("chaves", "valores", "filhos", "pai")

    def __init__(self, chaves=None, valores=None, filhos=None):
        self.chaves = chaves if chaves is not None else []
        self.valores = valores if valores is not None else []
        self.filhos = filhos if filhos is not None else []
        self.pai = None
        self.adotar()

    def adotar(self):
        """Faz cada filho apontar de volta para este nó."""
        for filho in self.filhos:
            filho.pai = self

    def folha(self):
        return not self.filhos


class Arvore234:
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

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------
    def _localizar(self, chave):
        """Devolve (nó, índice) onde a chave está, ou (None, None)."""
        no = self.raiz
        while no is not None:
            i = bisect_left(no.chaves, chave)
            if i < len(no.chaves) and no.chaves[i] == chave:
                return no, i
            if no.folha():
                break
            no = no.filhos[i]
        return None, None

    def contem(self, chave):
        return self._localizar(chave)[0] is not None

    def buscar(self, chave):
        no, i = self._localizar(chave)
        return no.valores[i] if no is not None else None

    def passos_busca(self, chave, formatar=str):
        """Caminho da busca: (nós visitados, explicação de cada passo, achou?)."""
        visitados, passos = [], []
        no = self.raiz
        while no is not None:
            visitados.append(no)
            nomes = " | ".join(formatar(c) for c in no.chaves)
            i = bisect_left(no.chaves, chave)
            if i < len(no.chaves) and no.chaves[i] == chave:
                passos.append(f"{formatar(chave)} encontrado no nó [{nomes}]")
                return visitados, passos, True
            if no.folha():
                break
            passos.append(f"No nó [{nomes}], segue para o {i + 1}º filho")
            no = no.filhos[i]
        passos.append(f"Chegou ao fim: {formatar(chave)} não está na árvore")
        return visitados, passos, False

    def em_ordem(self):
        saida = []

        def visitar(no):
            if no is None:
                return
            for i, chave in enumerate(no.chaves):
                if not no.folha():
                    visitar(no.filhos[i])
                saida.append((chave, no.valores[i]))
            if not no.folha():
                visitar(no.filhos[-1])

        visitar(self.raiz)
        return saida

    def altura(self):
        altura, no = 0, self.raiz
        while no is not None:
            altura += 1
            no = no.filhos[0] if no.filhos else None
        return altura

    # ------------------------------------------------------------------
    # Inserção
    # ------------------------------------------------------------------
    def inserir(self, chave, valor):
        no, i = self._localizar(chave)
        if no is not None:
            no.valores[i] = valor
            self._registrar(f"Chave {chave} já existia: valor atualizado, sem mudar a estrutura")
            return

        if self.raiz is None:
            self.raiz = No([chave], [valor])
        else:
            if len(self.raiz.chaves) == 3:
                antiga = self.raiz
                self.raiz = No([], [], [antiga])
                self._dividir(self.raiz, 0)
                self._registrar("Raiz cheia (3 chaves): dividida, e a altura cresce 1")
            self._inserir_nao_cheio(self.raiz, chave, valor)

        self._quantidade += 1
        self._registrar(f"Inserido {chave}")

    def _dividir(self, pai, i):
        cheio = pai.filhos[i]
        chave_meio = cheio.chaves[1]
        valor_meio = cheio.valores[1]
        esquerda = No(cheio.chaves[:1], cheio.valores[:1], cheio.filhos[:2])
        direita = No(cheio.chaves[2:], cheio.valores[2:], cheio.filhos[2:])
        pai.chaves.insert(i, chave_meio)
        pai.valores.insert(i, valor_meio)
        pai.filhos[i:i + 1] = [esquerda, direita]
        pai.adotar()
        self._registrar(
            f"Nó com {cheio.chaves} dividido: {chave_meio} sobe para o pai"
        )

    def _inserir_nao_cheio(self, no, chave, valor):
        while not no.folha():
            i = bisect_left(no.chaves, chave)
            if len(no.filhos[i].chaves) == 3:
                self._dividir(no, i)
                if chave > no.chaves[i]:
                    i += 1
            no = no.filhos[i]
        i = bisect_left(no.chaves, chave)
        no.chaves.insert(i, chave)
        no.valores.insert(i, valor)

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------
    def remover(self, chave):
        if not self.contem(chave):
            return False
        self._remover(self.raiz, chave)
        self._quantidade -= 1
        if not self.raiz.chaves:
            if self.raiz.folha():
                self.raiz = None
            else:
                self.raiz = self.raiz.filhos[0]
                self.raiz.pai = None
                self._registrar("Raiz ficou vazia: a altura diminui 1")
        self._registrar(f"Removido {chave}")
        return True

    def _remover(self, no, chave):
        i = bisect_left(no.chaves, chave)
        encontrou = i < len(no.chaves) and no.chaves[i] == chave

        if encontrou:
            if no.folha():
                del no.chaves[i]
                del no.valores[i]
                return
            esquerda, direita = no.filhos[i], no.filhos[i + 1]
            if len(esquerda.chaves) >= 2:
                chave_sub, valor_sub = self._maximo(esquerda)
                self._registrar(f"{chave} é interno: trocado pelo antecessor {chave_sub}")
                no.chaves[i], no.valores[i] = chave_sub, valor_sub
                self._remover(esquerda, chave_sub)
            elif len(direita.chaves) >= 2:
                chave_sub, valor_sub = self._minimo(direita)
                self._registrar(f"{chave} é interno: trocado pelo sucessor {chave_sub}")
                no.chaves[i], no.valores[i] = chave_sub, valor_sub
                self._remover(direita, chave_sub)
            else:
                self._fundir(no, i)
                self._registrar(f"Fusão de nós para remover {chave}")
                self._remover(no.filhos[i], chave)
            return

        if no.folha():
            return
        if len(no.filhos[i].chaves) == 1:
            i = self._reforcar(no, i)
        self._remover(no.filhos[i], chave)

    def _reforcar(self, pai, i):
        """Garante que pai.filhos[i] tenha pelo menos 2 chaves. Devolve o novo índice."""
        filho = pai.filhos[i]

        if i > 0 and len(pai.filhos[i - 1].chaves) >= 2:
            irmao = pai.filhos[i - 1]
            filho.chaves.insert(0, pai.chaves[i - 1])
            filho.valores.insert(0, pai.valores[i - 1])
            pai.chaves[i - 1] = irmao.chaves.pop()
            pai.valores[i - 1] = irmao.valores.pop()
            if not irmao.folha():
                filho.filhos.insert(0, irmao.filhos.pop())
                filho.adotar()
            self._registrar("Empréstimo do irmão da esquerda (nó com 1 chave)")
            return i

        if i < len(pai.filhos) - 1 and len(pai.filhos[i + 1].chaves) >= 2:
            irmao = pai.filhos[i + 1]
            filho.chaves.append(pai.chaves[i])
            filho.valores.append(pai.valores[i])
            pai.chaves[i] = irmao.chaves.pop(0)
            pai.valores[i] = irmao.valores.pop(0)
            if not irmao.folha():
                filho.filhos.append(irmao.filhos.pop(0))
                filho.adotar()
            self._registrar("Empréstimo do irmão da direita (nó com 1 chave)")
            return i

        if i > 0:
            self._fundir(pai, i - 1)
            self._registrar("Fusão com o irmão da esquerda (nó com 1 chave)")
            return i - 1

        self._fundir(pai, i)
        self._registrar("Fusão com o irmão da direita (nó com 1 chave)")
        return i

    def _fundir(self, pai, i):
        """Junta pai.filhos[i], a chave pai.chaves[i] e pai.filhos[i+1] em um nó."""
        esquerda = pai.filhos[i]
        direita = pai.filhos[i + 1]
        esquerda.chaves.append(pai.chaves.pop(i))
        esquerda.valores.append(pai.valores.pop(i))
        esquerda.chaves.extend(direita.chaves)
        esquerda.valores.extend(direita.valores)
        esquerda.filhos.extend(direita.filhos)
        esquerda.adotar()
        del pai.filhos[i + 1]

    def _maximo(self, no):
        while not no.folha():
            no = no.filhos[-1]
        return no.chaves[-1], no.valores[-1]

    def _minimo(self, no):
        while not no.folha():
            no = no.filhos[0]
        return no.chaves[0], no.valores[0]

    # ------------------------------------------------------------------
    # Validação e visualização
    # ------------------------------------------------------------------
    def validar(self):
        erros = []
        if self.raiz is None:
            return True, []

        profundidades = set()
        contagem = 0

        def visitar(no, lo, hi, prof):
            nonlocal contagem
            n = len(no.chaves)
            contagem += n
            if not (1 <= n <= 3):
                erros.append(f"nó com {n} chaves (deveria ter de 1 a 3)")
            for a, b in zip(no.chaves, no.chaves[1:]):
                if a >= b:
                    erros.append("chaves fora de ordem dentro de um nó")
            for c in no.chaves:
                if (lo is not None and c <= lo) or (hi is not None and c >= hi):
                    erros.append(f"chave {c} fora do intervalo do seu ramo")
            if no.folha():
                profundidades.add(prof)
                return
            if len(no.filhos) != n + 1:
                erros.append("número de filhos incorreto")
                return
            for j, filho in enumerate(no.filhos):
                if filho.pai is not no:
                    erros.append(f"ponteiro do pai incorreto em {filho.chaves}")
                nlo = no.chaves[j - 1] if j > 0 else lo
                nhi = no.chaves[j] if j < n else hi
                visitar(filho, nlo, nhi, prof + 1)

        if self.raiz.pai is not None:
            erros.append("a raiz não deveria ter pai")
        visitar(self.raiz, None, None, 0)
        if len(profundidades) > 1:
            erros.append("folhas em níveis diferentes")
        if contagem != self._quantidade:
            erros.append("contador de chaves inconsistente")
        return len(erros) == 0, erros

    # ------------------------------------------------------------------
    # Interface comum com a Rubro-Negra (usada pela troca de estrutura na agenda)
    # ------------------------------------------------------------------
    def adicionar(self, chave, valor):
        """Balde: a chave guarda uma lista de valores; o valor entra nessa lista."""
        no, i = self._localizar(chave)
        if no is None:
            self.inserir(chave, [valor])
            return
        no.valores[i].append(valor)
        self._registrar(f"Chave {chave} já existe: o valor entrou no balde, sem rebalancear")

    def remover_valor(self, chave, valor):
        no, i = self._localizar(chave)
        if no is None or valor not in no.valores[i]:
            return False
        if len(no.valores[i]) > 1:
            no.valores[i].remove(valor)
            self._registrar(f"Valor removido do balde da chave {chave}; estrutura não muda")
            return True
        return self.remover(chave)

    def intervalo(self, inicio, fim):
        """Chaves entre inicio e fim (inclusive), com ramos fora do intervalo ignorados."""
        saida = []

        def visitar(no):
            if no is None:
                return
            for i, chave in enumerate(no.chaves):
                if not no.folha() and inicio < chave:
                    visitar(no.filhos[i])
                if inicio <= chave <= fim:
                    saida.append((chave, list(no.valores[i])))
            if not no.folha() and fim > no.chaves[-1]:
                visitar(no.filhos[-1])

        visitar(self.raiz)
        return saida

    # ------------------------------------------------------------------
    # Inspeção da implementação
    # ------------------------------------------------------------------
    def implementacao(self, formatar=str):
        """Uma linha por nó, com as chaves e os ponteiros para os filhos."""
        ordem, ids = numerar(self.raiz, lambda n: n.filhos)
        return [
            {
                "nó": ids[id(no)],
                "chaves": " | ".join(formatar(c) for c in no.chaves),
                "nº de chaves": len(no.chaves),
                "ponteiro pai": ids[id(no.pai)] if no.pai is not None else "—",
                "ponteiros para filhos": ", ".join(ids[id(f)] for f in no.filhos) or "—",
                "folha": "sim" if no.folha() else "não",
            }
            for no in ordem
        ]

    def snapshot(self, formatar=str):
        """Retrato da árvore para desenho e comparação (antes/depois)."""
        def conv(no):
            partes = [formatar(chave) for chave in no.chaves]
            quantidades = [len(v) if isinstance(v, list) else 1 for v in no.valores]
            return {
                "id": id(no),
                "_ref": no,
                "rotulo": "  |  ".join(partes),
                "celulas": partes,
                "quantidades": quantidades,
                "estilo": "azul",
                "filhos": [conv(f) for f in no.filhos],
                "estado": None,
            }

        return conv(self.raiz) if self.raiz is not None else None

    def esquema(self, formatar=str):
        return esquema_texto(
            self.raiz,
            lambda n: n.filhos,
            lambda n: " | ".join(formatar(c) for c in n.chaves),
        )
