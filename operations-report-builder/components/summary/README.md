# OpsClean summary component

A small, local Streamlit v1 component renders four aggregate cleaning counts. It uses the v1 `componentReady`, `render`, and `setFrameHeight` messages, accepts events only from its parent frame, and resizes through `ResizeObserver`. It does not return values or trigger Python reruns.

Anime.js 4.5.0 is vendored under `vendor/` from the npm package, together with its MIT license. The v4 `animate` and `stagger` methods animate only opacity and a six-pixel translation for 220 ms, with a 25 ms stagger. Counts are never animated from zero. Repeated identical arguments do not restart motion. Active animations are cancelled on a new render, reduced-motion preference changes, and page exit.

Only aggregate counts and fixed UI labels are sent by `ui.py`. Cell values and filenames are not sent. Labels use `textContent`; no provided value becomes executable HTML. If Anime.js is unavailable, the summary still renders without animation.

No npm dependencies or frontend build step are needed when deploying. Upload this complete directory with `app.py` and `ui.py`.
