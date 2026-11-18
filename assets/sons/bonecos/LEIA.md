# Banco de sons dos bonecos

Sons gravados (gerados no ElevenLabs) que substituem as vozinhas sintéticas.
Formato: WAV mono 44,1 kHz, 16 bits, sem silêncio no começo. Várias versões: `oh_1.wav`, `oh_2.wav`…

| Pasta | Arquivos |
|---|---|
| `homem/`, `mulher/`, `crianca/` | `oh`, `uau`, `hmm`, `ih`, `ai`, `risada`, `suspiro`, `ha`, `uhum`, `aa`, `esforco`, `vivas` |
| `corpo/` | `passo`, `martelada`, `pazada`, `gole`, `palmas` |

Se um arquivo faltar: o som do corpo usa a versão sintetizada; a vozinha fica de fora
(a sintética só entra com `"som": { "sinteticosPersonagens": true }`).
