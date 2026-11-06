#!/usr/bin/env python3
"""Build a derivative Dede TV Kodi skin from a pinned checkout of Estuary.

The original Estuary license/attribution and all required dialog XML files
remain included. Dede-specific changes are intentionally limited and testable.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET


def replace_exact(text: str, original: str, replacement: str) -> str:
    if original not in text:
        raise ValueError(f"upstream Estuary layout changed: expected {original!r}")
    return text.replace(original, replacement)


def build(upstream: Path, destination: Path) -> None:
    if destination.exists():
        raise FileExistsError(f"build output already exists: {destination}")
    for required in ("addon.xml", "xml/Home.xml", "xml/DialogPVRChannelsOSD.xml"):
        if not (upstream / required).is_file():
            raise FileNotFoundError(upstream / required)
    shutil.copytree(upstream, destination)

    manifest = destination / "addon.xml"
    tree = ET.parse(manifest)
    addon = tree.getroot()
    addon.set("id", "skin.dede-tv")
    addon.set("name", "Dede TV OS")
    addon.set("version", "0.1.0")
    addon.set("provider-name", "Dede TV OS contributors and upstream Estuary authors")
    # Debian 13 ships Kodi 21.2 (Omega) and xbmc.gui ABI 5.17.0.
    gui_reqs = addon.findall("./requires/import[@addon='xbmc.gui']")
    if len(gui_reqs) != 1 or gui_reqs[0].get("version") != "5.17.0":
        raise ValueError("Skin base must be Kodi 21.2 Omega (xbmc.gui 5.17.0)")
    metadata = addon.find("./extension[@point='xbmc.addon.metadata']")
    if metadata is not None:
        for child in list(metadata):
            if child.tag in {"summary", "description", "disclaimer"}:
                metadata.remove(child)
        summary = ET.SubElement(metadata, "summary", {"lang": "en_GB"})
        summary.text = "Simple, large-screen TV-first Kodi interface"
        description = ET.SubElement(metadata, "description", {"lang": "en_GB"})
        description.text = (
            "Early Dede TV OS prototype derived from Estuary; "
            "not a complete production skin."
        )
        disclaimer = ET.SubElement(metadata, "disclaimer", {"lang": "en_GB"})
        disclaimer.text = "Experimental. No warranty or production compatibility."
        source = metadata.find("source")
        if source is not None:
            source.text = "https://github.com/MikailGtheG/dede-tv-skin"
    tree.write(manifest, encoding="utf-8", xml_declaration=True)

    # Preserve Estuary's PVR list bindings (control id=11, scrollbar id=60,
    # PVRListItemLayouts) while reducing obstruction of the playing video.
    popup = destination / "xml" / "DialogPVRChannelsOSD.xml"
    xml = popup.read_text(encoding="utf-8")
    xml = replace_exact(xml, 'name="width" value="1042"', 'name="width" value="800"')
    xml = replace_exact(xml, "<width>970</width>", "<width>720</width>")
    xml = replace_exact(xml, "<left>970</left>", "<left>720</left>")
    xml = replace_exact(xml, "<focusposition>4</focusposition>",
                        "<focusposition>2</focusposition>")
    xml = replace_exact(xml,
                        "<label>$VAR[BreadcrumbsPVRChannelsOSDVar]</label>",
                        "<label>DEDE TV  |  SENDER</label>")
    xml = replace_exact(xml, '<scrolltime tween="cubic" easing="out">500</scrolltime>',
                        '<scrolltime tween="cubic" easing="out">200</scrolltime>')
    # Dede TV palette: restrained silver on charcoal, without Estuary's blue.
    # Keep the original color names because hundreds of skin XML bindings
    # refer to them; change values rather than breaking those references.
    palette = {
        "primary_background": "FF17191C",
        "secondary_background": "CC292D32",
        "dialog_tint": "FF202328",
        "background": "FF101114",
        "bg_image": "FF70757C",
        "bg_overlay": "22000000",
        "white": "FFF4F5F6",
        "grey": "FFB8BDC5",
        "blue": "FFD5D9DF",
        "button_focus": "FFF1E4D9",
        "button_alt_focus": "80F1E4D9",
        "selected": "FFF1E4D9",
    }
    colors_path = destination / "colors" / "defaults.xml"
    colors_tree = ET.parse(colors_path)
    colors_root = colors_tree.getroot()
    for node in colors_root.findall("color"):
        name = node.get("name")
        if name in palette:
            node.text = palette[name]
    missing = palette.keys() - {node.get("name") for node in colors_root.findall("color")}
    if missing:
        raise ValueError(f"upstream Estuary colors missing: {sorted(missing)}")
    colors_tree.write(colors_path, encoding="utf-8", xml_declaration=True)

    # Replace the media-center home with a minimal TV-first launch surface.
    # The home is only a fallback: actual playback remains fullscreen and
    # takes precedence. Keep the original dialogs/includes for compatibility.
    home = destination / "xml" / "Home.xml"
    home.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<window>
    <defaultcontrol always="true">9000</defaultcontrol>
    <backgroundcolor>background</backgroundcolor>
    <controls>
        <control type="label">
            <left>112</left>
            <top>112</top>
            <width>1200</width>
            <height>90</height>
            <font>font45</font>
            <textcolor>white</textcolor>
            <label>DEDE TV</label>
        </control>
        <control type="label">
            <left>116</left>
            <top>215</top>
            <width>1300</width>
            <height>65</height>
            <font>font30</font>
            <textcolor>grey</textcolor>
            <label>Fernsehen, einfach einschalten.</label>
        </control>
        <control type="button" id="9000">
            <left>112</left>
            <top>420</top>
            <width>800</width>
            <height>125</height>
            <font>font35</font>
            <textcolor>white</textcolor>
            <focusedcolor>white</focusedcolor>
            <label>Live-TV und Sender</label>
            <onclick>ActivateWindow(TVChannels)</onclick>
            <onup>9000</onup>
            <ondown>9000</ondown>
        </control>
        <control type="label">
            <left>116</left>
            <top>920</top>
            <width>1600</width>
            <height>60</height>
            <font>font20</font>
            <textcolor>grey</textcolor>
            <label>OK: Senderliste öffnen</label>
        </control>
    </controls>
</window>
""", encoding="utf-8")
    ET.parse(home)

    # Preserve XML parseability and the original property expressions.
    ET.fromstring(xml)
    popup.write_text(xml, encoding="utf-8")
    ET.parse(manifest)

    # A derivative redistributes Estuary files and must keep upstream license.
    licenses = [p for p in destination.iterdir() if "licen" in p.name.lower()]
    if not licenses:
        raise FileNotFoundError("Estuary license file missing from source skin")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("estuary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.estuary, args.output)
    print(f"Built Dede TV test skin at {args.output}")
