#!/usr/bin/env node
// Instala sons gravados (ex.: ElevenLabs) no banco dos bonecos.
// Uso: node tools/sons-bonecos.mjs <pasta-com-os-arquivos>
// Nomes aceitos: <grupo>_<som>.mp3|wav (grupo: homem, mulher, crianca, corpo), com variação opcional: homem_oh_2.mp3
// Converte para WAV mono 44,1 kHz, corta o silêncio do começo e do fim e grava em assets/sons/bonecos/<grupo>/.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const raiz = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const origem = process.argv[2];
if (!origem || !fs.existsSync(origem)) {
  console.error('Uso: node tools/sons-bonecos.mjs <pasta-com-os-arquivos>');
  process.exit(1);
}
const GRUPOS = ['homem', 'mulher', 'crianca', 'corpo'];
const VOCAIS = ['oh', 'uau', 'hmm', 'ih', 'ai', 'risada', 'suspiro', 'ha', 'uhum', 'aa', 'esforco', 'vivas'];
const CORPO = ['passo', 'martelada', 'pazada', 'gole', 'palmas'];
const corta = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5';

const arquivos = fs.readdirSync(origem, { recursive: true }).map(String).filter((f) => /\.(mp3|wav|m4a|ogg)$/i.test(f));
let ok = 0;
const ignorados = [];
for (const rel of arquivos) {
  const base = path.basename(rel).replace(/\.[^.]+$/, '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const m = base.match(/^(homem|mulher|crianca|corpo)[_-]([a-z]+)(?:[_-](\d+))?$/);
  if (!m || !GRUPOS.includes(m[1]) || !(m[1] === 'corpo' ? CORPO : VOCAIS).includes(m[2])) { ignorados.push(rel); continue; }
  const pasta = path.join(raiz, 'assets', 'sons', 'bonecos', m[1]);
  fs.mkdirSync(pasta, { recursive: true });
  const destino = path.join(pasta, `${m[2]}${m[3] ? '_' + m[3] : ''}.wav`);
  const r = spawnSync('ffmpeg', ['-v', 'error', '-y', '-i', path.join(origem, rel), '-ac', '1', '-ar', '44100', '-af', corta, '-c:a', 'pcm_s16le', destino]);
  if (r.status === 0) ok++; else ignorados.push(`${rel} (ffmpeg: ${String(r.stderr).trim().slice(0, 120)})`);
}
console.log(`Instalados: ${ok}.`);
if (ignorados.length) console.log(`Ignorados (nome fora do padrão <grupo>_<som>): ${ignorados.join(', ')}`);
const faltam = [];
for (const g of ['homem', 'mulher', 'crianca']) for (const v of VOCAIS) if (!fs.readdirSync(path.join(raiz, 'assets/sons/bonecos', g)).some((f) => f.startsWith(v + '.') || f.startsWith(v + '_'))) faltam.push(`${g}_${v}`);
if (faltam.length) console.log(`Ainda faltam (${faltam.length}): ${faltam.join(', ')}`);
