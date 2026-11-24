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

from dede_tv_windows import write_textures, write_windows


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

    # Replace Estuary's channel list, full-screen TV and home windows with
    # the Dede TV layouts (see dede_tv_windows.py). Control id 11 is the
    # list Kodi's CGUIDialogPVRChannelsOSD binds to.
    write_windows(destination / "xml")
    write_textures(destination / "media")
    # Kodi's modal "Playback failed" dialog (heading string 16026) is
    # technical; dede-tv-guard closes it at once and Home explains the
    # situation instead. Keep it invisible meanwhile. Other confirmation
    # dialogs stay unchanged.
    confirm = destination / "xml" / "DialogConfirm.xml"
    confirm_xml = confirm.read_text(encoding="utf-8")
    confirm_xml = replace_exact(
        confirm_xml,
        "\t\t<control type=\"group\">\n\t\t\t<height>400</height>",
        "\t\t<control type=\"group\">\n"
        "\t\t\t<visible>!String.IsEqual(Control.GetLabel(1),$LOCALIZE[16026])</visible>\n"
        "\t\t\t<height>400</height>")
    ET.fromstring(confirm_xml)
    confirm.write_text(confirm_xml, encoding="utf-8")
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

    # Kodi on Linux resolves some font paths using lowercase file names.
    # Estuary's XML uses mixed-case font filenames; the older runtime emits
    # GUIFontManager::LoadTTF errors for lowercase paths. Bundle both spellings
    # without modifying the upstream files or font licenses.
    fonts_dir = destination / "fonts"
    font_aliases = {
        "NotoSans-Regular.ttf": "notosans-regular.ttf",
        "NotoMono-Regular.ttf": "notomono-regular.ttf",
        "Roboto-Thin.ttf": "roboto-thin.ttf",
    }
    for original, alias in font_aliases.items():
        source = fonts_dir / original
        target = fonts_dir / alias
        if not source.is_file() or source.stat().st_size < 1024:
            raise FileNotFoundError(f"Missing bundled Kodi font: {source}")
        if target.exists():
            raise FileExistsError(f"Font alias already exists: {target}")
        shutil.copyfile(source, target)


    for window in ("DialogPVRChannelsOSD.xml", "VideoFullScreen.xml", "Home.xml"):
        ET.parse(destination / "xml" / window)
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
