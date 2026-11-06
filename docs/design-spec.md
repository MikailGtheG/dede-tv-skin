# Dede TV OS – visual acceptance contract

The three approved reference screenshots in the design conversation describe
**three different interfaces**, not three variations of Kodi Home:

1. **TV playback / fullscreen**: the running channel occupies the complete
   TV frame. No Kodi chrome, Estuary navigation, panels or development HUD.
   The brief channel change indicator can show channel number + name, then
   disappear. The remote's OK key opens the channel list.
2. **Live-TV channel picker**: a translucent charcoal panel overlays the
   **left ~42%** of the fullscreen picture without stopping playback.
   It shows the small Dede TV OS wordmark, 'Channels', approximately six
   readable rows, a distinctly highlighted current row, and concise
   navigation instructions. OK selects, Back closes, +/- switches channels.
   The right-hand side of the picture remains unobstructed.
3. **Companion web remote (mobile)**: a separate responsive page, not Kodi
   Home, with the now-playing card, remote D-pad/OK, program +/- buttons,
   custom channels, and connection status. A connected-status indicator
   must come from live backend state; never hardcode 'Connected via Tailscale'.

## Non-negotiable behavior

- The appliance boots directly into the **last successfully playing TV
  channel**, if configured and available. No media-center Home screen
  should appear during healthy TV operation.
- With no configured channel, show a deliberately branded Dede TV setup /
  TV-launch fallback. Do not show Estuary's media-center Home or its
  film/series widget grid.
- Missing IPTV configuration is a setup state. A Kodi 'Enable IPTV Simple
  Client?' dialog is not an acceptable production first-run screen.
- Kodi is a playback engine; our skin is the sole visible TV interface.
  The administrative companion web app remains separate.
- All runtime screenshots must be identified as **real QEMU/hardware** or
  **design references**. A passing skin package/XML test does not prove a
  running Kodi window.
- Visual acceptance requires a real full-screen TV screenshot and a
  separate channel picker screenshot on top of the video, from the
  current image. Static mockups are not runtime evidence.

## Visual rules

- Dark charcoal / graphite panel, subtle silver framing, restrained warm
  ivory focus highlight. No blue Estuary accents.
- 1920x1080 reference canvas, scalable to other aspect ratios.
- PVR list binding/control 11 remains functional with real channel names.
- Seven-foot / couch viewing distance: large text and high contrast.
- No settings, logout, or shutdown controls exposed on the TV front page.
- Prefer simple animation and predictable remote navigation.
- Icons and channel labels are data-driven, not hardcoded fictional shows.

## Production release gates

- Automatic IPTV addon setup tested with an authorized playlist/test stream.
- Kodi reports `skin.dede-tv` active via runtime JSON-RPC, and QEMU
  captures the **new** branded windows, not Estuary.
- Boot-to-last-channel, remote OK/Back/+/- and overlays pass end-to-end.
- A reboot with persistent channel state passes on a real installed system.
- Kodi/OS/Core/Skin CI, security checks, and negative failure cases pass.

The home screen remains an operational fallback. The end-user product is
the fullscreen player plus channel overlay, matching the three references.
