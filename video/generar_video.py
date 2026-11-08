import math, os, random, subprocess, wave, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
W, H, FPS = 1280, 720, 25
SR = 22050

FD = os.path.join(HERE, "font0.ttf")      # Fredoka
FB = os.path.join(HERE, "font1.ttf")      # Atkinson regular
def font(p, s): return ImageFont.truetype(p, s)

ABYSS = (6, 26, 43); SEA = (11, 49, 80); FOAM = (232, 246, 251)
KELP = (159, 216, 196); MATEO = (255, 179, 71); LUCIA = (127, 214, 255); MUTED = (143, 179, 199)
COL = {"m": MATEO, "l": LUCIA}
NAME = {"m": "Mateo", "l": "Lucía"}
VOICE = {"m": ["-v", "es-419+m3", "-p", "68", "-s", "150"],
         "l": ["-v", "es-419+f4", "-p", "92", "-s", "150"]}

# (quién, texto en pantalla, texto hablado o None = igual)
DIALOGO = [
 ("m", "Lucía, ¿sabías que los tiburones son más antiguos que los árboles?", None),
 ("l", "¿Qué? ¡No puede ser! Los árboles siempre han estado ahí.", None),
 ("m", "¡Pues no! Hace más de 400 millones de años los primeros tiburones ya nadaban en los mares. Los primeros árboles aparecieron hace unos 385 millones de años.", None),
 ("l", "O sea que cuando nació el primer árbol, los tiburones ya llevaban un montón de tiempo nadando.", None),
 ("m", "¡Exacto! Y son todavía más antiguos que los dinosaurios.", None),
 ("l", "¿Más que el T. rex?", "¿Más que el tiranosaurio rex?"),
 ("m", "Muchísimo más. Además han sobrevivido a varias extinciones masivas, esas veces en que casi toda la vida de la Tierra desapareció. ¡Y ellos siguieron nadando!", None),
 ("l", "¡Qué fuertes! ¿Y cómo saben todo eso los científicos? ¿Encuentran sus huesos?", None),
 ("m", "Ahí está lo curioso: los tiburones casi no tienen huesos. Su esqueleto es de cartílago, como lo que tenemos en la nariz y en las orejas.", None),
 ("l", "(tocándose la oreja) ¿Esto? Es blandito.", "¿Esto? Es blandito."),
 ("m", "Sí, y por eso casi no deja fósiles. Casi todo lo que sabemos de ellos viene de sus dientes, que sí son duros y se conservan.", None),
 ("l", "Entonces los dientes son como las pistas de un detective.", None),
 ("m", "¡Justo! Pero hay algo triste: hoy muchos tiburones están en peligro.", None),
 ("l", "¿Por qué? Si sobrevivieron a todo…", "¿Por qué? Si sobrevivieron a todo."),
 ("m", "Por la pesca excesiva, la contaminación y porque destruimos los lugares donde viven.", None),
 ("l", "Entonces tenemos que cuidarlos.", None),
 ("m", "Sí. Cuidar a los tiburones es proteger a uno de los sobrevivientes más antiguos de la Tierra.", None),
 ("l", "Ya no les voy a tener tanto miedo. Les voy a tener respeto.", None),
]
LINEA_T = [
 ("m", "Primeros tiburones: hace unos 420 millones de años.", "420", "Primeros tiburones", MATEO, 1.0),
 ("l", "Primeros árboles: hace unos 385 millones de años.", "385", "Primeros árboles", KELP, 385/420),
 ("m", "Primeros dinosaurios: hace unos 230 millones de años.", "230", "Primeros dinosaurios", LUCIA, 230/420),
 ("l", "¡Y los humanos llevamos apenas 300 mil años!", "0,3", "Humanos", FOAM, 0.012),
]
FINAL = ("l", "¡Cuidemos a los tiburones!")

# ---------- audio ----------
def tts(who, text, path):
    subprocess.run(["espeak-ng", *VOICE[who], "-w", path, text], check=True, stderr=subprocess.DEVNULL)
    with wave.open(path) as w:
        assert w.getframerate() == SR
        return w.readframes(w.getnframes())

clips = []  # (start_s, pcm, who, kind, idx)
t = 5.0
for i, (who, txt, spoken) in enumerate(DIALOGO):
    pcm = tts(who, spoken or txt, os.path.join(HERE, f"a_{i}.wav"))
    clips.append((t, pcm, who, "d", i)); t += len(pcm) / 2 / SR + 0.9
chat_end = t + 0.8
t = chat_end + 1.6
for i, (who, txt, *_r) in enumerate(LINEA_T):
    pcm = tts(who, txt, os.path.join(HERE, f"b_{i}.wav"))
    clips.append((t, pcm, who, "t", i)); t += len(pcm) / 2 / SR + 0.7
tl_end = t + 1.2
fin_start = tl_end + 0.6
pcm = tts(FINAL[0], FINAL[1], os.path.join(HERE, "c.wav"))
clips.append((fin_start + 0.8, pcm, FINAL[0], "f", 0))
TOTAL = fin_start + 0.8 + len(pcm) / 2 / SR + 2.5

buf = bytearray(int(TOTAL * SR) * 2)
for st, pcm, *_ in clips:
    o = int(st * SR) * 2
    buf[o:o + len(pcm)] = pcm
with wave.open(os.path.join(HERE, "voz.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(buf))

def speaking(kind, idx, tt):
    for st, pcm, who, k, i in clips:
        if k == kind and i == idx:
            return st, st + len(pcm) / 2 / SR
    return None

# ---------- drawing helpers ----------
bg = Image.new("RGB", (W, H))
bd = ImageDraw.Draw(bg)
for y in range(H):
    f = min(1, y / (H * 0.8))
    bd.line([(0, y), (W, y)], fill=tuple(int(SEA[c] + (ABYSS[c] - SEA[c]) * f) for c in range(3)))

rnd = random.Random(7)
BUBS = [(rnd.random() * W, rnd.random() * H, 1 + rnd.random() * 4, 15 + rnd.random() * 40) for _ in range(60)]
SHARK = [(90, 0), (60, -18), (0, -16), (-12, -48), (-30, -14), (-70, -10), (-100, -4), (-130, -34), (-118, 0),
         (-132, 30), (-100, 6), (-40, 18), (10, 14), (-6, 34), (28, 14), (70, 14)]

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def pop(x):
    x = max(0, min(1, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def draw_bg(img, tt):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for x, y, r, v in BUBS:
        yy = (y - v * tt) % (H + 20) - 10
        xx = x + math.sin(tt * 0.7 + y) * 4
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(232, 246, 251, 45))
    period = 26
    sx = -220 + ((tt % period) / period) * (W + 440)
    sy = H * 0.74 + math.sin(tt * 0.5) * 14
    wag = math.sin(tt * 5) * 6
    pts = [(sx + px * 1.3, sy + (py + (wag if i in (7, 9) else 0)) * 1.3) for i, (px, py) in enumerate(SHARK)]
    d.polygon(pts, fill=(143, 179, 199, 50))
    img.alpha_composite(ov)

def avatar(d, cx, cy, r, who, mouth_open=False):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=COL[who])
    s = r / 22
    hair = (91, 52, 19) if who == "m" else (42, 26, 61)
    if who == "m":
        d.chord([cx - 18 * s, cy - 22 * s, cx + 18 * s, cy + 2 * s], 180, 360, fill=hair)
    else:
        d.chord([cx - 19 * s, cy - 22 * s, cx + 19 * s, cy + 6 * s], 180, 360, fill=hair)
        for ex in (-17, 17):
            d.ellipse([cx + (ex - 4) * s, cy + 1 * s, cx + (ex + 4) * s, cy + 9 * s], fill=hair)
    for ex in (-6, 6):
        d.ellipse([cx + (ex - 2.6) * s, cy + 0.5 * s, cx + (ex + 2.6) * s, cy + 5.7 * s], fill=ABYSS)
    if mouth_open:
        d.ellipse([cx - 4 * s, cy + 8 * s, cx + 4 * s, cy + 15 * s], fill=ABYSS)
    else:
        d.arc([cx - 7 * s, cy + 4 * s, cx + 7 * s, cy + 13 * s], 20, 160, fill=ABYSS, width=max(2, int(2.4 * s)))

def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if f.getlength(test) <= maxw: cur = test
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def center(d, y, text, f, fill):
    d.text(((W - f.getlength(text)) / 2, y), text, font=f, fill=fill)

# ---------- chat layout ----------
F_TXT = font(FB, 29); F_NAME = font(FD, 21)
LH = 38; PADX, PADY = 22, 14; AV = 34; MAXW = 820
lay = []
for who, txt, _ in DIALOGO:
    lines = wrap(txt, F_TXT, MAXW - 2 * PADX)
    bw = max(F_TXT.getlength(l) for l in lines) + 2 * PADX
    bw = max(bw, F_NAME.getlength(NAME[who]) + 2 * PADX)
    bh = PADY * 2 + 26 + LH * len(lines)
    lay.append((lines, bw, bh))
GAP = 18
ys, acc = [], 0
for _, _, bh in lay: ys.append(acc); acc += bh + GAP
D_START = [c[0] for c in clips if c[3] == "d"]
BOTTOM = H - 40

def chat_frame(img, tt):
    d = ImageDraw.Draw(img)
    shown = [i for i, s in enumerate(D_START) if tt >= s - 0.25]
    if not shown: return
    last = shown[-1]
    # scroll target so the last bubble bottom sits at BOTTOM; ease toward it
    def target(k): return max(0, ys[k] + lay[k][2] - (BOTTOM - 40))
    prev = target(last - 1) if last > 0 else 0
    p = ease((tt - (D_START[last] - 0.25)) / 0.5)
    off = prev + (target(last) - prev) * p
    for i in shown:
        lines, bw, bh = lay[i]
        who = DIALOGO[i][0]
        y = 40 + ys[i] - off
        if y + bh < -10 or y > H: continue
        sc = pop((tt - (D_START[i] - 0.25)) / 0.45)
        sp = speaking("d", i, tt)
        talking = sp and sp[0] <= tt <= sp[1]
        mo = talking and int(tt * 8) % 2 == 0
        bob = math.sin(tt * 12) * 3 if talking else 0
        if who == "m":
            ax = 70 + AV; bx = ax + AV + 16
        else:
            ax = W - 70 - AV; bx = ax - AV - 16 - bw
        ay = y + bh - AV
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        c = COL[who]
        ld.rounded_rectangle([bx, y, bx + bw, y + bh], radius=22, fill=(232, 246, 251, 26 if not talking else 40), outline=c, width=3)
        ld.text((bx + PADX, y + PADY - 2), NAME[who], font=F_NAME, fill=c)
        for k, l in enumerate(lines):
            col = MUTED if l.startswith("(") else FOAM
            if "(tocándose" in l:
                part = "(tocándose la oreja)"; rest = l[len(part):]
                ld.text((bx + PADX, y + PADY + 26 + k * LH), part, font=F_TXT, fill=MUTED)
                ld.text((bx + PADX + F_TXT.getlength(part), y + PADY + 26 + k * LH), rest, font=F_TXT, fill=FOAM)
            else:
                ld.text((bx + PADX, y + PADY + 26 + k * LH), l, font=F_TXT, fill=col)
        avatar(ld, ax, ay + bob, AV, who, mo)
        if sc < 0.999:
            cx, cy = (ax, ay)
            layer = layer.transform((W, H), Image.AFFINE, (1 / sc, 0, cx - cx / sc, 0, 1 / sc, cy - cy / sc), resample=Image.BILINEAR)
            a = layer.getchannel("A").point(lambda v: int(v * max(0, min(1, sc))))
            layer.putalpha(a)
        img.alpha_composite(layer)
    # typing dots for the next speaker
    nxt = last + 1
    if nxt < len(DIALOGO):
        sp = speaking("d", last, tt)
        if sp and tt > sp[1] and tt < D_START[nxt] - 0.25:
            who = DIALOGO[nxt][0]
            y = 40 + ys[last] + lay[last][2] + GAP - off
            y = min(y, BOTTOM - 10)
            bw, bh = 110, 56
            if who == "m": ax = 70 + AV; bx = ax + AV + 16
            else: ax = W - 70 - AV; bx = ax - AV - 16 - bw
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
            ld.rounded_rectangle([bx, y, bx + bw, y + bh], radius=22, fill=(232, 246, 251, 26), outline=COL[who], width=3)
            for k in range(3):
                ph = math.sin(tt * 7 - k * 0.9)
                cx = bx + 30 + k * 25; cy = y + bh / 2 - ph * 4
                ld.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=COL[who] + (int(140 + 110 * ph),))
            avatar(ld, ax, y + bh - AV + 6, AV, who)
            img.alpha_composite(layer)

def fade(img, a):
    if a >= 1: return
    ov = Image.new("RGBA", (W, H), ABYSS + (int(255 * (1 - max(0, a))),))
    img.alpha_composite(ov)

F_EYE = font(FD, 26); F_H1 = font(FD, 64); F_SUB = font(FB, 30); F_MA = font(FD, 36); F_SM = font(FB, 20); F_BAR = font(FD, 28)

def title_frame(img, tt):
    d = ImageDraw.Draw(img)
    a = ease(tt / 0.8)
    lay_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay_)
    center(ld, 170, "UNA CHARLA EN EL RECREO", F_EYE, KELP)
    l1 = "¿Sabías que los tiburones son"
    l2a, l2b = "más antiguos que los ", "árboles?"
    center(ld, 230, l1, F_H1, FOAM)
    x0 = (W - F_H1.getlength(l2a + l2b)) / 2
    ld.text((x0, 310), l2a, font=F_H1, fill=FOAM)
    ld.text((x0 + F_H1.getlength(l2a), 310), l2b, font=F_H1, fill=MATEO)
    avatar(ld, W / 2 - 110, 500 + math.sin(tt * 3) * 5, 50, "m")
    avatar(ld, W / 2 + 110, 500 + math.sin(tt * 3 + 1.5) * 5, 50, "l")
    center(ld, 575, "Mateo  y  Lucía", F_SUB, MUTED)
    al = lay_.getchannel("A").point(lambda v: int(v * a)); lay_.putalpha(al)
    img.alpha_composite(lay_)

T_STARTS = [c[0] for c in clips if c[3] == "t"]
def timeline_frame(img, tt):
    lay_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay_)
    center(ld, 70, "¿Quién llegó primero?", F_H1, FOAM)
    center(ld, 150, "millones de años atrás", F_SUB, MUTED)
    x0, x1 = 300, W - 90
    for i, (who, _, ma, lab, col, frac) in enumerate(LINEA_T):
        y = 230 + i * 105
        st = T_STARTS[i]
        if tt < st - 0.2: continue
        g = ease((tt - st + 0.2) / 1.4)
        ld.text((x0 - 30 - F_MA.getlength(ma), y + 6), ma, font=F_MA, fill=KELP)
        bw = max(14, (x1 - x0) * frac * g)
        ld.rounded_rectangle([x0, y, x0 + bw, y + 62], radius=12, fill=col)
        if frac > 0.3:
            ld.text((x0 + 18, y + 14), lab, font=F_BAR, fill=ABYSS)
        else:
            ld.text((x0 + bw + 16, y + 14), lab, font=F_BAR, fill=FOAM)
    img.alpha_composite(lay_)

FIN_SP = [c for c in clips if c[3] == "f"][0]
def final_frame(img, tt):
    lay_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay_)
    center(ld, 160, "Los tiburones sobrevivieron", F_H1, FOAM)
    center(ld, 240, "a casi todo en 400 millones de años.", F_H1, FOAM)
    center(ld, 345, "Ahora nos toca cuidarlos.", F_H1, MATEO)
    st, en = FIN_SP[0], FIN_SP[0] + len(FIN_SP[1]) / 2 / SR
    talk = st <= tt + fin_start <= en
    avatar(ld, W / 2 - 110, 520 + math.sin(tt * 3) * 5, 50, "m")
    avatar(ld, W / 2 + 110, 520 + (math.sin(tt * 12) * 4 if talk else 0), 50, "l", talk and int(tt * 8) % 2 == 0)
    a = ease(tt / 0.8)
    al = lay_.getchannel("A").point(lambda v: int(v * a)); lay_.putalpha(al)
    img.alpha_composite(lay_)

# ---------- render ----------
bg_rgba = bg.convert("RGBA")
N = int(TOTAL * FPS)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", os.path.join(HERE, "voz.wav"), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                       "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
for n in range(N):
    tt = n / FPS
    img = bg_rgba.copy()
    draw_bg(img, tt)
    if tt < 5.0:
        title_frame(img, tt)
        fade(img, min(1, (5.0 - tt) / 0.5) if tt > 4.5 else 1)
    elif tt < chat_end + 0.6:
        chat_frame(img, tt)
        if tt < 5.4: fade(img, (tt - 5.0) / 0.4)
        if tt > chat_end: fade(img, 1 - (tt - chat_end) / 0.6)
    elif tt < fin_start:
        timeline_frame(img, tt)
        if tt > tl_end: fade(img, 1 - (tt - tl_end) / 0.6)
    else:
        final_frame(img, tt - fin_start)
        if tt > TOTAL - 1: fade(img, TOTAL - tt)
    ff.stdin.write(img.convert("RGB").tobytes())
    if n % 250 == 0: print(f"{n}/{N}", flush=True)
ff.stdin.close(); ff.wait()
print("duración", round(TOTAL, 1), "s")
