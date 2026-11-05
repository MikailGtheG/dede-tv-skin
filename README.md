# Dede TV Skin — Kodi

A TV-first Kodi skin for Dede TV OS, developed from the complete upstream
Estuary skin rather than shipping incomplete Kodi dialogs.

## First working artifact: experimental skin archive

The package builder copies all required skin windows/media from Estuary in
our Kodi fork, retains upstream attribution and LICENSE.txt, changes the add-on
identity to `skin.dede-tv`, then applies a narrower live-TV channel overlay.

- Channel overlay width is reduced from the Estuary default to leave more
  live video visible.
- List focus position and scroll timing have been adjusted for faster remote
  navigation.
- Upstream controls, PVR list bindings and dialogs are retained.

Build locally:

```sh
python3 scripts/build_skin.py /path/to/xbmc/addons/skin.estuary /tmp/skin.dede-tv
```

GitHub Actions packages the derivative as a short-lived downloadable CI
artifact and validates the core Kodi XML files. The build process currently
targets the Kodi master branch used by `MikailGtheG/xbmc`.

## Important current limitations

This is an **experimental, packaged Kodi skin**, not the final Dede TV design.
It still contains the original Estuary artwork and most Estuary layouts.
Our charcoal/silver TV UI, custom lion assets, font integration and locked-down
navigation are not complete. Packaging CI is **not** evidence of successful
runtime skin loading, remote mapping or guaranteed accessibility. Validate
inside Kodi before applying it as the default skin.

## Licensing

The generated archive retains Estuary licensing and attribution. Any
derivative artwork or layout must respect the licenses shipped by upstream.
See the copied `LICENSE.txt` in the generated skin package.
