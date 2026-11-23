#!/usr/bin/env bash
# kathareel — ek command me poora flow (by raghv)
#
#   scripts/make_video.sh --minutes 3          # 1) script banao + review karo (AADHA FLOW)
#   scripts/make_video.sh --build              # 2) review ke baad: voice + render
#   scripts/make_video.sh --build --force      #    script review skip karke seedha bana do
#
# Har step par ruk kar tumhe batata hai ki kya karna hai.
set -euo pipefail
cd "$(dirname "$0")/.."

MINUTES=""
BUILD=0
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --minutes=*) MINUTES="${arg#*=}" ;;
    --minutes) shift_next=1 ;;
    --build) BUILD=1 ;;
    --force) FORCE=1 ;;
    -h|--help)
      sed -n '2,12p' "$0"; exit 0 ;;
  esac
done
# allow: --minutes 3
prev=""
for arg in "$@"; do
  if [ "$prev" = "--minutes" ]; then MINUTES="$arg"; fi
  prev="$arg"
done

PY=python3
command -v "$PY" >/dev/null || PY=python

section() { printf '\n\033[1;33m▸ %s\033[0m\n' "$1"; }

if [ "$BUILD" = "0" ]; then
  section "1/2  SCRIPT (review ke liye)"
  if [ -n "$MINUTES" ]; then
    $PY scripts/script_review.py --minutes "$MINUTES"
  else
    $PY scripts/script_review.py
  fi
  echo
  echo "  ┌──────────────────────────────────────────────────────────┐"
  echo "  │ script.md kholo, jo badalna hai badlo (say / sub / key)  │"
  echo "  │ phir:  scripts/make_video.sh --build                     │"
  echo "  └──────────────────────────────────────────────────────────┘"
  exit 0
fi

section "2/2  VOICE + VIDEO"
if [ "$FORCE" = "0" ]; then
  if [ ! -f script.md ]; then
    echo "script.md nahi mila - pehle: scripts/make_video.sh --minutes 3"
    exit 1
  fi
  echo "script.md ke edits content.ts me daal raha hoon..."
  $PY scripts/script_review.py --from-script
fi

section "check"
$PY scripts/check_content.py || { echo; echo "❌ upar ke errors fix karo (src/content.ts ya script.md)"; exit 1; }

section "voice (Hindi)"
$PY scripts/build_voice.py

section "render"
mkdir -p out
CORES=$(nproc 2>/dev/null || echo 2)
if [ "$CORES" -gt 4 ]; then CORES=4; fi
npx remotion render src/index.ts Explainer out/video.mp4 --concurrency="$CORES" 2>&1 | tail -3

echo
echo "✅ ready: out/video.mp4"
ls -lh out/video.mp4
