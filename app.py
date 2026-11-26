"""Agenda UBS: pacientes, consultas e unidades de saúde mais próximas.

Cada página tem três abas:
  uso do sistema · Árvore (busca passo a passo, antes e depois) · Implementação (nós e ponteiros)
"""

import re
from datetime import date, timedelta

import matplotlib.pyplot as plt
import streamlit as st

from arvores.arvore_234 import Arvore234
from arvores.bst import ArvoreBinariaSimples
from arvores.kdtree import ArvoreKD, esquema_kd, implementacao_kd
from arvores.rubro_negra import ArvoreRubroNegra
from dados.demo import (
    UBS_EXEMPLO,
    chave_horario,
    consultas_demo,
    horario_curto,
    horario_no,
    pacientes_com_endereco,
)
from mapa.cidade import cidade_svg, legenda_html
from visual import estilo
from visual.arvore_svg import arvore_svg, legenda
from visual.rebalanceamento import (
    TIPOS_DE_AJUSTE,
    descrever_ajustes,
    marcar,
    marcar_caminho,
    resumo_ajustes,
)

st.set_page_config(page_title="Agenda UBS", page_icon=":material/local_hospital:", layout="wide")
st.markdown(estilo.CSS, unsafe_allow_html=True)

ESTRUTURAS = ["Rubro-Negra", "2-3-4"]
INICIO = ":material/home: Início"
PACIENTES = ":material/group: Pacientes"
AGENDA = ":material/calendar_month: Agenda"
UNIDADES = ":material/map: Unidades de saúde"
COMPARACAO = ":material/bar_chart: Comparação"
PAGINAS = [INICIO, PACIENTES, AGENDA, UNIDADES, COMPARACAO]
DATA_EXEMPLO = date(2026, 11, 25)
HORARIOS = [(h, m) for h in range(7, 19) for m in (0, 30)]
ABA_ARVORE = ":material/account_tree: Árvore"
ABA_IMPLEMENTACAO = ":material/data_object: Implementação"


# ======================================================================
# Estado
# ======================================================================
def obter(chave, construir):
    if chave not in st.session_state:
        st.session_state[chave] = construir()
    return st.session_state[chave]


def criar_agenda(tipo):
    return ArvoreRubroNegra() if tipo == "Rubro-Negra" else Arvore234()


def obter_agenda(tipo):
    """Agenda no tipo escolhido.

    As duas árvores ficam sempre prontas e recebem as mesmas operações, na mesma ordem.
    Trocar só muda qual aparece: copiar os dados na troca reinseriria tudo em ordem de
    horário, o pior caso, e a Rubro-Negra ficaria torta para a direita.
    """
    if "agendas" not in st.session_state:
        st.session_state["agendas"] = {t: criar_agenda(t) for t in ESTRUTURAS}
    agendas = st.session_state["agendas"]
    if st.session_state.get("agenda_tipo") != tipo:
        st.session_state.pop("op_agenda", None)
    st.session_state["agenda_tipo"] = tipo
    st.session_state["agenda"] = agendas[tipo]
    return agendas[tipo]


def mudar_agenda(descricao, mudanca):
    """Aplica a mudança na árvore que aparece (com antes e depois) e na outra, em silêncio."""
    tipo = st.session_state["agenda_tipo"]
    ajustes = operar("agenda", obter_agenda(tipo), descricao,
                     lambda: mudanca(obter_agenda(tipo)), horario_no)
    for outro, arvore in st.session_state["agendas"].items():
        if outro != tipo:
            mudanca(arvore)
            arvore.limpar_eventos()
    return ajustes


def limpar_operacoes():
    for chave in ("op_pacientes", "op_agenda", "op_unidades", "mensagem",
                  "busca_pacientes", "busca_agenda", "busca_unidades"):
        st.session_state.pop(chave, None)


def carregar_exemplo(tipo):
    pacientes = Arvore234()
    for prontuario, dados in pacientes_com_endereco():
        pacientes.inserir(prontuario, dados)
    agendas = {t: criar_agenda(t) for t in ESTRUTURAS}
    for chave, item in consultas_demo():
        for agenda in agendas.values():
            agenda.adicionar(chave, item)
    unidades = ArvoreKD()
    for nome, x, y in UBS_EXEMPLO:
        unidades.inserir((x, y), nome)
    for arvore in (pacientes, unidades, *agendas.values()):
        arvore.limpar_eventos()
    st.session_state.update(pacientes=pacientes, agendas=agendas, unidades=unidades)
    obter_agenda(tipo)
    limpar_operacoes()


def trocar_estrutura():
    """Troca a árvore da agenda. Clicar na opção já marcada não desmarca."""
    novo = st.session_state["tipo_agenda"]
    if novo is None:
        st.session_state["tipo_agenda"] = st.session_state["agenda_tipo"]
    else:
        obter_agenda(novo)


def apagar_tudo(tipo):
    st.session_state.update(
        pacientes=Arvore234(), agendas={t: criar_agenda(t) for t in ESTRUTURAS}, unidades=ArvoreKD()
    )
    obter_agenda(tipo)
    limpar_operacoes()


def ir_para(pagina):
    st.session_state["menu"] = pagina


def mudar_dia(dias):
    st.session_state["a_dia"] += timedelta(days=dias)


# ======================================================================
# Operações com antes e depois
# ======================================================================
def retrato(arvore, formatar):
    return arvore.snapshot(formatar) if formatar is not None else arvore.snapshot()


def operar(nome, arvore, descricao, acao, formatar=None):
    """Executa a ação e guarda o retrato da árvore antes e depois, com os passos."""
    antes = retrato(arvore, formatar)
    arvore.limpar_eventos()
    acao()
    depois = retrato(arvore, formatar)
    marcar(antes, depois)
    ajustes = resumo_ajustes(arvore.eventos)
    st.session_state[f"op_{nome}"] = {
        "descricao": descricao,
        "antes": antes,
        "depois": depois,
        "eventos": list(arvore.eventos),
        "ajustes": ajustes,
    }
    st.session_state.pop(f"busca_{nome}", None)
    return ajustes


def concluir(texto, ajustes, tipo="sucesso"):
    """Guarda a mensagem e recarrega a página, para a tela já mostrar os dados novos."""
    st.session_state["mensagem"] = (texto, ajustes, tipo)
    st.rerun()


def mostrar_mensagem():
    if "mensagem" not in st.session_state:
        return
    texto, ajustes, tipo = st.session_state.pop("mensagem")
    (st.success if tipo == "sucesso" else st.info)(texto)
    if ajustes:
        st.markdown(
            '<div class="aviso-arvore">A árvore se rebalanceou nesta operação '
            f"({estilo.escape(descrever_ajustes(ajustes))}). "
            "Veja o antes e o depois na aba <b>Árvore</b>.</div>",
            unsafe_allow_html=True,
        )


def texto_legivel(eventos, formatar):
    """Troca chaves internas (ex.: 202611250930) por texto legível nos passos."""
    if formatar is None:
        return list(eventos)
    return [re.sub(r"\b\d{12}\b", lambda m: formatar(int(m.group())), e) for e in eventos]


# ======================================================================
# Abas Árvore e Implementação
# ======================================================================
def desenhar(raiz, ajustar):
    st.markdown(arvore_svg(raiz, ajustar), unsafe_allow_html=True)


def aba_arvore(nome, arvore, estilos, explicacao, buscar, formatar=None, formatar_no=None, observacao=""):
    """buscar() desenha o campo de busca e devolve (visitados, passos, achou), ou None."""
    st.caption(explicacao)
    op = st.session_state.get(f"op_{nome}")

    c1, c2 = st.columns([3, 2], vertical_alignment="bottom")
    with c1:
        busca = buscar() if len(arvore) else None
    with c2:
        ajustar = st.segmented_control(
            "Tamanho do desenho", ["Caber na tela", "Tamanho real"], default="Caber na tela",
            key=f"tamanho_{nome}",
        ) != "Tamanho real"

    if busca is not None:
        visitados, passos, achou = busca
        desenho = retrato(arvore, formatar_no)
        marcar_caminho(desenho, visitados, achou)
        st.markdown(
            estilo.operacao(
                f"{'Encontrado' if achou else 'Não encontrado'} em {len(visitados)} nó(s) visitado(s)",
                f"A árvore tem {arvore.altura()} níveis. A busca desce um nível por vez.", False)
            + legenda(estilos, ["caminho", "achado"]) + estilo.passos(passos),
            unsafe_allow_html=True,
        )
        desenhar(desenho, ajustar)
        return

    if op is None:
        st.markdown(legenda(estilos), unsafe_allow_html=True)
        desenhar(retrato(arvore, formatar_no), ajustar)
        if len(arvore):
            st.caption("Faça uma busca acima, ou adicione e remova algo, para ver o passo a passo aqui.")
        return

    eventos = texto_legivel(op["eventos"], formatar)
    if op["ajustes"]:
        titulo = f"Houve rebalanceamento: {descrever_ajustes(op['ajustes'])}"
    else:
        titulo = "Sem rebalanceamento nesta operação"
        if observacao:
            titulo += f". {observacao}"
    destacados = [i for i, e in enumerate(eventos) if any(p in e for p in TIPOS_DE_AJUSTE)]

    c1, c2 = st.columns([5, 1], vertical_alignment="center")
    c1.markdown(estilo.operacao(titulo, f"Última operação: {op['descricao']}", bool(op["ajustes"])),
                unsafe_allow_html=True)
    if c2.button("Fechar", key=f"fechar_{nome}", icon=":material/close:", width="stretch"):
        st.session_state.pop(f"op_{nome}", None)
        st.rerun()
    st.markdown(estilo.passos(eventos, destacados) if eventos else "", unsafe_allow_html=True)
    st.markdown(legenda(estilos, ["novo", "alterado", "removido"]), unsafe_allow_html=True)
    st.markdown('<div class="rotulo-fase">Antes</div>', unsafe_allow_html=True)
    desenhar(op["antes"], ajustar)
    st.markdown('<div class="rotulo-fase">Depois</div>', unsafe_allow_html=True)
    desenhar(op["depois"], ajustar)


def aba_implementacao(arvore, titulo, linhas, esquema, explicacao):
    st.caption(explicacao)
    ok, erros = arvore.validar()
    if not ok:
        st.error("Problemas encontrados: " + "; ".join(erros))
    if not linhas:
        st.info("A estrutura está vazia.")
        return
    if ok:
        st.success(f"{titulo}: {len(linhas)} nós, {arvore.altura()} níveis. Todas as regras conferidas.")
    st.dataframe(linhas, hide_index=True)
    with st.expander("Esquema em texto"):
        st.code(esquema, language=None)


# ======================================================================
# Páginas
# ======================================================================
def vitrine(tipo):
    """Dados que ilustram a página inicial: os atuais ou, se não houver, os de exemplo."""
    agenda = st.session_state["agenda"]
    if not len(agenda):
        agenda = criar_agenda(tipo)
        for chave, item in consultas_demo():
            agenda.adicionar(chave, item)
    pacientes = obter("pacientes", Arvore234).em_ordem() or sorted(pacientes_com_endereco(), key=lambda p: p[0])
    unidades = [(n.dados, n.ponto) for n in obter("unidades", ArvoreKD).todos()]
    if not unidades:
        unidades = [(nome, (x, y)) for nome, x, y in UBS_EXEMPLO]
    return agenda, pacientes, unidades


def previa_pacientes(pacientes):
    """Uma 2-3-4 pequena, com alguns prontuários reais da lista."""
    arvore = Arvore234()
    for prontuario, _ in pacientes[:8]:
        arvore.inserir(prontuario, None)
    return estilo.previa_desenho(arvore_svg(arvore.snapshot(), quadro=False))


def previa_agenda(agenda):
    itens = [(horario_curto(chave)[-5:], item["paciente"], horario_curto(chave)[:5])
             for chave, lista in agenda.em_ordem() for item in lista]
    return estilo.previa_lista(itens[:3])


def previa_unidades(pontos):
    """Uma faixa da cidade, recortada no meio das ruas e sem ícones partidos na borda."""
    x0, y0, x1, y1 = recorte = (0.0, 5.0, 20.0, 12.5)
    inteiros = [(nome, (x, y)) for nome, (x, y) in pontos
                if x0 + 0.5 <= x <= x1 - 0.5 and y0 + 0.5 <= y <= y1 - 0.5]
    return estilo.previa_mapa(cidade_svg(inteiros, recorte=recorte))


def cartao_inicio(chave, titulo, texto, previa, pagina):
    with st.container(key=f"cartao_{chave}"):
        st.markdown(estilo.resumo(titulo, texto), unsafe_allow_html=True)
        st.button(f"Abrir {titulo.lower()}", key=f"ir_{chave}", on_click=ir_para, args=(pagina,),
                  icon=":material/arrow_forward:", icon_position="right")
        st.markdown(previa, unsafe_allow_html=True)


def pagina_inicio(tipo):
    pacientes = obter("pacientes", Arvore234)
    unidades = obter("unidades", ArvoreKD)
    agenda, lista, pontos = vitrine(tipo)
    vazio = not (len(pacientes) or len(unidades) or len(st.session_state["agenda"]))

    with st.container(key="abertura"):
        texto, desenho = st.columns([5, 7], gap="large", vertical_alignment="center")
        with texto.container(key="abertura_texto"):
            st.markdown(estilo.abertura(
                "A agenda da UBS em árvores balanceadas",
                "Cadastre pacientes, marque consultas e encontre a unidade mais próxima. "
                "Cada busca percorre uma árvore escrita do zero.",
            ), unsafe_allow_html=True)
            if vazio:
                with st.container(horizontal=True):
                    if st.button("Carregar exemplo", key="exemplo_inicio", type="primary"):
                        carregar_exemplo(tipo)
                        st.rerun()
                    st.button("Novo paciente", key="ir_cadastro", on_click=ir_para, args=(PACIENTES,))
            else:
                st.button("Marcar consulta", key="ir_marcar", type="primary", on_click=ir_para, args=(AGENDA,))
        with desenho:
            st.markdown(estilo.tela(
                f"Agenda em árvore {tipo}", f"{len(agenda)} nós, {agenda.altura()} níveis",
                arvore_svg(agenda.snapshot(horario_no), quadro=False, animar=True),
            ), unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        cartao_inicio("pacientes", "Pacientes",
                      f"{len(pacientes) or 'Os'} cadastros em uma árvore 2-3-4, pelo número do prontuário.",
                      previa_pacientes(lista), PACIENTES)
        cartao_inicio("unidades", "Unidades de saúde",
                      f"{len(unidades) or 'As'} unidades em uma árvore k-D, para achar a mais perto do paciente.",
                      previa_unidades(pontos), UNIDADES)
    with c2:
        total = sum(len(v) for _, v in st.session_state["agenda"].em_ordem())
        cartao_inicio("agenda", "Agenda",
                      f"{total or 'As'} consultas em uma árvore {tipo}, sempre em ordem de horário.",
                      previa_agenda(agenda), AGENDA)
        cartao_inicio("comparacao", "Comparação",
                      "A altura da árvore comum e das balanceadas com as mesmas 100 chaves.",
                      estilo.previa_barras([("Binária", 100, True), ("Rubro-Negra", 11, False), ("2-3-4", 6, False)]),
                      COMPARACAO)


def formulario_paciente(arvore):
    # A chave muda a cada cadastro salvo, para o formulário voltar limpo e com o próximo número.
    versao = obter("p_versao", lambda: 0)
    st.subheader("Novo paciente")
    nome = st.text_input("Nome completo", key=f"p_nome_{versao}", placeholder="Maria Silva").strip()
    lista = arvore.em_ordem()
    sugestao = min(lista[-1][0] + 1, 99999) if lista else 10001
    prontuario = int(st.number_input(
        "Número do prontuário", min_value=10000, max_value=99999, value=sugestao, step=1,
        key=f"p_num_{versao}",
    ))
    c1, c2 = st.columns(2)
    x = c1.number_input("Endereço x (km)", 0.0, 20.0, 5.0, 0.5, key=f"p_x_{versao}")
    y = c2.number_input("Endereço y (km)", 0.0, 20.0, 5.0, 0.5, key=f"p_y_{versao}")

    atual = arvore.buscar(prontuario)
    substituir = False
    if atual is not None:
        st.warning(f"O prontuário {prontuario} já é de {atual['nome']}.")
        substituir = st.checkbox("Atualizar esse cadastro", key=f"p_atualizar_{versao}")

    rotulo = "Salvar paciente" if atual is None else "Atualizar cadastro"
    if st.button(rotulo, type="primary", key="p_salvar", width="stretch",
                 disabled=atual is not None and not substituir):
        if not nome:
            st.error("Digite o nome do paciente.")
            return
        acao = "Cadastro" if atual is None else "Atualização"
        ajustes = operar(
            "pacientes", arvore, f"{acao} de {nome} (prontuário {prontuario})",
            lambda: arvore.inserir(prontuario, {"nome": nome, "x": x, "y": y}),
        )
        st.session_state["p_versao"] += 1
        concluir(f"{nome} {'salvo' if atual is None else 'atualizado'} com o prontuário {prontuario}.", ajustes)


def consultas_do_paciente(agenda, prontuario):
    return [(chave, item) for chave, lista in agenda.em_ordem()
            for item in lista if item["prontuario"] == prontuario]


def remover_paciente(arvore, agenda, prontuario, nome, consultas):
    ajustes = operar("pacientes", arvore, f"Remoção de {nome} (prontuário {prontuario})",
                     lambda: arvore.remover(prontuario))
    if consultas:
        mudar_agenda(
            f"Cancelamento de {len(consultas)} consulta(s) de {nome}",
            lambda a: [a.remover_valor(chave, item) for chave, item in consultas],
        )
    extra = f" {len(consultas)} consulta(s) também cancelada(s)." if consultas else ""
    concluir(f"{nome} removido.{extra}", ajustes)


def pagina_pacientes(tipo):
    arvore = obter("pacientes", Arvore234)
    agenda = obter_agenda(tipo)
    st.markdown(estilo.topo("Pacientes", "Cadastro organizado pelo número do prontuário.", "Árvore 2-3-4"),
                unsafe_allow_html=True)
    uso, aba_arv, aba_impl = st.tabs(["Cadastro", ABA_ARVORE, ABA_IMPLEMENTACAO])

    with uso:
        mostrar_mensagem()
        esquerda, direita = st.columns([2, 3])
        with esquerda.container(border=True, key="painel_cadastro"):
            formulario_paciente(arvore)
        with direita.container(border=True, key="painel_lista"):
            st.subheader(f"Pacientes cadastrados ({len(arvore)})")
            lista = arvore.em_ordem()
            if not lista:
                st.info("Nenhum paciente cadastrado. Preencha o formulário ao lado.")
            else:
                termo = st.text_input("Buscar por prontuário ou nome", key="p_busca",
                                      placeholder="Prontuário completo ou parte do nome").strip()
                if termo.isdigit() and len(termo) == 5:
                    # Prontuário completo: busca direta na árvore, sem percorrer a lista.
                    dados = arvore.buscar(int(termo))
                    lista = [(int(termo), dados)] if dados else []
                elif termo:
                    lista = [(p, d) for p, d in lista
                             if termo.lower() in d["nome"].lower() or termo in str(p)]
                if not lista:
                    st.info(f"Nenhum paciente encontrado para “{termo}”.")
                else:
                    st.dataframe(
                        [{"Prontuário": p, "Nome": d["nome"], "Endereço (km)": f"{d['x']:g}, {d['y']:g}"}
                         for p, d in lista],
                        hide_index=True, height=min(38 + 35 * len(lista), 290),
                        column_config={"Prontuário": st.column_config.NumberColumn(format="%d", width="small")},
                    )
                    opcoes = {p: d["nome"] for p, d in lista}
                    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
                    p = c1.selectbox("Remover paciente", list(opcoes), key="p_remover_escolha",
                                     format_func=lambda n: f"{opcoes.get(n, '')} ({n})")
                    consultas = consultas_do_paciente(agenda, p)
                    if c2.button("Remover", key="p_remover", icon=":material/delete:", width="stretch"):
                        remover_paciente(arvore, agenda, p, opcoes[p], consultas)
                    if consultas:
                        st.caption(f"Remover {opcoes[p]} também cancela {len(consultas)} consulta(s) na agenda.")

    with aba_arv:
        def buscar():
            termo = st.text_input("Buscar um prontuário na árvore", key="busca_pacientes",
                                  placeholder="Digite o número e tecle Enter").strip()
            return arvore.passos_busca(int(termo)) if termo.isdigit() else None

        aba_arvore(
            "pacientes", arvore, ["azul"],
            "Cada caixa é um nó com 1 a 3 prontuários. Nó cheio se divide e a chave do meio sobe. "
            "Na remoção, o nó com uma só chave pega emprestado do irmão ou se funde com ele.",
            buscar,
        )
    with aba_impl:
        aba_implementacao(
            arvore, "Árvore 2-3-4", arvore.implementacao(), arvore.esquema(),
            "Cada nó guarda suas chaves, os ponteiros para os filhos e o ponteiro para o pai.",
        )


def marcar_consulta(arvore, pacientes):
    st.subheader("Marcar consulta")
    if not pacientes:
        st.info("Cadastre um paciente antes de marcar consultas.")
        st.button("Ir para Pacientes", key="a_ir_pacientes", on_click=ir_para, args=(PACIENTES,))
        return
    nomes = {p: d["nome"] for p, d in pacientes}
    prontuario = st.selectbox("Paciente", list(nomes), key="a_paciente",
                              format_func=lambda n: f"{nomes.get(n, '')} ({n})")
    c1, c2 = st.columns(2)
    data = c1.date_input("Data", value=DATA_EXEMPLO, key="a_data", format="DD/MM/YYYY")

    def rotulo(hm):
        marcadas = len(arvore.buscar(chave_horario(data, *hm)) or [])
        return f"{hm[0]:02d}:{hm[1]:02d}" + (f" ({marcadas})" if marcadas else "")

    hora, minuto = c2.selectbox("Horário", HORARIOS, index=HORARIOS.index((9, 0)), key="a_hora",
                                format_func=rotulo)
    if st.button("Marcar consulta", type="primary", key="a_marcar", width="stretch"):
        chave = chave_horario(data, hora, minuto)
        existentes = arvore.buscar(chave) or []
        if any(item["prontuario"] == prontuario for item in existentes):
            st.error(f"{nomes[prontuario]} já tem consulta em {horario_curto(chave)}.")
            return
        ajustes = mudar_agenda(
            f"Consulta de {nomes[prontuario]} em {horario_curto(chave)}",
            lambda a: a.adicionar(chave, {"prontuario": prontuario, "paciente": nomes[prontuario]}),
        )
        extra = " O horário já existia: ela entrou na lista do mesmo nó." if existentes else ""
        st.session_state["a_dia"] = data
        concluir(f"Consulta marcada para {data:%d/%m} às {hora:02d}:{minuto:02d}.{extra}", ajustes)


def consultas_do_dia(arvore):
    st.subheader("Consultas do dia")
    c1, c2, c3 = st.columns([1, 3, 1], vertical_alignment="bottom")
    c1.button("Anterior", key="a_ant", on_click=mudar_dia, args=(-1,), width="stretch")
    dia = c2.date_input("Dia", key="a_dia", format="DD/MM/YYYY", label_visibility="collapsed")
    c3.button("Próximo", key="a_prox", on_click=mudar_dia, args=(1,), width="stretch")

    consultas = [(chave, item)
                 for chave, lista in arvore.intervalo(chave_horario(dia, 0, 0), chave_horario(dia, 23, 59))
                 for item in lista]
    if not consultas:
        st.info(f"Nenhuma consulta em {dia:%d/%m/%Y}.")
        return
    st.caption(f"{len(consultas)} consulta(s) em {dia:%d/%m/%Y}")
    for chave, item in consultas:
        c1, c2 = st.columns([4, 1], vertical_alignment="center")
        c1.markdown(estilo.consulta(horario_curto(chave)[-5:], item["paciente"],
                                    f"Prontuário {item['prontuario']}"), unsafe_allow_html=True)
        if c2.button("Cancelar", key=f"a_cancelar_{chave}_{item['prontuario']}", width="stretch"):
            ajustes = mudar_agenda(
                f"Cancelamento de {item['paciente']} em {horario_curto(chave)}",
                lambda a: a.remover_valor(chave, item),
            )
            concluir(f"Consulta de {item['paciente']} cancelada.", ajustes)


def pagina_agenda(tipo):
    arvore = obter_agenda(tipo)
    obter("a_dia", lambda: DATA_EXEMPLO)
    cabecalho, escolha = st.columns([3, 2], vertical_alignment="bottom")
    cabecalho.markdown(estilo.topo("Agenda", "Consultas em ordem de data e horário."), unsafe_allow_html=True)
    with escolha.container(key="escolha_estrutura"):
        obter("tipo_agenda", lambda: tipo)
        st.segmented_control(
            "Árvore da agenda", ESTRUTURAS, key="tipo_agenda", on_change=trocar_estrutura,
            help="As duas árvores guardam a mesma agenda e recebem as mesmas operações. Trocar só muda qual aparece.",
        )
    uso, aba_arv, aba_impl = st.tabs(["Consultas", ABA_ARVORE, ABA_IMPLEMENTACAO])

    with uso:
        mostrar_mensagem()
        esquerda, direita = st.columns([2, 3])
        with esquerda.container(border=True, key="painel_marcar"):
            marcar_consulta(arvore, obter("pacientes", Arvore234).em_ordem())
        with direita.container(border=True, key="painel_dia"):
            consultas_do_dia(arvore)

    with aba_arv:
        def buscar():
            chave = st.selectbox(
                "Buscar um horário na árvore", [c for c, _ in arvore.em_ordem()], index=None,
                key="busca_agenda", format_func=horario_curto, placeholder="Escolha um horário",
            )
            return arvore.passos_busca(chave, horario_curto) if chave is not None else None

        if tipo == "Rubro-Negra":
            estilos = ["vermelho", "preto"]
            explicacao = ("Cada nó é um horário. Um vermelho nunca tem filho vermelho, e todo caminho até uma "
                          "folha tem o mesmo número de pretos. Quando uma regra quebra, a árvore recolore ou "
                          "rotaciona. A bolinha mostra quantas consultas há no mesmo horário.")
        else:
            estilos = ["azul"]
            explicacao = ("Cada nó guarda de 1 a 3 horários. Nó cheio se divide e a chave do meio sobe. "
                          "A bolinha mostra quantas consultas há no mesmo horário.")
        aba_arvore("agenda", arvore, estilos, explicacao, buscar, horario_curto, horario_no)
    with aba_impl:
        aba_implementacao(
            arvore, f"Agenda em {tipo}", arvore.implementacao(horario_curto), arvore.esquema(horario_curto),
            "Os nós são numerados por nível (N1 é a raiz). Os ponteiros mostram para qual nó cada um aponta.",
        )


def cadastro_unidades(unidades):
    with st.expander("Cadastrar ou remover unidade"):
        versao = obter("u_versao", lambda: 0)
        nome = st.text_input("Nome da unidade", key=f"u_nome_{versao}", placeholder="UBS Jardim").strip()
        c1, c2 = st.columns(2)
        x = c1.number_input("x (km)", 0.0, 20.0, 5.0, 0.5, key=f"u_x_{versao}")
        y = c2.number_input("y (km)", 0.0, 20.0, 5.0, 0.5, key=f"u_y_{versao}")
        if st.button("Cadastrar unidade", type="primary", key="u_cadastrar", width="stretch"):
            if not nome:
                st.error("Digite o nome da unidade.")
            elif any(n.dados.lower() == nome.lower() for n in unidades.todos()):
                st.error(f"Já existe uma unidade chamada {nome}.")
            else:
                ajustes = operar("unidades", unidades, f"Cadastro da {nome}",
                                 lambda: unidades.inserir((x, y), nome))
                st.session_state["u_versao"] += 1
                concluir(f"{nome} cadastrada em ({x:g}, {y:g}).", ajustes)
        if len(unidades):
            pontos = {n.dados: n.ponto for n in unidades.todos()}
            c1, c2 = st.columns([3, 2], vertical_alignment="bottom")
            alvo = c1.selectbox("Remover unidade", sorted(pontos), key="u_remover_escolha")
            if c2.button("Remover", key="u_remover", icon=":material/delete:", width="stretch"):
                ajustes = operar("unidades", unidades, f"Remoção da {alvo}",
                                 lambda: unidades.remover(pontos[alvo], alvo))
                concluir(f"{alvo} removida.", ajustes)


def pagina_unidades():
    unidades = obter("unidades", ArvoreKD)
    pacientes = obter("pacientes", Arvore234).em_ordem()
    st.markdown(estilo.topo("Unidades de saúde", "Escolha um paciente e veja as unidades mais próximas da casa dele.",
                            "Árvore k-D"), unsafe_allow_html=True)
    uso, aba_arv, aba_impl = st.tabs(["Mapa", ABA_ARVORE, ABA_IMPLEMENTACAO])

    with uso:
        mostrar_mensagem()
        esquerda, direita = st.columns([2, 3])
        ponto, resultado = None, []
        with esquerda:
            with st.container(border=True, key="painel_proxima"):
                st.subheader("Unidade mais próxima")
                if not pacientes:
                    st.info("Cadastre pacientes para encontrar a unidade mais próxima.")
                else:
                    dados = dict(pacientes)
                    p = st.selectbox("Paciente", list(dados), key="u_paciente",
                                     format_func=lambda n: f"{dados[n]['nome']} ({n})" if n in dados else str(n))
                    ponto = (dados[p]["x"], dados[p]["y"])
                    quantas = st.slider("Quantas unidades mostrar", 1, 5, 3, key="u_quantas")
                    if len(unidades):
                        resultado = unidades.k_mais_proximos(ponto, quantas)
                        st.markdown("".join(
                            estilo.unidade(i + 1, no.dados, d, i == 0) for i, (d, no) in enumerate(resultado)
                        ), unsafe_allow_html=True)
                    else:
                        st.info("Cadastre unidades de saúde para ver o resultado.")
            cadastro_unidades(unidades)
        with direita:
            svg = cidade_svg(
                [(n.dados, n.ponto) for n in unidades.todos()],
                paciente=ponto,
                rotas=[(d, no.dados, no.ponto) for d, no in resultado],
                pacientes=[(d["x"], d["y"]) for _, d in pacientes],
            )
            st.markdown(f'<div class="mapa">{svg}</div>' + legenda_html(), unsafe_allow_html=True)

    with aba_arv:
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
        c1.markdown(f'<div class="aviso-arvore">Altura atual: <b>{unidades.altura()}</b> níveis '
                    f"com {len(unidades)} unidades.</div>", unsafe_allow_html=True)
        if c2.button("Reorganizar (balancear)", key="u_balancear", type="primary", width="stretch",
                     disabled=not len(unidades)):
            itens = [(n.ponto, n.dados) for n in unidades.todos()]
            operar("unidades", unidades, "Reorganização pela mediana",
                   lambda: unidades.construir_balanceada(itens))
            st.rerun()

        def buscar():
            pontos = {n.dados: n.ponto for n in unidades.todos()}
            nome = st.selectbox("Buscar uma unidade na árvore", sorted(pontos), index=None,
                                key="busca_unidades", placeholder="Escolha uma unidade")
            return unidades.passos_busca(pontos[nome], nome) if nome else None

        aba_arvore(
            "unidades", unidades, ["kd_x", "kd_y"],
            "Cada nível divide o mapa por uma coordenada, alternando x e y: menores à esquerda, maiores ou "
            "iguais à direita. A k-D não se rebalanceia sozinha; Reorganizar a reconstrói pela mediana.",
            buscar, observacao="A k-D não se rebalanceia sozinha; use Reorganizar",
        )
    with aba_impl:
        aba_implementacao(
            unidades, "Árvore k-D", implementacao_kd(unidades), esquema_kd(unidades),
            "Cada nó guarda um ponto (x, y), o eixo de corte e os ponteiros esquerdo, direito e pai.",
        )


def pagina_comparacao():
    st.markdown(estilo.topo(
        "Por que balancear?",
        "Altura das árvores com as mesmas chaves inseridas em ordem crescente, o pior caso da binária comum.",
    ), unsafe_allow_html=True)

    n = st.slider("Quantidade de chaves", 21, 300, 100, key="c_n")
    bst, rb, t234 = ArvoreBinariaSimples(), ArvoreRubroNegra(), Arvore234()
    for c in range(1, n + 1):
        bst.inserir(c)
        rb.inserir(c, c)
        t234.adicionar(c, c)
    alturas = {"Binária comum": bst.altura(), "Rubro-Negra": rb.altura(), "2-3-4": t234.altura()}

    with st.container(border=True, key="painel_altura"):
        st.subheader(f"Altura com {n} chaves")
        fig, ax = plt.subplots(figsize=(9, 2.4))
        barras = ax.barh(list(alturas)[::-1], list(alturas.values())[::-1],
                         color=["#0d7480", "#0d7480", "#b3c1c6"], height=0.5)
        ax.bar_label(barras, labels=[f"{v} níveis" for v in list(alturas.values())[::-1]],
                     padding=5, fontsize=10, color="#1f3038")
        ax.set_xlim(0, max(alturas.values()) * 1.12)
        for lado in ("top", "right", "bottom", "left"):
            ax.spines[lado].set_visible(False)
        ax.tick_params(left=False, bottom=False, labelbottom=False, labelsize=10, labelcolor="#1f3038")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Em ordem crescente, a binária comum vira uma lista: cada chave fica à direita da anterior, "
                   "e a altura é igual ao número de chaves.")

    st.subheader("Como cada árvore se equilibra")
    st.table([
        {"Árvore": "Rubro-Negra", "Quando age": "A cada inserção ou remoção que quebra uma regra de cor",
         "Como age": "Recoloração e rotações", "Altura máxima": "2 · log₂(n + 1)"},
        {"Árvore": "2-3-4", "Quando age": "Ao descer por um nó cheio (inserção) ou com uma só chave (remoção)",
         "Como age": "Divisão, empréstimo e fusão de nós", "Altura máxima": "log₂(n + 1)"},
        {"Árvore": "k-D", "Quando age": "Só quando se pede a reorganização",
         "Como age": "Reconstrução pela mediana, alternando x e y",
         "Altura máxima": "n (sem reorganizar)"},
    ])


# ======================================================================
# Barra lateral e navegação
# ======================================================================
with st.sidebar:
    st.markdown(estilo.marca(), unsafe_allow_html=True)
    pagina = st.radio("Menu", PAGINAS, label_visibility="collapsed", key="menu")
    st.divider()
    tipo = obter("agenda_tipo", lambda: ESTRUTURAS[0])
    if st.button("Carregar dados de exemplo", key="exemplo", icon=":material/download:", width="stretch",
                 help="Substitui os dados atuais pelos de exemplo."):
        carregar_exemplo(tipo)
        st.rerun()
    with st.popover("Apagar tudo", icon=":material/delete:", width="stretch"):
        st.write("Apagar todos os pacientes, consultas e unidades?")
        if st.button("Sim, apagar", key="apagar", type="primary"):
            apagar_tudo(tipo)
            st.rerun()
    st.caption("Dados fictícios, apenas para demonstração.")

obter_agenda(tipo)
if pagina == INICIO:
    pagina_inicio(tipo)
elif pagina == PACIENTES:
    pagina_pacientes(tipo)
elif pagina == AGENDA:
    pagina_agenda(tipo)
elif pagina == UNIDADES:
    pagina_unidades()
else:
    pagina_comparacao()
