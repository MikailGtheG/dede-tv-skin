"""Dede TV windows and textures that replace Estuary's media-center UI.

Layout follows the product vision (1920x1080 skin coordinates):
  * channel list: dark rounded panel on the left, the live picture stays
    visible on the right; current row is a light "pill" with dark text;
    key hints in the footer.
  * channel banner on switch: "03 | Kanal D" bottom left plus "OK" hint.
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
                    <font>font45</font><textcolor>{color}</textcolor><aligny>center</aligny>
                    <label>{bold[0]}$INFO[ListItem.ChannelNumberLabel]{bold[1]}</label>
                </control>
                <control type="label">
                    <left>170</left><top>6</top><width>560</width><height>100</height>
                    <font>font45</font><textcolor>{color}</textcolor><aligny>center</aligny>
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
                <label>Sender</label>
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
            </control>{_key_hint(48, 944, "▲ ▼", 84, "Auswählen")}{_key_hint(318, 944, "OK", 64, "Ansehen")}{_key_hint(546, 944, "Zurück", 100, "Schließen")}
        </control>
        <include>PVRChannelNumberInput</include>
    </controls>
</window>
"""


FULLSCREEN = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Dede TV full-screen TV: only a channel banner after switching. -->
<window>
    <controls>
        <control type="group">
            <visible>Player.ShowInfo + !Window.IsVisible(PVROSDChannels)</visible>
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
            </control>{_key_hint(800, 990, "OK", 64, "Senderliste")}
        </control>
        <control type="group">
            <visible>Player.Caching | (Player.HasMedia + !Player.HasVideo)</visible>
            <control type="image">
                <left>660</left><top>480</top><width>600</width><height>120</height>
                {_texture("pill.png", "D91C1D20")}
            </control>
            <control type="label">
                <left>660</left><top>480</top><width>600</width><height>120</height>
                <font>font37</font><textcolor>{TEXT}</textcolor>
                <align>center</align><aligny>center</aligny>
                <label>Sender wird geladen …</label>
            </control>
        </control>
        <include>PVRChannelNumberInput</include>
    </controls>
</window>
"""


HOME = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Shown only when no channel is playing (e.g. no IPTV source yet). -->
<window>
    <defaultcontrol always="true">9000</defaultcontrol>
    <backgroundcolor>background</backgroundcolor>
    <controls>
        <control type="label">
            <left>112</left><top>112</top><width>1200</width><height>90</height>
            <font>font45</font><textcolor>white</textcolor>
            <label>DEDE TV</label>
        </control>
        <control type="label">
            <left>116</left><top>215</top><width>1300</width><height>65</height>
            <font>font30_title</font><textcolor>grey</textcolor>
            <label>Fernsehen, einfach einschalten.</label>
        </control>
        <control type="button" id="9000">
            <left>112</left><top>420</top><width>800</width><height>125</height>
            <font>font37</font><textcolor>white</textcolor><focusedcolor>{PILL_TEXT}</focusedcolor>
            <texturefocus border="50" colordiffuse="{PILL}">dede/pill.png</texturefocus>
            <texturenofocus border="50" colordiffuse="{PANEL}">dede/pill.png</texturenofocus>
            <textoffsetx>48</textoffsetx>
            <label>Senderliste öffnen</label>
            <onclick>ActivateWindow(PVROSDChannels)</onclick>
            <onup>9000</onup><ondown>9000</ondown><onleft>9000</onleft><onright>9000</onright>
        </control>
        <control type="label">
            <left>116</left><top>920</top><width>1600</width><height>60</height>
            <font>font27</font><textcolor>grey</textcolor>
            <visible>!PVR.HasTVChannels</visible>
            <label>Noch keine Sender eingerichtet. Bitte den Administrator kontaktieren.</label>
        </control>
    </controls>
</window>
"""


def write_windows(xml_dir: Path):
    (xml_dir / "DialogPVRChannelsOSD.xml").write_text(CHANNEL_LIST, encoding="utf-8")
    (xml_dir / "VideoFullScreen.xml").write_text(FULLSCREEN, encoding="utf-8")
    (xml_dir / "Home.xml").write_text(HOME, encoding="utf-8")
