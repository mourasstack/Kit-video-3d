// Usa uma narração GRAVADA (sua voz ou ElevenLabs baixado) no projeto: corta silêncio, normaliza volume,
// alinha cada palavra do roteiro com o áudio (Whisper via sherpa-onnx) e gera palavras.json, frases.json e voz.json.
// Uso: node tools/usar-gravacao.mjs <raizDoKit> <pastaProjeto> <arquivoDeAudio> [provedor]
// Requisitos (uma vez): .voz/venv com sherpa-onnx e o modelo .voz/modelos/sherpa-onnx-whisper-small (GitHub k2-fsa/sherpa-onnx, release asr-models).
import fs from 'node:fs'; import path from 'node:path'; import { spawnSync } from 'node:child_process';
const [raiz, pasta, audio, provedor = 'gravacao'] = process.argv.slice(2);
const { normalizarNarracao } = await import(path.join(raiz, 'tools/voz/normalizar.mjs'));
const { frasesDePalavras, duracaoAudio } = await import(path.join(raiz, 'tools/voz/gerar.mjs'));
const { texto } = normalizarNarracao(fs.readFileSync(path.join(pasta, 'narracao.txt'), 'utf8'));
const falado = path.join(pasta, 'narracao.falado.txt'); fs.writeFileSync(falado, texto + '\n');
const wav = path.join(pasta, 'narracao.wav');
const tmp = path.join(pasta, '_tmp.wav');
// corta silêncio do começo/fim (deixa 0,15 s), normaliza volume, 44,1 kHz mono
let r = spawnSync('ffmpeg', ['-y', '-v', 'error', '-i', audio, '-af',
  'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,areverse,loudnorm=I=-16:TP=-1.5:LRA=11',
  '-ar', '44100', '-ac', '1', tmp], { encoding: 'utf8' });
if (r.status) throw new Error(r.stderr);
fs.renameSync(tmp, wav);
const pal = path.join(pasta, 'palavras.json');
r = spawnSync(path.join(raiz, '.voz/venv/bin/python'), ['-I', path.join(raiz, 'tools/voz/py/alinhar_gravacao.py'), '--audio', wav, '--texto', falado,
  '--saida', pal, '--modelo', path.join(raiz, '.voz/modelos/sherpa-onnx-whisper-small/small')], { encoding: 'utf8', maxBuffer: 1 << 26 });
if (r.status) throw new Error(r.stderr);
const res = JSON.parse(r.stdout.trim().split('\n').pop());
const palavras = JSON.parse(fs.readFileSync(pal, 'utf8'));
const frases = frasesDePalavras(palavras);
fs.writeFileSync(path.join(pasta, 'frases.json'), JSON.stringify(frases, null, 1));
const dur = duracaoAudio(wav);
fs.writeFileSync(path.join(pasta, 'voz.json'), JSON.stringify({ provedor, audio: 'narracao.wav', duracao: +dur.toFixed(2),
  palavras: palavras.length, frases: frases.length, coberturaTempos: res.cobertura, geradoEm: new Date().toISOString() }, null, 2));
console.log(JSON.stringify({ duracao: +dur.toFixed(2), cobertura: res.cobertura, frases: frases.length }));
