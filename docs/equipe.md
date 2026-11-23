# Modo equipe: vários chats no mesmo vídeo ao mesmo tempo

Cada chat roda numa máquina própria (2 núcleos). Renderizar um vídeo de 2 min em 60 fps num chat só
demora; com 3 chats cada um faz 1/3 do vídeo **ao mesmo tempo** e o render fica ~3× mais rápido.
O lugar em comum é o GitHub **privado** da criadora: `mourasstack/Studio-agent-ai`, branch `videos`,
pasta `videos/<nome>/` (`projeto/` = o vídeo aprovado; `trechos/` = os pedaços renderizados).
A conversa da tarefa agendada não acessa o repositório privado: o modo equipe roda em chats que ela abre.

## Quem faz o quê

**Chat principal** (o que fez roteiro, narração, storyboard e a folha de quadros aprovada):
1. `node tools/equipe.mjs dividir projects/<nome> 3` (2 a 8 trechos; corta no começo de cenas, nunca no meio de um ⏪).
2. Sobe o projeto: `add_repo` em `mourasstack/Studio-agent-ai` (push), clona a branch `videos`
   (se não existir: cria a partir da main com `git checkout -b videos`), copia `projects/<nome>/` **sem a pasta `render/`**
   para `videos/<nome>/projeto/`, faz commit e push.
3. Gera um convite por trecho: `node tools/equipe.mjs convite projects/<nome> <n>` e manda para a criadora
   cada texto **pronto para colar**, um em cada chat novo (uma mensagem por chat, sem nada a explicar).
4. Enquanto os ajudantes trabalham, pode renderizar o trecho 1 ele mesmo (`renderizar ... 1`).
5. Quando a criadora avisar (ou `git pull` mostrar todos), copia `videos/<nome>/trechos/*.mp4` para
   `projects/<nome>/render/trechos/`, roda `node tools/equipe.mjs juntar projects/<nome>` e entrega o
   `render/video-final.mp4` (60 fps, narração, música e efeitos) + capa + postagem.
6. Depois de entregue, pode apagar `videos/<nome>/trechos/` do repositório (com permissão) para ele não crescer.

**Chats ajudantes:** só seguem o convite: clonam, baixam o kit, renderizam o seu trecho e devolvem.
Não mudam roteiro, storyboard nem trechos dos outros.

## Garantias do `equipe.mjs`
- Cortes em quadros exatos: os trechos se encaixam sem pulo nem quadro repetido.
- Cada trecho é conferido (quantidade de quadros e 60 fps) antes de ser aceito; `juntar` confere de novo.
- O som é feito uma vez só, no vídeo inteiro (a música não "pula" entre trechos).

## O que não dá
- Dois chats **editando** roteiro ou storyboard ao mesmo tempo: um não vê o que o outro mudou.
  Divida só depois que a folha de quadros estiver aprovada.
