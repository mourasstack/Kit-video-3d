// Geometrias e materiais compartilhados (cache) para manter o visual low-poly consistente e leve.

import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const geoCache = new Map();
const matCache = new Map();

// Estilo de construção em uso: 'redondo' (padrão: personagens lisos e arredondados, sombreado toon do
// CineCore) ou 'lowpoly' (facetado original). makeCharacter troca o estilo enquanto monta cada boneco.
let ESTILO = 'lowpoly'; // o cenário usa sempre o facetado; só o personagem troca
export const ESTILOS_PERSONAGEM = ['redondo', 'lowpoly'];
export function setEstilo(e) { ESTILO = ESTILOS_PERSONAGEM.includes(e) ? e : 'lowpoly'; }
export function getEstilo() { return ESTILO; }
const R = () => ESTILO === 'redondo';
// Mais segmentos no estilo redondo: a superfície fica lisa em vez de facetada.
const seg = (n, k = 3) => (R() ? Math.max(n, Math.round(n * k)) : n);

// Rampa de 3 tons (sombra / meio / luz) do material toon, igual à do CineCore.
let rampa = null;
function toonRamp() {
  if (rampa) return rampa;
  const tons = [140, 200, 255];
  const data = new Uint8Array(tons.length * 4);
  tons.forEach((v, i) => data.set([v, v, v, 255], i * 4));
  rampa = new THREE.DataTexture(data, tons.length, 1, THREE.RGBAFormat);
  rampa.minFilter = THREE.NearestFilter;
  rampa.magFilter = THREE.NearestFilter;
  rampa.generateMipmaps = false;
  rampa.needsUpdate = true;
  return rampa;
}

export function mat(color) {
  const key = `${ESTILO}:${String(color)}`;
  let m = matCache.get(key);
  if (!m) {
    m = R()
      ? new THREE.MeshToonMaterial({ color, gradientMap: toonRamp() })
      : new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.85, metalness: 0 });
    matCache.set(key, m);
  }
  return m;
}

function cached(key, make) {
  let g = geoCache.get(key);
  if (!g) { g = make(); geoCache.set(key, g); }
  return g;
}

// Caixa de cantos chanfrados (2 segmentos = facetas visíveis, estilo low-poly).
export function rbox(w, h, d, r = 0.03) {
  const rr = R() ? Math.max(r, Math.min(w, h, d) * 0.32) : r; // redondo: cantos bem arredondados
  const rad = Math.min(rr, Math.min(w, h, d) / 2 - 1e-4);
  const sg = R() ? 5 : 2;
  return cached(`rb:${w}:${h}:${d}:${rad}:${sg}`, () => new RoundedBoxGeometry(w, h, d, sg, rad));
}

export function sphere(r, ws = 8, hs = 6) {
  const a = seg(ws, 4), b = seg(hs, 4);
  return cached(`sp:${r}:${a}:${b}`, () => new THREE.SphereGeometry(r, a, b));
}

export function cylinder(rTop, rBottom, h, n = 8) {
  const k = seg(n, 3);
  return cached(`cy:${rTop}:${rBottom}:${h}:${k}`, () => new THREE.CylinderGeometry(rTop, rBottom, h, k));
}

// Esfera facetada (icosaedro): é a cabeça redonda low-poly.
export function ico(detail = 2) {
  if (R()) return cached('ic:liso', () => new THREE.SphereGeometry(1, 40, 28));
  return cached(`ic:${detail}`, () => new THREE.IcosahedronGeometry(1, detail));
}

// Casca de esfera de raio 1 (escale para a cabeça). theta: do topo (0) à base (π); phi: ao redor
// (z negativo = nuca = phiStart π, phiLength π).
export function shell(thetaStart, thetaLength, phiStart = 0, phiLength = Math.PI * 2, ws = 12, hs = 6) {
  const a = seg(ws, 3), b = seg(hs, 3);
  return cached(`sh:${thetaStart}:${thetaLength}:${phiStart}:${phiLength}:${a}:${b}`,
    () => new THREE.SphereGeometry(1, a, b, phiStart, phiLength, thetaStart, thetaLength));
}

export function dome(r, n = 10) {
  const a = seg(n, 3), b = seg(6, 3);
  return cached(`dm:${r}:${a}:${b}`, () => new THREE.SphereGeometry(r, a, b, 0, Math.PI * 2, 0, Math.PI / 2));
}

export function torus(r, tube, arc = Math.PI * 2, rs = 4, ts = 10) {
  const a = seg(rs, 2), b = seg(ts, 2);
  return cached(`to:${r}:${tube}:${arc}:${a}:${b}`, () => new THREE.TorusGeometry(r, tube, a, b, arc));
}

// Cápsula (corpo e membros do estilo redondo). Comprimento = parte reta entre as duas meias-esferas.
export function capsule(r, len) {
  return cached(`ca:${r}:${len}`, () => new THREE.CapsuleGeometry(r, len, 8, 20));
}

// Cria uma malha já posicionada. opts: { pos, rot (rad), scale, parent }
export function mesh(geometry, color, opts = {}) {
  const m = new THREE.Mesh(geometry, mat(color));
  m.castShadow = true;
  m.receiveShadow = true;
  if (opts.pos) m.position.set(...opts.pos);
  if (opts.rot) m.rotation.set(...opts.rot);
  if (opts.scale) {
    if (Array.isArray(opts.scale)) m.scale.set(...opts.scale);
    else m.scale.setScalar(opts.scale);
  }
  if (opts.parent) opts.parent.add(m);
  return m;
}
