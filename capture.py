"""Browser check and store media for Monster Mash Kitchen (Apache-2.0), by MV2 of Munim, Inc., made with AI agents.

Runs index.html in headless Chromium (Playwright): #selftest must report no problems and the page must log no
errors; then it saves screenshots at phone and desktop sizes, the three covers from #cover and a 20-second
portrait gameplay video from #demo (no sound).

    python3 capture.py --html index.html --out /out
"""
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

COVERS = [("square-1024", 1024, 1024), ("portrait-720x1280", 720, 1280), ("landscape-1280x720", 1280, 720)]
VIDEOS = [("portrait", 720, 1280)]
SHOTS = [("play-phone-390x844", 390, 844), ("play-720x1280", 720, 1280), ("play-1280x720", 1280, 720)]


def watch(page, report, label):
    page.on("pageerror", lambda e: report["errors"].append("%s pageerror: %s" % (label, e)))
    page.on("console", lambda m: report["errors"].append("%s console %s: %s" % (label, m.type, m.text))
            if m.type in ("error", "warning") else None)


def to_mp4(src, dst, w, h):
    # skip the first half second (page load), keep 20 s, H.264 for upload
    if not shutil.which("ffmpeg"):
        return "ffmpeg not installed; kept the .webm"
    out = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", src, "-t", "20", "-an",
                          "-vf", "scale=%d:%d" % (w, h), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                          "-movflags", "+faststart", dst], capture_output=True, text=True)
    return "ok" if out.returncode == 0 else out.stderr[-1000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    url = "file://" + os.path.abspath(a.html)
    report = {"errors": [], "files": [], "video": {}}
    with sync_playwright() as p:
        browser = p.chromium.launch()

        page = browser.new_page(viewport={"width": 720, "height": 1280})
        watch(page, report, "selftest")
        page.goto(url + "#selftest")
        page.wait_for_selector("#test:not([hidden])", timeout=60000)
        report["selftest"] = page.inner_text("#test")
        page.screenshot(path=os.path.join(a.out, "selftest.png"))
        page.close()

        for name, w, h in SHOTS:
            page = browser.new_page(viewport={"width": w, "height": h})
            watch(page, report, name)
            page.goto(url)
            page.wait_for_timeout(2500)
            path = os.path.join(a.out, name + ".png")
            page.screenshot(path=path)
            report["files"].append(os.path.basename(path))
            page.close()

        # a served customer and the Monster Book, through the page's own functions
        page = browser.new_page(viewport={"width": 720, "height": 1280})
        watch(page, report, "screens")
        page.goto(url)
        page.wait_for_timeout(1000)
        page.evaluate("()=>{const b=bestPair(orderNow(),save.ing,save.book).pair;pick(b[0]);pick(b[1]);mash();}")
        page.wait_for_timeout(2200)
        page.screenshot(path=os.path.join(a.out, "play-result-720x1280.png"))
        page.evaluate("()=>{noSave=true;overlay='book';bookSel=0;}")
        page.wait_for_timeout(600)
        page.screenshot(path=os.path.join(a.out, "play-book-720x1280.png"))
        report["files"] += ["play-result-720x1280.png", "play-book-720x1280.png"]
        page.close()

        page = browser.new_page(viewport={"width": 1280, "height": 720})
        watch(page, report, "cover")
        page.goto(url + "#cover")
        page.wait_for_timeout(1500)
        for name, w, h in COVERS:
            data = page.evaluate("([w,h])=>renderCover(w,h)", [w, h])
            path = os.path.join(a.out, "monster-mash-%s.png" % name)
            with open(path, "wb") as f:
                f.write(base64.b64decode(data.split(",", 1)[1]))
            report["files"].append(os.path.basename(path))
        page.close()

        for name, w, h in VIDEOS:
            tmp = tempfile.mkdtemp()
            ctx = browser.new_context(viewport={"width": w, "height": h}, record_video_dir=tmp,
                                      record_video_size={"width": w, "height": h})
            page = ctx.new_page()
            watch(page, report, "demo-" + name)
            page.goto(url + "#demo")
            page.wait_for_timeout(21500)
            src = page.video.path()
            ctx.close()
            webm = os.path.join(a.out, "monster-mash-%s.webm" % name)
            shutil.move(src, webm)
            mp4 = os.path.join(a.out, "monster-mash-%s.mp4" % name)
            report["video"][name] = to_mp4(webm, mp4, w, h)
            report["files"] += [os.path.basename(webm)] + ([os.path.basename(mp4)] if os.path.exists(mp4) else [])
        browser.close()

    ok = "No problems found." in report.get("selftest", "") and not report["errors"]
    report["ok"] = ok
    with open(os.path.join(a.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
