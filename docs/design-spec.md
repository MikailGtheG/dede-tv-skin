# Dede TV visual specification v0

Design is screen-first: no visible homescreen, browser or Debian desktop.

## Visible states
1. Video only, full screen.
2. Translucent channel list overlay, left aligned, with 6–7 visible rows.
3. Temporary, minimal connection/error notice that never blocks remote control.

## Interaction
- OK opens overlay; Up/Down moves focused channel; OK selects.
- Back closes overlay; programme +/- switches directly.
- Inactivity timeout closes overlay; focus always begins on current channel.
- Any hidden Kodi shortcuts must be audited and remapped to avoid accidental settings changes.

## Accessibility
- Layout reference: 1920×1080, rescale for other displays.
- Typography: Inter or Noto Sans with Turkish glyph support; 38–42 px channel labels reference size.
- High contrast and sufficiently generous touch/focus targets.
- No color-only focus indicator, no auto-scrolling text for primary information.
- Test readability at actual couch distance with the real TV and remote.

Kodi skin implementation is pending integration/version validation.
