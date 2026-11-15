"""Alinha um áudio gravado com o texto do roteiro (tempo por palavra).
Corta o áudio nas pausas, transcreve cada trecho com Whisper (sherpa-onnx), casa o texto
com o roteiro e distribui as palavras dentro de cada trecho, proporcional ao tamanho."""
import argparse, difflib, json, re, subprocess
import numpy as np
import sherpa_onnx


def norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s)


def carregar(arq):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def segmentos(x, sr=16000, min_sil=0.12, min_fala=0.08):
    h = int(sr * 0.01)
    n = len(x) // h
    e = np.sqrt(np.mean(x[:n * h].reshape(n, h) ** 2, axis=1) + 1e-12)
    ed = 20 * np.log10(e)
    lim = max(np.percentile(ed, 10) + 12, np.percentile(ed, 95) - 32)
    fala = ed > lim
    segs, k = [], 0
    while k < n:
        if not fala[k]:
            k += 1
            continue
        a, sil = k, 0
        while k < n:
            if fala[k]:
                sil = 0
            else:
                sil += 1
                if sil * 0.01 >= min_sil:
                    break
            k += 1
        b = k - sil
        if (b - a) * 0.01 >= min_fala:
            segs.append([a * 0.01, b * 0.01])
    out = []  # junta pedaços curtos para o Whisper ter contexto
    for sg in segs:
        if out and (sg[1] - sg[0] < 0.6 or out[-1][1] - out[-1][0] < 0.6) and sg[0] - out[-1][1] < 0.25:
            out[-1][1] = sg[1]
        else:
            out.append(sg)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--texto", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--modelo", required=True)
    a = ap.parse_args()
    tokens = open(a.texto, encoding="utf-8").read().split()
    m = a.modelo
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=f"{m}-encoder.int8.onnx", decoder=f"{m}-decoder.int8.onnx", tokens=f"{m}-tokens.txt",
        language="pt", num_threads=2)
    sr = 16000
    x = carregar(a.audio)
    duracao = len(x) / sr
    segs = segmentos(x)
    reco = []
    for si, (t0, t1) in enumerate(segs):
        p0, p1 = max(0, int((t0 - 0.05) * sr)), min(len(x), int((t1 + 0.05) * sr))
        st = rec.create_stream()
        st.accept_waveform(sr, x[p0:p1])
        rec.decode_stream(st)
        for w in st.result.text.split():
            n = norm(w)
            if n:
                reco.append((n, si))
    alvo = [norm(t) for t in tokens]
    seg = [None] * len(tokens)
    sm = difflib.SequenceMatcher(None, alvo, [r[0] for r in reco], autojunk=False)
    for bl in sm.get_matching_blocks():
        for k in range(bl.size):
            seg[bl.a + k] = reco[bl.b + k][1]
    casadas = sum(v is not None for v in seg)
    for k in range(len(tokens)):
        if seg[k] is None:
            ant = next((seg[j] for j in range(k - 1, -1, -1) if seg[j] is not None), None)
            prox = next((seg[j] for j in range(k + 1, len(tokens)) if seg[j] is not None), None)
            if ant is None:
                seg[k] = prox if prox is not None else 0
            elif prox is None or not re.search(r"[.!?]$", tokens[k - 1]):
                seg[k] = ant
            else:
                seg[k] = prox
    for k in range(1, len(tokens)):
        seg[k] = max(seg[k], seg[k - 1])
    grupos = {}
    for k, s_ in enumerate(seg):
        grupos.setdefault(s_, []).append(k)
    chaves = sorted(grupos)
    ini, fim = [0.0] * len(tokens), [0.0] * len(tokens)
    for i, s_ in enumerate(chaves):
        ks = grupos[s_]
        t0 = segs[s_][0]
        ultimo = (chaves[i + 1] - 1) if i + 1 < len(chaves) else len(segs) - 1
        t1 = segs[ultimo][1]
        pesos = [len(alvo[k]) + 2 for k in ks]
        tot, c = sum(pesos), t0
        for k, p in zip(ks, pesos):
            d = (t1 - t0) * p / tot
            ini[k], fim[k] = c, c + d
            c += d
    out = []
    for k, tok in enumerate(tokens):
        out.append({"palavra": tok, "inicio": round(ini[k], 3), "fim": round(max(fim[k], ini[k] + 0.05), 3)})
    json.dump(out, open(a.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"palavras": len(out), "casadas": casadas, "cobertura": round(casadas / len(tokens), 3),
                      "trechos": len(segs), "duracaoAudio": round(duracao, 3)}))


main()
