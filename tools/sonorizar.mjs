#!/usr/bin/env node
// Trilha de fundo + efeitos sonoros (sintetizados, livres de direitos) misturados com a narração.
//   node tools/sonorizar.mjs projects/<nome>                       → render/audio-final.wav
//   node tools/sonorizar.mjs projects/<nome> --video render/video.mp4 → render/video-final.mp4 (vídeo copiado, áudio novo)
// Opções: --estilo animado|curioso|tenso  --musica 0.8  --sfx 1.2  --sem-musica  --sem-sfx  --saida <arquivo.mp4>
// No storyboard (opcional): "som": { "estilo": "animado", "volumeMusica": 1, "volumeEfeitos": 1, "musica": true, "efeitos": true }
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const proj = args.find((a) => !a.startsWith('--'));
if (!proj) { console.error('Uso: node tools/sonorizar.mjs projects/<nome> [--video render/video.mp4]'); process.exit(1); }
const pasta = path.resolve(proj);
const valor = (k) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : undefined; };
const flag = (k) => args.includes(`--${k}`);

const sb = JSON.parse(fs.readFileSync(path.join(pasta, 'storyboard.json'), 'utf8'));
const narr = path.join(pasta, sb.audio || 'narracao.wav');
if (!fs.existsSync(narr)) { console.error(`Narração não encontrada: ${narr}`); process.exit(1); }
const renderDir = path.join(pasta, 'render');
fs.mkdirSync(renderDir, { recursive: true });
const wav = path.join(renderDir, 'audio-final.wav');

const venv = path.join(raiz, '.voz', 'venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const py = fs.existsSync(venv) ? venv : (process.platform === 'win32' ? 'python' : 'python3');
const pyArgs = ['-I', path.join(raiz, 'tools', 'som', 'sonorizar.py'), '--storyboard', path.join(pasta, 'storyboard.json'), '--narracao', narr, '--saida', wav];
for (const k of ['estilo', 'musica', 'sfx']) if (valor(k)) pyArgs.push(`--${k}`, valor(k));
for (const k of ['sem-musica', 'sem-sfx']) if (flag(k)) pyArgs.push(`--${k}`);
const r = spawnSync(py, pyArgs, { stdio: ['ignore', 'pipe', 'inherit'], encoding: 'utf8' });
if (r.status !== 0) { console.error('Falha ao gerar o áudio (precisa de numpy: pip install numpy).'); process.exit(1); }
console.log(`Áudio: ${path.relative(raiz, wav)} ${r.stdout.trim()}`);

const video = valor('video');
if (video) {
  const entrada = path.isAbsolute(video) ? video : fs.existsSync(path.resolve(video)) ? path.resolve(video) : path.join(pasta, video);
  const saida = valor('saida') ? path.resolve(valor('saida')) : path.join(renderDir, 'video-final.mp4');
  const f = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', entrada, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-t', String(sb.duracao), '-movflags', '+faststart', saida], { stdio: 'inherit' });
  if (f.status !== 0) process.exit(1);
  console.log(`Vídeo com som: ${path.relative(raiz, saida)}`);
}
