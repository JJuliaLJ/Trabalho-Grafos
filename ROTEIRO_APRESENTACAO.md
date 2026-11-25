# Roteiro de apresentação (12 minutos, tolerância de 15)

A apresentação deve mostrar conceitos, implementação e demonstração, e os 4 integrantes devem falar.
Cada um precisa saber explicar o código da sua parte.

| Integrante | Parte | Arquivo para dominar |
|---|---|---|
| 1 | Problema, árvore binária e comparação | `arvores/bst.py`, `app.py` |
| 2 | Rubro-Negra | `arvores/rubro_negra.py` |
| 3 | 2-3-4 | `arvores/arvore_234.py` |
| 4 | k-D, repetidos, testes e conclusão | `arvores/kdtree.py`, `testes/test_arvores.py` |

## Antes de começar

- Rode `streamlit run app.py`, abra em uma aba limpa e clique em **Carregar dados de exemplo**.
- Deixe o código aberto em `arvores/`, para mostrar as funções quando for preciso.

## Linha do tempo

| Tempo | Parte | O que mostrar |
|---|---|---|
| 0:00 a 1:00 | Problema | Página Início: cadastro, agenda e unidade mais próxima. Cada parte usa uma árvore. |
| 1:00 a 2:30 | Por que balancear | Página Comparação com 300 chaves: binária comum com 300 níveis; Rubro-Negra, 14; 2-3-4, 8. |
| 2:30 a 5:30 | Rubro-Negra | Agenda. Buscar um horário na aba Árvore. Marcar consultas até aparecer o aviso de rebalanceamento e mostrar o antes e o depois. Cancelar uma. Na aba Implementação, mostrar cores e ponteiros. |
| 5:30 a 8:00 | 2-3-4 | Pacientes: buscar um prontuário, cadastrar até haver divisão e remover até haver empréstimo ou fusão. Depois trocar a árvore no topo da Agenda para 2-3-4. |
| 8:00 a 10:00 | k-D | Unidades de saúde: escolher um paciente e mostrar as mais próximas. Na aba Árvore, usar Reorganizar e comparar a altura. |
| 10:00 a 11:00 | Repetidos e testes | Regra de cada estrutura e execução dos testes. |
| 11:00 a 12:00 | Conclusão | O que foi implementado e as limitações. |

## Conceitos para explicar

### Rubro-Negra

1. A raiz é preta. 2. Vermelho não tem filho vermelho. 3. Todo caminho até uma folha vazia tem o
mesmo número de pretos. Por isso o caminho mais longo tem no máximo o dobro do mais curto.

- **Inserção:** o nó entra vermelho. Se o pai também é vermelho, olha-se o tio. Tio vermelho:
  recolorir pai, tio e avô e continuar do avô. Tio preto: uma ou duas rotações e recoloração.
- **Remoção:** com dois filhos, o sucessor ocupa o lugar e a cor do removido. Se saiu um preto,
  falta um preto naquele lado: o irmão é recolorido ou se rotaciona até compensar.
- **Exemplo curto:** inserir 10, 20 e 30. O 30 entra vermelho sob o 20 vermelho, e o tio é vazio
  (preto): 20 vira preto, 10 vira vermelho e há rotação à esquerda em 10. A raiz passa a ser 20.

### 2-3-4

Cada nó tem de 1 a 3 chaves e todas as folhas ficam no mesmo nível. A árvore cresce pela raiz.

- **Inserção:** ao descer, todo nó com 3 chaves é dividido e a chave do meio sobe.
- **Remoção:** ao descer, todo nó com 1 chave é reforçado: empréstimo de um irmão com 2 ou mais
  chaves, ou fusão com o irmão e uma chave do pai.
- **Exemplo curto:** inserir 10, 20 e 30 forma o nó [10 | 20 | 30]. Ao inserir 40, ele se divide:
  20 sobe e os filhos ficam [10] e [30 | 40].

### k-D

Cada nível corta o plano por uma coordenada, alternando x e y: menores à esquerda, maiores ou iguais
à direita.

- **Exemplo curto:** inserir (2, 3), (8, 9) e (4, 7). O (2, 3) corta em x. O (8, 9) tem x maior e vai
  para a direita, cortando em y. O (4, 7) vai para a direita do primeiro e, como 7 < 9, para a
  esquerda do segundo.
- **Vizinho mais próximo:** desce pelo lado do alvo e só visita o outro lado se a linha de corte
  estiver mais perto do que o melhor ponto já achado.

### Diferenças entre os balanceamentos

| | Rubro-Negra | 2-3-4 | k-D |
|---|---|---|---|
| Quando age | Regra de cor quebrada | Nó cheio ou com 1 chave na descida | Só quando se pede |
| Como age | Recoloração e rotação | Divisão, empréstimo e fusão | Reconstrução pela mediana |
| Altura máxima | 2 · log₂(n + 1) | log₂(n + 1) | n, sem reorganizar |

A Rubro-Negra representa uma 2-3-4: um nó preto com seus filhos vermelhos equivale a um nó da 2-3-4.
A recoloração corresponde à divisão de um nó cheio.

## Perguntas prováveis

- **Por que dá para trocar a estrutura da agenda?** As duas têm os mesmos métodos (adicionar, remover
  valor, buscar, intervalo). A diferença está em como guardam os nós.
- **Por que a k-D não usa rotações?** Uma rotação mudaria o nível do nó e, com isso, o eixo de corte,
  o que quebraria a divisão do plano.
- **Como as chaves repetidas são tratadas?** Na agenda, balde no mesmo nó. Nos pacientes, atualização
  do cadastro, com confirmação. Na k-D, o repetido vai para a direita.
- **Que outras estruturas foram usadas?** Ver a tabela do README: sentinela, lista, pilha e fila.
