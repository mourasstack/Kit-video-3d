"""Trilha de fundo + efeitos sonoros sintetizados (sem arquivos de terceiros, livre de direitos autorais).

Lê o storyboard.json, gera uma música instrumental em loop no tamanho do vídeo, coloca efeitos
sonoros nos eventos visuais (troca de cena, peça aparecendo, termo, etiqueta, zoom, tremor...)
e mistura com a narração, abaixando a música enquanto alguém fala (ducking).

Uso: python sonorizar.py --storyboard storyboard.json --narracao narracao.wav --saida mix.wav
     [--estilo animado|curioso|tenso] [--musica 1.0] [--sfx 1.0] [--sem-musica] [--sem-sfx]
Só depende de numpy.
"""
import argparse, json, wave
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


# ---------------- utilidades ----------------
def ler_wav(caminho):
    with wave.open(caminho, 'rb') as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        dados = w.readframes(n)
    if sw != 2:
        raise SystemExit('narração precisa ser WAV 16 bits')
    x = np.frombuffer(dados, dtype='<i2').astype(np.float32) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:  # reamostragem linear simples
        t = np.arange(int(len(x) * SR / sr)) * sr / SR
        x = np.interp(t, np.arange(len(x)), x).astype(np.float32)
    return x


def gravar_wav(caminho, x):
    x = np.clip(x, -1, 1)
    est = np.stack([x, x], axis=1) if x.ndim == 1 else x
    with wave.open(caminho, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((est * 32767).astype('<i2').tobytes())


def env(n, ataque=0.005, decai=0.2):
    t = np.arange(n) / SR
    a = np.clip(t / max(ataque, 1e-4), 0, 1)
    return a * np.exp(-t / max(decai, 1e-4))


def filtro_fft(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    return np.fft.irfft(X * g, len(x)).astype(np.float32)


def nota(m):  # midi -> Hz
    return 440.0 * 2 ** ((m - 69) / 12)


def somar(dest, sinal, t, ganho=1.0):
    i = int(t * SR)
    if i >= len(dest) or i < 0:
        return
    j = min(len(dest), i + len(sinal))
    dest[i:j] += sinal[: j - i] * ganho


def normal(x, pico=1.0):
    m = np.max(np.abs(x)) or 1.0
    return (x / m * pico).astype(np.float32)


# ---------------- instrumentos ----------------
def kick(d=0.32):
    n = int(d * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t / 0.035)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)).astype(np.float32)


def palma(d=0.18):
    n = int(d * SR)
    ruido = filtro_fft(rng.standard_normal(n).astype(np.float32), lo=900, hi=6000)
    e = env(n, 0.001, 0.05) + 0.5 * env(n, 0.001, 0.012) * (np.arange(n) < SR * 0.02)
    return normal(ruido * e, 0.8)


def chimbal(d=0.05, aberto=False):
    d = 0.18 if aberto else d
    n = int(d * SR)
    ruido = filtro_fft(rng.standard_normal(n).astype(np.float32), lo=7000)
    return normal(ruido * env(n, 0.0005, d / 3), 0.5)


def baixo(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
    return (np.tanh(1.6 * s) * env(n, 0.004, d * 0.6)).astype(np.float32)


def pluck(f, d=0.35, brilho=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum((brilho ** (k - 1)) / k * np.sin(2 * np.pi * f * k * t) for k in range(1, 6))
    return (s * env(n, 0.002, d * 0.35)).astype(np.float32)


def pad(fs, d):
    n = int(d * SR); t = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for f in fs:
        for k, a in ((1, 1), (2, 0.35), (3, 0.15)):
            s += a * np.sin(2 * np.pi * f * k * t * (1 + 0.002 * np.sin(2 * np.pi * 0.3 * t)))
    vol = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    return (s * vol / len(fs)).astype(np.float32)


ESTILOS = {
    # tônica midi, bpm, progressão (graus em semitons a partir da tônica, tríade maior/menor)
    'animado': dict(tonica=60, bpm=104, acordes=[(0, 'M'), (7, 'M'), (9, 'm'), (5, 'M')]),
    'curioso': dict(tonica=57, bpm=96, acordes=[(0, 'm'), (8, 'M'), (3, 'M'), (10, 'M')]),
    'tenso': dict(tonica=62, bpm=90, acordes=[(0, 'm'), (0, 'm'), (8, 'M'), (7, 'M')]),
}


def musica(dur, estilo='animado'):
    cfg = ESTILOS.get(estilo, ESTILOS['animado'])
    batida = 60 / cfg['bpm']; compasso = 4 * batida
    out = np.zeros(int((dur + 3) * SR), np.float32)
    K, P, H, HO = kick(), palma(), chimbal(), chimbal(aberto=True)
    nc = int(dur / compasso) + 2
    for c in range(nc):
        t0 = c * compasso
        grau, tipo = cfg['acordes'][c % len(cfg['acordes'])]
        raiz = cfg['tonica'] + grau
        triade = [raiz, raiz + (4 if tipo == 'M' else 3), raiz + 7]
        intro = c < 2  # 2 compassos só com pad e arpejo
        out_pad = pad([nota(m) for m in triade], compasso + 0.05)
        somar(out, out_pad, t0, 0.18)
        # arpejo em colcheias (sobe e desce) uma oitava acima
        ordem = [0, 1, 2, 1, 0, 2, 1, 2]
        for k in range(8):
            m = triade[ordem[k]] + 12 + (12 if (c % 4 == 3 and k >= 6) else 0)
            somar(out, pluck(nota(m), 0.3), t0 + k * batida / 2, 0.16 if k % 2 == 0 else 0.11)
        if intro:
            continue
        for b in range(4):
            tb = t0 + b * batida
            if b in (0, 2) or (b == 3 and c % 2 == 1):
                somar(out, K, tb if b != 3 else tb + batida / 2, 0.55)
            if b in (1, 3):
                somar(out, P, tb, 0.28)
            somar(out, H, tb + batida / 2, 0.14)
            somar(out, H, tb, 0.07)
            # baixo: tônica nas colcheias com oitava no contratempo
            somar(out, baixo(nota(raiz - 24), batida / 2 * 0.95), tb, 0.32)
            somar(out, baixo(nota(raiz - 12), batida / 2 * 0.9), tb + batida / 2, 0.2)
        if c % 8 == 7:  # virada a cada 8 compassos
            for k in range(4):
                somar(out, P, t0 + 3 * batida + k * batida / 4, 0.18 + 0.04 * k)
            somar(out, HO, t0 + 3.5 * batida, 0.12)
    out = out[: int(dur * SR)]
    fade = int(1.8 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    out[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    return normal(out, 1.0)


# ---------------- efeitos sonoros ----------------
def whoosh(d=0.42, forte=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    ruido = rng.standard_normal(n).astype(np.float32)
    bandas = [filtro_fft(ruido, lo=lo, hi=hi) for lo, hi in ((150, 700), (700, 2500), (2500, 9000))]
    pos = t / d
    pesos = [np.clip(1 - 2 * np.abs(pos - c), 0, 1) for c in (0.25, 0.5, 0.75)]
    s = sum(b * w for b, w in zip(bandas, pesos))
    forma = np.sin(np.pi * np.clip(pos, 0, 1)) ** 1.5
    return normal(s * forma, 0.9 * forma.max() * forte)


def pop(f0=620, d=0.11):
    n = int(d * SR); t = np.arange(n) / SR
    f = f0 * (0.45 + 0.55 * np.exp(-t / 0.025))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.035)
    return normal(s, 0.9)


def ding(f=1320, d=1.1):
    n = int(d * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a, dec in ((1, 1, 0.45), (2.76, 0.45, 0.2), (5.4, 0.25, 0.08), (2, 0.3, 0.3)):
        s += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / dec)
    return normal(s * np.minimum(1, t / 0.002), 0.8)


def clique(d=0.035):
    n = int(d * SR); t = np.arange(n) / SR
    return normal(np.sin(2 * np.pi * 2300 * t) * env(n, 0.0005, 0.008), 0.6)


def baque(d=0.45):
    n = int(d * SR); t = np.arange(n) / SR
    f = 38 + 70 * np.exp(-t / 0.05)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    s[: int(0.012 * SR)] += filtro_fft(rng.standard_normal(int(0.012 * SR)).astype(np.float32), hi=3000) * 0.5
    return normal(s, 1.0)


def ronco(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    s = filtro_fft(rng.standard_normal(n).astype(np.float32), hi=160)
    s = s * (0.6 + 0.4 * np.sin(2 * np.pi * 13 * t)) * np.sin(np.pi * t / d)
    return normal(s, 1.0)


def queda(d=0.55):  # "erro"/parou: tom descendo e áspero
    n = int(d * SR); t = np.arange(n) / SR
    f = 700 * np.exp(-t / 0.22) + 110
    s = np.tanh(3 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.003, 0.25)
    return normal(filtro_fft(s.astype(np.float32), hi=4000), 0.8)


def subida(d=0.35):  # texto entrando
    n = int(d * SR); t = np.arange(n) / SR
    f = 300 + 900 * (t / d) ** 1.5
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * 0.5 + whoosh(d) * 0.6
    return normal(s, 0.8)


def rebobinar(d=0.9):  # fita VHS voltando: guincho agudo subindo e tremendo + chiado + "clack" no início e no fim
    n = int(d * SR); t = np.arange(n) / SR
    f = 380 + 2600 * (t / d) ** 1.3
    f = f * (1 + 0.08 * np.sin(2 * np.pi * 23 * t))
    fase = 2 * np.pi * np.cumsum(f) / SR
    serra = 2 * ((fase / (2 * np.pi)) % 1) - 1
    s = 0.55 * serra * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t))
    s += 0.35 * filtro_fft(rng.standard_normal(n).astype(np.float32), lo=1500, hi=9000)
    s = filtro_fft(s.astype(np.float32), hi=7000) * env(n, 0.02, d * 0.9) * np.minimum(1, (d - t) / 0.05)
    s[: int(0.03 * SR)] += clique(0.03)[: int(0.03 * SR)] * 1.5
    k = clique(0.03); s[-len(k):] += k * 1.2
    return normal(s, 0.85)


def avancar(d=0.5):  # avançar o tempo: "trrrr" agudo acelerado
    n = int(d * SR); t = np.arange(n) / SR
    pulsos = (np.sin(2 * np.pi * (18 + 30 * t / d) * t) > 0.6).astype(np.float32)
    s = pulsos * np.sin(2 * np.pi * (900 + 900 * t / d) * t)
    return normal(filtro_fft(s.astype(np.float32), hi=6000) * np.sin(np.pi * t / d), 0.7)


def brilho(d=0.6):  # a peça acende quando é nomeada: brilho cintilante
    n = int(d * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, f in enumerate((1568, 2093, 2637, 3136)):
        t0 = k * 0.05
        m = t >= t0
        s[m] += np.sin(2 * np.pi * f * (t[m] - t0)) * np.exp(-(t[m] - t0) / 0.18)
    return normal(s, 0.6)


def desaba(d=1.1):  # parede/estrutura desabando: estrondo grave + entulho
    n = int(d * SR); t = np.arange(n) / SR
    s = baque(min(d, 0.6)); s = np.pad(s, (0, n - len(s)))
    ent = filtro_fft(rng.standard_normal(n).astype(np.float32), lo=200, hi=5000) * np.exp(-t / 0.35)
    graos = (rng.random(n) > 0.9993).astype(np.float32) * rng.standard_normal(n).astype(np.float32)
    graos = np.convolve(graos, np.exp(-np.arange(int(0.01 * SR)) / (0.002 * SR)), mode='same') * np.exp(-t / 0.6)
    return normal(s * 0.9 + ent * 0.5 + graos * 0.8, 1.0)


# ---------------- eventos a partir do storyboard ----------------
def eventos(sb):
    ev = []
    cenas = sb.get('cenas', [])
    for i, c in enumerate(cenas):
        a, b = c['inicio'], c['fim']
        dentro = lambda t: t is not None and a + 0.08 < t < b - 0.05
        if i > 0:
            ev.append((a - 0.18, 'whoosh_forte' if c.get('transicao') == 'flash' else 'whoosh'))
        for o in c.get('objetos', []):
            if dentro(o.get('aparece')):
                ev.append((o['aparece'], 'pop'))
        for e in c.get('elementos', []):
            de = e.get('de')
            if not dentro(de):
                continue
            tipo = e.get('tipo')
            if tipo == 'icone' and e.get('icone') == 'avancar':
                ev.append((de, 'avancar')); continue
            ev.append((de, {'termo': 'ding', 'etiqueta': 'clique', 'icone': 'pop_agudo', 'painel': 'clique', 'seta': 'clique'}.get(tipo, 'clique')))
        for e in c.get('efeitos', []):
            de = e.get('de')
            if de is None or not (a - 0.01 <= de < b):
                continue
            tp = e.get('tipo')
            if tp == 'desaba': ev.append((de, 'desaba')); continue
            if tp == 'zoom': ev.append((de, 'baque'))
            elif tp == 'tremor': ev.append((de, 'ronco'))
            elif tp == 'pretoebranco': ev.append((de, 'queda'))
        for o in c.get('objetos', []) + c.get('personagens', []):
            rs = o.get('realce')
            for r in (rs if isinstance(rs, list) else [rs] if rs else []):
                if dentro(r.get('de')): ev.append((r['de'], 'brilho'))
        for tx in c.get('textos', []):
            if tx.get('de') is not None and a - 0.01 <= tx['de'] < b:
                ev.append((tx['de'], 'subida'))
    for r in sb.get('rebobinar', []) or []:
        ev.append((r['em'], 'rebobinar'))
    # vários "pops" juntos viram um só; no máximo um a cada 0,12 s
    ev.sort()
    final, ultimo = [], {}
    for t, k in ev:
        base = 'pop' if k.startswith('pop') else k
        # peças aparecendo em sequência (pontinhos, aletas) viram poucos pops, não uma metralhadora
        if t - ultimo.get(base, -9) < (0.32 if base == 'pop' else 0.3):
            continue
        ultimo[base] = t
        final.append((t, k))
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--storyboard', required=True)
    ap.add_argument('--narracao', required=True)
    ap.add_argument('--saida', required=True)
    ap.add_argument('--estilo', default=None)
    ap.add_argument('--musica', type=float, default=1.0)
    ap.add_argument('--sfx', type=float, default=1.0)
    ap.add_argument('--sem-musica', action='store_true')
    ap.add_argument('--sem-sfx', action='store_true')
    a = ap.parse_args()

    sb = json.load(open(a.storyboard, encoding='utf8'))
    som = sb.get('som') or {}
    estilo = a.estilo or som.get('estilo', 'animado')
    vol_m = a.musica * float(som.get('volumeMusica', 1.0))
    vol_s = a.sfx * float(som.get('volumeEfeitos', 1.0))
    dur = float(sb['duracao'])
    voz = ler_wav(a.narracao)
    n = int(dur * SR)
    voz = np.pad(voz, (0, max(0, n - len(voz))))[:n]

    mix = voz.copy()
    if not a.sem_musica and som.get('musica', True):
        m = musica(dur, estilo)[:n]
        m = np.pad(m, (0, n - len(m)))
        # ducking: envelope da voz (janela de 60 ms, suavizado) abaixa a música na fala
        jan = int(0.06 * SR)
        e = np.sqrt(np.convolve(voz ** 2, np.ones(jan) / jan, mode='same'))
        e = np.convolve(e, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
        fala = np.clip(e / (np.percentile(e, 90) * 0.5 + 1e-6), 0, 1)
        ganho = 0.16 - 0.08 * fala  # ~ -16 dB sob a voz, ~ -10 dB nas pausas
        mix += m * ganho * vol_m
    lista = []
    if not a.sem_sfx and som.get('efeitos', True):
        sons = {
            'whoosh': (whoosh(0.4), 0.22), 'whoosh_forte': (whoosh(0.5, 1.0), 0.32),
            'pop': (None, 0.2), 'pop_agudo': (pop(980, 0.09), 0.18), 'ding': (ding(), 0.2),
            'clique': (clique(), 0.16), 'baque': (baque(), 0.42), 'ronco': (ronco(1.0), 0.4),
            'queda': (queda(), 0.26), 'subida': (subida(), 0.2),
            'rebobinar': (None, 0.34), 'avancar': (avancar(), 0.2), 'brilho': (brilho(), 0.2), 'desaba': (desaba(), 0.45),
        }
        notas_pop = [560, 640, 720, 840]
        for k, (t, nome) in enumerate(eventos(sb)):
            sinal, g = sons[nome]
            if nome == 'pop':
                sinal = pop(notas_pop[k % len(notas_pop)])
            if nome == 'rebobinar':
                r = next((x for x in sb.get('rebobinar', []) if abs(x['em'] - t) < 1e-6), {})
                sinal = rebobinar(float(r.get('duracao', 0.9)))
            somar(mix, sinal, max(0.0, t), g * vol_s)
            lista.append((round(t, 2), nome))
    # limitador suave
    pico = np.max(np.abs(mix))
    if pico > 0.98:
        mix = np.tanh(mix / pico * 1.2) / np.tanh(1.2) * 0.98
    gravar_wav(a.saida, mix)
    print(json.dumps({'estilo': estilo, 'efeitos': len(lista), 'duracao': dur}))


if __name__ == '__main__':
    main()
