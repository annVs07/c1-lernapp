"""Splits the two .txt exports into sections and renders each with edge-tts.
Output: audio/NN.mp3 + texts.js (window.TEXTS = [...] with sentence cues)."""
import asyncio, json, re, sys, pathlib, hashlib, shutil
import edge_tts

ROOT = pathlib.Path(__file__).parent
VOICE = "de-DE-FlorianMultilingualNeural"
SOURCES = [("src/Schriftlicher Ausdruck.txt", "Schreiben"), ("src/Mündlicher Ausdruck.txt", "Sprechen"), ("src/Texte.txt", "Neu")]
SKIP_START = ("Guten Tag", "Prüfungspartner", "-", "Deine", "Du:", "Gesprächspartner", "Mögliche")


def clean(l):
    return l.replace(" ", " ").replace("\t", " – ").strip()


def sections(path, cat):
    lines = [clean(l) for l in (ROOT / path).read_text().splitlines()]
    def next_nonblank(i):
        for j in range(i + 1, len(lines)):
            if lines[j]:
                return lines[j]
        return ""
    def upcoming(i, n=4):
        return [x for x in lines[i + 1:i + 12] if x][:n]
    out, cur, prev = [], None, ""
    for i, l in enumerate(lines):
        nxt = next_nonblank(i)
        title, c = None, cat
        if re.match(r"^(Und noch )?Thema\b", l):
            title = re.sub(r"^(Und noch )?Thema( \d+)?:?\s*\*?", "", l)
        elif cat == "Neu":
            if l.startswith("PRÜFUNGSSIMULATION"):
                title = "Diskussion: " + l.split("DISKUSSION", 1)[-1].strip().replace('"', "„", 1).replace('"', "“", 1)
            elif l == "Vorstellung":
                title = "Vorstellung (über mich)"
        elif l.startswith("„") and l.endswith("“") and any(x.startswith("Mögliche Bedeutung") for x in upcoming(i)):
            title, c = l, "Zitate"
        elif l and len(l) < 130 and not l.endswith(":") and not l.startswith(SKIP_START) and len(nxt) > 150 and not prev.startswith("„"):
            title = l
        if title:
            cur = {"title": title, "cat": c, "lines": []}
            out.append(cur)
        elif cur and l:
            cur["lines"].append(l)
        if l:
            prev = l
    return out


async def render(text, mp3):
    com = edge_tts.Communicate(text, VOICE, rate="-5%", boundary="SentenceBoundary")
    cues = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] in ("SentenceBoundary", "WordBoundary"):
                cues.append({"t": round(ch["offset"] / 1e7, 2), "s": ch["text"]})
    return cues


async def main():
    (ROOT / "audio").mkdir(exist_ok=True)
    secs = [s for p, c in SOURCES for s in sections(p, c)]
    old = {}
    if (ROOT / "texts.js").exists():
        for t in json.loads((ROOT / "texts.js").read_text()[len("window.TEXTS="):-1]):
            old[t["title"].split(" (")[0] + ".\n" + t["body"]] = t
    seen, texts = {}, []
    for n, s in enumerate(secs):
        seen[s["title"]] = seen.get(s["title"], 0) + 1
        title = s["title"] + (f" ({seen[s['title']]})" if seen[s["title"]] > 1 else "")
        body = "\n".join(s["lines"])
        spoken = s["title"] + ".\n" + body
        mp3 = "audio/" + hashlib.md5((VOICE + spoken).encode()).hexdigest()[:10] + ".mp3"
        if "--dry" in sys.argv:
            print(n, s["cat"], title[:70], len(body)); continue
        prev = old.get(spoken)
        if prev and (ROOT / prev["audio"]).exists():
            if prev["audio"] != mp3:
                shutil.copy(ROOT / prev["audio"], ROOT / mp3)
            cues = prev["cues"]; print("reuse", n); 
        else:
            cues = await render(spoken, ROOT / mp3)
        texts.append({"id": n, "title": title, "cat": s["cat"], "body": body, "audio": mp3, "cues": cues})
        print("ok", n, title[:60], len(cues), "cues")
    if texts:
        (ROOT / "texts.js").write_text("window.TEXTS=" + json.dumps(texts, ensure_ascii=False) + ";")
        keep = {t["audio"] for t in texts}
        for f in (ROOT / "audio").glob("*.mp3"):
            if "audio/" + f.name not in keep:
                f.unlink()

asyncio.run(main())
