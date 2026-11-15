# Estilo de referência (perfil @desmontandoomundo)

Análise de 3 vídeos de referência (paraquedas, casa, elevador; ~3 min cada). É o nível a buscar.

## Roteiro: a corrente "problema → solução → nome"
- Abre com uma situação absurda: "Se você levantar quatro paredes de tijolo num quadrado, você não vai ter um quarto. Vai ter um monte de entulho."
- Cada passo: **"Então você** [solução]. **Essa é a** [NOME TÉCNICO]. **Mas** [novo problema]…" e repete até o objeto ficar pronto.
- Analogias do dia a dia ("como água num pano", "que nem numa gangorra").
- Fecha com a consequência prática ("é por isso que o mofo aparece sempre no pé da parede") e um CTA de palavra-chave:
  "Sabia? Comente PEDREIRO. Não sabia? Comente SERVENTE."
- Duração: o que o assunto pedir (2–3 min é normal), desde que cada passo traga um problema novo.

## Imagem
- **Um objeto montado do zero num único cenário que cresce** (a casa sendo construída, o elevador sendo montado). Poucos cortes; quem dá ritmo é a câmera se movendo.
- **Demonstração física** em vez de ícone: a parede tomba, a água sobe pelo tijolo, a gangorra explica o contrapeso.
- O protagonista (construtor) **faz** a ação: martela, pinta, assenta tijolo.
- Corte do terreno / vista em corte para mostrar o que fica escondido.
- Gráficos mínimos e com função:
  - `termo` amarelo em arco com o NOME TÉCNICO na hora em que é dito;
  - `etiqueta` para apontar partes;
  - `painel` com números ao vivo (altura, velocidade, temperatura);
  - ícones `avancar` ⏩ / `voltar` ⏪ para pular o tempo;
  - tela dividida (`camera2`) para analogias e comparações.
- Legenda: **uma palavra por vez**, branca com contorno (padrão do kit; não use maiúsculas nem 2+ palavras).
- Final: o objeto pronto + CTA na tela + confete (`fluxos` de `luz`).

## Regras desta criadora
- Toda cena precisa de cenário que faça sentido (nada caindo do céu, nada solto no meio da rua).
- Telas de celular e mensagens sempre com rabiscos de texto, avatares e reações nos balões.

## Como montar no kit (aprendido no vídeo do ar-condicionado)
- **Câmera `percurso`** (docs/storyboard.md): uma cena longa no mesmo cenário com 3–6 chaves em tempos de palavras da narração (`tw('compressor')`). Cada chave é uma batida: aproxima da peça que está sendo dita, recua para mostrar o todo. Plano contínuo, sem cortes, e ainda com ritmo.
- **Cenário vertical**: uma casa "de bonecas" (parede da frente removida) com o lado de fora ao lado. Em retrato, a largura visível é só ~0,5 × a distância da câmera: mantenha o conjunto com **≤ 6 m de largura** para caber num plano geral.
- **Peças montadas aos poucos**: `aparece` em cada peça no instante em que ela é citada. Para canos, use o `tubo` com a origem no 1º ponto (pos = 1º ponto, pontos relativos): o cano cresce a partir de onde começa.
- **Carcaça transparente** (`opacidade` 0.2–0.3) + fundo/tampa opacos: o público vê por dentro sem perder a forma do aparelho.
- **O que corre dentro do cano**: canos em cobre semitransparentes; quem muda de cor é o fluxo (`cores`), com `tamanho` ~0,5 × o raio do cano (0,02–0,035) e `dispersao` ≤ 0,01. Partícula grande vira "pedra" no close.
- **Câmera nunca atravessa parede**: em casa em corte, os movimentos de dentro para fora passam pela frente da casa (z maior que a borda das paredes).
- **Personagem não pode ficar entre a câmera e a peça** nos closes; tire-o da cena ou mande-o para o lado.
- **Confira com `--tempos`** os instantes das chaves e dos termos antes de renderizar.
