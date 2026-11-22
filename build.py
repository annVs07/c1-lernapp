"""Splits the two .txt exports into sections and renders each with edge-tts.
Output: audio/NN.mp3 + texts.js (window.TEXTS = [...] with sentence cues)."""
import asyncio, json, re, sys, pathlib
import edge_tts

ROOT = pathlib.Path(__file__).parent
VOICE = "de-DE-FlorianMultilingualNeural"
SOURCES = [("src/Schriftlicher Ausdruck.txt", "Schreiben"), ("src/Mündlicher Ausdruck.txt", "Sprechen")]
SKIP_START = ("Prüfungspartner", "-", "Deine", "Du:", "Gesprächspartner", "Mögliche")


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
            title = re.sub(r"^(Und noch )?Thema( \d+)?:?\s*", "", l)
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
    seen, texts = {}, []
    for n, s in enumerate(secs):
        seen[s["title"]] = seen.get(s["title"], 0) + 1
        title = s["title"] + (f" ({seen[s['title']]})" if seen[s["title"]] > 1 else "")
        body = "\n".join(s["lines"])
        mp3 = f"audio/{n:02d}.mp3"
        if "--dry" in sys.argv:
            print(n, s["cat"], title[:70], len(body)); continue
        cues = await render(title + ".\n" + body, ROOT / mp3)
        texts.append({"id": n, "title": title, "cat": s["cat"], "body": body, "audio": mp3, "cues": cues})
        print("ok", n, title[:60], len(cues), "cues")
    if texts:
        (ROOT / "texts.js").write_text("window.TEXTS=" + json.dumps(texts, ensure_ascii=False) + ";")

asyncio.run(main())
