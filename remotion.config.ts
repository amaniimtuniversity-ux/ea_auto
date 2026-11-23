import {Config} from '@remotion/cli/config';

// Render settings: 1280x720 H.264, CPU-friendly defaults.
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(18);
// On ARM/Linux without a bundled browser, point at system Chromium:
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
