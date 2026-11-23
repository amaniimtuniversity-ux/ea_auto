# Kaggle par studio chalane ke exact steps

## Kyun 404 aata hai

Kaggle ka `.../proxy/8000/` URL **do cheezon** par depend karta hai:

| Zaroorat | Kaise pata kare |
|---|---|
| Notebook ka **version save** ho (kam se kam ek baar) | URL `/edit` se `/code/...` me badal jata hai |
| **Session running** ho (kernel zinda) | Notebook ke top-right me green dot / "Running" |

Dono me se ek bhi nahi → **404**. Ye Kaggle ka behaviour hai, studio ka bug nahi.

---

## Steps (exact)

### 1. Notebook kholo
Apna notebook editor me kholo: `.../kathareel-kaggle/edit`

### 2. Ek cell banao
`+ Code` dabao, purane cells delete kar do (ya naye notebook me), aur
`kathareel_onecell.py` ka **poora content paste** karo.

### 3. Chalao
`Shift + Enter`. Pehli baar 3-4 min lagega (ffmpeg + pip install).

Aakhir me aisa dikhega:

```
studio files: scripts/content_io.py, web/doctor.py, web/index.html, ...
ffmpeg: True | node: True

==========================================================================
  KHOLO (kaggle proxy — hamesha chalta hai):
  https://www.kaggle.com/code/amanraghav1111111/kathareel-kaggle/proxy/8000/

  ya upar jo PUBLIC https://.... URL print hua wo bhi kaam karega
==========================================================================
```

### 4. Save Version (zaroori, ek baar)
Top-right **Save Version** → **"Quick Save"** chuno.

- ❌ **"Save & Run All (Commit)"** mat chuno — commit ke baad session band ho jata hai, proxy mar jata hai
- ✅ **Quick Save** — version ban jata hai, session zinda rehta hai

### 5. Session chalu rakho
Cell chalne ke baad session khud zinda rehta hai. Tab tak proxy URL kaam karega.

### 6. Ab proxy URL kholo (naye tab me)
```
https://www.kaggle.com/code/amanraghav1111111/kathareel-kaggle/proxy/8000/
```

---

## Agar phir bhi 404

Notebook ke **naye cell** me:

```python
!python web/doctor.py
```

Output dekho:
- `port 8000 band hai` → server nahi chala, onecell dobara chalao
- `koi server nahi chal raha` → same
- `health 200` + `tunnel URL` → server theek hai, sirf proxy ka issue hai

Phir **PUBLIC trycloudflare URL** try karo (cell ne print kiya tha) — wo proxy se
independent hai.

---

## Sabse pakka raasta (agar Kaggle proxy na chale)

Cell chalane ke baad jo **PUBLIC** URL print hota hai, wahi kholo:

```
PUBLIC  : https://xyz-abc-123.trycloudflare.com
```

Ye Kaggle se banaya jata hai (tumhare sandbox se nahi), isliye ye zyada reliable hai.
Free tunnel 2-3 ghante me mar sakta hai — mar jaye to `!python web/doctor.py` se
naya URL lo, ya cell dobara chalao.

---

## Common galtiyan

| Galti | Result |
|---|---|
| Cell chalaya hi nahi | 404 |
| "Save & Run All (Commit)" kiya | Session band → 404 |
| Kaggle tab band kar diya / laptop sleep | Session suspend → 404 |
| Purana `server.py` (version 1.1 ya purana) | Tunnel khud restart nahi hota → 530/1033 |
| `pip install` fail (Internet OFF) | Server start hi nahi hota |

Version check: browser me `<proxy-url>/api/health` kholo — `"version":"1.2"` dikhna chahiye.
