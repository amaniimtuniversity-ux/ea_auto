---
name: kathareel
description: Turn any topic into a YouTube-style teaching video with a Hindi (Hinglish) voiceover and English on-screen text. Use when the user asks for an explainer video, a study/lecture video, or wants a topic explained in Hindi with visuals — the output is a code-drawn Remotion MP4 (dark canvas, step-by-step diagrams, chapter progress bar).
---

# kathareel — Hinglish explainer video

**Hindi bolo, English dikhao.** The voiceover is Hindi (natural neural voice); every word on screen is English.

## The two rules

1. **Voiceover = Hindi (Devanagari script), with English technical words inside.**
   Write `say` in Devanagari: `"देखो भाई, एक language model अपनी याद से ही जवाब देता है"`.
   Do **not** write Latin-script Hindi (`"dekho bhai..."`) — Hindi TTS mispronounces it. This was the
   single biggest quality bug in the first version.
2. **Board = English only.** `subtitle`, `keyword`, `bullets`, `steps[].label`, chapter `title`,
   end credit — all English. Hindi never appears on screen.

## Review-first workflow (default)

User topic + duration deta hai. **Pehle script, phir video.** Kabhi seedha render mat karo.

1. `python3 scripts/script_review.py --minutes <N>` → `script.md` banao.
2. User ko script dikhao (paste karo, ya file present karo) aur bolo: "ye narration hai, badalna hai to bolo".
   Chapter names, har beat ki Hindi narration, English caption, aur estimated length — sab dikhao.
3. User ke edits lo (script.md me ya chat me), `--from-script` se apply karo.
4. `check_content.py` → `build_voice.py` → render.
5. Duration target se >15% door ho to script chhota/lamba karo, speed se mat khelo.

Ek command me: `./scripts/make_video.sh --minutes <N>` then `./scripts/make_video.sh --build`.

## Workflow

0. **Input**: user ek topic deta hai (ya article/document). Isi se tum `src/content.ts` likhte ho —
   code me kuch aur chhune ki zaroorat nahi. Agar user khud narration de to usko waisa hi use karo.
   Skeleton chahiye to: `python3 scripts/new_topic.py --topic "<slug>" --title "<Title>"`.
1. **Ask** what topic, how long, and which voice (`hi-IN-MadhurNeural` male, `hi-IN-SwaraNeural` female,
   or offline piper). Default: Madhur, `-5%`.
2. **Write `src/content.ts`** — chapters, then scenes. Follow the narration rules below.
3. **Check**: `python3 scripts/check_content.py` — Devanagari narration, English board, length, duplicate ids.
4. **Voiceover**: `python3 scripts/build_voice.py` → writes `public/voice/<slug>.wav` + `src/timeline.ts`.
4. **Check timings**: `python3 scripts/build_voice.py --check` prints frame ranges per beat.
5. **Render**: `npx remotion render src/index.ts Explainer out/video.mp4 --concurrency=2`.
6. **Verify**: render 6–8 stills across the timeline and look at them. Check: nothing collides with the
   subtitle band, every beat has a visual change, no empty frames.
7. **Deliver**: the MP4 plus the content file.

## Narration rules (Hinglish study-channel style)

- **Open with the situation, not the definition.** "Dekho bhai, ek language model apni yaad se hi jawab deta hai"
  beats "RAG ek technique hai jo...".
- **One idea per beat.** Roughly 12–20 Hindi words per `say`; that is 6–10 seconds of speech.
- **Speak to one person.** "Dekho", "samajh lo", "yaad rakho" — the tone of a teacher, not a manual.
- **Technical words stay English**: chunk, embed, retrieval, vector, model, pipeline, token. Do not transliterate them.
- **Numbers stay digits**: "3 chunks", "2024 me". Never write numbers in Hindi words.
- **Explain the why before the how.** Problem → idea → mechanism → result.
- **Close with a recap** in the viewer's words: "Bas itna yaad rakho..."
- **No filler** ("aaj hum baat karenge...") and no reporting the visuals ("ab screen par dekhiye...").

## Pacing (encoded in `scripts/build_voice.py`)

| Knob | Value | Why |
|---|---|---|
| `--rate` | `-5%` | teaching pace; `+0%` sounds rushed for Hindi |
| `LEAD` | 105 frames | title card needs ~3.5 s before speech starts |
| `GAP` | 12 frames | breath between two beats of the same scene |
| `SCENE_PAD` | 26 frames | hold the last visual so the viewer can read it |
| `OUTRO` | 110 frames | end card |

Scene changes get a 7-frame dip to black (`CutFlash`) so cuts register without jarring.

## Scene types

`hook` · `concept` · `steps` · `compare` · `number` · `recap` — see README for what each one draws.
If a topic needs something else, add a new component in `src/components/Scenes.tsx` and a case in
`src/Video.tsx`; keep the same `Common` props so content stays declarative.

## What NOT to do

- Do not put Hindi/Roman-Hindi text on screen (breaks the board rule and the visual rhythm).
- Do not hard-code colours or sizes in scenes — use `src/theme.ts`.
- Do not animate with randomness or timers: every value must be a pure function of `useCurrentFrame()`.
- Do not place content below y=520: the subtitle band and progress bar live there.
- Do not commit `public/voice/*.wav` for big videos if the repo should stay small — regenerate with the script.

## Files

| Path | Role |
|---|---|
| `src/content.ts` | **the only file to edit per video** |
| `scripts/build_voice.py` | Hindi TTS + timeline (edge default, piper offline) |
| `src/Video.tsx` | composition: title card → scenes → end card, audio, chrome |
| `src/components/Scenes.tsx` | six scene visuals |
| `src/components/Chrome.tsx` | progress bar (chapter segments), signature, cut flash |
| `src/timeline.ts` | generated frame numbers — never edited by hand |
| `demo_topic.txt` | example topic walkthrough (RAG) with the finished narration |
