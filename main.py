import io, json, os, random, threading, time
from urllib.parse import quote
import requests
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

TK = "9105676237:AAF7YRYP2ntV9NENs4PzpSS4UIVYghbdH_4"
TU = f"https://api.telegram.org/bot{TK}"
A1 = "https://us-central1-llmchat-22d7a.cloudfunctions.net/generate"
A2 = "https://text.pollinations.ai/openai"
IB = "https://image.pollinations.ai/prompt/"
AD = 8838998677
DF = os.path.join(os.path.expanduser("~"), "hdb.json")
um, md, db = {}, {}, {"u": [AD], "p": None, "t": None}

if os.path.exists(DF):
    try: db.update(json.load(open(DF)))
    except: pass

def sdb():
    try: json.dump(db, open(DF, "w"))
    except: pass

def tg(m, d=None, f=None):
    try: return requests.post(f"{TU}/{m}", data=d, files=f, timeout=30).json()
    except: return {}

def sm(c, t, k=None):
    d = {"chat_id": c, "text": str(t).replace("*", "")[:4000] or "..."}
    if k: d["reply_markup"] = k
    return tg("sendMessage", d).get("result", {}).get("message_id")

def em(c, i, t):
    t = str(t).replace("*", "")[:4000] or "..."
    if i: tg("editMessageText", {"chat_id": c, "message_id": i, "text": t})
    else: sm(c, t)

def ai(c, p, m=True):
    sp = "Sen Humo AI (Argon) tahlilchisan. Yulduzcha (*) ishlatma. Aniq statistika bilan o'zbekcha yoz."
    h = um.get(c, [])[-4:] if m else []
    try:
        ms = [{"role": "system", "content": sp}] + [{"role": k, "content": v} for x in h for k, v in [("user", x["u"]), ("assistant", x["a"])]] + [{"role": "user", "content": p}]
        r = requests.post(A2, json={"model": "openai", "messages": ms}, timeout=20)
        if r.status_code == 200:
            a = r.json()["choices"][0]["message"]["content"].replace("*", "").strip()
            if a:
                if m: um[c] = (h + [{"u": p, "a": a}])[-4:]
                return a
    except: pass
    try:
        cx = sp + "\n" + "\n".join(f"U:{x['u']}\nA:{x['a']}" for x in h) + f"\nU:{p}\nA:"
        r = requests.post(A1, json={"input": cx, "app-name": "notebook", "version": "1", "platform": "mobile"}, headers={"qtcy6-key": "bOBHq59mhSJ7aPK5Ut4k"}, timeout=25).json()
        a = str(r.get("output") or r.get("response") or "").replace("*", "").strip()
        if a:
            if m: um[c] = (h + [{"u": p, "a": a}])[-4:]
            return a
    except: pass
    return "Server band, qayta yozing."

def tr(t):
    try:
        r = requests.get("https://translate.googleapis.com/translate_a/single", params={"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": t}, timeout=5)
        return "".join(i[0] for i in r.json()[0] if i[0])
    except: return t

def gim(p, w=1024):
    for m in ["flux", "turbo"]:
        try:
            r = requests.get(f"{IB}{quote(p)}?width={w}&height={w}&seed={random.randint(1,99999)}&nologo=true&model={m}", timeout=35)
            if r.status_code == 200 and len(r.content) > 3000: return r.content
        except: pass
    return None
def m_im(c, t):
    i = sm(c, "🎨 8K Rasm chizilmoqda...")
    im = gim(f"{tr(t)}, photorealistic, 8k")
    tg("deleteMessage", {"chat_id": c, "message_id": i})
    if im: tg("sendPhoto", {"chat_id": c, "caption": f"🖼 {t}\n✨ Humo AI"}, {"photo": ("i.jpg", im, "image/jpeg")})
    else: sm(c, "Server band.")

def m_vd(c, t):
    i = sm(c, "🎬 Video tayyorlanmoqda...")
    im = gim(f"cinematic, {tr(t)}, 8k", 768)
    tg("deleteMessage", {"chat_id": c, "message_id": i})
    if not im:
        sm(c, "Server band.")
        return
    try:
        b = Image.open(io.BytesIO(im)).convert("RGB")
        w, h = b.size
        fs = [b.crop(((w - int(w * (1 - 0.008 * k))) // 2, (h - int(h * (1 - 0.008 * k))) // 2, (w + int(w * (1 - 0.008 * k))) // 2, (h + int(h * (1 - 0.008 * k))) // 2)).resize((480, 480)) for k in range(18)]
        lp = fs + fs[::-1]
        bf = io.BytesIO()
        lp[0].save(bf, format="GIF", save_all=True, append_images=lp[1:], duration=50, loop=0)
        bf.seek(0)
        tg("sendAnimation", {"chat_id": c, "caption": f"🎬 {t}\n✨ Humo AI"}, {"animation": ("v.gif", bf.read(), "image/gif")})
    except: sm(c, "Xatolik.")

def m_px(c, t):
    mid = sm(c, "📊 Prezentatsiya tuzilmoqda...")
    raw = ai(c, f"Mavzu: '{t}'. O'zbekcha 5 ta slaydga faqat JSON ber:\n" + '{"title":"...","slides":[{"title":"...","points":["...","...","..."]}]}', False)
    try: pl = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
    except: pl = {"title": t, "slides": [{"title": t, "points": [raw[:200]]}]}
    pr = Presentation()
    pr.slide_width, pr.slide_height = Inches(13.33), Inches(7.5)
    bl = pr.slide_layouts[6]
    dk, ac, bg, wh, ik = RGBColor(15, 23, 42), RGBColor(20, 184, 166), RGBColor(245, 247, 250), RGBColor(255, 255, 255), RGBColor(30, 41, 59)
    s1 = pr.slides.add_slide(bl)
    s1.background.fill.solid()
    s1.background.fill.fore_color.rgb = dk
    r = s1.shapes.add_textbox(Inches(1), Inches(2.3), Inches(11), Inches(2.5)).text_frame.paragraphs[0].add_run()
    r.text, r.font.size, r.font.bold, r.font.color.rgb = pl.get("title", t), Pt(42), True, wh
    for sd in pl.get("slides", []):
        s = pr.slides.add_slide(bl)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = bg
        hd = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.33), Inches(1.3))
        hd.fill.solid()
        hd.fill.fore_color.rgb = dk
        hr = s.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(11.5), Inches(0.9)).text_frame.paragraphs[0].add_run()
        hr.text, hr.font.size, hr.font.bold, hr.font.color.rgb = str(sd.get("title", "")), Pt(28), True, wh
        for idx, pt in enumerate(sd.get("points", [])[:4]):
            y = 1.65 + idx * 1.35
            cd = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(y), Inches(11.7), Inches(1.1))
            cd.fill.solid()
            cd.fill.fore_color.rgb = wh
            cd.line.color.rgb = ac
            tb = s.shapes.add_textbox(Inches(1.1), Inches(y + 0.15), Inches(11.1), Inches(0.85)).text_frame
            tb.word_wrap = True
            cr = tb.paragraphs[0].add_run()
            cr.text, cr.font.size, cr.font.color.rgb = f"• {pt}", Pt(18), ik
    bf = io.BytesIO()
    pr.save(bf)
    bf.seek(0)
    tg("deleteMessage", {"chat_id": c, "message_id": mid})
    tg("sendDocument", {"chat_id": c, "caption": f"📊 {t}\n✨ Humo AI"}, {"document": ("Slayd.pptx", bf.read(), "application/vnd.openxmlformats-officedocument.presentationml.presentation")})

def kb(c):
    r = [[{"text": "📊 Prezentatsiya"}, {"text": "🎬 Video yaratish"}], [{"text": "🎨 Rasm chizish"}, {"text": "🧹 Tozalash"}]]
    if c == AD: r.append([{"text": "👑 Admin"}, {"text": "📢 Reklama"}])
    return json.dumps({"keyboard": r, "resize_keyboard": True})

def hdl(m):
    c = m.get("chat", {}).get("id")
    if not c: return
    if c not in db["u"]:
        db["u"].append(c)
        sdb()
    tx, ph, k = m.get("text") or m.get("caption") or "", m.get("photo"), kb(c)
    if c == AD:
        mo = md.get(c, "")
        if tx in ["👑 Admin", "/stat"]:
            sm(c, f"👑 Jami: {len(db['u'])} ta\n/setphoto - Rasm\n/settext - Matn\n/reklama - E'lon", k)
            return
        if tx in ["📢 Reklama", "/reklama"]:
            md[c] = "rk"
            sm(c, "📢 E'lonni yuboring:")
            return
        if tx in ["/setphoto", "/settext"]:
            md[c] = tx[1:]
            sm(c, "Yuboring:")
            return
        if mo == "setphoto" and ph:
            db["p"], md[c] = ph[-1]["file_id"], ""
            sdb()
            sm(c, "✅ Saqlandi!", k)
            return
        if mo == "settext" and tx:
            db["t"], md[c] = tx, ""
            sdb()
            sm(c, "✅ Saqlandi!", k)
            return
        if mo == "rk":
            md[c], n = "", 0
            for u in list(db["u"]):
                r = tg("sendPhoto", {"chat_id": u, "photo": ph[-1]["file_id"], "caption": tx}) if ph else tg("sendMessage", {"chat_id": u, "text": f"📢 {tx}"})
                if r.get("ok"): n += 1
            sm(c, f"✅ {n} kishiga bordi!", k)
            return
    if not tx: return
    if tx == "/start":
        um[c], md[c] = [], ""
        wt = db.get("t") or "Assalomu alaykum! Humo AI 24/7 tayyor:"
        if db.get("p"): tg("sendPhoto", {"chat_id": c, "photo": db["p"], "caption": wt, "reply_markup": k})
        else: sm(c, wt, k)
    elif tx in ["📊 Prezentatsiya", "🎬 Video yaratish", "🎨 Rasm chizish"]:
        md[c] = tx[:2]
        sm(c, "Mavzuni yozing:")
    elif tx == "🧹 Tozalash":
        um[c] = []
        sm(c, "Tozalandi.")
    else:
        mo = md.get(c, "")
        md[c] = ""
        if mo == "📊 ": m_px(c, tx)
        elif mo == "🎨 ": m_im(c, tx)
        elif mo == "🎬 ": m_vd(c, tx)
        else:
            i = sm(c, "⚡ O'ylamoqda...")
            em(c, i, ai(c, tx))

tg("deleteWebhook", {"drop_pending_updates": "true"})
of = 0
print("🚀 HUMO AI 24/7 ISHGA TUSHDI!")
while True:
    try:
        for x in requests.get(f"{TU}/getUpdates", params={"offset": of, "timeout": 25}, timeout=35).json().get("result", []):
            of = x["update_id"] + 1
            if x.get("message"): threading.Thread(target=hdl, args=(x["message"],), daemon=True).start()
    except: time.sleep(1)
