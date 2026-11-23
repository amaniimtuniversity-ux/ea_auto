# kathareel demo (Kaggle / Colab / Linux) — by raghv

Ye folder ek **ready-made demo** hai: repo clone karne ke baad ek hi command se 37-second ka video ban jaata hai —
**Hinglish voiceover + English board**, poori pipeline ke saath (TTS → timeline → subtitles → Remotion render).

| File | Kya hai |
|---|---|
| `kathareel_demo.ipynb` | Kaggle notebook — upload karo, cell-by-cell chalao (recommended) |
| `setup_demo.py` | wahi kaam CLI se: project setup + TTS + render |
| `../demo/narration.txt` | demo narration (Hinglish, chapter + subtitle blocks ke saath) |
| `../demo/Demo.tsx` | 3 demo shots (LLM card, RAG + doc cards, CHUNK→EMBED→RETRIEVE pipeline) |

## Kaggle par (recommended)

1. [kaggle.com/code](https://www.kaggle.com/code) → **New Notebook**
2. Right sidebar → **Internet: On** (warna clone + npm install nahi honge)
3. **File → Import Notebook** → `kathareel_demo.ipynb` upload karo
4. **Run All** — pehli baar ~6–8 minute (npm install + Chromium + render), video `demo.mp4` ban jayegi

Notebook kya dikhata hai: config (`lang: 'hi'`, `built by raghv`), timeline (frame numbers), video player
aur ek contact sheet taaki ek nazar me verify ho jaye ki board par sab English hai.

## CLI se (Kaggle terminal / Colab / koi bhi Linux)

```bash
git clone https://github.com/amaniimtuniversity-ux/ea_auto.git
cd ea_auto
python3 kaggle/setup_demo.py --work ~/demo        # setup + TTS + render
# ya:
python3 kaggle/setup_demo.py --work ~/demo --skip-render   # sirf setup
python3 kaggle/setup_demo.py --work ~/demo --frames 60,420,900   # sirf stills
```

Output: `~/demo/demo.mp4`, `~/demo/demo_f*.png`, plus `~/demo/src/` (poora Remotion project, edit karne layak).

## Honest notes

- **Kaggle se edge-tts block hai.** Microsoft ka endpoint 403 deta hai, isliye installer apne aap **espeak-ng**
  (offline Hindi voice) par gir jaata hai. Aawaz robotic/mechanical hai — video "sahi chal raha hai" prove karne ke liye
  kaafi hai, par delivery quality nahi. Apne laptop par edge-tts `hi-IN-MadhurNeural` (natural male) chalti hai;
  ya koi bhi TTS se finished `audio.wav` de do, interface same rehta hai.
- **GPU ki zarurt nahi.** Remotion CPU par Chromium se render karta hai. Kaggle par 2 cores hain → `--concurrency=2`.
- **Pehli baar slow, baad me fast.** `npm install` + Chromium download pehli baar hote hain; `sudo` ke bina Chromium ke
  system libs missing hote hain, isliye notebook pehle `apt-get install` karta hai.
- Demo ke shots minimal hain (3 shots, 5 sentences) — asli film me agent `SKILL.md` ke 9 stages chalata hai
  (research → 40–50 shots → QC), jo ghante ka kaam hai. Demo sirf "pipeline chal rahi hai" ka proof hai.
