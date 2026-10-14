"""Tests for Monster Mash Kitchen (Apache-2.0), by MV2 of Munim, Inc., made with AI agents.

Static checks always run. With Node.js installed, the rules block (<script id="logic">) runs and
selfTestLogic() must return no problems, and the whole page runs against a stub browser (a canvas that
rejects NaN and negative radii, pointer and key events, localStorage, a fake clock) in four modes:
#selftest, normal play, #demo and #cover.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

GAME_FILE = "index.html"

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, GAME_FILE), encoding="utf-8") as f:
    HTML = f.read()
LOGIC = re.search(r'<script id="logic">(.*?)</script>', HTML, re.S).group(1)
PAGE = "\n".join(re.findall(r"<script>(.*?)</script>", HTML, re.S))

HARNESS = """
;(function(){
  const problems=selfTestLogic();
  console.log(JSON.stringify({problems:problems.slice(0,25)}));
  process.exitCode=problems.length?1:0;
})();
"""

# a stub browser: enough of document, window, canvas, events and storage to run the page script
STUB = r"""
"use strict";
const __clock={t:1000};
try{Object.defineProperty(globalThis,"performance",{value:{now:()=>__clock.t},configurable:true,writable:true});}catch(e){performance.now=()=>__clock.t;}
const __raf=[];globalThis.requestAnimationFrame=cb=>{__raf.push(cb);return __raf.length;};
const __handlers={};globalThis.addEventListener=(type,fn)=>{(__handlers[type]=__handlers[type]||[]).push(fn);};
function __fire(type,props){const e=Object.assign({preventDefault(){},button:0,pointerType:"mouse",shiftKey:false},props);for(const fn of (__handlers[type]||[]))fn(e);}
function __click(x,y,button){__fire("pointermove",{clientX:x,clientY:y});__fire("pointerdown",{clientX:x,clientY:y,button:button||0});}
function __clickL(x,y,button){__click(view.ox+x*view.scale,view.oy+y*view.scale,button);}
function __key(key,extra){__fire("keydown",Object.assign({key},extra||{}));}
function __frames(n,dt){for(let k=0;k<n;k++){__clock.t+=dt*1000;const cbs=__raf.splice(0);for(const cb of cbs)cb(__clock.t);}}
function __num(p,a){for(const x of a)if(typeof x==="number"&&!isFinite(x))throw new Error("non-finite number passed to "+String(p));}
const __any=new Proxy(function(){},{get(t,p){if(p===Symbol.toPrimitive)return()=>0;if(p==="then")return undefined;return __any;},apply(){return __any;},construct(){return __any;},set(){return true;}});
function __ctx(){
  const store={};
  return new Proxy({},{
    get(t,p){
      if(p in store)return store[p];
      if(p==="measureText")return s=>({width:String(s).length*11});
      if(p==="createLinearGradient")return(...a)=>{__num(p,a);return {addColorStop(){}};};
      return(...a)=>{
        __num(p,a);
        if(p==="arc"&&a[2]<0)throw new Error("negative arc radius "+a[2]);
        if(p==="ellipse"&&(a[2]<0||a[3]<0))throw new Error("negative ellipse radius");
        if(p==="arcTo"&&a[4]<0)throw new Error("negative arcTo radius");
      };
    },
    set(t,p,v){if(typeof v==="number"&&!isFinite(v))throw new Error("bad "+String(p)+": "+v);store[p]=v;return true;}
  });
}
function __el(tag){
  const e={tag,hidden:true,textContent:"",style:{},children:[],onclick:null,classList:{add(){}},appendChild(c){this.children.push(c);return c;}};
  if(tag==="canvas"){e.width=300;e.height=150;e.getContext=()=>__ctx();e.toDataURL=()=>"data:image/png;base64,AAAA";}
  return e;
}
const __els={c:__el("canvas"),test:__el("div"),covers:__el("div")};
globalThis.document={getElementById:id=>__els[id],createElement:__el,body:__el("body"),hidden:false,addEventListener(){}};
globalThis.window=globalThis;globalThis.innerWidth=1280;globalThis.innerHeight=720;globalThis.devicePixelRatio=1;
globalThis.location={hash:__HASH__};
const __ls=new Map();
Object.defineProperty(globalThis,"localStorage",{value:{getItem:k=>__ls.has(k)?__ls.get(k):null,setItem:(k,v)=>__ls.set(k,String(v))},configurable:true,writable:true});
globalThis.AudioContext=__any;
"""

AFTER = {
    "#selftest": r"""
__frames(3,0.016);
console.log(JSON.stringify({box:__els.test.textContent,hidden:__els.test.hidden}));
""",
    "": r"""
const __out={};
__frames(5,0.016);
__out.lands=phase==="kitchen"&&save.night===1&&save.k===0&&overlay===null&&picked.length===0;
__key("m");__out.muted=save.mute===true;__key("M");__out.unmuted=save.mute===false;
// night 1, played with clicks: two cards, MASH, then the next customer
let __stars=0;
for(let q=0;q<6;q++){
  const b=bestPair(orderNow(),save.ing,save.book).pair;
  for(const i of b){const r=cardRect(i);__clickL(r.x+20,r.y+20);}
  __clickL(BTN.mash.x+20,BTN.mash.y+20);
  __frames(40,0.05);
  if(phase!=="result"){__out.stuck=phase+" at order "+(q+1);break;}
  __stars+=result.stars;
  __clickL(RESULT_BTN.x+20,RESULT_BTN.y+20);__frames(2,0.016);
}
__out.night1=phase==="night"&&__stars===18&&save.tonight===18;
__out.coins=save.coins;
__clickL(NIGHT_BTN.x+20,NIGHT_BTN.y+20);__frames(2,0.016);
__out.night2=phase==="kitchen"&&save.night===2&&save.k===0;
const __s=JSON.parse(__ls.get(SAVE_KEY));__out.savedNight=__s.night;__out.savedBook=Object.keys(__s.book).length;
// a card tapped twice comes back out of the cauldron
{const r=cardRect(3);__clickL(r.x+20,r.y+20);const one=picked.length===1;__clickL(r.x+20,r.y+20);__out.unpick=one&&picked.length===0;}
// keys: 1 and 2 pick, Enter mashes, Enter serves the next customer
__key("1");__key("2");__out.keyPick=picked.join()==="0,1";
__key("Enter");__out.keyMash=phase==="mashing";
__frames(40,0.05);__key("Enter");__frames(2,0.016);__out.keyNext=phase==="kitchen"&&save.k===1;
// a locked card opens the shop; buy spider silk
{const r=cardRect(8);__clickL(r.x+20,r.y+20);__out.lockedOpensShop=overlay==="shop";
 const c0=save.coins,b=shopBtn(0);__clickL(b.x+20,b.y+20);__out.bought=save.ing===9&&save.coins===c0-ING[8].price;
 __clickL(SHOP_CLOSE.x+20,SHOP_CLOSE.y+20);__out.shopClosed=overlay===null;}
// the Monster Book
{__key("b");__out.bookOpen=overlay==="book";const s=bookSlot(0);__clickL(s.x+20,s.y+20);__out.bookSel=bookSel===0;
 __clickL(BOOK_CLOSE.x+20,BOOK_CLOSE.y+20);__out.bookClosed=overlay===null;}
// today's Moon Recipe
{save.moonFound="";const mp=moonPair(today());for(const i of mp){const r=cardRect(i);__clickL(r.x+20,r.y+20);}
 __clickL(BTN.mash.x+20,BTN.mash.y+20);__frames(40,0.05);
 __out.moon=phase==="result"&&result.moon===true&&save.daily.streak===1&&save.moonFound===today();}
// a phone-shaped window
globalThis.innerWidth=390;globalThis.innerHeight=844;__fire("resize",{});__frames(3,0.016);
__out.phone=Math.abs(view.scale-390/720)<1e-9&&Math.abs(view.ox)<1e-6;
__clickL(RESULT_BTN.x+20,RESULT_BTN.y+20);__frames(2,0.016);__out.phoneNext=phase==="kitchen";
__frames(10,0.05);
console.log(JSON.stringify(__out));
""",
    "#demo": r"""
for(let k=0;k<1200;k++)__frames(1,0.05);
console.log(JSON.stringify({night:save.night,book:Object.keys(save.book).length,saved:__ls.has(SAVE_KEY),demo}));
""",
    "#cover": r"""
__frames(2,0.016);
console.log(JSON.stringify({children:__els.covers.children.length,hidden:__els.covers.hidden,srcs:__els.covers.children.filter(c=>c.tag==="img").map(c=>c.src.slice(0,22))}));
""",
}


def node(path):
    return subprocess.run(["node", path], capture_output=True, text=True, encoding="utf-8", timeout=300)


def run_page(hash_):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "page.js")
        with open(path, "w", encoding="utf-8") as f:
            f.write(STUB.replace("__HASH__", json.dumps(hash_)) + LOGIC + "\n" + PAGE + "\n" + AFTER[hash_])
        out = node(path)
    if out.returncode != 0:
        raise AssertionError("page run %r failed:\n%s\n%s" % (hash_, out.stdout[-3000:], out.stderr[-3000:]))
    lines = [l for l in out.stdout.splitlines() if l.startswith("{")]
    return json.loads(lines[-1])


class Static(unittest.TestCase):
    def test_one_self_contained_file(self):
        # RUN serves the build folder as is; one file that works offline and inside an app webview
        self.assertIsNone(re.search(r'\b(src|href)\s*=\s*["\']?(https?:)?//', HTML))
        self.assertIsNone(re.search(r'\b(fetch|import)\(\s*["\']https?://', HTML))
        self.assertIsNone(re.search(r"<link\b[^>]*stylesheet", HTML))
        self.assertNotIn("http://", HTML)
        self.assertNotIn("https://", HTML)

    def test_logic_has_no_browser_code(self):
        for name in ("document", "window", "AudioContext", "requestAnimationFrame", "localStorage"):
            self.assertIsNone(re.search(r"\b" + name + r"\b", LOGIC), name + " in the rules block")
        self.assertIn("function selfTestLogic(", LOGIC)
        self.assertRegex(LOGIC, r"\bconst W=720,H=1280;")

    def test_audio_waits_for_a_gesture(self):
        self.assertEqual(len(re.findall(r"new \(window\.AudioContext", PAGE)), 1)
        self.assertRegex(PAGE, r'addEventListener\("pointerdown",[^\n]*audio\.unlock\(\)')
        self.assertRegex(PAGE, r'addEventListener\("keydown",e=>\{\s*audio\.unlock\(\)')
        self.assertIn("audio.started()", PAGE)

    def test_sound_can_be_turned_off_on_screen_and_with_m(self):
        self.assertRegex(PAGE, r'e\.key==="m"\|\|e\.key==="M"\)\{audio\.toggle\(\)')
        self.assertIn('"🔇 Sound"', PAGE)

    def test_progress_is_kept(self):
        self.assertIn('SAVE_KEY="monstermash.v1"', PAGE)
        self.assertRegex(PAGE, r"localStorage\.setItem\(SAVE_KEY")
        self.assertNotIn("requestFullscreen", HTML)

    def test_selftest_cover_and_demo_hooks(self):
        self.assertIn('location.hash==="#selftest"', PAGE)
        self.assertIn('location.hash==="#cover"', PAGE)
        self.assertIn('location.hash==="#demo"', PAGE)

    def test_disclosure_licence_and_wording(self):
        self.assertIn("Made by MV2 of Munim, Inc. with AI agents", HTML)
        self.assertIn("Apache-2.0", HTML)
        self.assertIsNone(re.search(r"MV2[^.]{0,60}\b(an AI|a bot|AI assistant)\b", HTML))
        self.assertIsNone(re.search(r"(License|Licence)\s*:\s*MIT|MIT License", HTML))


@unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
class Node(unittest.TestCase):
    def test_rules(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "logic.js")
            with open(path, "w", encoding="utf-8") as f:
                f.write(LOGIC + "\n" + HARNESS)
            out = node(path)
        self.assertEqual(out.returncode, 0, out.stdout[-3000:] + out.stderr[-3000:])
        self.assertEqual(json.loads(out.stdout[out.stdout.index("{"):])["problems"], [])

    def test_page_script_parses(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "page.js")
            with open(path, "w", encoding="utf-8") as f:
                f.write(LOGIC + "\n" + PAGE)
            out = subprocess.run(["node", "--check", path], capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr[-3000:])

    def test_page_selftest(self):
        r = run_page("#selftest")
        self.assertFalse(r["hidden"])
        self.assertIn("No problems found.", r["box"], r["box"])

    def test_page_play(self):
        r = run_page("")
        for key in ("lands", "muted", "unmuted", "night1", "night2", "unpick", "keyPick", "keyMash", "keyNext",
                    "lockedOpensShop", "bought", "shopClosed", "bookOpen", "bookSel", "bookClosed", "moon",
                    "phone", "phoneNext"):
            self.assertTrue(r.get(key), "%s failed: %r" % (key, r))
        self.assertNotIn("stuck", r)
        self.assertGreaterEqual(r["coins"], 180, r)
        self.assertEqual(r["savedNight"], 2, r)
        self.assertEqual(r["savedBook"], 6, r)

    def test_page_demo_plays_itself_and_never_saves(self):
        r = run_page("#demo")
        self.assertTrue(r["demo"])
        self.assertGreaterEqual(r["night"], 2, r)
        self.assertGreaterEqual(r["book"], 6, r)
        self.assertFalse(r["saved"], r)

    def test_page_covers(self):
        r = run_page("#cover")
        self.assertFalse(r["hidden"])
        self.assertEqual(r["children"], 6, r)
        self.assertEqual(r["srcs"], ["data:image/png;base64,"] * 3, r)


if __name__ == "__main__":
    unittest.main()
