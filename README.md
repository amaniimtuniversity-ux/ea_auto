# kathareel

**Hinglish explainer videos, from scratch — by raghv**

Turn any topic into a YouTube-style teaching video: **Hindi voiceover (natural neural voice), English on screen.**
Every frame is drawn in code with [Remotion](https://remotion.dev) (React + TypeScript). No stock footage,
no Chinese source, no copied project — this repo is written fresh.

```
topic  →  content.ts  →  Hindi voiceover  →  timeline  →  rendered MP4
```

## What it makes

| | |
|---|---|
| Format | 1280×720, H.264, 30 fps |
| Voiceover | Hindi (Devanagari script, English tech words inside) — `hi-IN-MadhurNeural` male / `hi-IN-SwaraNeural` female |
| On screen | **English only** — captions, keywords, step names, chapter names, end credit |
| Look | dark canvas, one accent colour per beat, big type, step-by-step walks, chapter progress bar |
| Length | whatever your content needs (the demo is 84 s) |

## Sabse aasan flow: script pehle, video baad me

Tum topic + duration do — **script pehle aayega review ke liye**, video baad me.

```bash
# 1) script banao (video nahi banegi abhi)
./scripts/make_video.sh --minutes 3
```
Ye `script.md` bana deta hai: chapters, har scene ki Hindi narration, English caption, keyword,
aur estimate (kitna lamba banega). Agar target se kam/zyada hai to tool khud batata hai
"~45 words add karo" / "~30 words hatao".

```bash
# 2) script.md me jo chahiye badlo, phir:
./scripts/make_video.sh --build
```
Ye tumhare edits `src/content.ts` me daalta hai → check → Hindi voice → render. Bas.

| Command | Kya karta hai |
|---|---|
| `./scripts/make_video.sh --minutes 3` | script.md banao + duration check (video nahi) |
| `./scripts/make_video.sh --build` | script.md ke edits laga kar video banao |
| `./scripts/make_video.sh --build --force` | script review skip, seedha video |
| `python3 scripts/script_review.py --from-script` | sirf edits apply (script.md → content.ts) |

Script.md me sirf ye 3 line types badalne hote hain:

```
say: देखो भाई, एक language model अपनी याद से जवाब देता है।   ← Hindi (Devanagari), yahi bola jayega
sub: The model answers from memory                          ← English, screen par
key: Wrong answer                                           ← English, bada word
```

## Topic kaise do? (3 tareeke)

### 1. Sirf AI agent ko bolo (sabse aasan)
```
"Photosynthesis par ek 3-minute ka Hinglish explainer banao"
```
Agent `SKILL.md` padh kar khud `src/content.ts` likh dega (Hindi narration + English captions),
voice banayega aur render karega. Tumhe code chhune ki zaroorat nahi.

### 2. Skeleton banao, narration khud bharo
```bash
python3 scripts/new_topic.py --topic "Photosynthesis" --title "Photosynthesis"
```
Ye `src/content.ts` bana deta hai — 3 parts, 6 scenes, har scene me Hindi hint likha hota hai
ki kya likhna hai. Bas `say` lines apne words se badal do, `subtitle`/`keyword` English hi rakho.

### 3. Seedha narration script do (best control)
```bash
python3 scripts/new_topic.py --topic "photosynthesis" \
  --say "देखो भाई, पौधा अपना खाना खुद बनाता है।" \
  --say "इस process को photosynthesis कहते हैं।" \
  --subtitle "Plants make their own food" \
  --subtitle "The name of the process" \
  --keyword "Photosynthesis" --keyword "Plants"
```
Har `--say` ek scene banta hai. `--subtitle` aur `--keyword` usi order me.

## Web studio (browser se poora flow)

Script ko terminal me edit karne ki zaroorat nahi — ek page par sab kuch:

```bash
python3 web/kaggle_launch.py       # Kaggle/Colab: setup + public URL
python3 web/server.py --port 8000  # laptop par
```

Banner me jo URL aaye use kholo. Page par:

| Step | Kya hota hai |
|---|---|
| 1 · Script | topic + minutes → outline banti hai; har scene ka Hindi narration, English caption, keyword, bullets, steps, number, compare — sab editable |
| 2 · Length | live duration vs target, "17s kam hai — 45 words add karo" |
| 3 · Generate video | Hindi voice + render, live log + progress steps |
| 4 · Result | video browser me play, voiceover audio check, mp4 download |

Kaggle par URL aisa hota hai: `https://www.kaggle.com/code/<user>/<notebook>/proxy/8000/`

No CDN, no build step — poora UI ek hi `web/index.html` me inline hai.


## Quick start (manual)

```bash
git clone https://github.com/amaniimtuniversity-ux/ea_auto.git
cd ea_auto
npm install
pip install edge-tts numpy                 # Hindi voice ke liye
sudo apt install ffmpeg                    # ya: brew install ffmpeg

# 1. content likho (upar ke 3 tareeke)
# 2. check karo
python3 scripts/check_content.py           # Devanagari, English board, length - sab check

# 3. voice + timeline
python3 scripts/build_voice.py

# 4. render
npx remotion render src/index.ts Explainer out/video.mp4 --concurrency=2
```

Preview while editing: `npx remotion studio src/index.ts`

## Tumhe kaunsi files chhune padenge?

**Sirf ek: `src/content.ts`.** Baaki sab (`timeline.ts`, `voice/*.wav`) script khud banata hai.

| File | Tum chhoona? |
|---|---|
| `src/content.ts` | ✅ haan — yahi tumhara topic hai |
| `src/theme.ts` | optional — colours/fonts badalne ho to |
| `src/timeline.ts` | ❌ kabhi nahi (auto-generated) |
| `src/components/*` | optional — naya visual type chahiye to |

## `src/content.ts` ka format

```ts
{
  id: 's3',
  type: 'steps',                       // hook | concept | steps | compare | number | recap
  say: 'Ab pipeline dekho. Pehle document chhote chunks me toote jaate hain...',  // Hindi, Devanagari
  subtitle: 'Chunk → Embed → Retrieve', // ENGLISH, one short line
  keyword: 'Pipeline',                  // ENGLISH, big word on screen
  steps: [{label: 'CHUNK', note: 'split the docs'}, ...],

  // optional — screen ka look (web UI se set hote hain)
  layout: 'timeline',        // 18 layouts, type ke hisaab se list badalta hai
  accent: 'blue',            // is scene ka apna rang (video ka accent override)
  transition: 'slide',       // fade | slide | pop | zoom | wipe
}
```

Video-level theme (top of `content.ts`):

```ts
accent: 'orange',       // orange | blue | green | violet | pink | amber | red | teal
background: 'glow',     // glow | grid | dots | plain | mesh
```

Two rules that make the video work:

1. **`say` is written in Devanagari**, with English technical words left in Latin (`chunk`, `RAG`, `embedding`).
   Hindi TTS needs Devanagari — Latin-script Hindi ("matlab kya hai") is pronounced wrong, which is exactly
   why the first version of this project sounded off.
2. **Everything on screen is English.** Hindi lives only in the audio. That keeps the board clean for
   screenshots and search.

## Scene types

| type | visual | best for |
|---|---|---|
| `hook` | big keyword + a chat card showing a wrong/right answer | opening problem |
| `concept` | keyword in a ring, documents flying in, points | one idea explained |
| `steps` | 3–5 cards, highlighted one at a time, dot travelling | pipelines, processes |
| `compare` | two columns, red ✕ vs green ✓ | before/after, pros/cons |
| `number` | big counted number + kept/dropped cards | stats, "top 3" |
| `recap` | numbered cards | closing summary |

### Layouts (18) — ek type, kai screen

`type` batata hai **matlab**, `layout` batata hai **screen**. Isliye ek hi video me har scene
alag dikh sakta hai — koi fixed template nahi.

| type | layouts |
|---|---|
| `hook` | `hook` (chat card) · `quote` · `bigword` |
| `concept` | `concept` (ring + bullets) · `bullets` · `cards` · `two-col` |
| `steps` | `steps` · `timeline` · `numbered` |
| `compare` | `compare` · `versus` · `table` |
| `number` | `number` · `stat` |
| `recap` | `recap` · `checklist` · `takeaways` |

### Theme, transitions, order

- **Accent** — 8 rang. Video-level chuno, aur har scene par chaho to alag (`inherit` default hai).
- **Background** — `glow` (soft), `grid`, `dots`, `plain`, `mesh` (dheere move karta hua gradient).
- **Transition** — per scene entry animation: `fade`, `slide`, `pop`, `zoom`, `wipe`.
- **Order** — web studio me scene ke `⠿` handle se drag karo (mouse, touch, stylus — sab chalta hai).
  Part bhi drag hota hai. Drag karte waqt page khud scroll hota hai.

Sab kuch `web/index.html` se, aur `scripts/content_io.py` wahi values `content.ts` me likhta hai.
Galat naam (jaise `accent: 'purple'`) teen jagah pakde jaate hain — UI validation, `POST /api/content`
(400) aur `scripts/check_content.py` — kyunki aisi value render todti hai.

## Voiceover

```bash
python3 scripts/build_voice.py                        # edge, Madhur, -5% (teaching pace)
python3 scripts/build_voice.py --voice hi-IN-SwaraNeural
python3 scripts/build_voice.py --rate=-8%
python3 scripts/build_voice.py --engine piper         # fully offline (hi_IN-pratham / priyamvada / rohan)
python3 scripts/build_voice.py --check                # timings only, no audio
```

- Sentences are cached in `voice_cache/`, so editing one line only re-synthesises that line.
- The script writes `src/timeline.ts` (frame numbers per beat) and `public/voice/<slug>.wav`.
- Rendering never touches the network: fonts are in `public/fonts`, audio is local.
- Bring your own voice? Drop any wav at `public/voice/<slug>.wav` with matching length and keep the timeline
  the script produced (or hand-edit `src/timeline.ts`).

## CPU or GPU?

**GPU ki zaroorat nahi, aur GPU se fayda bhi nahi.** Remotion headless Chromium me frames banata hai
aur ffmpeg se video encode karta hai — dono CPU par. Hamare scenes plain 2D + CSS hain (koi WebGL nahi),
isliye GPU ko kaam nahi milta.

Speed **CPU cores** se aati hai (`--concurrency`). Is project par naapa hua (150 frames, 2-core machine):

| Setting | Time |
|---|---|
| `--concurrency=1` | 25.3 s |
| `--concurrency=2` | **12.7 s** ← 2x, sirf CPU parallelism |
| `--concurrency=2 --gl=swiftshader` | 13.7 s (koi fayda nahi) |

- Kaggle/Colab: **Accelerator = None**, `--concurrency=2` (2 cores).
- Apne laptop par: `--concurrency=$(nproc)`.
- GPU machine ho to `--gl=angle-egl` ya `--gl=vulkan` try kar sakte ho — correctness par asar nahi padta.

Poori detail + tuning: [`docs/CORE-USAGE.md`](docs/CORE-USAGE.md)

## Requirements

```bash
node -v      # 18+
python3 -V   # 3.10+
ffmpeg -version
# GPU ki zaroorat NAHI — sab kuch CPU par chalta hai
pip install edge-tts numpy          # cloud Hindi voices (default)
pip install piper-tts               # optional: offline voices
```

Linux/ARM: Remotion has no bundled browser there —
`sudo apt install chromium` and set `REMOTION_BROWSER_EXECUTABLE=/usr/bin/chromium`.

## Project layout

```
src/content.ts            the only file you edit per video
src/timeline.ts           auto-generated frame timings (do not edit)
src/theme.ts              colours, fonts, safe areas
src/Video.tsx             main composition: title card, scenes, subtitles, chrome, end card
src/components/Scenes.tsx   six scene visuals
src/components/Cards.tsx    title card, end card, chapter bump
src/components/Chrome.tsx   progress bar, signature, cut flash, dot grid
src/components/Subtitle.tsx English caption + keyword
src/lib/anim.ts           easing helpers (pure functions of the frame)
src/lib/fonts.tsx         local font loading
scripts/build_voice.py    Hindi voiceover + timeline builder
public/fonts/             Noto Sans, Noto Sans Devanagari, Inter, JetBrains Mono (OFL)
```

## Design decisions

- **Devanagari narration.** The voice quality problem in v1 was a script problem, not a voice problem.
- **English board.** Hindi on screen makes the video hard to scan and impossible to screenshot for notes.
- **One accent per beat.** The eye follows exactly one orange element at a time.
- **Walk, don't show.** `steps` highlights cards sequentially so the narration and the picture move together.
- **Deterministic.** Every animation is a pure function of the frame number, so renders are reproducible.

## Credits

Built by **raghv**. Fonts are SIL OFL 1.1 (`public/fonts/OFL.txt`).
The method was inspired by the broader "explainer video from code" idea; everything in this repo is written
from scratch — see [LICENSE](LICENSE).

### Sabse aasan: ek cell (Kaggle)

`kathareel_onecell.py` ka poora content ek Kaggle cell me paste karke chalao —
setup + studio + URL, sab andar. Koi `git pull`, koi missing file nahi.
Regenerate: `python3 scripts/make_onecell.py`

### URL khulta nahi? Doctor chalao

```bash
python3 web/doctor.py
```

Ye batata hai: code purana hai ya nahi (version), server chal raha hai ya nahi,
duplicate/zombie process, ffmpeg/node, tunnel zinda hai ya nahi, aur public URL
asal me jawab de raha hai ya nahi (1033 = tunnel dead, 530 = server se connect nahi).

### Link kaun sa use karna hai

| Link | Kab tak chalta hai |
|---|---|
| `https://www.kaggle.com/code/<user>/<notebook>/proxy/8000/` | **Hamesha** — Kaggle notebook chal raha ho to chalta hai. Roz ke kaam ke liye yahi bookmark karo. |
| `https://....trycloudflare.com` | Free tunnel — 2–3 ghante me ya restart par mar sakta hai, phir naya ban jata hai. Server `/api/health` me current URL deta hai aur UI ke top-right 🔗 button me dikhata hai. |

Tunnel marne par server khud naya banata hai (backoff ke saath), kaam rukta nahi.
