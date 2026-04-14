#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Convert Emulation Station theme XML files to JSON format.

This script converts theme XML files to JSON format compatible with Emulation Station.
It handles includes, views, subsets, features, and variables.
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET

FILTER_KEYS = {
    "if",
    "lang",
    "region",
    "tinyScreen",
    "verticalScreen",
    "ifHelpPrompts",
    "ifCheevos",
    "ifArch",
    "ifNotArch",
    "ifSubset",
    "cache",
}

# Embedded theme schema (generated from resources/theme_schema.json)
# Eliminates external file dependency for conversion.
EMBEDDED_SCHEMA = {
    "elements": {
        "batteryIcon": {
            "at25",
            "at50",
            "at75",
            "empty",
            "full",
            "incharge",
        },
        "batteryIndicator": {
            "activityColor",
            "at25",
            "at50",
            "at75",
            "color",
            "empty",
            "full",
            "horizontalAlignment",
            "hotkeyColor",
            "imagePath",
            "incharge",
            "itemSpacing",
            "networkIcon",
            "planemodeIcon",
            "pos",
            "size",
            "visible",
            "zIndex",
        },
        "batteryText": set(),
        "carousel": {
            "color",
            "colorEnd",
            "defaultTransition",
            "gradientType",
            "logoAlignment",
            "logoPos",
            "logoRotation",
            "logoRotationOrigin",
            "logoScale",
            "logoSize",
            "maxLogoCount",
            "minLogoOpacity",
            "origin",
            "pos",
            "scaledLogoSpacing",
            "scrollSound",
            "size",
            "systemInfoCountOnly",
            "systemInfoDelay",
            "transitionSpeed",
            "type",
            "zIndex",
        },
        "clock": set(),
        "container": {
            "clipChildren",
            "h",
            "opacity",
            "origin",
            "padding",
            "pos",
            "scale",
            "scaleOrigin",
            "size",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "control": {
            "clipChildren",
            "clipRect",
            "h",
            "offset",
            "offsetX",
            "offsetY",
            "opacity",
            "pos",
            "rotation",
            "rotationOrigin",
            "scale",
            "scaleOrigin",
            "size",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "controllerActivity": {
            "activityColor",
            "at25",
            "at50",
            "at75",
            "color",
            "empty",
            "full",
            "gunPath",
            "horizontalAlignment",
            "hotkeyColor",
            "imagePath",
            "incharge",
            "itemSpacing",
            "networkIcon",
            "planemodeIcon",
            "pos",
            "size",
            "visible",
            "wheelPath",
            "zIndex",
        },
        "datetime": {
            "alignment",
            "backgroundColor",
            "color",
            "displayRelative",
            "fontPath",
            "fontSize",
            "forceUppercase",
            "format",
            "h",
            "lineSpacing",
            "opacity",
            "origin",
            "pos",
            "rotation",
            "rotationOrigin",
            "scale",
            "scaleOrigin",
            "size",
            "value",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "gamecarousel": {
            "color",
            "colorEnd",
            "defaultTransition",
            "gradientType",
            "imageSource",
            "logoAlignment",
            "logoPos",
            "logoRotation",
            "logoRotationOrigin",
            "logoScale",
            "logoSize",
            "maxLogoCount",
            "minLogoOpacity",
            "origin",
            "pos",
            "scaledLogoSpacing",
            "scrollSound",
            "size",
            "transitionSpeed",
            "type",
            "zIndex",
        },
        "gameextras": {
            "path",
        },
        "gridtile": {
            "backgroundCenterColor",
            "backgroundColor",
            "backgroundCornerSize",
            "backgroundEdgeColor",
            "backgroundImage",
            "imageColor",
            "imageSizeMode",
            "padding",
            "reflexion",
            "selectionMode",
            "size",
        },
        "helpsystem": {
            "fontPath",
            "fontSize",
            "glowColor",
            "glowOffset",
            "glowSize",
            "iconA",
            "iconB",
            "iconColor",
            "iconF1",
            "iconL",
            "iconLeftRight",
            "iconR",
            "iconSelect",
            "iconStart",
            "iconUpDown",
            "iconUpDownLeftRight",
            "iconX",
            "iconY",
            "origin",
            "pos",
            "textColor",
        },
        "image": {
            "autoFade",
            "clipRect",
            "color",
            "colorEnd",
            "default",
            "flipX",
            "flipY",
            "gradientType",
            "h",
            "horizontalAlignment",
            "linearSmooth",
            "maxSize",
            "minSize",
            "offset",
            "offsetX",
            "offsetY",
            "onclick",
            "opacity",
            "origin",
            "padding",
            "path",
            "pos",
            "reflexion",
            "reflexionOnFrame",
            "rotation",
            "rotationOrigin",
            "roundCorners",
            "saturation",
            "scale",
            "scaleOrigin",
            "shared",
            "size",
            "tile",
            "verticalAlignment",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "imagegrid": {
            "animateSelection",
            "autoLayout",
            "autoLayoutSelectedZoom",
            "cellProportion",
            "centerSelection",
            "folderImage",
            "gameImage",
            "h",
            "imageSource",
            "logoBackgroundImage",
            "margin",
            "opacity",
            "padding",
            "pos",
            "scale",
            "scaleOrigin",
            "scrollDirection",
            "scrollLoop",
            "scrollSound",
            "scrollbarAlignment",
            "scrollbarColor",
            "scrollbarCorner",
            "scrollbarSize",
            "showVideoAtDelay",
            "size",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "menuBackground": {
            "centerColor",
            "color",
            "cornerSize",
            "fadePath",
            "path",
            "scrollbarAlignment",
            "scrollbarColor",
            "scrollbarCorner",
            "scrollbarSize",
        },
        "menuButton": {
            "cornerSize",
            "filledPath",
            "path",
        },
        "menuGroup": {
            "alignment",
            "backgroundColor",
            "color",
            "fontPath",
            "fontSize",
            "lineSpacing",
            "separatorColor",
            "visible",
        },
        "menuIcons": {
            "iconAdvanced",
            "iconControllers",
            "iconGames",
            "iconNetwork",
            "iconQuit",
            "iconScraper",
            "iconSound",
            "iconSystem",
            "iconUI",
            "iconUpdates",
        },
        "menuSlider": {
            "path",
        },
        "menuSwitch": {
            "pathOff",
            "pathOn",
        },
        "menuText": {
            "color",
            "fontPath",
            "fontSize",
            "selectedColor",
            "selectorColor",
            "selectorColorEnd",
            "selectorGradientType",
            "separatorColor",
        },
        "menuTextEdit": {
            "active",
            "inactive",
        },
        "menuTextSmall": {
            "color",
            "fontPath",
            "fontSize",
        },
        "networkIcon": {
            "networkIcon",
            "planemodeIcon",
        },
        "ninepatch": {
            "animateColor",
            "animateColorTime",
            "centerColor",
            "color",
            "cornerSize",
            "edgeColor",
            "h",
            "opacity",
            "padding",
            "path",
            "pos",
            "rotation",
            "rotationOrigin",
            "scale",
            "scaleOrigin",
            "size",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "rating": {
            "clipRect",
            "color",
            "filledPath",
            "h",
            "horizontalAlignment",
            "offset",
            "offsetX",
            "offsetY",
            "opacity",
            "origin",
            "padding",
            "pos",
            "rotation",
            "rotationOrigin",
            "scale",
            "scaleOrigin",
            "size",
            "unfilledColor",
            "unfilledPath",
            "value",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "rectangle": {
            "borderColor",
            "borderSize",
            "clipChildren",
            "color",
            "h",
            "opacity",
            "padding",
            "pos",
            "roundCorners",
            "size",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "screenshader": {
            "clipRect",
            "path",
            "pos",
            "size",
            "visible",
            "zIndex",
        },
        "shader": set(),
        "sound": {
            "path",
        },
        "splash": {
            "backgroundColor",
        },
        "stackpanel": {
            "clipChildren",
            "h",
            "opacity",
            "orientation",
            "pos",
            "reverse",
            "separator",
            "size",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "text": {
            "alignment",
            "autoScroll",
            "autoScrollDelay",
            "autoScrollSpeed",
            "backgroundColor",
            "clipRect",
            "color",
            "emptyTextDefaults",
            "extraTextColor",
            "fontPath",
            "fontSize",
            "forceUppercase",
            "glowColor",
            "glowOffset",
            "glowSize",
            "h",
            "lineSpacing",
            "multiLine",
            "offset",
            "offsetX",
            "offsetY",
            "onclick",
            "opacity",
            "origin",
            "padding",
            "pos",
            "reflexion",
            "reflexionOnFrame",
            "rotation",
            "rotationOrigin",
            "scale",
            "scaleOrigin",
            "singleLineScroll",
            "size",
            "text",
            "value",
            "verticalAlignment",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "textlist": {
            "alignment",
            "extraTextColor",
            "extraTextSelectedColor",
            "fontPath",
            "fontSize",
            "forceUppercase",
            "glowColor",
            "glowOffset",
            "glowSize",
            "h",
            "horizontalMargin",
            "lineSpacing",
            "lines",
            "opacity",
            "origin",
            "pos",
            "primaryColor",
            "rotation",
            "rotationOrigin",
            "scale",
            "scaleOrigin",
            "scrollSound",
            "scrollbarAlignment",
            "scrollbarColor",
            "scrollbarCorner",
            "scrollbarSize",
            "secondaryColor",
            "selectedColor",
            "selectorColor",
            "selectorColorEnd",
            "selectorGradientType",
            "selectorHeight",
            "selectorImagePath",
            "selectorImageTile",
            "selectorOffsetY",
            "size",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "video": {
            "audio",
            "clipRect",
            "color",
            "default",
            "defaultSnapshot",
            "delay",
            "effect",
            "enabled",
            "h",
            "linearSmooth",
            "loops",
            "maxSize",
            "minSize",
            "offset",
            "offsetX",
            "offsetY",
            "onclick",
            "opacity",
            "origin",
            "padding",
            "path",
            "pos",
            "rotation",
            "rotationOrigin",
            "roundCorners",
            "saturation",
            "scale",
            "scaleOrigin",
            "showSnapshotDelay",
            "showSnapshotNoVideo",
            "size",
            "snapshotSource",
            "visible",
            "w",
            "x",
            "y",
            "zIndex",
        },
        "webimage": {
            "path",
        },
    },
    "aliases": {
        # Element aliases from theme_schema.json
        "itemTemplate": "control",
        # Metadata label aliases (used in detailed view)
        "md_lblRating": "text",
        "md_lblReleaseDate": "text",
        "md_lblDeveloper": "text",
        "md_lblPublisher": "text",
        "md_lblGenre": "text",
        "md_lblPlayers": "text",
        "md_lblLastPlayed": "text",
        "md_lblPlayCount": "text",
        # Metadata element aliases
        "md_image": "image",
        "md_video": "video",
        "md_rating": "rating",
        "md_releasedate": "datetime",
        # Common element aliases
        "headerImage": "image",
        "logo": "image",
        "background": "image",
        "gridtile": "image",
    },
    "base_classes": {
        # Base class inheritance from theme_schema.json
        "batteryIcon": "image",
        "batteryText": "text",
        "clock": "text",
        "networkIcon": "image",
        "webimage": "image",
        # Menu component base classes
        "menuComponent": "image",
        "menuText": "text",
        "menuTextEdit": "text",
        "menuSwitch": "image",
        "menuButton": "image",
        "menuSlider": "image",
        "menuTextSmall": "text",
    },
}


def load_schema(schema_path=None):
    """Return theme schema. Uses embedded schema by default."""
    if schema_path is not None:
        if not os.path.exists(schema_path):
            print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
            sys.exit(1)
        try:
            with open(schema_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            elements = {
                element["name"]: {
                    prop["name"] for prop in element.get("properties", [])
                }
                for element in data.get("elements", [])
            }
            aliases = {
                alias["alias"]: alias["target"]
                for alias in data.get("element_aliases", [])
            }
            base_classes = {
                item["type"]: item["base"] for item in data.get("base_classes", [])
            }
            return {
                "elements": elements,
                "aliases": aliases,
                "base_classes": base_classes,
            }
        except json.JSONDecodeError as exc:
            print(
                f"Error: Invalid JSON in schema file {schema_path}: {exc}",
                file=sys.stderr,
            )
            sys.exit(1)
        except IOError as exc:
            print(
                f"Error: Cannot read schema file {schema_path}: {exc}", file=sys.stderr
            )
            sys.exit(1)

    return EMBEDDED_SCHEMA


def resolve_element_type(tag, schema):
    return schema["aliases"].get(tag, tag)


def collect_properties(element_type, schema):
    properties = set()
    current = resolve_element_type(element_type, schema)
    visited = set()
    while current and current not in visited:
        visited.add(current)
        properties.update(schema["elements"].get(current, set()))
        current = schema["base_classes"].get(current)
    return properties


def is_element_tag(tag, schema):
    resolved = resolve_element_type(tag, schema)
    return resolved in schema["elements"]


def extract_filters(attrs):
    filters = {}
    for key in FILTER_KEYS:
        if key in attrs:
            filters[key] = attrs[key]
    return filters


def normalize_bool(value):
    """Normalize boolean-like string values to Python bool.

    Returns bool for 'true'/'false', otherwise returns the original string.
    NOTE: Do NOT convert '1'/'0' as those can be valid numeric values (e.g., zIndex).
    """
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def rewrite_include_path(path, rewrite):
    if not rewrite:
        return path
    if path.endswith(".xml"):
        return path[:-4] + ".json"
    return path


def convert_storyboard(node):
    obj: dict = {"type": "storyboard"}
    for key in ("event", "repeat", "repeatAt", "repeatat"):
        if key in node.attrib:
            if key == "repeatat":
                obj["repeatAt"] = str(node.attrib[key])
            else:
                obj[key] = str(node.attrib[key])

    animations = []
    sounds = []
    for child in node:
        if child.tag == "animation":
            anim: dict = {}
            for attr, value in child.attrib.items():
                if attr in ("mode", "easingMode"):
                    anim["mode"] = str(value)
                elif attr in ("autoreverse", "autoReverse"):
                    anim["autoReverse"] = normalize_bool(value)
                elif attr in ("enabled",):
                    anim["enabled"] = normalize_bool(value)
                elif attr in ("to", "from", "duration", "begin", "repeat"):
                    anim[attr] = str(value)
                else:
                    anim[attr] = str(value)
            animations.append(anim)
        elif child.tag == "sound":
            snd: dict = {}
            for attr, value in child.attrib.items():
                if attr in ("autoreverse", "autoReverse"):
                    snd["autoReverse"] = normalize_bool(value)
                elif attr == "at":
                    snd["begin"] = str(value)
                else:
                    snd[attr] = str(value)
            sounds.append(snd)

    if animations:
        obj["animations"] = animations
    if sounds:
        obj["sounds"] = sounds

    return obj


def convert_element(node, schema):
    obj: dict = {"type": node.tag}

    if "name" in node.attrib:
        obj["name"] = str(node.attrib["name"])
    if "extra" in node.attrib:
        obj["extra"] = normalize_bool(node.attrib["extra"])
    if "importProperties" in node.attrib:
        obj["importProperties"] = str(node.attrib["importProperties"])

    filters = extract_filters(node.attrib)
    if filters:
        obj["filters"] = filters

    props = []
    children = []

    reserved = {"name", "extra", "importProperties"} | FILTER_KEYS

    for key, value in node.attrib.items():
        if key in reserved:
            continue
        props.append({"name": key, "value": normalize_bool(value)})

    property_set = collect_properties(node.tag, schema)
    is_shader = node.tag in {"shader", "screenshader", "menuShader", "fadeShader"}

    for child in node:
        if child.tag == "storyboard":
            children.append(convert_storyboard(child))
            continue
        if child.tag == "itemTemplate":
            child_obj = convert_element(child, schema)
            children.append(child_obj)
            continue

        has_children = any(grand.tag for grand in child)
        child_filters = extract_filters(child.attrib)

        prop_name = child.tag
        if prop_name == "animate" and node.tag == "imagegrid":
            prop_name = "animateSelection"

        known_element = is_element_tag(child.tag, schema)
        if not has_children and (
            prop_name in property_set
            or is_shader
            or node.tag == "menuIcons"
            or not known_element
        ):
            value = (child.text or "").strip()
            value = normalize_bool(value)
            entry: dict = {"name": prop_name, "value": value}
            if child_filters:
                entry["filters"] = child_filters
            props.append(entry)
            continue

        child_obj = convert_element(child, schema)
        if child_filters:
            child_obj["filters"] = child_filters
        children.append(child_obj)

    if props:
        obj["props"] = props
    if children:
        obj["children"] = children

    return obj


def convert_include(node, rewrite):
    """Convert an XML include element to JSON format."""
    obj: dict = {"type": "include"}
    path = (node.text or "").strip()
    if path:
        obj["path"] = rewrite_include_path(path, rewrite)

    for key in ("subset", "name", "displayName", "subSetDisplayName", "appliesTo"):
        if key in node.attrib:
            obj[key] = str(node.attrib[key])

    filters = extract_filters(node.attrib)
    if filters:
        obj["filters"] = filters

    return obj


def convert_view(node, schema, node_type):
    obj: dict = {"type": node_type}
    if "name" in node.attrib:
        obj["name"] = str(node.attrib["name"])
    if "displayName" in node.attrib:
        obj["displayName"] = str(node.attrib["displayName"])
    if "inherits" in node.attrib:
        obj["inherits"] = str(node.attrib["inherits"])
    if "extraTransition" in node.attrib:
        obj["extraTransition"] = str(node.attrib["extraTransition"])
    if "extraTransitionSpeed" in node.attrib:
        obj["extraTransitionSpeed"] = str(node.attrib["extraTransitionSpeed"])
    if "extraTransitionDirection" in node.attrib:
        obj["extraTransitionDirection"] = str(node.attrib["extraTransitionDirection"])

    filters = extract_filters(node.attrib)
    if filters:
        obj["filters"] = filters

    elements = []
    for child in node:
        elements.append(convert_element(child, schema))

    if elements:
        obj["elements"] = elements

    return obj


def convert_subset(node, schema, rewrite):
    obj: dict = {"type": "subset"}
    if "name" in node.attrib:
        obj["name"] = str(node.attrib["name"])
    if "displayName" in node.attrib:
        obj["displayName"] = str(node.attrib["displayName"])
    if "subSetDisplayName" in node.attrib:
        obj["subSetDisplayName"] = str(node.attrib["subSetDisplayName"])
    if "appliesTo" in node.attrib:
        obj["appliesTo"] = str(node.attrib["appliesTo"])

    filters = extract_filters(node.attrib)
    if filters:
        obj["filters"] = filters

    includes = []
    for child in node:
        if child.tag == "include":
            includes.append(convert_include(child, rewrite))

    if includes:
        obj["nodes"] = includes

    return obj


def convert_feature(node, schema, rewrite):
    obj: dict = {"type": "feature"}
    if "supported" in node.attrib:
        obj["supported"] = str(node.attrib["supported"])

    filters = extract_filters(node.attrib)
    if filters:
        obj["filters"] = filters

    nodes = []
    for child in node:
        if child.tag == "view":
            nodes.append(convert_view(child, schema, "view"))
        elif child.tag == "customView":
            nodes.append(convert_view(child, schema, "customView"))
        elif child.tag == "include":
            nodes.append(convert_include(child, rewrite))
        elif child.tag == "subset":
            nodes.append(convert_subset(child, schema, rewrite))

    if nodes:
        obj["nodes"] = nodes

    return obj


def convert_variables(root):
    vars_entries = []
    for variables in root.findall("variables"):
        base_filters = extract_filters(variables.attrib)
        for child in variables:
            if child.tag is None:
                continue
            value = (child.text or "").strip()
            entry = {"key": child.tag, "value": value}
            child_filters = extract_filters(child.attrib)
            merged = {}
            merged.update(base_filters)
            merged.update(child_filters)
            if merged:
                entry["filters"] = merged
            vars_entries.append(entry)
    return vars_entries


def convert_theme(xml_path, schema, rewrite):
    """Convert a theme XML file to JSON format."""
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        print(f"Error: XML parse error in {xml_path}: {exc}", file=sys.stderr)
        return None
    except IOError as exc:
        print(f"Error: Cannot read file {xml_path}: {exc}", file=sys.stderr)
        return None

    root = tree.getroot()
    if root.tag != "theme":
        print(
            f"Warning: {xml_path} does not have a <theme> root element, skipping",
            file=sys.stderr,
        )
        return None

    theme: dict = {}
    if "defaultView" in root.attrib:
        theme["defaultView"] = str(root.attrib["defaultView"])
    if "defaultTransition" in root.attrib:
        theme["defaultTransition"] = str(root.attrib["defaultTransition"])

    format_version: int | float | None = None
    nodes = []

    for child in root:
        if child.tag == "formatVersion":
            try:
                format_version = float((child.text or "").strip())
            except ValueError:
                format_version = None
            continue

        if child.tag == "variables":
            # Variables are handled separately by convert_variables()
            continue

        if child.tag == "include":
            nodes.append(convert_include(child, rewrite))
        elif child.tag == "view":
            nodes.append(convert_view(child, schema, "view"))
        elif child.tag == "customView":
            nodes.append(convert_view(child, schema, "customView"))
        elif child.tag == "subset":
            nodes.append(convert_subset(child, schema, rewrite))
        elif child.tag == "feature":
            nodes.append(convert_feature(child, schema, rewrite))

    if format_version is None:
        format_version = 7
    theme["formatVersion"] = format_version

    # Process variables that are direct children of <theme>
    vars_entries = convert_variables(root)
    if vars_entries:
        theme["variables"] = vars_entries

    if nodes:
        theme["nodes"] = nodes

    return theme


def collect_xml_files(target):
    if os.path.isdir(target):
        matches = []
        for root, _, files in os.walk(target):
            for name in files:
                if name.lower().endswith(".xml"):
                    matches.append(os.path.join(root, name))
        return matches
    return [target]


def main():
    """Main entry point for the theme XML to JSON converter."""
    parser = argparse.ArgumentParser(
        description="Convert Emulation Station theme XML files to JSON format."
    )
    parser.add_argument("input", help="Theme XML file or directory to convert.")
    parser.add_argument(
        "--output", "-o", help="Output file path (only used for single input file)."
    )
    parser.add_argument(
        "--schema",
        "-s",
        default=None,
        help="Path to external schema JSON (default: use embedded schema).",
    )
    parser.add_argument(
        "--no-rewrite-includes",
        action="store_true",
        help="Do not rewrite .xml include paths to .json.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output."
    )
    args = parser.parse_args()

    # Load schema (embedded by default, or external if --schema provided)
    schema_path = args.schema
    schema = load_schema(schema_path)
    rewrite_includes = not args.no_rewrite_includes

    # Validate input path
    if not os.path.exists(args.input):
        print(f"Error: Input path does not exist: {args.input}", file=sys.stderr)
        return 1

    xml_files = collect_xml_files(args.input)

    if not xml_files:
        print("No XML files found to convert.", file=sys.stderr)
        return 1

    # Determine output paths
    if len(xml_files) == 1 and args.output:
        output_paths = [args.output]
    else:
        output_paths = []
        for xml_path in xml_files:
            if os.path.basename(xml_path).lower() == "theme.xml":
                output_paths.append(
                    os.path.join(os.path.dirname(xml_path), "theme.json")
                )
            else:
                base, _ = os.path.splitext(xml_path)
                output_paths.append(base + ".json")

    if args.verbose:
        print(f"Found {len(xml_files)} XML file(s) to convert:")
        for xml_path in xml_files:
            print(f"  - {xml_path}")

    # Convert files
    converted = 0
    failed = 0

    for xml_path, output_path in zip(xml_files, output_paths):
        if args.verbose:
            print(f"Converting: {xml_path} -> {output_path}")

        try:
            theme = convert_theme(xml_path, schema, rewrite_includes)
        except Exception as exc:
            print(
                f"Error converting {xml_path}: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            failed += 1
            continue

        if theme is None:
            failed += 1
            continue

        try:
            out_dir = os.path.dirname(output_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as handle:
                json.dump(theme, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            converted += 1
            if args.verbose:
                print(f"  ✓ Successfully converted to {output_path}")
        except IOError as exc:
            print(f"Error writing output file {output_path}: {exc}", file=sys.stderr)
            failed += 1

    # Summary
    print(
        f"Conversion complete: {converted} file(s) converted, {failed} file(s) failed."
    )

    if converted == 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
