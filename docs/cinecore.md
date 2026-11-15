# Integração CineCore (vale em todo vídeo)

Este kit agora é o **motor padrão** dos vídeos da criadora: o **mundo 3D completo** e as
ferramentas deste kit (cenários, fluxos, máquinas, validador, legendas, sonorização) com os
**personagens redondinhos** e as regras de roteiro/retenção do CineCore.

## 1. Personagens redondos (padrão)

- Todo personagem sai no estilo **redondo** (CineCore): cabeça grande e lisa, olhos brancos com
  pupila e brilho, bochechas rosadas, corpo e membros em cápsulas, sombreado toon de 3 tons.
- Usam o **mesmo esqueleto** de antes: todas as animações (`walk`, `talk`, `dig`, `cheer`...) e
  expressões continuam funcionando.
- Controle no `storyboard.json`:
  - `"estiloPersonagens": "redondo"` (padrão, pode omitir) ou `"lowpoly"` (visual facetado antigo);
  - por personagem: `"overrides": { "estilo": "lowpoly" }`.
- Elenco do CineCore pronto como preset: **`bia`**, **`teo`**, **`vovo`** (além dos 11 originais).
- O cenário continua low-poly facetado de propósito (contraste bonito com os bonecos lisos).
- Elenco: manter o mesmo personagem no mesmo papel; personagem principal novo e roupa nova a cada
  tema (regra de figurinos do CineCore) — use `overrides` de cor/roupa/cabelo.

## 2. Mundo 3D completo (nunca diorama flutuando)

Já é regra do motor: sempre `ambiente.fundo` (`campo`, `cidade`, `floresta`, `deserto`, `litoral`,
`industrial`, `interior`) + chão real. Nunca quadrado/base flutuando, fundo liso ou borda do chão
no quadro. Cenário coerente com o tema (barranco para deslizamento, cozinha para itens de casa);
nada caindo do céu, nada solto no meio da rua.

## 3. Regra do primeiro segundo (retenção / taxa de deslize)

Meta: "Ficaram para assistir" do Shorts de ~60% para média 70–75%, vários acima de 80%.
A decisão de deslizar acontece em ~1,7 s. Na **primeira cena** do storyboard:

| Camada | Como fazer neste kit |
| --- | --- |
| Imagem | (No método: a tentativa ingênua já acontecendo, acelerada ⏩, e o desastre em até ~5 s.) Cena 1 começa em `inicio: 0` **já com a consequência acontecendo**: um `fluxo`, `movimento`, `anim` ou ação começando em `de: 0` (nunca `de` > 0,3 s). Plano `detalhe` ou `medio` no objeto do problema; plano `geral` só depois de ~2 s. Sem `transicao` na entrada. Use `pretoebranco`/`alerta`/cor de perigo se o tema for problema. |
| Texto no topo | `textos: [{ "texto": "3 A 5 PALAVRAS", "de": 0, "ate": 2.5, "estilo": "titulo" }]` — promessa ou contradição, sem repetir a legenda. |
| Voz | Primeira sílaba no quadro 0: corte o silêncio inicial da gravação antes de `usar-gravacao`. Tema na 1ª frase e "mas/só que" antes de 3 s. Fórmula: [familiar] + [mas/só que] + [virada oposta]. Proibido "Você sabia que…", "Hoje vou explicar…". |
| Som | `sonorizar` sempre (música + efeitos). Para abrir com impacto, a cena 1 deve ter um evento visual em `t ≈ 0` (aparece/etapa/zoom/tremor) — o sonorizador põe o efeito nele. |

Personagem na cena 1 → expressão forte (`surprised`, `worried`) nos 2 s iniciais.

## 4. Estrutura do roteiro

**Desde 14/11/2026 a estrutura é a do `docs/metodo-desmontando.md` (ciclos falha → ⏪ → solução → nome). O texto abaixo vale só como apoio.**

0–2 s gancho → 2–5 s promessa (abre o ciclo) → até 40% contexto + revelação 1 → **45–55%
reengajamento** ("mas isso nem é o pior") → 55–90% revelações 2–3 e prova → últimos 10% payoff +
CTA ≤ 2 s + **última imagem/frase emendando no quadro 0 (loop)**. Quebra de padrão a cada 3–4 s.

CTA: nunca no começo; padrão do método: "Se você já sabia, comente '[palavra 1]'. Se não sabia, comente '[palavra 2]'". A
pergunta final do kit (`estilo: "pergunta"`) continua valendo, curta.

## 5. Padrão audiovisual do CineCore

- **60 fps reais quando der:** `"formato": { "largura": 1080, "altura": 1920, "fps": 60 }`
  (o render demora ~2× mais). Se precisar ficar em 30, avisar.
- Legenda palavra por palavra (o kit já faz); texto na tela nunca repete a legenda.
- Celular/mensagens na tela: balões com rabiscos/linhas de texto, nunca balão vazio.
- Duração: a que a história pedir; pode ser longo se estiver bem explicado.
- Música de fundo + efeitos sonoros sempre (`tools/sonorizar.mjs`).

## 6. Fluxo com portões (como a criadora prefere)

1. Ideia → sinopse + gancho do primeiro segundo (quadro 0, texto do topo, primeira fala, loop final) → **aprovação**.
2. Roteiro completo (narração em parágrafo único para ela gravar no ElevenLabs), títulos, descrição, capa ≤ 5 palavras, curiosidades com fontes → **aprovação**.
3. Ela envia a narração → `node tools/usar-gravacao.mjs . projects/<nome> <arquivo>`.
4. Storyboard → `validar` → `render --quadros` (folha visual) → **aprovação**.
5. Render final + `sonorizar` + capa + `postagem.md`.

Não pedir de novo uma aprovação já dada para a mesma etapa. Não gastar créditos pagos sem autorização.

## 7. Checklist extra antes do render final

- [ ] Personagens no estilo redondo (ou `lowpoly` só se pedido).
- [ ] Mundo 3D completo em todos os quadros.
- [ ] Cena 1: ação começando em t = 0, plano próximo, texto do topo 3–5 palavras até ~2,5 s.
- [ ] Sem silêncio no começo da narração.
- [ ] Teste do print: o primeiro quadro sozinho, sem som, gera curiosidade.
- [ ] Reengajamento perto da metade; final em loop; CTA ≤ 2 s.
