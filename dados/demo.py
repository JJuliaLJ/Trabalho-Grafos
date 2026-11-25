"""Dados fictícios para demonstração."""

import random
from datetime import date

NOMES_PACIENTES = [
    "Ana Souza", "Bruno Lima", "Carla Mendes", "Diego Rocha", "Elisa Nunes",
    "Felipe Costa", "Gabriela Reis", "Hugo Barros", "Irene Alves", "João Pires",
    "Karen Matos", "Lucas Ferreira", "Marta Dias", "Nelson Gomes", "Olívia Pinto",
    "Paulo Teixeira", "Quésia Moura", "Rafael Araújo", "Sofia Ribeiro", "Tiago Melo",
    "Úrsula Campos", "Vinícius Cunha", "Wesley Correia", "Yasmin Freitas", "Zélia Lopes",
]

UBS_EXEMPLO = [
    ("UBS Centro", 2.0, 3.0),
    ("UBS Vila Norte", 8.5, 9.0),
    ("UBS Bela Vista", 4.0, 7.5),
    ("UBS Jardim Leste", 12.0, 2.5),
    ("UBS Parque Sul", 6.0, 1.0),
    ("UBS Morro Alto", 14.0, 11.0),
    ("UBS Vale Verde", 10.0, 6.0),
    ("UBS Porto", 1.2, 11.0),
    ("UBS Horizonte", 17.5, 6.2),
    ("UBS Ipê", 6.3, 14.0),
    ("UBS Lagoa", 11.2, 13.8),
    ("UBS Santa Rita", 15.8, 16.5),
    ("UBS Nova Era", 3.1, 17.2),
    ("UBS Estação", 8.8, 18.0),
    ("UBS Mirante", 18.6, 12.6),
    ("UBS Campo Belo", 16.2, 1.1),
    ("UBS Aurora", 13.1, 18.9),
    ("UBS Palmeiras", 19.2, 18.2),
    ("UBS Ribeira", 0.8, 14.4),
    ("UBS Cedro", 12.8, 7.9),
    ("UBS Boa Vista", 9.1, 0.8),
    ("UBS Pedreira", 18.9, 3.4),
    ("UBS Marambaia", 5.2, 10.9),
    ("UBS Guamá", 16.6, 9.0),
]


def chave_horario(data, hora, minuto):
    """Transforma data e horário em um inteiro ordenável: AAAAMMDDHHMM."""
    return int(f"{data:%Y%m%d}{hora:02d}{minuto:02d}")


def horario_curto(chave):
    """Versão curta para os nós da árvore: 25/11 09:00."""
    texto = str(chave)
    return f"{texto[6:8]}/{texto[4:6]} {texto[8:10]}:{texto[10:12]}"


def horario_no(chave):
    """Versão em duas linhas, para caber dentro do nó desenhado."""
    return horario_curto(chave).replace(" ", "\n")


def pacientes_demo():
    """Lista de (prontuário, nome) em ordem aleatória, para testar a inserção."""
    rnd = random.Random(7)
    prontuarios = rnd.sample(range(10001, 99999), len(NOMES_PACIENTES))
    pares = list(zip(prontuarios, NOMES_PACIENTES))
    rnd.shuffle(pares)
    return pares


def consultas_demo():
    """Lista de (chave_horario, valor) com 24 horários distintos e 2 horários repetidos."""
    rnd = random.Random(11)
    pacientes = pacientes_demo()
    dias = [date(2026, 11, 25), date(2026, 11, 26), date(2026, 11, 27)]
    slots = [(d, h, m) for d in dias for h in range(8, 17) for m in (0, 30)]
    escolhidos = rnd.sample(slots, 24)

    consultas = []
    for i, (d, h, m) in enumerate(escolhidos):
        prontuario, nome = pacientes[i % len(pacientes)]
        consultas.append((chave_horario(d, h, m), {"prontuario": prontuario, "paciente": nome}))

    # Dois horários com mais de uma consulta: mostram o balde da Rubro-Negra.
    for d, h, m in escolhidos[:2]:
        prontuario, nome = pacientes[(len(consultas) + 3) % len(pacientes)]
        consultas.append((chave_horario(d, h, m), {"prontuario": prontuario, "paciente": nome}))

    rnd.shuffle(consultas)
    return consultas


def pacientes_com_endereco():
    """(prontuário, {nome, x, y}) com uma localização fictícia em km para cada paciente."""
    rnd = random.Random(21)
    saida = []
    for prontuario, nome in pacientes_demo():
        saida.append((prontuario, {
            "nome": nome,
            "x": round(rnd.uniform(0.5, 15.0), 1),
            "y": round(rnd.uniform(0.5, 12.0), 1),
        }))
    return saida
