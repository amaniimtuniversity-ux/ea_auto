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

## Quick start

```bash
git clone https://github.com/amaniimtuniversity-ux/ea_auto.git
cd ea_auto
npm install

# 1. edit the content (one file)
open src/content.ts        # Hindi lines + English captions

# 2. build the voiceover + timeline
python3 scripts/build_voice.py            # needs: pip install edge-tts numpy, ffmpeg

# 3. render
npx remotion render src/index.ts Explainer out/video.mp4
```

Preview while editing: `npx remotion studio src/index.ts`

## The one file you edit: `src/content.ts`

```ts
{
  id: 's3',
  type: 'steps',                       // hook | concept | steps | compare | number | recap
  say: 'Ab pipeline dekho. Pehle document chhote chunks me toote jaate hain...',  // Hindi, Devanagari
  subtitle: 'Chunk → Embed → Retrieve', // ENGLISH, one short line
  keyword: 'Pipeline',                  // ENGLISH, big word on screen
  steps: [{label: 'CHUNK', note: 'split the docs'}, ...],
}
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

## Requirements

```bash
node -v      # 18+
python3 -V   # 3.10+
ffmpeg -version
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
