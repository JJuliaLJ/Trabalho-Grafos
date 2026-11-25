# Agenda de UBS com árvores implementadas do zero

Projeto sobre árvores binárias, Rubro-Negra, k-D e 2-3-4 não binária.</br>
O sistema simula uma Unidade Básica de Saúde: cadastro de pacientes, agenda de consultas
e localização da UBS mais próxima do paciente. As estruturas são implementadas com nós
e ponteiros, sem bibliotecas de árvores. Todos os dados são fictícios.

## Como executar

Requisitos: Git e Python 3.10 ou mais novo. Testado com Python 3.13, Streamlit 1.58 e Matplotlib 3.10.

1. Baixe o projeto:

   ```bash
   git clone <url-do-repositorio>
   cd Trabalho-Grafos
   ```

2. Crie e ative um ambiente virtual.

   Windows (PowerShell):

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   Linux ou macOS:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências e abra o programa:

   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

O navegador abre em `http://localhost:8501`. O botão **Carregar dados de exemplo**, na barra
lateral, preenche os pacientes, as consultas e as unidades.

Testes automatizados (comparam cada operação com uma implementação simples, força bruta):

```bash
python -m unittest discover -s testes -t . -v
```

## Como usar

1. Clique em **Carregar dados de exemplo** na barra lateral.
2. Escolha uma página no menu: **Pacientes**, **Agenda**, **Unidades de saúde** ou **Comparação**.
3. Pacientes, Agenda e Unidades de saúde têm três abas:
   - a aba de uso (Cadastro, Consultas ou Mapa), onde o sistema funciona como um app comum;
   - **Árvore**: mostra a árvore com seus nós. O campo de busca destaca em azul o caminho
     percorrido e explica cada comparação. Depois de adicionar ou remover algo, mostra o
     **antes e o depois**, com o passo a passo e os nós destacados: verde para o nó criado,
     laranja para os nós ajustados pelo rebalanceamento (rotação, recoloração, divisão, fusão)
     e vermelho para o nó removido. O desenho pode caber na tela ou ficar em tamanho real;
   - **Implementação**: tabela com cada nó, seus ponteiros e a verificação das regras da árvore.
4. No topo da página Agenda, **Árvore da agenda** troca entre Rubro-Negra e 2-3-4. Os dados são copiados.

Quando uma operação provoca rebalanceamento, a aba de uso mostra um aviso apontando para a aba Árvore.

## Requisitos do trabalho

| Requisito | Onde está |
|---|---|
| Árvores implementadas com nós ligados nos dois sentidos (filhos e pai) | `arvores/rubro_negra.py`, `arvores/arvore_234.py`, `arvores/kdtree.py` |
| Sem bibliotecas de árvores | Nenhuma. Só `math`, `bisect` (busca binária em lista), `collections.deque` (fila) e `random` |
| Inserção com balanceamento | Rubro-Negra (`inserir`, `_corrigir_insercao`) e 2-3-4 (`inserir`, `_dividir`) |
| Remoção com balanceamento | Rubro-Negra (`remover`, `_corrigir_remocao`) e 2-3-4 (`remover`, `_reforcar`, `_fundir`) |
| Busca | `buscar` e `passos_busca` (caminho explicado) em todas; `intervalo` na Rubro-Negra e na 2-3-4; vizinhos na k-D |
| Árvores binárias com pelo menos 21 nós | Demonstração com 24 nós na Rubro-Negra e 24 na k-D (`dados/demo.py`); a comparação aceita de 21 a 300 |
| Método para elementos repetidos | Ver seção abaixo |
| Biblioteca de plotagem | matplotlib no gráfico de comparação; desenho das árvores e do mapa em SVG |
| Explicação e exemplo da k-D | Página Unidades de saúde e roteiro de apresentação |
| Testes | `testes/test_arvores.py`, 31 testes, incluindo sequências aleatórias comparadas com um modelo simples |

## Método para elementos repetidos

- **Rubro-Negra:** chave repetida acrescenta um valor à lista (balde) do nó. A estrutura não muda
  e não rebalanceia. O nó só sai quando o balde fica vazio.
- **2-3-4 (prontuários):** prontuário repetido atualiza o cadastro existente.
  Na agenda, a 2-3-4 usa o mesmo balde da Rubro-Negra (método `adicionar`), para que a troca funcione.
- **k-D:** ponto repetido vai para a subárvore direita (critério "maior ou igual"), e a busca usa
  o mesmo critério. A remoção recebe o ponto e o nome, para tirar o registro certo entre os repetidos.

## Outras estruturas de dados usadas

| Estrutura | Onde | Para quê |
|---|---|---|
| Nó sentinela (NIL) | Rubro-Negra | Representa as folhas vazias, sempre pretas, e evita casos especiais na remoção |
| Lista | Nós da 2-3-4; balde da Rubro-Negra | Guardar chaves e filhos em ordem; guardar vários valores da mesma chave |
| Pilha (lista) | Percurso em ordem da Rubro-Negra | Percorrer sem recursão |
| Fila (`deque`) | `arvores/inspecao.py` | Numerar os nós por nível |
| Lista ordenada | `k_mais_proximos` da k-D | Manter os k melhores candidatos |
| Dicionário e conjunto | Interface, desenho e testes | Comparar antes e depois; modelo simples para conferir as árvores |

## Estrutura do projeto

```
├── .streamlit/                      
│   └── config.toml     ## cores do tema                                                 
├── arvores/
│   ├── arvore_234.py 
│   ├── bst.py
│   ├── inspecao.py
│   ├── kdtree.py
│   └── rubro_negra.py  
├── dados/                                                                     
│   └── demo.py     ## dados fictícios de demonstração                        
├── mapa/
│   └── cidade.py     ## mapa 2D estilizado da cidade (SVG)                                        
├── testes/
│   └── test_arvores.py     ## testes automatizados                                                
├── visual/
│   ├── arvore_svg.py     ## desenho das árvores (SVG)
│   ├── estilo.py     ## tema visual do site
│   └── rebalanceamento.py     ## comparação antes/depois e resumo dos ajustes 
├── .gitignore
├── app.py     ## interface Streamlit                                              
├── README.md                                                            
└── requirements.txt

```


## Limitações

- A k-D não se rebalanceia sozinha. Use o botão "Reorganizar (balancear)".
- Não há banco de dados nem autenticação: os dados ficam na sessão do navegador.
- Os dados são fictícios. Dados reais de pacientes exigem tratamento adequado de privacidade (LGPD).
- Splay e B-Tree não fazem parte do trabalho: a equipe tem 4 integrantes.

## Equipe

- Júlia Labad Jatene
- Pedro Andrade Gonçalves de Souza
- João Paulo Oliveira Rodrigues
- Luan Piedade de Oliveira
