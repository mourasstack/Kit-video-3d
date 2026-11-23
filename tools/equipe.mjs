#!/usr/bin/env node
// MODO EQUIPE: vários chats renderizam o MESMO vídeo ao mesmo tempo, cada um um trecho.
//
//   node tools/equipe.mjs dividir projects/<nome> [N]     → divide em N trechos (padrão 3) e grava equipe.json
//   node tools/equipe.mjs renderizar projects/<nome> <n>  → renderiza o trecho n (só imagem) em render/trechos/
//   node tools/equipe.mjs status projects/<nome>          → quais trechos já estão prontos
//   node tools/equipe.mjs juntar projects/<nome>          → junta os trechos, confere 60 fps e sonoriza → render/video-final.mp4
//   node tools/equipe.mjs convite projects/<nome> <n>     → mensagem pronta para a criadora colar no chat ajudante n
//
// Como os chats trocam os arquivos: veja docs/equipe.md (GitHub privado da criadora).
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [cmd, proj, extra] = process.argv.slice(2);
const uso = () => { console.error('Uso: node tools/equipe.mjs dividir|renderizar|status|juntar projects/<nome> [N|n]'); process.exit(1); };
if (!cmd || !proj) uso();
const pasta = path.resolve(raiz, proj);
const sbArq = path.join(pasta, 'storyboard.json');
if (!fs.existsSync(sbArq)) { console.error(`Não achei ${sbArq}`); process.exit(1); }
const sb = JSON.parse(fs.readFileSync(sbArq, 'utf8'));
const fps = sb.formato?.fps || 60;
const dur = sb.duracao;
const eqArq = path.join(pasta, 'equipe.json');
const trechosDir = path.join(pasta, 'render', 'trechos');
const arqTrecho = (n) => path.join(trechosDir, `trecho-${String(n).padStart(2, '0')}.mp4`);
const quadro = (t) => Math.round(t * fps) / fps;
const roda = (bin, a, opts = {}) => spawnSync(bin, a, { stdio: 'inherit', cwd: raiz, ...opts });
const contaQuadros = (arq) => {
  const r = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets,r_frame_rate', '-of', 'json', arq], { encoding: 'utf8' });
  try { const s = JSON.parse(r.stdout).streams[0]; return { quadros: Number(s.nb_read_packets), fps: s.r_frame_rate }; } catch { return null; }
};
const lerEquipe = () => {
  if (!fs.existsSync(eqArq)) { console.error('Ainda não foi dividido. Rode primeiro: node tools/equipe.mjs dividir ' + proj); process.exit(1); }
  return JSON.parse(fs.readFileSync(eqArq, 'utf8'));
};

if (cmd === 'dividir') {
  const N = Math.max(2, Math.min(8, Number(extra) || 3));
  if (fps < 60) console.warn(`Aviso: o storyboard está em ${fps} fps; o padrão é 60.`);
  // cortes de preferência no início de uma cena, longe de um "rebobinar"
  const inicios = (sb.cenas || []).map((c) => c.inicio).filter((t) => t > 0.5 && t < dur - 0.5);
  const proibido = (t) => (sb.rebobinar || []).some((r) => t > r.em - 0.05 && t < r.em + (r.duracao ?? 0.9) + 0.05);
  const cortes = [];
  for (let k = 1; k < N; k++) {
    const alvo = (dur * k) / N;
    const cand = inicios.filter((t) => !proibido(t) && !cortes.includes(t)).sort((a, b) => Math.abs(a - alvo) - Math.abs(b - alvo))[0];
    cortes.push(quadro(cand !== undefined && Math.abs(cand - alvo) < dur / (2 * N) ? cand : alvo));
  }
  cortes.sort((a, b) => a - b);
  const pontos = [0, ...cortes, quadro(dur)];
  const trechos = pontos.slice(0, -1).map((de, i) => ({ n: i + 1, de, ate: pontos[i + 1] }));
  fs.writeFileSync(eqArq, JSON.stringify({ projeto: path.basename(pasta), fps, duracao: dur, trechos }, null, 2));
  console.log(`Dividido em ${N} trechos (${fps} fps):`);
  for (const t of trechos) console.log(`  trecho ${t.n}: ${t.de.toFixed(2)}s → ${t.ate.toFixed(2)}s (${(t.ate - t.de).toFixed(1)} s)`);
  console.log(`\nCada chat ajudante roda:  node tools/equipe.mjs renderizar ${proj} <n>`);
  console.log(`O chat principal, no fim:  node tools/equipe.mjs juntar ${proj}`);
} else if (cmd === 'renderizar') {
  const eq = lerEquipe();
  const t = eq.trechos.find((x) => x.n === Number(extra));
  if (!t) { console.error(`Trecho "${extra}" não existe. Trechos: ${eq.trechos.map((x) => x.n).join(', ')}`); process.exit(1); }
  fs.mkdirSync(trechosDir, { recursive: true });
  const saida = arqTrecho(t.n);
  console.log(`Renderizando o trecho ${t.n} (${t.de}s → ${t.ate}s)…`);
  const r = roda('node', ['tools/render.mjs', proj, '--de', String(t.de), '--ate', String(t.ate), '--sem-audio', '--saida', saida]);
  if (r.status !== 0) process.exit(r.status || 1);
  const info = contaQuadros(saida);
  const esperado = Math.round((t.ate - t.de) * eq.fps);
  if (!info || info.quadros !== esperado) { console.error(`Trecho saiu com ${info?.quadros} quadros; esperado ${esperado}. Renderize de novo.`); process.exit(1); }
  console.log(`Trecho ${t.n} pronto: ${path.relative(raiz, saida)} (${info.quadros} quadros, ${info.fps} fps).`);
} else if (cmd === 'status') {
  const eq = lerEquipe();
  for (const t of eq.trechos) {
    const ok = fs.existsSync(arqTrecho(t.n));
    console.log(`  trecho ${t.n} (${t.de}s → ${t.ate}s): ${ok ? 'PRONTO' : 'falta'}`);
  }
} else if (cmd === 'juntar') {
  const eq = lerEquipe();
  const faltam = eq.trechos.filter((t) => !fs.existsSync(arqTrecho(t.n)));
  if (faltam.length) { console.error(`Faltam os trechos: ${faltam.map((t) => t.n).join(', ')}.`); process.exit(1); }
  for (const t of eq.trechos) {
    const info = contaQuadros(arqTrecho(t.n));
    const esperado = Math.round((t.ate - t.de) * eq.fps);
    if (!info || info.quadros !== esperado) { console.error(`Trecho ${t.n} com ${info?.quadros} quadros (esperado ${esperado}); renderize de novo.`); process.exit(1); }
  }
  const lista = path.join(trechosDir, 'lista.txt');
  fs.writeFileSync(lista, eq.trechos.map((t) => `file '${path.basename(arqTrecho(t.n))}'`).join('\n') + '\n');
  const video = path.join(pasta, 'render', 'video.mp4');
  const c = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lista, '-c', 'copy', '-movflags', '+faststart', video], { stdio: 'inherit' });
  if (c.status !== 0) process.exit(1);
  const info = contaQuadros(video);
  console.log(`Vídeo juntado: ${info?.quadros} quadros, ${info?.fps} fps.`);
  if (info && info.fps !== '60/1') console.warn(`Aviso: o vídeo está em ${info.fps}; o padrão é 60 fps.`);
  const s = roda('node', ['tools/sonorizar.mjs', proj, '--video', path.relative(raiz, video)]);
  if (s.status !== 0) process.exit(s.status || 1);
  console.log('Pronto: render/video-final.mp4 (vídeo inteiro com narração, música e efeitos).');
} else if (cmd === 'convite') {
  const eq = lerEquipe();
  const t = eq.trechos.find((x) => x.n === Number(extra));
  if (!t) { console.error(`Trecho "${extra}" não existe.`); process.exit(1); }
  const nome = path.basename(pasta);
  console.log(`Você é um chat ajudante do MODO EQUIPE do kit de vídeo 3D. Renderize SÓ o trecho ${t.n} de ${eq.trechos.length} do vídeo "${nome}" (${t.de}s → ${t.ate}s, ${eq.fps} fps) e devolva pelo GitHub privado. Passos:
1. Chame add_repo (owner "mourasstack", repo "Studio-agent-ai", access "push") e clone: git clone --depth 1 -b videos https://github.com/mourasstack/studio-agent-ai /home/claude/estudio
2. Baixe o kit: mkdir -p /home/claude/kit && cd /home/claude/kit && curl -sSL https://codeload.github.com/mourasstack/kit-video-3d/tar.gz/refs/heads/main | tar xz --strip-components=1 && npm install
3. Copie o projeto: cp -r /home/claude/estudio/videos/${nome}/projeto /home/claude/kit/projects/${nome}
4. Renderize: cd /home/claude/kit && node tools/equipe.mjs renderizar projects/${nome} ${t.n}
5. Devolva: mkdir -p /home/claude/estudio/videos/${nome}/trechos && cp projects/${nome}/render/trechos/trecho-${String(t.n).padStart(2, '0')}.mp4 /home/claude/estudio/videos/${nome}/trechos/ && cd /home/claude/estudio && git add videos/${nome}/trechos && git commit -m "trecho ${t.n} de ${nome}" && git pull --rebase origin videos && git push origin videos
Não mude roteiro, storyboard nem nada além do seu trecho. No fim, diga só: "Trecho ${t.n} pronto e enviado".`);
} else uso();
