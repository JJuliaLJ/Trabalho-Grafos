"""Testes das estruturas. Compara cada operação com uma implementação simples (força bruta)."""

import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arvores.arvore_234 import Arvore234  # noqa: E402
from arvores.bst import ArvoreBinariaSimples  # noqa: E402
from arvores.kdtree import ArvoreKD  # noqa: E402
from arvores.rubro_negra import ArvoreRubroNegra  # noqa: E402
from arvores.kdtree import implementacao_kd  # noqa: E402
from dados.demo import consultas_demo, pacientes_demo, UBS_EXEMPLO  # noqa: E402


class TestesRubroNegra(unittest.TestCase):
    def test_demonstracao_tem_pelo_menos_21_nos_e_e_valida(self):
        arvore = ArvoreRubroNegra()
        for chave, valor in consultas_demo():
            arvore.inserir(chave, valor)
        self.assertGreaterEqual(len(arvore), 21)
        self.assertTrue(arvore.validar()[0])

    def test_toda_troca_de_cor_aparece_nos_eventos(self):
        for semente in range(20):
            rnd = random.Random(semente)
            arvore = ArvoreRubroNegra()
            for _ in range(300):
                cores = {no.chave: no.cor for no in arvore._percorrer()}
                arvore.limpar_eventos()
                chave = rnd.randint(0, 60)
                if rnd.random() < 0.55:
                    arvore.inserir(chave, chave)
                else:
                    arvore.remover(chave)
                # O sucessor herda a cor do removido; isso tem um evento próprio.
                herdou = [e for e in arvore.eventos if "ocupa o lugar" in e]
                mudaram = [no.chave for no in arvore._percorrer()
                           if no.chave in cores and cores[no.chave] != no.cor]
                texto = " ".join(e for e in arvore.eventos if "Recoloração" in e) + " ".join(herdou)
                for c in mudaram:
                    self.assertRegex(texto, rf"\b{c}\b")

    def test_passos_da_busca(self):
        arvore = ArvoreRubroNegra()
        for c in range(1, 25):
            arvore.inserir(c, c)
        for c in range(0, 27):
            visitados, passos, achou = arvore.passos_busca(c)
            self.assertEqual(achou, arvore.buscar(c) is not None)
            self.assertLessEqual(len(visitados), arvore.altura())
            self.assertGreaterEqual(len(passos), len(visitados))

    def test_inserir_chave_repetida_entra_no_balde(self):
        arvore = ArvoreRubroNegra()
        arvore.inserir(10, "a")
        arvore.inserir(10, "b")
        self.assertEqual(len(arvore), 1)
        self.assertEqual(arvore.buscar(10), ["a", "b"])

    def test_aleatorio_contra_dicionario(self):
        for semente in range(30):
            rnd = random.Random(semente)
            arvore = ArvoreRubroNegra()
            modelo = {}
            for passo in range(400):
                op = rnd.random()
                chave = rnd.randint(0, 60)
                if op < 0.55:
                    arvore.inserir(chave, passo)
                    modelo.setdefault(chave, []).append(passo)
                elif op < 0.75:
                    removido = arvore.remover(chave)
                    self.assertEqual(removido, chave in modelo)
                    modelo.pop(chave, None)
                elif op < 0.9 and chave in modelo:
                    valor = rnd.choice(modelo[chave])
                    arvore.remover_valor(chave, valor)
                    modelo[chave].remove(valor)
                    if not modelo[chave]:
                        del modelo[chave]
                else:
                    self.assertEqual(arvore.buscar(chave), modelo.get(chave))
                ok, erros = arvore.validar()
                self.assertTrue(ok, f"semente {semente}, passo {passo}: {erros}")
                self.assertEqual(len(arvore), len(modelo))
            self.assertEqual(arvore.em_ordem(), sorted(modelo.items()))

    def test_intervalo_contra_forca_bruta(self):
        rnd = random.Random(3)
        arvore = ArvoreRubroNegra()
        chaves = rnd.sample(range(0, 300), 120)
        for c in chaves:
            arvore.inserir(c, c)
        for _ in range(100):
            a, b = sorted(rnd.sample(range(0, 300), 2))
            esperado = [(c, [c]) for c in sorted(chaves) if a <= c <= b]
            self.assertEqual(arvore.intervalo(a, b), esperado)


class TestesArvore234(unittest.TestCase):
    def test_aleatorio_contra_dicionario(self):
        for semente in range(30):
            rnd = random.Random(semente)
            arvore = Arvore234()
            modelo = {}
            for passo in range(400):
                op = rnd.random()
                chave = rnd.randint(0, 80)
                if op < 0.55:
                    arvore.inserir(chave, passo)
                    modelo[chave] = passo
                elif op < 0.85:
                    removido = arvore.remover(chave)
                    self.assertEqual(removido, chave in modelo)
                    modelo.pop(chave, None)
                else:
                    self.assertEqual(arvore.buscar(chave), modelo.get(chave))
                ok, erros = arvore.validar()
                self.assertTrue(ok, f"semente {semente}, passo {passo}: {erros}")
                self.assertEqual(len(arvore), len(modelo))
            self.assertEqual(arvore.em_ordem(), sorted(modelo.items()))

    def test_ponteiros_de_pai_e_passos_da_busca(self):
        arvore = Arvore234()
        for c in range(1, 60):
            arvore.inserir(c, c)
        for c in range(1, 60, 3):
            arvore.remover(c)

        def conferir(no):
            for filho in no.filhos:
                self.assertIs(filho.pai, no)
                conferir(filho)

        self.assertIsNone(arvore.raiz.pai)
        conferir(arvore.raiz)
        for c in range(0, 62):
            visitados, _, achou = arvore.passos_busca(c)
            self.assertEqual(achou, arvore.contem(c))
            self.assertLessEqual(len(visitados), arvore.altura())

    def test_chave_repetida_atualiza_cadastro(self):
        arvore = Arvore234()
        arvore.inserir(10001, "Ana")
        arvore.inserir(10001, "Ana Souza")
        self.assertEqual(len(arvore), 1)
        self.assertEqual(arvore.buscar(10001), "Ana Souza")

    def test_altura_cresce_so_com_divisao_da_raiz(self):
        arvore = Arvore234()
        for c in range(1, 22):
            arvore.inserir(c, c)
        # Em 2-3-4, altura máxima com n chaves = floor(log2(n + 1)).
        self.assertLessEqual(arvore.altura(), math.floor(math.log2(21 + 1)))
        self.assertTrue(arvore.validar()[0])


class TestesKD(unittest.TestCase):
    def _pontos(self, n, semente):
        rnd = random.Random(semente)
        conjunto = set()
        while len(conjunto) < n:
            conjunto.add((rnd.randint(0, 50), rnd.randint(0, 50)))
        return list(conjunto)

    def test_vizinho_mais_proximo_contra_forca_bruta(self):
        for semente in range(20):
            pontos = self._pontos(60, semente)
            arvore = ArvoreKD()
            for p in pontos:
                arvore.inserir(p)
            rnd = random.Random(semente + 100)
            for _ in range(30):
                alvo = (rnd.uniform(-5, 55), rnd.uniform(-5, 55))
                _, distancia = arvore.mais_proximo(alvo)
                esperado = min(math.dist(p, alvo) for p in pontos)
                self.assertAlmostEqual(distancia, esperado, places=9)

    def test_k_mais_proximos_e_raio_contra_forca_bruta(self):
        pontos = self._pontos(80, 5)
        arvore = ArvoreKD()
        for p in pontos:
            arvore.inserir(p)
        alvo = (25.3, 18.7)
        k = 5
        esperado_k = sorted(math.dist(p, alvo) for p in pontos)[:k]
        obtido_k = [d for d, _ in arvore.k_mais_proximos(alvo, k)]
        for a, b in zip(obtido_k, esperado_k):
            self.assertAlmostEqual(a, b, places=9)
        esperado_raio = sorted(math.dist(p, alvo) for p in pontos if math.dist(p, alvo) <= 12)
        obtido_raio = [d for d, _ in arvore.dentro_do_raio(alvo, 12)]
        self.assertEqual(len(obtido_raio), len(esperado_raio))

    def test_remocao_mantem_particao_e_busca(self):
        for semente in range(15):
            pontos = self._pontos(50, semente)
            arvore = ArvoreKD()
            for p in pontos:
                arvore.inserir(p)
            rnd = random.Random(semente)
            restantes = list(pontos)
            rnd.shuffle(restantes)
            for p in restantes[:25]:
                self.assertTrue(arvore.remover(p))
                ok, erros = arvore.validar()
                self.assertTrue(ok, erros)
            sobra = restantes[25:]
            self.assertEqual(len(arvore), len(sobra))
            for p in sobra:
                self.assertIsNotNone(arvore.buscar(p))
            for p in restantes[:25]:
                self.assertIsNone(arvore.buscar(p))

    def test_construcao_balanceada_reduz_altura(self):
        pontos = [((i, i), f"P{i}") for i in range(31)]
        comum = ArvoreKD()
        for p, d in pontos:
            comum.inserir(p, d)
        balanceada = ArvoreKD()
        balanceada.construir_balanceada(pontos)
        self.assertGreater(comum.altura(), balanceada.altura())
        self.assertLessEqual(balanceada.altura(), 5)
        self.assertTrue(balanceada.validar()[0])

    def test_ubs_de_exemplo(self):
        arvore = ArvoreKD()
        for nome, x, y in UBS_EXEMPLO:
            arvore.inserir((x, y), nome)
        no, _ = arvore.mais_proximo((5.0, 6.0))
        self.assertEqual(no.dados, "UBS Bela Vista")

    def test_ponto_repetido_vai_para_direita_e_e_encontrado(self):
        arvore = ArvoreKD()
        arvore.inserir((1, 1), "A")
        arvore.inserir((1, 1), "B")
        self.assertEqual(len(arvore), 2)
        self.assertIsNotNone(arvore.buscar((1, 1)))


    def test_demonstracao_tem_pelo_menos_21_nos(self):
        self.assertGreaterEqual(len(UBS_EXEMPLO), 21)
        self.assertEqual(len({nome for nome, _, _ in UBS_EXEMPLO}), len(UBS_EXEMPLO))

    def test_remove_o_registro_certo_entre_pontos_repetidos(self):
        for semente in range(300):
            rnd = random.Random(semente)
            arvore, itens = ArvoreKD(), []
            for i in range(25):
                p = (float(rnd.randint(0, 3)), float(rnd.randint(0, 3)))
                arvore.inserir(p, f"U{i}")
                itens.append((p, f"U{i}"))
            if semente % 2:
                arvore.construir_balanceada(itens)
            rnd.shuffle(itens)
            while itens:
                ponto, nome = itens.pop()
                self.assertTrue(arvore.passos_busca(ponto, nome)[2])
                self.assertTrue(arvore.remover(ponto, nome))
                ok, erros = arvore.validar()
                self.assertTrue(ok, erros)
                self.assertEqual(sorted((n.ponto, n.dados) for n in arvore.todos()), sorted(itens))


class TestesBST(unittest.TestCase):
    def test_ordem_crescente_degenera_em_lista(self):
        arvore = ArvoreBinariaSimples()
        for c in range(1, 41):
            arvore.inserir(c)
        self.assertEqual(arvore.altura(), 40)

    def test_demo_de_pacientes_nao_tem_repeticao(self):
        pares = pacientes_demo()
        self.assertEqual(len({p for p, _ in pares}), len(pares))


class TestesInterfaceComum(unittest.TestCase):
    """Agenda: Rubro-Negra e 2-3-4 precisam se comportar igual para a troca de estrutura."""

    def test_baldes_e_intervalo_iguais_nas_duas_arvores(self):
        for semente in range(20):
            rnd = random.Random(semente)
            rb, t = ArvoreRubroNegra(), Arvore234()
            modelo = {}
            for passo in range(300):
                op = rnd.random()
                chave = rnd.randint(0, 40)
                if op < 0.6:
                    rb.adicionar(chave, passo)
                    t.adicionar(chave, passo)
                    modelo.setdefault(chave, []).append(passo)
                elif op < 0.8 and chave in modelo:
                    valor = rnd.choice(modelo[chave])
                    self.assertTrue(rb.remover_valor(chave, valor))
                    self.assertTrue(t.remover_valor(chave, valor))
                    modelo[chave].remove(valor)
                    if not modelo[chave]:
                        del modelo[chave]
                else:
                    a, b = sorted(rnd.sample(range(0, 41), 2))
                    esperado = [(c, list(modelo[c])) for c in sorted(modelo) if a <= c <= b]
                    self.assertEqual(rb.intervalo(a, b), esperado)
                    self.assertEqual(t.intervalo(a, b), esperado)
                self.assertTrue(rb.validar()[0])
                self.assertTrue(t.validar()[0])
            self.assertEqual(rb.em_ordem(), t.em_ordem())

    def test_troca_de_estrutura_preserva_a_agenda(self):
        origem = ArvoreRubroNegra()
        for chave, valor in consultas_demo():
            origem.adicionar(chave, valor)
        destino = Arvore234()
        for chave, lista in origem.em_ordem():
            for valor in lista:
                destino.adicionar(chave, valor)
        self.assertEqual(origem.em_ordem(), destino.em_ordem())
        self.assertEqual(len(origem), len(destino))

    def test_implementacao_lista_todos_os_nos(self):
        rb = ArvoreRubroNegra()
        t = Arvore234()
        for c in range(1, 40):
            rb.inserir(c, c)
            t.inserir(c, c)
        self.assertEqual(len(rb.implementacao()), len(rb))
        self.assertEqual(sum(l["nº de chaves"] for l in t.implementacao()), len(t))
        self.assertIn("cor", rb.implementacao()[0])
        self.assertIn("ponteiro pai", rb.implementacao()[0])
        self.assertTrue(rb.esquema().startswith("N1"))
        self.assertTrue(t.esquema().startswith("N1"))

    def test_kd_implementacao_lista_todos_os_nos(self):
        kd = ArvoreKD()
        for nome, x, y in UBS_EXEMPLO:
            kd.inserir((x, y), nome)
        linhas = implementacao_kd(kd)
        self.assertEqual(len(linhas), len(kd))
        self.assertEqual(linhas[0]["eixo de corte"], "x")


class TestesRebalanceamentoVisual(unittest.TestCase):
    def test_rotacao_marca_no_novo_e_nos_ajustados(self):
        from visual.rebalanceamento import marcar, resumo_ajustes
        rb = ArvoreRubroNegra()
        rb.inserir(10, 10)
        rb.inserir(20, 20)
        antes = rb.snapshot()
        rb.limpar_eventos()
        rb.inserir(30, 30)
        depois = rb.snapshot()
        marcar(antes, depois)
        estados = {depois["rotulo"]: depois["estado"]}
        for filho in depois["filhos"]:
            estados[filho["rotulo"]] = filho["estado"]
        self.assertEqual(estados, {"20": "alterado", "10": "alterado", "30": "novo"})
        self.assertEqual(resumo_ajustes(rb.eventos), {"rotação": 1, "recoloração": 2})

    def test_divisao_na_234_aparece_como_ajuste(self):
        from visual.rebalanceamento import marcar, resumo_ajustes
        t = Arvore234()
        for c in (10, 20, 30):
            t.inserir(c, c)
        antes = t.snapshot()
        t.limpar_eventos()
        t.inserir(40, 40)
        depois = t.snapshot()
        marcar(antes, depois)
        self.assertEqual(antes["estado"], "removido")
        self.assertEqual(depois["rotulo"], "20")
        self.assertIn("divisão de nó", resumo_ajustes(t.eventos))

    def test_insercao_sem_ajuste(self):
        from visual.rebalanceamento import resumo_ajustes
        rb = ArvoreRubroNegra()
        rb.inserir(10, 10)
        rb.limpar_eventos()
        rb.inserir(5, 5)
        self.assertEqual(resumo_ajustes(rb.eventos), {})

    def test_desenho_nao_sobrepoe_nos(self):
        from visual.arvore_svg import _posicionar, _todos
        rb, t, kd = ArvoreRubroNegra(), Arvore234(), ArvoreKD()
        for chave, valor in consultas_demo():
            rb.adicionar(chave, valor)
            t.adicionar(chave, valor)
        for nome, x, y in UBS_EXEMPLO:
            kd.inserir((x, y), nome)
        for arvore in (rb, t, kd):
            raiz = arvore.snapshot()
            _posicionar(raiz, 0, 0)
            niveis = {}
            for no in _todos(raiz, []):
                if not no.get("oculto"):
                    niveis.setdefault(no["_y"], []).append((no["_x"] - no["_w"] / 2, no["_x"] + no["_w"] / 2))
            for caixas in niveis.values():
                caixas.sort()
                for (_, fim), (inicio, _) in zip(caixas, caixas[1:]):
                    self.assertGreaterEqual(inicio - fim, 5)

    def test_desenho_gera_svg_para_as_tres_arvores(self):
        from visual.arvore_svg import arvore_svg
        rb, t, kd = ArvoreRubroNegra(), Arvore234(), ArvoreKD()
        for c in range(1, 30):
            rb.inserir(c, c)
            t.inserir(c, c)
            kd.inserir((c % 7, c // 7), f"P{c}")
        for arvore in (rb, t, kd):
            self.assertIn("<svg", arvore_svg(arvore.snapshot()))
        self.assertIn("vazia", arvore_svg(None))


class TestesMapa(unittest.TestCase):
    def test_mapa_e_deterministico_e_contem_unidades(self):
        from mapa.cidade import cidade_svg
        unidades = [("UBS Centro", (2.0, 3.0)), ("UBS Teste", (8.0, 9.0))]
        a = cidade_svg(unidades, paciente=(5.0, 6.0), rotas=[(4.2, "UBS Centro", (2.0, 3.0))])
        b = cidade_svg(unidades, paciente=(5.0, 6.0), rotas=[(4.2, "UBS Centro", (2.0, 3.0))])
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("<svg"))
        self.assertIn("UBS Centro", a)
        self.assertIn("4,2 km", a)


if __name__ == "__main__":
    unittest.main()
