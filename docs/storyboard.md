# Referência do `storyboard.json`

O storyboard é o **roteiro de cenas** do vídeo: um arquivo JSON em `projects/<nome>/storyboard.json`. O motor (`engine/`) lê esse arquivo e desenha cada quadro; você **não escreve código**, só descreve o que aparece e quando. Valide sempre com `node tools/validar.mjs projects/<nome>` antes de renderizar.

Todos os tempos são em **segundos desde o início do vídeo** (não desde o início da cena).

## Estrutura geral

```json
{
  "versao": 1,
  "titulo": "Como uma casa fica de pé",
  "formato": { "largura": 1080, "altura": 1920, "fps": 30 },
  "duracao": 32.5,
  "audio": "narracao.wav",
  "palavras": "palavras.json",
  "legendas": { "ativo": true, "palavrasPorBloco": 3, "corDestaque": "#ffd60a" },
  "ambiente": { "horario": "dia", "chao": "grama", "nuvens": true },
  "cenas": [ ... ]
}
```

| Campo | Valores |
|---|---|
| `duracao` | segundos; use a duração do áudio + 0,3 a 1 s de folga (`voz.json` e `frases.json` ajudam) |
| `audio` / `palavras` | nomes dos arquivos gerados por `node tools/voz.mjs gerar` (ficam na pasta do projeto) |
| `legendas` | padrão: **uma palavra por vez**, branca com contorno preto, pequena, no terço inferior (como nos Shorts de referência). Opções: `palavrasPorBloco` (1 a 3), `maiusculas` (false), `corDestaque` (cor da palavra falada; padrão branca), `posicaoY` (0.68), `tamanho` (1) |
| `ambiente.horario` | `dia`, `tarde`, `nublado` |
| `ambiente.chao` | `grama`, `terra`, `areia`, `concreto`, `asfalto`, `madeira`, `piso` (padrão pelo `fundo`; não existe chão vazio) |
| `ambiente.clima` | `limpo` (padrão) ou `chuva` (céu escuro, riscos de chuva e menos luz) |
| `ambiente.fundo` | **sempre existe um cenário de fundo** (nunca cor sólida): `campo` (padrão: colinas com pinheiros), `cidade` (prédios com janelas), `floresta`, `deserto`, `litoral`, `industrial`, `interior` (sala). Veja a tabela de escolha em `docs/processos.md` |
| `ambiente.decoracao` | `false` desliga os tufos de grama e flores (já ficam desligados em cenas com `rua_reta`/`cruzamento`) |
| `qualidade` | `alta` (padrão: sombra suave, oclusão de luz, brilho e correção de cor) ou `basica` (mais rápida, sem pós-processamento) |
| `som` | opcional: `{ "estilo": "animado" \| "curioso" \| "tenso", "volumeMusica": 1, "volumeEfeitos": 1, "musica": true, "efeitos": true }`. Usado por `tools/sonorizar.mjs` (trilha + efeitos sonoros automáticos a partir das cenas, objetos com `aparece`, termos, etiquetas, zoom, tremor e preto e branco) |

As **cenas** devem cobrir o vídeo inteiro sem buracos: a primeira começa em `0`, cada uma começa onde a anterior termina e a última termina em `duracao`. Cada cena pode repetir `ambiente` para mudar o horário/chão só nela.

## Cena

```json
{
  "inicio": 0, "fim": 5.6,
  "transicao": "flash",
  "objetos":     [ ... ],
  "personagens": [ ... ],
  "camera":      { ... },
  "textos":      [ ... ]
}
```

`transicao` (opcional, vale no início da cena): `corte` (padrão), `flash` (clarão branco rápido), `fade` (vem do preto). Use `flash` em cortes de capítulo.

**Cada cena é montada do zero**: o que não estiver listado nela não aparece. Para manter a continuidade (a mesma casa, as mesmas árvores), repita o objeto com o mesmo `asset`, `pos` e `params`.

### Sistema de coordenadas

- Metros. `x` para a direita, `y` para cima, `z` para perto da câmera padrão. O chão é `y = 0`.
- Assets e personagens olham para `+Z` quando `giro = 0`. `giro` é em graus (positivo gira para a esquerda do personagem).
- `pos` é `[x, z]` (no chão) ou `[x, y, z]` (ex.: em cima da calçada: `y = 0.2`; sobre o asfalto: `y = 0.06`).
- Um quarteirão típico: casas a ~8 m umas das outras; personagens a ~2–4 m da fachada.

### Objetos (cenário)

```json
{ "id": "casa", "asset": "casa_obra", "pos": [0, 0, 0], "giro": 0, "escala": 1,
  "variante": "verde", "params": { "progress": 1 },
  "etapa": [[8.3, 0], [13, 0.1]],
  "aparece": 6.2, "some": 12,
  "movimentos": [{ "de": 2, "ate": 6, "para": [10, 0] }] }
```

| Campo | O que faz |
|---|---|
| `id` | nome único **na cena** (a câmera e os personagens referenciam por ele) |
| `asset`, `variante`, `params` | do catálogo (`catalog/RESUMO.md`) |
| `escala` | multiplica o tamanho (use com moderação) |
| `etapa` | `[[tempo, 0..1], ...]`: etapa de obra, só nos assets "etapas" (`casa_obra`, `predio_estrutura`, `rua_camadas`, `corte_terreno`, `guindaste`, `caminhao_cacamba`) |
| `aparece` / `some` | o objeto surge com um "pop" no instante dado / desaparece. Ótimo para revelar um item junto da fala |
| `movimentos` | desloca o objeto em linha reta de `de` a `ate` até `para: [x, z]`; vira na direção do movimento; as rodas dos veículos giram sozinhas |

### Personagens

```json
{ "id": "guia", "preset": "construtor", "pos": [0, 0, 2], "giro": 0,
  "overrides": { "top": { "color": "#2d9cdb" } },
  "viraPara": [{ "em": 5.6, "alvo": "camera" }],
  "movimentos": [{ "de": 6, "ate": 9, "para": [4, 2], "clip": "walk" }],
  "acoes": [
    { "clip": "point", "de": 6.3, "ate": 8.3, "params": { "dir": "down" } },
    { "clip": "talk", "de": 5.6, "ate": 8.3, "fala": true, "camada": 1, "mascara": ["head", "face", "armL"] }
  ] }
```

| Campo | O que faz |
|---|---|
| `preset` | um dos personagens do catálogo; `overrides` muda cores/chapéu/etc. (mesmos campos de `makePreset`) |
| `viraPara` | `[{ "em": t, "alvo": "camera" \| "<id>" \| [x, z] \| ângulo_em_graus }]`: o personagem gira suavemente para o alvo no instante `em`. **Use `camera` em quem fala para o público.** |
| `movimentos` | andar/correr em linha reta: `{ de, ate, para: [x, z], clip: "walk" \| "run" \| "push" \| "carry", velocidade }`. O motor ajusta a velocidade da passada para os pés não patinarem e vira o personagem na direção do movimento |
| `acoes` | animações: `{ clip, de, ate, params, expressao, velocidade, mascara, camada, fala }` |
| `acoes[].fala` | só com `clip: "talk"`: a boca abre e fecha **no ritmo das palavras da narração** (use no personagem que "está falando") |
| `acoes[].camada` | `0` = corpo base (padrão). `1` ou mais sobrepõem só as partes da `mascara` (ex.: falar com a cabeça e uma mão enquanto o corpo faz outra coisa) |
| `acoes[].mascara` | grupos: `head`, `face`, `arms`, `armL`, `armR`, `legs`, `torso` |
| `acoes[].expressao` | `neutral`, `happy`, `laugh`, `sad`, `angry`, `surprised`, `worried`, `thinking`, `sleepy` |

Sem nenhuma ação num trecho, o personagem fica em `idle` (respirando). As animações disponíveis e seus parâmetros estão em `catalog/RESUMO.md`.

### Câmera

Três tipos:

**`enquadrar`** (o mais usado): a câmera se posiciona sozinha para enquadrar um objeto ou personagem.

```json
{ "tipo": "enquadrar", "alvo": "casa", "plano": "geral",
  "angulo": 25, "elevacao": 14, "deriva": -18, "aproxima": 0.8, "fov": 38 }
```

| Campo | Significado |
|---|---|
| `alvo` | `id` de um objeto ou personagem da cena |
| `plano` | `geral` (mostra tudo), `medio` (cintura para cima / metade do objeto), `close` (rosto / detalhe), `topo` (de cima) |
| `angulo` | graus ao redor do alvo, **contados a partir da frente do alvo** (`giro`): `0` = de frente, `90` = lado, `180` = de costas |
| `elevacao` | graus de altura da câmera (0 = na altura do alvo; 40 = de cima) |
| `deriva` | quantos graus a câmera **gira em volta** do alvo durante a cena (movimento orbital suave) |
| `aproxima` | `0.8` = termina a cena 20% mais perto (dolly-in); `1.2` = afasta |

> **Cuidado com o `giro` do alvo.** Como `angulo: 0` é "de frente para o alvo", um personagem com `giro: 180` (olhando para a casa) fará a câmera ficar entre ele e a casa, possivelmente dentro da parede (tela cinza ou escura). Para mostrar um personagem de frente com o cenário atrás dele, use `giro: 0` e ponha-o à frente da casa (`z` maior que a casa). **Sempre confira com `node tools/render.mjs projects/<nome> --quadros`.**

**`fixa`**: posição escolhida por você.

```json
{ "tipo": "fixa", "pos": [10, 4, 12], "olha": "casa", "fov": 40 }
```

**`travelling`**: a câmera vai de um ponto a outro durante a cena.

```json
{ "tipo": "travelling",
  "de":   { "pos": [12, 3, 14], "olha": [0, 2, 0] },
  "para": { "pos": [4, 2, 8],  "olha": "casa" } }
```

**`percurso`**: vários pontos de câmera em **tempos absolutos** do vídeo, com movimento suave entre eles. É o jeito de fazer um plano longo e contínuo (um cenário só, poucas trocas de cena) que ainda "bate" a cada 2–4 s: cada chave é uma nova batida (aproxima da peça que está sendo dita, recua para mostrar o todo). O validador conta cada trecho como uma batida, então uma cena de 12 s com 4 chaves não é "longa".

```json
{ "tipo": "percurso", "chaves": [
  { "t": 39.0, "pos": [0.8, 2.8, 3.4], "olha": [0.5, 2.6, -2.7], "fov": 48 },
  { "t": 43.0, "pos": [1.2, 2.6, 4.6], "olha": "evap" },
  { "t": 47.5, "pos": [1.6, 2.4, 6.6], "olha": [1.0, 1.7, -1.6] } ] }
```

Antes da primeira chave a câmera fica parada nela; depois da última, também.

### Textos na tela

```json
{ "texto": "POR QUE ELA NÃO AFUNDA?", "de": 0.2, "ate": 5.3, "estilo": "titulo" }
```

| `estilo` | Onde | Para quê |
|---|---|---|
| `titulo` | alto (6–14%), pequeno | a pergunta/gancho dos primeiros segundos |
| `destaque` | 16–24%, amarelo, levemente inclinado | uma ideia-chave (até ~30 caracteres) |
| `pergunta` | 10–22%, painel amarelo | **a pergunta final** para comentar |
| `rodape` | ~74% | informação curta (fonte, "parte 2") |

**Use poucos textos**: o gancho no começo, no máximo uma ou duas ideias-chave e a pergunta final. A legenda já mostra o que é falado; o texto de destaque deve **acrescentar** (um número, um rótulo, uma provocação), nunca repetir. Quando há título/destaque na tela, a legenda desce um pouco sozinha.

### Mostrar o processo: fluxos, rastros, animação livre e transparência

Receitas prontas e o vocabulário completo estão em **`docs/processos.md`**. Aqui, o formato:

**`fluxos`** (partículas que mostram matéria/energia em movimento) — dentro da cena:
```json
"fluxos": [{ "material": "pedra", "origem": { "ancora": "cam", "desloca": [0,1.6,-4.6] }, "destino": [-5,0.5,0],
             "taxa": 45, "de": 28, "ate": 30.5, "dispersao": 0.3, "espalha": 0.6 }]
```
- `material`: `pedra`, `brita`, `areia`, `terra`, `concreto`, `asfalto`, `agua`, `fumaca`, `vapor`, `poeira`, `fogo`, `fagulha`, `ar`, `bolha`, `neve`, `eletricidade`, `luz`.
- `origem`/`destino`: `[x,y,z]` no mundo **ou** `{ "ancora": "id", "desloca": [dx,dy,dz] }` (segue o objeto/personagem e gira junto com ele; `desloca` é relativo ao centro da base do objeto).
- `caminho`: lista de pontos `[x,y,z]` (no lugar de origem/destino) para o fluxo **percorrer um cano, fio ou veia**; `velocidade` em m/s.
- Opcionais: `taxa` (partículas/s), `tamanho`, `dispersao` (espalhamento na origem), `espalha` (no destino), `vida` (s), `arco` (curva do jato), `subida`/`vento` (fumaça, vapor).
- `cores`: lista de cores que **substitui as do material** (ex.: `"material": "agua", "cores": ["#ff5a3c", "#ffa040"]` para um gás quente andando no cano). Assim o mesmo formato de partícula muda de cor conforme a temperatura.
- Fluxo em `caminho` dentro de cano fino: use `dispersao` ~0.02–0.03 (o padrão 0.25 espalha as partículas para fora do tubo).
- Fumaça, vapor, poeira e fogo **sobem** da origem; sólidos e líquidos **caem/jorram** até o destino.

**`rastros`** — faixa que cresce atrás de uma máquina que se move (asfalto novo, trilha molhada, linha pintada):
```json
"rastros": [{ "seguir": "pav", "largura": 3.2, "altura": 0.07, "cor": "#222226", "recuo": 2.6, "de": 78, "ate": 84 }]
```
O objeto seguido precisa ter `movimentos` (a faixa vai do ponto inicial até onde ele chegou, menos `recuo`).

**`anim`** (em qualquer objeto) — animação livre, sempre em função do tempo:
```json
"anim": { "pos": [[0,[0,3,0]],[4,[0,0.5,0]]], "gira": 90, "eixo": "z", "oscila": { "eixo": "y", "amp": 0.4, "freq": 0.5 }, "escala": [[0,1],[3,1.4]], "pulsa": 0.05 }
```
`pos` (keyframes `[tempo,[x,y,z]]`, suaves), `giro` (keyframes em graus), `gira` (graus/s contínuo), `eixo` (`x`,`y`,`z` do giro), `escala` (keyframes), `oscila`, `pulsa`.

**`opacidade`** (0 a 1, em qualquer objeto) — deixa transparente para ver por dentro (tubos, máquinas, tanques).

**Assets que se mexem sozinhos** (tocam em qualquer cena sem configurar nada): `escavadeira`, `esteira`, `misturador`, `engrenagem`, `helice`, `fabrica_processo`, `betoneira`. **Assets com nível/crescimento** (`etapa`): `monte`, `tanque`, `casa_obra`, `predio_estrutura`, `rua_camadas`, `corte_terreno`, `guindaste`, `caminhao_cacamba`.

### Elementos opcionais: setas, ícones e etiquetas

Só use **quando o vídeo exigir** (mostrar direção ou força, contrastar certo/errado, destacar um dado). Em excesso, poluem.

```json
"elementos": [
  { "tipo": "seta",     "direcao": "baixo", "ancora": "casa", "alturaRel": 0.55, "tamanho": 0.2, "pulsa": true, "de": 8.8, "ate": 12.6 },
  { "tipo": "icone",    "icone": "x", "pos": [0.5, 0.4], "tamanho": 0.22 },
  { "tipo": "etiqueta", "texto": "meio mais alto", "pos": [0.5, 0.3], "ponto": "#ffd60a" }
]
```

| Campo | O que faz |
|---|---|
| `tipo` | `seta` (azul, contorno preto), `icone` (cartoon com contorno preto), `etiqueta` (pílula branca com bolinha colorida, para rótulos e dados), `painel` (números ao vivo), `termo` (nome técnico em arco amarelo) |
| `direcao` (seta) | `direita`, `esquerda`, `cima`, `baixo`, `horizontal` (dupla), `vertical` (dupla) |
| `icone` | `x` (vermelho: errado), `v` (verde: certo), `alerta`, `interrogacao`, `exclamacao`, `coracao`, `estrela`, `lampada`, `relogio`, `dinheiro`, `fogo`, `proibido`, `raio`, `avancar` (⏩ passar o tempo), `voltar` (⏪ voltar no tempo) |
| `pos` | `[x, y]` em fração da tela (0 a 1); por exemplo `[0.5, 0.4]` é o centro, um pouco acima do meio |
| `ancora` | **id** de um objeto/personagem da cena: o elemento acompanha esse item na tela. Ajuste com `alturaRel` (0 = pé, 1 = topo), `y` (metros), `dx`/`dy` (fração da tela) |
| `tamanho` | fração da largura da tela (padrão 0.22; etiqueta 1 = tamanho normal do texto) |
| `cor` | cor da seta/ícone (padrão por tipo); na etiqueta, `ponto` é a cor da bolinha |
| `de` / `ate` | quando aparece (padrão: a cena inteira); entra com um "pop" e sai com fade |
| `pulsa` | pulsa de leve (chama atenção); setas balançam sozinhas na direção que apontam (`"balanca": false` desliga) |

Evite colocar elementos sobre o rosto de quem fala ou sobre a legenda (faixa ~62–74%).

**Painel de números ao vivo** (ex.: ALTURA / DESCIDA do paraquedas, TEMPERATURA, PRESSÃO): caixa escura com borda colorida; o número anda pelos keyframes `valores` e é escrito no formato brasileiro (3.890).

```json
{ "tipo": "painel", "titulo": "ALTURA", "unidade": "metros", "valores": [[0, 3910], [12, 1230]], "casas": 0, "pos": [0.24, 0.1], "cor": "#2ecc71" }
```
Para um valor que não é número puro, use `"texto": "500+"` no lugar de `valores` (o painel mostra o texto fixo).

**Termo técnico** (o nome da peça na hora em que é dito: FUNDAÇÃO, VELAME, CONTRAPESO): texto amarelo em arco com contorno preto, ancorado no objeto. `curva` (0 = reto, 1 = arco padrão), `tamanho` (fração da largura, padrão 0.6), `cor`, `fonte` (tamanho da letra; se omitido, diminui sozinho para nomes longos: use `tamanho` 0.8–0.9 em nomes com 15+ letras).

```json
{ "tipo": "termo", "texto": "FUNDAÇÃO", "ancora": "viga", "alturaRel": 1.2, "de": 8.4, "ate": 11 }
```

### Tela dividida

Uma cena com `camera2` divide a tela: a metade de cima mostra `camera` e a de baixo mostra `camera2` (mesmo formato de câmera), com uma faixa branca no meio. Use para comparar duas coisas ao mesmo tempo (a gangorra do parque × o contrapeso do elevador; antes × depois). Monte os dois lugares na mesma cena, longe um do outro (ex.: um em x = 0 e outro em x = 60). Elementos ancorados usam a câmera de cima; com `"camera": 2` usam a de baixo. Na tela dividida o pós-processamento da qualidade alta não é aplicado.

```json
"camera":  { "tipo": "fixa", "pos": [3, 3, 10],  "olha": [0, 2, -4] },
"camera2": { "tipo": "fixa", "pos": [61, 2, 7], "olha": [60, 1, 0] }
```

### Efeitos de imagem

```json
"efeitos": [
  { "tipo": "pretoebranco", "de": 19.8, "ate": 22.2, "zoom": 1.1 },
  { "tipo": "zoom", "de": 5, "ate": 8, "para": 1.2 },
  { "tipo": "tremor", "de": 12, "ate": 12.8, "intensidade": 0.6 }
]
```

- `pretoebranco`: a imagem 3D vai a preto e branco com um zoom lento (use em momentos **ruins, perigosos ou dramáticos**: o problema, o erro, o desastre). Combine com um ícone `x` ou `alerta`.
- `zoom`: aproximação lenta (de 1 até `para`) para dar ênfase.
- `tremor`: a imagem treme (impacto, explosão, queda).
Os efeitos afetam só o 3D; legendas, textos e elementos continuam normais. Ao fim do intervalo voltam ao normal.

### Zonas da tela (vertical 9:16)

O topo (~8%) e a base (~20%) ficam cobertos pela interface do Shorts/Reels/TikTok. Por isso: título 6–14%, destaque 16–24%, pergunta final 10–22%, **legenda em ~68% (uma palavra por vez)**. Não coloque nada importante fora de ~8%–80%.

## Ritmo (o que mantém as pessoas assistindo)

- Uma cena nova a cada **3 a 5 segundos** (nunca mais que 7). Cada corte deve mudar algo: ângulo, plano, alvo ou cenário.
- Cenas alinhadas com as **frases** da narração (`projects/<nome>/frases.json` dá o início e o fim de cada uma).
- A cada cena, algo se **move ou muda**: uma etapa de obra, um personagem que anda/aponta, um objeto que aparece.
- Os primeiros 3 segundos precisam ter o título/pergunta na tela.

## Fluxo de trabalho

```bash
node tools/validar.mjs projects/<nome>             # erros e avisos de qualidade
node tools/render.mjs projects/<nome> --quadros    # 2 imagens por cena para você olhar (rápido)
node tools/render.mjs projects/<nome> --previa     # vídeo rápido 540×960
node tools/render.mjs projects/<nome>              # render final 1080×1920
node tools/render.mjs projects/<nome> --capa 1.2   # capa.png do instante 1.2 s
```

Para ver no navegador com controles: `npm run preview` e abra `http://localhost:5173/engine/player.html?projeto=projects/<nome>`.


## Método Desmontando: voltar no tempo, realce, desabar (veja `docs/metodo-desmontando.md`)

| Campo | Onde | O que faz |
|---|---|---|
| `rebobinar: [{ em, duracao, volta }]` | raiz do storyboard | entre `em` e `em + duracao` (padrão 0,9 s) o mundo 3D roda de trás para frente até `volta`, com ⏪, linhas de VHS e som de fita. Legenda/voz seguem normais; textos e etiquetas somem. A cena seguinte começa em `em + duracao`. |
| `realce: { de, ate, cor }` (ou lista) | objeto ou personagem | a peça acende pulsando na cor (padrão amarelo `#ffd60a`; problema: `#ff3b30`). Som "brilho". |
| `efeitos: [{ "tipo": "desaba", de, ate, intensidade }]` | cena | treme a imagem como `tremor` e toca o estrondo de desabamento. |
| `legendas.termos: ["viga baldrame", …]` | raiz | palavras extras que saem em amarelo na legenda (todo `termo` dos elementos já entra sozinho). |


## Sons humanos dos bonecos (automático no `sonorizar`)

Os bonecos ganham **vozinhas de desenho animado** (sem palavras) e **sons do corpo**, sintetizados (livres de direitos), cada um com o timbre do seu preset (criança fina, homem grave, Bia/Vovó médias…). A narração continua sendo a voz principal: as vozinhas ficam por baixo e abaixam quando a narração fala.

| Quando | Som |
|---|---|
| `expressao`: `surprised` / `worried` / `sad` / `thinking` / `laugh` / `angry` / `sleepy` / `happy` | "oh!" / "ih…" / suspiro / "hmm" / risadinha / "ã-ã" / suspiro / "uau!" |
| clipe `cheer` / `surprised` / `think` / `shrug` e `look_around` / `nod` / `shake_head` / `push` e `carry` / `laugh` | "êêê!" + palmas / "oh!" / "hmm" / "hã?" / "uhum" / "ã-ã" / esforço "hnf!" / risadinha |
| `walk`, `run` e `movimentos` | passos no ritmo da passada |
| `hammer` / `dig` / `beber` | martelada / pá na terra / goles |

- O boneco que está com `talk` + `fala: true` não faz vozinha (a narração é a voz dele).
- No máximo uma vozinha por boneco a cada 1,2 s.
- Som pontual: no personagem, `"sons": [{ "em": 12.4, "som": "ai" }]`. Nomes: `oh`, `uau`, `hmm`, `ih`, `ai`, `risada`, `suspiro`, `ha`, `uhum`, `aa`, `esforco`, `vivas`, `passo`, `martelada`, `pazada`, `gole`, `palmas`.
- Silenciar um boneco: `"mudo": true` no personagem. Desligar tudo: `"som": { "sonsPersonagens": false }`; só as vozinhas: `"som": { "vozesPersonagens": false }`.
