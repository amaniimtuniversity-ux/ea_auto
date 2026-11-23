import {Config} from '@remotion/cli/config';

// Render settings: 1280x720 H.264, CPU-friendly defaults.
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(18);
// CPU vs GPU — read this before changing anything.
//
// Remotion renders in headless Chromium and encodes with ffmpeg, both on the CPU.
// A GPU is NOT required and normally gives nothing: Chromium's WebGL is only used
// for a few compositing ops, and our scenes use plain 2D + CSS. Benchmarks on this
// project (150 frames, 1280x720, 2-core machine):
//   concurrency=1 ......... 25.3 s
//   concurrency=2 ......... 12.7 s   <- ~2x faster, purely from CPU parallelism
//   --gl=swiftshader ...... 13.7 s   <- software GL, same speed as default
//
// So: scale speed with --concurrency (cores), not with a GPU.
// On a GPU machine you *can* try --gl=angle-egl or --gl=vulkan; it sometimes helps
// scenes that use WebGL/backdrop-filter, and never hurts correctness.

// On ARM/Linux without a bundled browser, point at system Chromium:
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
