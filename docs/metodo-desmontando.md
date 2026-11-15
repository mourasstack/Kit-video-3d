# Método Desmontando (padrão obrigatório de todos os vídeos)

Baseado no vídeo de referência da criadora (estilo @desmontandoomundo, "como construir uma casa",
2 min 50 s). Vale para **todo** vídeo: roteiro, explicação visual, voltar no tempo e efeitos sonoros.
Onde outro documento do kit divergir, **vale este**.

## 1. A ideia em uma frase

O espectador **constrói a coisa junto com você, errando primeiro**: cada etapa nasce porque a
tentativa anterior **deu errado na frente dele**. O vídeo mostra a falha, **volta no tempo** e
aplica a solução, que ganha o **nome técnico** e uma **ponte com a vida real**.

## 2. Roteiro: o ciclo que se repete

Narração sempre em **segunda pessoa** ("você levanta", "você cava"), frases curtas, sem "nós" e sem
"neste vídeo". Um mesmo objeto vai sendo construído do começo ao fim (casa, carro, celular, rua…).

**Abertura (0–6 s): a tentativa ingênua que falha.**
"Se você [faz o óbvio], você não vai ter [o resultado]. Vai ter [o desastre]."
Na tela: você faz o óbvio **acelerado (⏩)** e o desastre acontece. Tema claro na 1ª frase.

**Ciclo (repete 8–12 vezes, 10–20 s cada):**

| Passo | Fala (molde) | Tela |
| --- | --- | --- |
| 1. Problema | "Mas [o que dá errado]…" + a consequência física | a falha acontecendo: desaba, racha, mofa, vaza, afunda; etiqueta na causa (`• TERRA FOFA`, `• UMIDADE`) |
| 2. Voltar no tempo | (a fala segue: "Então…") | **⏪ rebobinar** 0,8–1 s: o mundo volta até antes da falha |
| 3. Solução | "Então você [ação concreta]…" | a solução sendo feita (personagem fazendo ou peça montando), muitas vezes acelerada ⏩ |
| 4. Nome técnico | "Essa é a [nome]." | a peça **acende em amarelo** + **nome em amarelo** preso nela + a palavra amarela na legenda |
| 5. Ponte com a vida real (em ~metade dos ciclos) | "É por isso que [sinal que a pessoa já viu]." | mostra o defeito real quando a etapa falta (rachadura torta na janela, mofo no pé da parede); etiqueta vermelha `• FALHA NA PINTURA` |
| 6. Gancho para o próximo | "Mas…" | já começa o próximo problema |

Regras do ciclo:
- **Todo ciclo começa com "Mas"** e toda solução com **"Então você"**. Esse ritmo é o que prende.
- A falha é **física e visível** (nunca só falada). A solução é **concreta** (o que se faz, com o quê).
- Medidas e materiais reais quando ajudam ("trinta centímetros para cada lado", "cimento, areia e água").
- A ordem segue a construção de verdade (do chão para cima, de dentro para fora).

**Acabamento rápido (5–8 s):** lista curta e acelerada do resto ("Coloque portas, janelas, fios…"),
com uma piada visual leve (ex.: um cachorro).

**Final (6–8 s):**
"Agora é só [usar a coisa]. Parabéns! Você construiu [X]."
CTA de duas opções com palavras do tema: **"Se você já sabia, comente '[palavra 1]'. Se não sabia,
comente '[palavra 2]'."** (no vídeo: "pedreiro" / "servente"). Na tela: o texto empilhado em amarelo
no alto ("SABIA? COMENTE "PEDREIRO"" / "NÃO SABIA? COMENTE "SERVENTE""), aparecendo em sincronia
com a fala. Fechamento com o nome do canal / mascote acenando.

Duração: a que a construção pedir (a referência tem ~2 min 50 s com 10 ciclos). Pode ser longo.

## 3. Explicação visual

- **Um único mundo contínuo** do começo ao fim (o mesmo terreno, o mesmo muro, a casa do vizinho
  ao fundo). A obra cresce nele; o espectador reconhece o lugar.
- **Corte transversal** sempre que a causa é escondida: terreno em corte mostrando terra fofa e
  terra firme, estacas dentro do chão, parede por dentro (`corte_terreno`, `forma`, câmera rente).
- **Partículas e setas para o invisível:** umidade = bolinhas azuis subindo; peso = setas vermelhas
  para baixo; caminho da carga = setas verdes; água nos canos = pontinhos azuis correndo (`fluxos`).
- **Zona do problema em vermelho translúcido** (`realce` com `cor` vermelha) e **peça da solução em
  amarelo** (`realce` padrão) na hora em que é nomeada.
- **Etiquetas pílula** brancas com bolinha colorida para causas e medidas (`• 30 cm`).
- **Câmera que explica:** close no defeito, plano aberto para mostrar a obra, câmera baixa no
  corte do terreno. Um corte a cada 1–3 s, sempre mostrando o que a frase fala.
- **Legenda:** uma palavra por vez, branca com contorno, no meio-baixo; **nomes técnicos em amarelo**
  (automático para todo `termo` do storyboard).

## 4. Efeitos sonoros

| Momento | Som (automático no `sonorizar`) |
| --- | --- |
| ⏪ voltar no tempo | **rebobinar**: fita voltando (guincho subindo + chiado + "clack") |
| ⏩ acelerar | **avancar**: "trrrr" agudo |
| Estrutura desabando | **desaba**: estrondo grave + entulho (efeito `desaba`, que também treme a imagem) |
| Peça acende (nome técnico) | **brilho** + **ding** do termo |
| Etiqueta / seta | clique |
| Peça aparecendo | pop |
| Troca de cena | whoosh |
| Fundo | música leve, abaixando sob a voz |

## 5. Como montar no storyboard (receitas)

**Voltar no tempo** (nível do storyboard, tempos absolutos):

```json
"rebobinar": [ { "em": 12.0, "duracao": 0.9, "volta": 6.0 } ]
```

Entre 12,0 e 12,9 s o mundo 3D roda de trás para frente de 12,0 até 6,0 (⏪ no alto, linhas de VHS,
cores lavadas, tremidinha). Legenda e voz continuam normais. A cena seguinte (a solução) começa em
12,9 s mostrando o estado de antes da falha. Textos e etiquetas somem durante o rebobinar.

**Acelerar:** elemento `{ "tipo": "icone", "icone": "avancar", "pos": [0.86, 0.12], "tamanho": 0.1, "de": 0, "ate": 3 }`
e a ação acontecendo rápido (etapa/anim curtas).

**Falha física:** `anim` no objeto (tombar com `giro` no eixo x/z, afundar com `pos`), fluxos de
partículas (umidade, água), `efeitos: [{ "tipo": "desaba", "de": t, "ate": t + 1 }]`.

**Peça acendendo + nome:** no objeto `"realce": { "de": 20.8, "ate": 22.5 }` (amarelo; para problema
use `"cor": "#ff3b30"`) e o elemento `{ "tipo": "termo", "texto": "FUNDAÇÃO", "ancora": "<id>", "de": 20.8, "ate": 22.5 }`.

**CTA final:** dois textos `estilo: "pergunta"` (ou `titulo`) empilhados no alto, aparecendo quando
cada frase é falada.

## 6. Checklist do método (antes de aprovar o roteiro e antes do render)

- [ ] Abertura: tentativa ingênua acelerada + desastre nos primeiros ~5 s; tema na 1ª frase.
- [ ] 8–12 ciclos "Mas… → ⏪ → Então você… → Essa é a…".
- [ ] Toda falha aparece fisicamente; todo ciclo de falha tem `rebobinar`.
- [ ] Todo nome técnico: peça acende em amarelo + `termo` + palavra amarela na legenda.
- [ ] Pontes "É por isso que…" com o defeito real em pelo menos metade dos ciclos.
- [ ] Causas escondidas mostradas em corte; invisível com partículas/setas.
- [ ] Um único mundo contínuo; a obra cresce nele.
- [ ] Final "Parabéns! Você construiu…" + CTA de duas palavras ("já sabia / não sabia").
- [ ] Sons: rebobinar, avançar, desaba, brilho/ding, música sob a voz.
