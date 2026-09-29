import os, re, json, sqlite3, random, hashlib, httpx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from trades import TRADES, BUYERS, PROVIDERS, TESTIMONY
T = {t["id"]: t for t in TRADES}
app = FastAPI(title="PathPal")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "pathpal.db")
DIST = ["Villupuram", "Barmer", "Gaya", "Nuh"]
SAATHIS = ["Kalpana (ASHA worker)", "Ravi (CSC operator)", "Fatima (SHG leader)", "Suresh (volunteer)"]

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c
def init():
    c = db(); c.execute("create table if not exists p(id integer primary key, district text, trade text, stage text, kind text default 'build')")
    if c.execute("select count(*) from p").fetchone()[0] == 0:  # MOCK seed data
        r = random.Random(1)
        for _ in range(60):
            c.execute("insert into p(district,trade,stage,kind) values(?,?,?,?)", (r.choice(DIST), r.choice(["tailor","mobile","beauty","food"]), r.choice(["profiled","enrolled","certified","placed"]), r.choices(["build","upgrade","leap"], weights=[5,3,2])[0]))
    c.commit(); c.close()
init()

LIKE = re.compile(r"like|want|interest|love|dream|पसंद|चाहत|चाहता|चाहती|ஆசை|விருப்ப", re.I)
def rules(text):
    sk, it = [], []
    for s in re.split(r"[.।!?\n]", text):
        for t in TRADES:
            if any(k in s.lower() for k in t["kw"]):
                (it if LIKE.search(s) else sk).append(t["id"])
    y = re.search(r"(\d+)\s*(year|yr|साल|वर्ष)", text, re.I)
    e = re.search(r"\b(5|8|10|12)(th)?\b|दसवीं|बारहवीं|graduate", text, re.I)
    return dict(education=e.group(0) if e else "unknown", years=int(y.group(1)) if y else (3 if sk else 0),
        skills=list(dict.fromkeys(sk)), interests=list(dict.fromkeys(it)),
        home=bool(re.search(r"home|ghar|घर|வீட்டி", text, re.I)),
        limited=bool(re.search(r"wheelchair|disab|limp|दिव्यांग|विकलांग|चल नहीं|cannot walk", text, re.I)),
        job=bool(re.search(r"\bjob\b|naukri|नौकरी|வேலை", text, re.I)))

async def gemini(text):
    k = os.getenv("GEMINI_API_KEY")
    if not k: return None
    ids = list(T)
    prompt = (f"Extract JSON from a beneficiary's words (any Indian language). Keys: education(str), years(int, experience), "
              f"skills(list of ids from {ids} they already practise), interests(list of ids from {ids} they like), "
              f"home(bool wants home-based work), limited(bool mobility limitation), job(bool prefers job over self-employment). JSON only.\nText: {text}")
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(f"https://generativelanguage.googleapis.com/v1beta/models/{os.getenv('GEMINI_MODEL','gemini-2.5-flash-lite')}:generateContent",
                params={"key": k}, json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0}})
        d = json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
        d["skills"] = [x for x in d.get("skills", []) if x in T]; d["interests"] = [x for x in d.get("interests", []) if x in T]
        d.setdefault("education", "unknown"); d["years"] = int(d.get("years") or 0)
        return d
    except Exception:
        return None

def feas(t, p):  # Livelihood Feasibility Score, 0-100 (rule-based)
    s = t["demand"] * 3
    s += 20 if (t["home"] or not p["home"]) else 6
    s += 15 if (t["walk"] or not p["limited"]) else 0
    s += 15 if t["cost"] <= 10000 else 10 if t["cost"] <= 25000 else 5
    s += 20 if t["months"] <= 2 else 12 if t["months"] <= 3 else 6
    return s

WHY = {"en": {"build": "You already have experience in this trade.", "rpl": " RPL can certify your existing skill quickly, so you may not need the full course.",
        "fit": "Best fit for your situation and local demand.", "upgrade": "A natural next step from your current work, with higher earning potential.",
        "leap": "You told us you are interested in this, so we added it as a new path.", "leap2": "A new option with strong local demand that fits your situation.",
        "inc": "Expected income {a} to {b} rupees per month. Cost about {c} rupees.", "hello": "Your three paths are ready."},
       "hi": {"build": "आपको इस काम का अनुभव पहले से है।", "rpl": " RPL से आपका मौजूदा हुनर जल्दी प्रमाणित हो सकता है, पूरा कोर्स शायद ज़रूरी न हो।",
        "fit": "आपकी स्थिति और स्थानीय मांग के हिसाब से सबसे उपयुक्त।", "upgrade": "आपके मौजूदा काम से अगला कदम, कमाई की ज़्यादा संभावना के साथ।",
        "leap": "आपने इसमें रुचि बताई, इसलिए इसे नए रास्ते के रूप में जोड़ा।", "leap2": "स्थानीय मांग वाला नया विकल्प जो आपकी स्थिति में फिट बैठता है।",
        "inc": "अनुमानित आय {a} से {b} रुपये प्रति माह। खर्च लगभग {c} रुपये।", "hello": "आपके तीन रास्ते तैयार हैं।"}}

def recommend(p, lang):
    W = WHY.get(lang, WHY["en"]); F = {i: feas(t, p) for i, t in T.items()}
    rank = sorted(F, key=F.get, reverse=True); used = []
    def pick(c):
        for i in c:
            if i not in used: used.append(i); return i
    b = pick(sorted(p["skills"], key=F.get, reverse=True) + rank)
    u = pick(([T[b]["up"]] if T[b]["up"] else []) + rank)
    l = pick(sorted(p["interests"], key=F.get, reverse=True) + rank)
    out = []
    for kind, i in (("build", b), ("upgrade", u), ("leap", l)):
        t = T[i]; rpl = kind == "build" and i in p["skills"] and p["years"] >= 2
        why = (W["build"] + (W["rpl"] if rpl else "")) if kind == "build" and i in p["skills"] else W["fit"] if kind == "build" else W["upgrade"] if kind == "upgrade" else W["leap"] if i in p["interests"] else W["leap2"]
        nm = t["hi"] if lang == "hi" else t["name"]
        say = f'{nm}. {why} ' + W["inc"].format(a=t["inc"][0], b=t["inc"][1], c=t["cost"])
        tv = TESTIMONY.get(lang, TESTIMONY["en"])[kind].format(n=nm)
        out.append(dict(kind=kind, id=i, name=nm, nsqf=t["nsqf"], feas=F[i], cost=t["cost"], months=t["months"], inc=t["inc"], scheme=t["scheme"],
            rpl=rpl, why=why, say=say, buyers=BUYERS.get(i, []), providers=PROVIDERS.get(i, []), testimony=tv))
    return out

def confidence(p, text):
    matched = len(p["skills"]) + len(p["interests"]) + (1 if p["education"] != "unknown" else 0)
    score = min(96, 30 + matched * 18 + min(len(text), 200) // 10)
    return score

class A(BaseModel):
    text: str
    lang: str = "en"
class C(BaseModel):
    trade: str
    district: str
    kind: str = "build"
class K(BaseModel):
    trade: str
    day: int

@app.post("/api/analyze")
async def analyze(a: A):
    p = await gemini(a.text); eng = "gemini"
    if p is None: p, eng = rules(a.text), "rules"
    for k, v in dict(skills=[], interests=[], home=False, limited=False, job=False, years=0).items(): p.setdefault(k, v)
    conf = confidence(p, a.text)
    return dict(engine=eng, profile=p, confidence=conf, handover=conf < 50,
        pathways=recommend(p, a.lang), intro=WHY.get(a.lang, WHY["en"])["hello"])

@app.post("/api/choose")
def choose(c: C):
    x = db(); x.execute("insert into p(district,trade,stage,kind) values(?,?,'enrolled',?)", (c.district, c.trade, c.kind)); x.commit(); x.close(); return {"ok": True}

@app.post("/api/checkin")
def checkin(k: K):
    # Deterministic MOCK dropout-risk model: a real system would use attendance/outcome data
    h = int(hashlib.sha1(f"{k.trade}{k.day}".encode()).hexdigest(), 16)
    risk = (h % 100) < (18 if k.day <= 30 else 10)
    saathi = SAATHIS[h % len(SAATHIS)]
    msg = (f"Risk flagged: no attendance signal for {k.trade} since last check-in. {saathi} has been alerted to visit." if risk
           else f"On track. {saathi} will call again at the next milestone.")
    return dict(day=k.day, risk=risk, saathi=saathi, message=msg)

@app.get("/api/dashboard")
def dashboard():
    x = db(); rows = [dict(r) for r in x.execute("select district,trade,stage,kind from p")]
    order = ["profiled", "enrolled", "certified", "placed"]
    funnel = {s: sum(1 for r in rows if order.index(r["stage"]) >= i) for i, s in enumerate(order)}
    g = {}
    for r in rows: g[(r["district"], r["trade"])] = g.get((r["district"], r["trade"]), 0) + 1
    props = [dict(district=d, trade=T[t]["name"], n=n) for (d, t), n in sorted(g.items(), key=lambda z: -z[1]) if n >= 4][:6]
    fair = {kd: sum(1 for r in rows if r["kind"] == kd) for kd in ("build", "upgrade", "leap")}
    x.close(); return dict(funnel=funnel, proposals=props, fairness=fair, total=len(rows), note="Mock seed data + live choices")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

