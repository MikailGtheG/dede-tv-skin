"""Dede TV windows and textures that replace Estuary's media-center UI.

Layout follows the product vision (1920x1080 skin coordinates):
  * channel list: dark rounded panel on the left, the live picture stays
    visible on the right; current row is a light "pill" with dark text;
    key hints in the footer.
  * channel banner on switch: "03 | Kanal D" bottom left plus "OK" hint,
    with "Jetzt / Danach" from the programme guide when there is one.
Textures are generated here (white RGBA shapes, tinted via colordiffuse),
so no third-party artwork is shipped.
"""
import struct
import zlib
from pathlib import Path

TEXT = "FFEDE6DC"          # warm white
TEXT_DIM = "B3EDE6DC"
ACCENT = "FFC9A98A"        # restrained gold-silver accent under the brand
PANEL = "E61C1D20"         # anthracite, slightly translucent
PILL = "FFEFE6DA"          # focused row
PILL_TEXT = "FF141414"
KEY_OUTLINE = "99EDE6DC"


def _png(width, height, alpha):
    """Encode an 8-bit white RGBA PNG whose alpha comes from alpha(x, y)."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw += bytes((255, 255, 255, alpha(x, y)))

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def _rounded(width, height, radius, outline=None):
    """Anti-aliased rounded rectangle (filled, or an outline of given width)."""
    def coverage(x, y, w, h, r):
        # Distance from pixel centre to the rounded-rect edge (inside > 0).
        px, py = x + 0.5, y + 0.5
        cx = min(max(px, r), w - r)
        cy = min(max(py, r), h - r)
        d = r - ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
        return max(0.0, min(1.0, d + 0.5))

    def alpha(x, y):
        outer = coverage(x, y, width, height, radius)
        if outline is None:
            return round(255 * outer)
        inner = coverage(x - outline, y - outline, width - 2 * outline,
                         height - 2 * outline, max(1, radius - outline))
        if not (outline <= x < width - outline and outline <= y < height - outline):
            inner = 0.0
        return round(255 * max(0.0, outer - inner))
    return _png(width, height, alpha)


TEXTURES = {
    "panel.png": (lambda: _rounded(128, 128, 40), "40"),
    "pill.png": (lambda: _rounded(160, 100, 50), "50"),
    "key.png": (lambda: _rounded(64, 48, 14, outline=2), "16"),
    "line.png": (lambda: _png(4, 4, lambda x, y: 255), "0"),
}


def write_textures(media: Path):
    target = media / "dede"
    target.mkdir(parents=True, exist_ok=True)
    for name, (make, _border) in TEXTURES.items():
        (target / name).write_bytes(make())


def _texture(name, color, extra=""):
    border = TEXTURES[name][1]
    return f'<texture border="{border}" colordiffuse="{color}"{extra}>dede/{name}</texture>'


# Texts shown on the TV, as Kodi string ids (skin range 32100+): English
# source text, German and Turkish translations.
STRINGS = {
    32100: ('Channels', 'Sender', 'Kanallar'),
    32101: ('Select', 'Auswählen', 'Seç'),
    32102: ('Watch', 'Ansehen', 'İzle'),
    32103: ('Back', 'Zurück', 'Geri'),
    32104: ('Close', 'Schließen', 'Kapat'),
    32105: ('Channel list', 'Senderliste', 'Kanal listesi'),
    32106: ('Now: ', 'Jetzt: ', 'Şimdi: '),
    32107: ('   ·   Next: ', '   ·   Danach: ', '   ·   Sonra: '),
    32108: ('Setup', 'Einrichtung', 'Kurulum'),
    32109: ('Open on a phone or PC:', 'Am Handy oder PC öffnen:', 'Telefonda veya bilgisayarda açın:'),
    32110: ('Code:', 'Code:', 'Kod:'),
    32111: ('Loading channel …', 'Sender wird geladen …', 'Kanal yükleniyor …'),
    32112: ('Connecting TV …', 'Fernsehen wird verbunden …', 'Televizyon bağlanıyor …'),
    32113: ('Please wait a moment, it retries automatically.[CR][CR]With ▲ ▼ and OK you can also choose another channel.', 'Bitte einen Moment Geduld, es wird automatisch erneut versucht.[CR][CR]Mit ▲ ▼ und OK können Sie auch einen anderen Sender wählen.', 'Lütfen biraz bekleyin, otomatik olarak yeniden deneniyor.[CR][CR]▲ ▼ ve OK ile başka bir kanal da seçebilirsiniz.'),
    32114: ('No channels yet', 'Noch keine Sender', 'Henüz kanal yok'),
    32115: ('The channel list is loading or not set up yet. Please contact the administrator if this stays.', 'Die Senderliste wird gerade geladen oder ist noch nicht eingerichtet. Bitte den Administrator kontaktieren, falls dies so bleibt.', 'Kanal listesi yükleniyor veya henüz kurulmadı. Bu durum sürerse lütfen yöneticiye başvurun.'),
}

LANGUAGES = {"resource.language.en_gb": 0, "resource.language.de_de": 1, "resource.language.tr_tr": 2}


def _po_quote(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def write_strings(language_dir):
    """Append Dede TV's strings to the skin's en_gb, de_de and tr_tr catalogues."""
    for language, column in LANGUAGES.items():
        po = language_dir / language / "strings.po"
        text = po.read_text(encoding="utf-8")
        if 'msgctxt "#32100"' in text:
            raise ValueError(f"{po}: string id 32100 already used upstream")
        entries = []
        for number, texts in STRINGS.items():
            msgstr = "" if column == 0 else _po_quote(texts[column])
            entries.append(f'msgctxt "#{number}"\nmsgid "{_po_quote(texts[0])}"\nmsgstr "{msgstr}"\n')
        po.write_text(text.rstrip("\n") + "\n\n# Dede TV\n\n" + "\n".join(entries), encoding="utf-8")

def _key_hint(left, top, key, key_width, text):
    return f"""
            <control type="image">
                <left>{left}</left><top>{top}</top><width>{key_width}</width><height>48</height>
                {_texture("key.png", KEY_OUTLINE)}
            </control>
            <control type="label">
                <left>{left}</left><top>{top}</top><width>{key_width}</width><height>48</height>
                <font>font13</font><textcolor>{TEXT}</textcolor>
                <align>center</align><aligny>center</aligny>
                <label>{key}</label>
            </control>
            <control type="label">
                <left>{left + key_width + 14}</left><top>{top}</top><width>200</width><height>48</height>
                <font>font13</font><textcolor>{TEXT_DIM}</textcolor><aligny>center</aligny>
                <label>{text}</label>
            </control>"""


def _row(focused):
    pill = f"""
                <control type="image">
                    <left>0</left><top>6</top><width>760</width><height>100</height>
                    {_texture("pill.png", PILL)}
                </control>""" if focused else ""
    color = PILL_TEXT if focused else TEXT
    bold = ("[B]", "[/B]") if focused else ("", "")
    return f"""{pill}
                <control type="label">
                    <left>48</left><top>6</top><width>110</width><height>100</height>
                    <font>font45</font><textcolor>{color}</textcolor><selectedcolor>{color}</selectedcolor>
                    <aligny>center</aligny>
                    <label>{bold[0]}$INFO[ListItem.ChannelNumberLabel]{bold[1]}</label>
                </control>
                <control type="label">
                    <left>170</left><top>6</top><width>560</width><height>100</height>
                    <font>font45</font><textcolor>{color}</textcolor><selectedcolor>{color}</selectedcolor>
                    <aligny>center</aligny>
                    <label>{bold[0]}$INFO[ListItem.Label]{bold[1]}</label>
                </control>"""


CHANNEL_LIST = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV channel list: overlay on the left, picture stays visible. -->
<window>
    <defaultcontrol always="true">11</defaultcontrol>
    <controls>
        <control type="group">
            <animation effect="fade" start="0" end="100" time="120">WindowOpen</animation>
            <animation effect="fade" start="100" end="0" time="120">WindowClose</animation>
            <left>36</left>
            <top>36</top>
            <control type="image">
                <left>0</left><top>0</top><width>820</width><height>1008</height>
                {_texture("panel.png", PANEL)}
            </control>
            <control type="label">
                <left>64</left><top>40</top><width>600</width><height>60</height>
                <font>font32</font><textcolor>{TEXT}</textcolor>
                <label>[B]Dede[/B] TV OS</label>
            </control>
            <control type="image">
                <left>66</left><top>98</top><width>104</width><height>4</height>
                {_texture("line.png", ACCENT)}
            </control>
            <control type="label">
                <left>64</left><top>118</top><width>700</width><height>110</height>
                <font>font52_title</font><textcolor>{TEXT}</textcolor>
                <label>$LOCALIZE[32100]</label>
            </control>
            <control type="list" id="11">
                <left>30</left><top>248</top><width>760</width><height>672</height>
                <onup>11</onup><ondown>11</ondown><onleft>11</onleft><onright>11</onright>
                <scrolltime tween="linear">120</scrolltime>
                <itemlayout height="112" width="760">{_row(False)}
                </itemlayout>
                <focusedlayout height="112" width="760">{_row(True)}
                </focusedlayout>
            </control>
            <control type="image">
                <left>40</left><top>928</top><width>740</width><height>2</height>
                {_texture("line.png", "33EDE6DC")}
            </control>{_key_hint(48, 944, "▲ ▼", 84, "$LOCALIZE[32101]")}{_key_hint(318, 944, "OK", 64, "$LOCALIZE[32102]")}{_key_hint(546, 944, "$LOCALIZE[32103]", 100, "$LOCALIZE[32104]")}
        </control>
        <include>PVRChannelNumberInput</include>
    </controls>
</window>
"""


# Kodi shows the auto-visible DialogSeekBar window on Player.ShowInfo
# (every channel switch), pause, seeking and channel-number entry. Estuary's
# version is a full media-player bar; ours is only the channel banner.
SEEKBAR = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV channel banner after switching: "03 | Kanal D" + OK hint. -->
<window>
    <visible>Window.IsActive(fullscreenvideo)</visible>
    <visible>!Window.IsActive(pvrosdchannels)</visible>
    <visible>Player.ShowInfo | !String.IsEmpty(PVR.ChannelNumberInput)</visible>
    <controls>
        <control type="group">
            <visible>String.IsEmpty(PVR.ChannelNumberInput)</visible>
            <animation effect="fade" start="0" end="100" time="150">Visible</animation>
            <animation effect="fade" start="100" end="0" time="300">Hidden</animation>
            <control type="image">
                <left>120</left><top>800</top><width>640</width><height>116</height>
                {_texture("pill.png", "D91C1D20")}
            </control>
            <control type="label">
                <left>160</left><top>800</top><width>130</width><height>116</height>
                <font>font52_title</font><textcolor>{TEXT}</textcolor>
                <align>center</align><aligny>center</aligny>
                <label>$INFO[VideoPlayer.ChannelNumberLabel]</label>
            </control>
            <control type="image">
                <left>310</left><top>828</top><width>2</width><height>60</height>
                {_texture("line.png", "66EDE6DC")}
            </control>
            <control type="label">
                <left>340</left><top>800</top><width>400</width><height>116</height>
                <font>font52_title</font><textcolor>{TEXT}</textcolor><aligny>center</aligny>
                <label>$INFO[VideoPlayer.ChannelName]</label>
            </control>
            <control type="label">
                <visible>VideoPlayer.HasEpg</visible>
                <left>130</left><top>922</top><width>1400</width><height>56</height>
                <font>font32</font><textcolor>{TEXT_DIM}</textcolor><aligny>center</aligny>
                <label>$INFO[Player.Title,$LOCALIZE[32106]]$INFO[VideoPlayer.NextTitle,$LOCALIZE[32107]]</label>
            </control>{_key_hint(800, 990, "OK", 64, "$LOCALIZE[32105]")}
        </control>
        <control type="group">
            <visible>!String.IsEmpty(PVR.ChannelNumberInput)</visible>
            <control type="image">
                <left>120</left><top>800</top><width>300</width><height>116</height>
                {_texture("pill.png", "D91C1D20")}
            </control>
            <control type="label">
                <left>120</left><top>800</top><width>300</width><height>116</height>
                <font>font52_title</font><textcolor>{TEXT}</textcolor>
                <align>center</align><aligny>center</aligny>
                <label>$INFO[PVR.ChannelNumberInput]</label>
            </control>
        </control>
    </controls>
</window>
"""


# Setup card while the administration has no password yet: address and
# one-time code, published by the service.dede-setup add-on. Kept clear of
# the picture's sample regions used by the QEMU tests (top right corner).
def _setup_card():
    return f"""
        <control type="group">
            <visible>!String.IsEmpty(Window(Home).Property(dede.setup.code))</visible>
            <left>920</left><top>40</top>
            <control type="image">
                <left>0</left><top>0</top><width>560</width><height>280</height>
                {_texture("panel.png", PANEL)}
            </control>
            <control type="label">
                <left>36</left><top>24</top><width>500</width><height>50</height>
                <font>font32</font><textcolor>{ACCENT}</textcolor>
                <label>[B]$LOCALIZE[32108][/B]</label>
            </control>
            <control type="label">
                <left>36</left><top>78</top><width>500</width><height>44</height>
                <font>font13</font><textcolor>{TEXT_DIM}</textcolor>
                <label>$LOCALIZE[32109]</label>
            </control>
            <control type="label">
                <left>36</left><top>118</top><width>500</width><height>56</height>
                <font>font32</font><textcolor>{TEXT}</textcolor>
                <label>$INFO[Window(Home).Property(dede.setup.url)]</label>
            </control>
            <control type="label">
                <left>36</left><top>186</top><width>500</width><height>70</height>
                <font>font45</font><textcolor>{TEXT}</textcolor>
                <label>$LOCALIZE[32110] [B]$INFO[Window(Home).Property(dede.setup.code)][/B]</label>
            </control>
        </control>"""


FULLSCREEN = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV full-screen TV: picture only. Controls placed here are not drawn
     over the picture; overlays live in auto-visible dialogs instead. -->
<window>
    <controls />
</window>
"""

# Loading indicator while a channel starts, as an auto-visible dialog so it
# is drawn over the (still black) picture.
LOADING_OVERLAY = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV: "loading" pill while a channel starts. -->
<window type="dialog" id="1150">
    <visible>Window.IsActive(fullscreenvideo) + [Player.Caching | [Player.HasMedia + !Player.HasVideo]]</visible>
    <controls>
        <control type="image">
            <left>660</left><top>480</top><width>600</width><height>120</height>
            {_texture("pill.png", "D91C1D20")}
        </control>
        <control type="label">
            <left>660</left><top>480</top><width>600</width><height>120</height>
            <font>font37</font><textcolor>{TEXT}</textcolor>
            <align>center</align><aligny>center</aligny>
            <label>$LOCALIZE[32111]</label>
        </control>
    </controls>
</window>
"""


# Home is the "no picture" screen: shown at power-on until the first channel
# plays and whenever a channel cannot be played. Kodi's channel-list dialog
# only fills while a channel plays, so Home carries its own channel list,
# filled from the PVR database. Clicking a channel plays it (PlayMedia).
HOME = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV home: channel list + reconnect message when no picture plays. -->
<window>
    <defaultcontrol always="true">50</defaultcontrol>
    <backgroundcolor>background</backgroundcolor>
    <controls>
        <control type="group">
            <left>36</left>
            <top>36</top>
            <control type="image">
                <left>0</left><top>0</top><width>820</width><height>1008</height>
                {_texture("panel.png", PANEL)}
            </control>
            <control type="label">
                <left>64</left><top>40</top><width>600</width><height>60</height>
                <font>font32</font><textcolor>{TEXT}</textcolor>
                <label>[B]Dede[/B] TV OS</label>
            </control>
            <control type="image">
                <left>66</left><top>98</top><width>104</width><height>4</height>
                {_texture("line.png", ACCENT)}
            </control>
            <control type="label">
                <left>64</left><top>118</top><width>700</width><height>110</height>
                <font>font52_title</font><textcolor>{TEXT}</textcolor>
                <label>$LOCALIZE[32100]</label>
            </control>
            <control type="list" id="50">
                <left>30</left><top>248</top><width>760</width><height>672</height>
                <onup>50</onup><ondown>50</ondown><onleft>50</onleft><onright>50</onright>
                <scrolltime tween="linear">120</scrolltime>
                <content target="pvr">pvr://channels/tv/*</content>
                <itemlayout height="112" width="760">{_row(False)}
                </itemlayout>
                <focusedlayout height="112" width="760">{_row(True)}
                </focusedlayout>
            </control>
            <control type="image">
                <left>40</left><top>928</top><width>740</width><height>2</height>
                {_texture("line.png", "33EDE6DC")}
            </control>{_key_hint(48, 944, "▲ ▼", 84, "$LOCALIZE[32101]")}{_key_hint(318, 944, "OK", 64, "$LOCALIZE[32102]")}
        </control>
        <control type="group">
            <visible>PVR.HasTVChannels</visible>
            <control type="label">
                <left>1000</left><top>380</top><width>860</width><height>100</height>
                <font>font52_title</font><textcolor>{TEXT}</textcolor>
                <label>$LOCALIZE[32112]</label>
            </control>
            <control type="textbox">
                <left>1004</left><top>500</top><width>820</width><height>240</height>
                <font>font30_title</font><textcolor>{TEXT_DIM}</textcolor>
                <label>$LOCALIZE[32113]</label>
            </control>
        </control>
        <control type="group">
            <visible>!PVR.HasTVChannels</visible>
            <control type="label">
                <left>1000</left><top>380</top><width>860</width><height>100</height>
                <font>font52_title</font><textcolor>{TEXT}</textcolor>
                <label>$LOCALIZE[32114]</label>
            </control>
            <control type="textbox">
                <left>1004</left><top>500</top><width>820</width><height>200</height>
                <font>font30_title</font><textcolor>{TEXT_DIM}</textcolor>
                <label>$LOCALIZE[32115]</label>
            </control>
        </control>
    </controls>
</window>
"""


# Estuary's clock/"ends at" bar over full-screen video.
# Estuary's top bar slot (custom dialog 1109) is reused for the setup card:
# Kodi shows such auto-visible dialogs over full-screen video and Home alike,
# while controls inside VideoFullScreen did not appear over the picture.
SETUP_OVERLAY = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV: setup card only; no media-center overlays over live TV.
     Custom windows need their id, or Kodi rejects the file. -->
<window type="dialog" id="1109">
    <visible>!String.IsEmpty(Window(Home).Property(dede.setup.code))</visible>
    <controls>{_setup_card()}
    </controls>
</window>
"""

# Kodi and add-on toasts ("Loaded 5 channels", update hints, PVR import
# notices) are technical messages for a TV viewer. The window stays defined
# so Kodi can open and close it, but renders nothing.
NOTIFICATION = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV: technical Kodi/add-on toasts are never shown to viewers. -->
<window>
    <visible>false</visible>
    <controls />
</window>
"""


def write_windows(xml_dir: Path):
    (xml_dir / "DialogPVRChannelsOSD.xml").write_text(CHANNEL_LIST, encoding="utf-8")
    (xml_dir / "VideoFullScreen.xml").write_text(FULLSCREEN, encoding="utf-8")
    (xml_dir / "Home.xml").write_text(HOME, encoding="utf-8")
    (xml_dir / "DialogNotification.xml").write_text(NOTIFICATION, encoding="utf-8")
    (xml_dir / "DialogSeekBar.xml").write_text(SEEKBAR, encoding="utf-8")
    (xml_dir / "Custom_1109_TopBarOverlay.xml").write_text(SETUP_OVERLAY, encoding="utf-8")
    (xml_dir / "Custom_1150_DedeLoading.xml").write_text(LOADING_OVERLAY, encoding="utf-8")
