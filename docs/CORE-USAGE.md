# CPU vs GPU — kathareel kaise chalta hai

> Chhota jawab: **GPU ki zaroorat nahi hai, aur GPU se fayda bhi nahi hota.**
> Speed **CPU cores** se aati hai (`--concurrency`). Benchmark numbers neeche hain.

## Ye project kya use karta hai

| Kaam | Kaun karta hai | GPU chahiye? |
|---|---|---|
| Scene draw karna (React → frames) | Headless Chromium (CPU) | Nahi |
| Animation / layout / fonts | Chromium (CPU) | Nahi |
| WebGL effects (hum use nahi karte) | Chromium ka GL backend | Optional |
| Video encode (H.264) | ffmpeg (libx264, CPU) | Nahi |
| Hindi voice (edge-tts) | Microsoft cloud | Nahi |
| Hindi voice (piper, offline) | onnxruntime (CPU) | Nahi |

Kyunki scenes plain 2D + CSS hain (koi Three.js / WebGL / shader nahi), GPU ko kaam hi nahi milta.

## Benchmark (asli numbers, is project par)

Machine: 2 CPU cores, no GPU. 150 frames @ 1280×720, H.264.

| Setting | Time | Notes |
|---|---|---|
| `--concurrency=1` | **25.3 s** | ek core |
| `--concurrency=2` | **12.7 s** | ~2x faster — CPU parallelism |
| `--concurrency=2 --gl=swiftshader` | 13.7 s | software GL, koi fayda nahi |

Poori 84-second video (2524 frames): **~3 minute** at concurrency=2.

**Seekh:** speed = cores. GPU lagane se kuch nahi badla.

## Speed kaise badhaye (GPU ke bina)

```bash
# 1. concurrency = apne cores jitna
nproc                      # kitne cores hain
npx remotion render src/index.ts Explainer out/video.mp4 --concurrency=4

# 2. sirf test render karo, poora nahi
npx remotion render src/index.ts Explainer out/test.mp4 --frames=0-299

# 3. JPEG frames (chhota, tez) — already default hai
#    quality chahiye to PNG:
npx remotion render src/index.ts Explainer out/hq.mp4 --image-format=png

# 4. encode halka karo (quality thodi kam, file chhoti, tez)
npx remotion render src/index.ts Explainer out/small.mp4 --crf=23
```

Kaggle / Colab par **2 cores** hote hain → `--concurrency=2` hi rakho. Usse zyada dene se
memory khatam hoti hai aur render fail ho sakta hai.

## Agar GPU waali machine ho (optional)

Kabhi kabhi GL backend badalne se fayda hota hai — try kar sakte ho, correctness par asar nahi:

```bash
npx remotion render src/index.ts Explainer out/video.mp4 --gl=angle-egl   # NVIDIA/AMD par
npx remotion render src/index.ts Explainer out/video.mp4 --gl=vulkan
npx remotion render src/index.ts Explainer out/video.mp4 --gl=swiftshader # pure software (fallback)
```

Valid values: `angle`, `egl`, `swangle`, `swiftshader`, `vulkan`, `angle-egl`.
Default `swangle` (software) hai — yaani GPU ho na ho, output same rehta hai.

## Kaggle par kya select karo

| Setting | Kya chuno | Kyun |
|---|---|---|
| Accelerator | **None** | GPU se koi fayda nahi, aur T4/P100 quota bachta hai |
| Internet | **On** | clone + npm + edge-tts voice |
| Render | `--concurrency=2` | 2 cores |

GPU notebook use karna sirf tab theek hai jab tum **voice model** (jaise XTTS / Orpheus jaise heavy TTS)
khud chalana chaho — wo alag baat hai, is project ka default pipeline GPU use nahi karta.
