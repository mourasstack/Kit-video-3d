"""Sons humanos dos bonecos, sintetizados (sem gravações de terceiros, livres de direitos).

Vozinhas de desenho animado (síntese de formantes: pulso glotal + filtro das vogais), sem palavras:
"oh!", "uau!", "hmm", "ih…", "ai!", risadinha, suspiro, "hã?", "uhum", "ã-ã", esforço, vivas.
E foley do corpo: passos, martelada, pá na terra, gole, palmas.
Cada personagem tem um timbre (altura da voz e tamanho do "trato vocal") conforme o preset.
Só depende de numpy.
"""
import numpy as np

SR = 44100
_rng = np.random.default_rng(11)

# vogais: (F1, F2, F3) em Hz para um adulto médio
VOGAIS = {
    'a': (800, 1250, 2600), 'e': (480, 1900, 2600), 'i': (300, 2300, 3000),
    'o': (500, 900, 2500), 'u': (340, 820, 2300), 'm': (260, 1100, 2400),
}

# timbre por preset: (f0 em Hz, multiplicador de formantes)
TIMBRES = {
    'homem': (118, 1.0), 'construtor': (108, 0.98), 'engenheiro': (125, 1.0), 'servente': (115, 1.0),
    'motorista': (112, 0.99), 'velhinho': (102, 0.97), 'teo': (135, 1.03),
    'mulher': (210, 1.12), 'engenheira': (215, 1.12), 'velhinha': (190, 1.1), 'vovo': (195, 1.1), 'bia': (232, 1.14),
    'crianca': (300, 1.25), 'menina': (320, 1.28),
}
TIMBRE_PADRAO = (150, 1.05)


def timbre(preset, overrides=None):
    f0, k = TIMBRES.get(preset or '', TIMBRE_PADRAO)
    h = (overrides or {}).get('height')
    if isinstance(h, (int, float)) and h < 0.8:  # boneco bem baixinho = voz de criança
        f0, k = max(f0, 280), max(k, 1.22)
    return f0, k


def _formantes(frame_spec, freqs, F, k, nasal=False):
    """Envelope espectral (soma de ressonâncias) para um quadro."""
    env = np.zeros_like(freqs)
    larg = (90, 120, 160)
    ganho = (1.0, 0.55, 0.3) if not nasal else (1.0, 0.12, 0.06)
    for f, b, g in zip(F, larg, ganho):
        f = f * k
        env += g / (1 + ((freqs - f) / (b * k)) ** 2)
    if nasal:
        env *= 1 / (1 + (freqs / 900) ** 4)
    return frame_spec * env


def _vozinha(trechos, f0base, k, sopro=0.08, rouco=0.0):
    """trechos: lista de (dur, vogal_ini, vogal_fim, f0_ini_mult, f0_fim_mult, amp)."""
    total = int(sum(t[0] for t in trechos) * SR) + 1
    f0 = np.zeros(total); amp = np.zeros(total)
    vA = np.zeros((total, 3)); nas = np.zeros(total)
    i = 0
    for dur, va, vb, pa, pb, a in trechos:
        n = int(dur * SR)
        u = np.linspace(0, 1, n, endpoint=False)
        f0[i:i + n] = f0base * (pa + (pb - pa) * u)
        amp[i:i + n] = a
        Fa, Fb = np.array(VOGAIS[va]), np.array(VOGAIS[vb])
        vA[i:i + n] = Fa + (Fb - Fa) * u[:, None]
        nas[i:i + n] = 1.0 if (va == 'm' and vb == 'm') else 0.0
        i += n
    # pulso glotal: dente-de-serra suavizado com micro-variação (soa vivo, não robótico)
    vib = 1 + 0.012 * np.sin(2 * np.pi * 5.5 * np.arange(total) / SR) + 0.006 * _rng.standard_normal(total).cumsum() / np.sqrt(total)
    fase = np.cumsum(f0 * vib) / SR
    glote = (fase % 1.0)
    glote = (1 - glote) ** 3 - 0.25
    fonte = glote + sopro * _rng.standard_normal(total)
    if rouco:
        fonte += rouco * _rng.standard_normal(total) * (np.sin(2 * np.pi * 37 * np.arange(total) / SR) > 0)
    # filtragem por quadros (formantes podem deslizar: "u-a-u")
    N, H = 1024, 256
    jan = np.hanning(N)
    saida = np.zeros(total + N)
    norma = np.zeros(total + N)
    freqs = np.fft.rfftfreq(N, 1 / SR)
    x = np.pad(fonte, (0, N))
    for s in range(0, total, H):
        meio = min(s + N // 2, total - 1)
        spec = np.fft.rfft(x[s:s + N] * jan)
        spec = _formantes(spec, freqs, vA[meio], k, nasal=nas[meio] > 0.5)
        saida[s:s + N] += np.fft.irfft(spec, N) * jan
        norma[s:s + N] += jan ** 2
    y = saida[:total] / np.maximum(norma[:total], 1e-3)
    # envelope: ataque e soltura suaves + amplitude pedida
    a_env = np.convolve(amp, np.ones(int(0.012 * SR)) / int(0.012 * SR), mode='same')
    y *= a_env
    m = np.max(np.abs(y)) or 1
    return (y / m * 0.9).astype(np.float32)


def _sopro(d, F=(800, 1250, 2600), k=1.0, forma='cai'):
    n = int(d * SR)
    x = _rng.standard_normal(n + 1024)
    N, H = 1024, 256
    jan = np.hanning(N); freqs = np.fft.rfftfreq(N, 1 / SR)
    out = np.zeros(n + N); nor = np.zeros(n + N)
    for s in range(0, n, H):
        spec = _formantes(np.fft.rfft(x[s:s + N] * jan), freqs, np.array(F), k)
        out[s:s + N] += np.fft.irfft(spec, N) * jan; nor[s:s + N] += jan ** 2
    y = out[:n] / np.maximum(nor[:n], 1e-3)
    t = np.arange(n) / n
    y *= (np.sin(np.pi * t) ** 0.6) * (1 - 0.7 * t if forma == 'cai' else 0.4 + 0.6 * t)
    return (y / (np.max(np.abs(y)) or 1) * 0.8).astype(np.float32)


def _junta(*partes, pausa=0.0):
    gap = np.zeros(int(pausa * SR), np.float32)
    out = []
    for p in partes:
        out += [p, gap]
    return np.concatenate(out[:-1]) if out else np.zeros(1, np.float32)


# ---------------- vozinhas ----------------
def vocal(nome, f0, k):
    V = lambda tr, **kw: _vozinha(tr, f0, k, **kw)
    if nome == 'oh':        # surpresa
        return V([(0.06, 'o', 'o', 1.25, 1.4, 1), (0.26, 'o', 'o', 1.4, 1.0, 1)])
    if nome == 'uau':       # admiração
        return V([(0.1, 'u', 'u', 1.1, 1.2, 0.8), (0.16, 'u', 'a', 1.2, 1.45, 1), (0.22, 'a', 'u', 1.45, 1.05, 0.9)])
    if nome == 'hmm':       # pensando
        return V([(0.45, 'm', 'm', 1.0, 0.94, 0.8), (0.18, 'm', 'm', 0.94, 1.08, 0.7)], sopro=0.03)
    if nome == 'ih':        # preocupação / "xi"
        return V([(0.08, 'i', 'i', 1.3, 1.35, 0.9), (0.3, 'i', 'i', 1.35, 0.9, 0.8)])
    if nome == 'ai':        # dor / susto ruim
        return V([(0.05, 'a', 'a', 1.6, 1.7, 1), (0.32, 'a', 'i', 1.7, 1.1, 1)], rouco=0.05)
    if nome == 'risada':    # "ha-ha-ha"
        p = []
        for j, m in enumerate((1.5, 1.42, 1.34, 1.25)):
            p.append(_sopro(0.035, k=k) * 0.5)
            p.append(V([(0.085, 'a', 'a', m, m * 0.96, 1)]))
        return _junta(*p, pausa=0.025)
    if nome == 'suspiro':   # cansaço / alívio
        return _junta(_sopro(0.35, (500, 900, 2500), k, 'sobe') * 0.6, _sopro(0.55, (800, 1250, 2600), k, 'cai'), pausa=0.05)
    if nome == 'ha':        # "hã?" dúvida
        return V([(0.32, 'a', 'e', 0.95, 1.4, 0.9)])
    if nome == 'uhum':      # concordando
        return _junta(V([(0.13, 'm', 'm', 1.0, 1.05, 0.8)], sopro=0.02), V([(0.2, 'm', 'm', 1.25, 1.05, 0.9)], sopro=0.02), pausa=0.06)
    if nome == 'aa':        # "ã-ã" negando
        return _junta(V([(0.15, 'm', 'm', 1.15, 1.1, 0.8)], sopro=0.02), V([(0.24, 'm', 'm', 0.98, 0.92, 0.9)], sopro=0.02), pausa=0.07)
    if nome == 'esforco':   # "hnf!" empurrando/carregando
        return V([(0.05, 'e', 'e', 0.95, 1.0, 0.6), (0.18, 'e', 'a', 1.0, 0.85, 1)], sopro=0.25, rouco=0.12)
    if nome == 'vivas':     # "êêê!" comemorando
        return V([(0.08, 'e', 'e', 1.4, 1.6, 0.9), (0.42, 'e', 'e', 1.6, 1.45, 1)])
    raise KeyError(nome)


VOCAIS = ['oh', 'uau', 'hmm', 'ih', 'ai', 'risada', 'suspiro', 'ha', 'uhum', 'aa', 'esforco', 'vivas']


# ---------------- foley do corpo ----------------
def _lp_ruido(n, hi):
    x = _rng.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X[f > hi] = 0
    return np.fft.irfft(X, n)


def passo(peso=1.0):
    n = int(0.09 * SR); t = np.arange(n) / SR
    y = _lp_ruido(n, 900) * np.exp(-t / 0.018) + 0.6 * np.sin(2 * np.pi * (90 * peso) * t) * np.exp(-t / 0.03)
    y += 0.15 * _lp_ruido(n, 5000) * np.exp(-t / 0.006)
    return (y / (np.max(np.abs(y)) or 1) * 0.8).astype(np.float32)


def martelada():
    n = int(0.35 * SR); t = np.arange(n) / SR
    tink = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, d in ((2150, 0.09), (3380, 0.05), (5100, 0.03)))
    y = 0.5 * tink
    y[:int(0.09 * SR)] += passo(1.3)[:int(0.09 * SR)]
    return (y / (np.max(np.abs(y)) or 1) * 0.8).astype(np.float32)


def pazada():
    n = int(0.32 * SR); t = np.arange(n) / SR
    x = _rng.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < 350) | (f > 2600)] = 0
    raspa = np.fft.irfft(X, n) * np.sin(np.pi * np.clip(t / 0.22, 0, 1)) * (t < 0.22)
    y = raspa
    y[int(0.2 * SR):int(0.2 * SR) + int(0.09 * SR)] += passo(0.8) * 0.8
    return (y / (np.max(np.abs(y)) or 1) * 0.8).astype(np.float32)


def gole():
    partes = []
    for f in (420, 380, 450):
        n = int(0.09 * SR); t = np.arange(n) / SR
        partes.append((np.sin(2 * np.pi * (f + 900 * t) * t) * np.exp(-t / 0.03)).astype(np.float32))
    return _junta(*partes, pausa=0.12)


def palmas(qtd=5):
    out = []
    for _ in range(qtd):
        n = int(0.06 * SR); t = np.arange(n) / SR
        x = _rng.standard_normal(n)
        X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); X[(f < 800) | (f > 6000)] = 0
        out.append((np.fft.irfft(X, n) * np.exp(-t / 0.012)).astype(np.float32))
    y = _junta(*out, pausa=0.17)
    return y / (np.max(np.abs(y)) or 1) * 0.8


FOLEY = {'passo': passo, 'martelada': martelada, 'pazada': pazada, 'gole': gole, 'palmas': palmas}

# o que cada animação / expressão "fala" ou faz soar
CLIPE_VOCAL = {'cheer': 'vivas', 'surprised': 'oh', 'think': 'hmm', 'shrug': 'ha', 'look_around': 'ha',
               'nod': 'uhum', 'shake_head': 'aa', 'push': 'esforco', 'carry': 'esforco', 'laugh': 'risada'}
EXPRESSAO_VOCAL = {'surprised': 'oh', 'worried': 'ih', 'sad': 'suspiro', 'thinking': 'hmm', 'laugh': 'risada',
                   'angry': 'aa', 'sleepy': 'suspiro', 'happy': 'uau'}
# foley repetido enquanto a animação dura: (som, intervalo em s)
CLIPE_FOLEY = {'walk': ('passo', 0.5), 'run': ('passo', 0.3), 'hammer': ('martelada', 0.6), 'dig': ('pazada', 0.95),
               'beber': ('gole', 2.0), 'cheer': ('palmas', 9.0)}
TODOS = VOCAIS + list(FOLEY)


# ---------------- banco de sons gravados (ElevenLabs etc.) ----------------
# Se existir assets/sons/bonecos/<grupo>/<nome>.wav (ou <nome>_1.wav, <nome>_2.wav… para variar),
# ele é usado no lugar do som sintetizado. Grupos de voz: homem, mulher, crianca. Corpo: corpo/<nome>.wav.
import os, glob
BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'sons', 'bonecos')
GRUPO = {'homem': 'homem', 'construtor': 'homem', 'engenheiro': 'homem', 'servente': 'homem', 'motorista': 'homem',
         'velhinho': 'homem', 'teo': 'homem', 'mulher': 'mulher', 'engenheira': 'mulher', 'velhinha': 'mulher',
         'vovo': 'mulher', 'bia': 'mulher', 'crianca': 'crianca', 'menina': 'crianca'}


def grupo(preset, overrides=None):
    h = (overrides or {}).get('height')
    if isinstance(h, (int, float)) and h < 0.8:
        return 'crianca'
    return GRUPO.get(preset or '', 'homem')


def arquivos(nome, grp):
    pasta = os.path.join(BANCO, 'corpo' if nome in FOLEY else grp)
    return sorted(glob.glob(os.path.join(pasta, f'{nome}.wav')) + glob.glob(os.path.join(pasta, f'{nome}_*.wav')))
