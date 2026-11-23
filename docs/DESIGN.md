# Design notes — kathareel (by raghv)

## What makes it feel like a study video, not a slideshow

| Choice | Why |
|---|---|
| One accent colour per beat (orange) | The eye has a single target; nothing competes with the narration |
| Keyword + caption, never a paragraph | The viewer reads 2–3 words and goes back to listening |
| `steps` highlights sequentially every 1.6 s | Picture and speech move together; the pipeline is *walked* |
| 7-frame dip at every cut | Cuts register as beats instead of jumps |
| Chapter segments in the progress bar | The viewer always knows where they are in the explanation |
| `-5%` speech rate + 26-frame scene pad | Hindi at `+0%` sounds rushed; the pad is the "let it land" moment |
| Recap as numbered cards | Gives a note-taking moment at the end |

## Type and layout

- **Noto Sans Devanagari** for Hindi (only used in the title card meta and, if you add it, any Hindi display).
- **Inter** for everything on screen: captions 40px/700, keywords 78–92px/800, body 26–30px/500.
- **JetBrains Mono** only inside the chat card, so machine output reads as machine output.
- Safe area: content lives between y≈96 and y≈520. Subtitles start at y=556, progress bar at y=674.

## Colour roles

```
bg        #0B0D12   canvas
panel     #171B25   cards
text      #F4F6FB   primary
textDim   #A7AFBF   secondary
accent    #FF6B2C   the current hero of the beat
cool      #3BC9F5   data / flow / "kept"
good      #5BE58B   correct side of a comparison
warn      #FF4D5E   wrong side, missing source
```

## Determinism

Every animation is a pure function of the frame number (`src/lib/anim.ts`). No `Math.random()`, no
`Date.now()`, no CSS transitions. Two renders of the same commit produce identical frames.

## Extending

1. Add a component to `src/components/Scenes.tsx` with the shared `Common` props
   (`keyword`, `bullets`) plus whatever fields your visual needs.
2. Add the field to the `Scene` type in `src/content.ts`.
3. Add one `case` in `SceneBody` (`src/Video.tsx`).
4. Keep the visual inside `Stage` so it respects the subtitle band.
