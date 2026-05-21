import argparse
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "assets_led"
SVG_NS = "http://www.w3.org/2000/svg"

CONFIG = {
    "canvas_size": 450,
    "grid": 45,
    "cell": 10,
    "center": 225,
    "bg_color_rgb": (0, 0, 0, 255),
    "bg_color_hex": "#000000",
    "off_dot_edge_color_rgb": (48, 48, 48, 255),
    "off_dot_edge_color_hex": "#303030",
    "off_dot_color_rgb": (26, 26, 26, 255),
    "off_dot_color_hex": "#1A1A1A",
    "on_dot_color_rgb": (255, 255, 255, 255),
    "on_dot_color_hex": "#FFFFFF",
    "black_rgb": (0, 0, 0, 255),
    "black_hex": "#000000",
    "transparent_rgb": (0, 0, 0, 0),
    "dot_radius_off_edge": 3.5,
    "dot_radius_off": 2.6,
    "dot_radius_on": 3.5,
    "num_cell": 10,
    "num_pad_x": 5,
    "num_pad_y": 7,
    "label_cell": 10,
    "label_pad_x": 5,
    "label_pad_y": 5,
    "aa_scale": 4,
}

DIGIT_GLYPHS = {
    "0": [[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]],
    "1": [[0, 0, 1, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 1, 1, 1, 0]],
    "2": [[1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1]],
    "3": [[1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 1, 1, 1, 1]],
    "4": [[1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1]],
    "5": [[1, 1, 1, 1, 1], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 1, 1, 1, 1]],
    "6": [[1, 1, 1, 1, 1], [1, 0, 0, 0, 0], [1, 0, 0, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]],
    "7": [[1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [0, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]],
    "8": [[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]],
    "9": [[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1], [0, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 1, 1, 1, 1]],
}

SYMBOL_GLYPHS = {
    "colon": [[0], [1], [0], [0], [0], [1], [0]],
    "dash": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [1, 1, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
    "dot": [[0], [0], [0], [0], [0], [0], [1]],
    "percent": [
        [1, 1, 0, 0, 1],
        [1, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 1],
        [1, 0, 0, 1, 1],
    ],
}

LABEL_GLYPHS = {
    "A": [[0, 1, 1, 0], [1, 0, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1]],
    "B": [[1, 1, 1, 0], [1, 0, 0, 1], [1, 1, 1, 0], [1, 0, 0, 1], [1, 1, 1, 0]],
    "C": [[0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [0, 1, 1, 1]],
    "D": [[1, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 0]],
    "E": [[1, 1, 1, 1], [1, 0, 0, 0], [1, 1, 1, 0], [1, 0, 0, 0], [1, 1, 1, 1]],
    "F": [[1, 1, 1, 1], [1, 0, 0, 0], [1, 1, 1, 0], [1, 0, 0, 0], [1, 0, 0, 0]],
    "G": [[0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 1, 1], [1, 0, 0, 1], [0, 1, 1, 1]],
    "H": [[1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1]],
    "I": [[1, 1, 1, 1], [0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0], [1, 1, 1, 1]],
    "J": [[0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]],
    "K": [[1, 0, 0, 1], [1, 0, 1, 0], [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1]],
    "L": [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 1, 1]],
    "M": [[1, 0, 0, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1]],
    "N": [[1, 0, 0, 1], [1, 1, 0, 1], [1, 0, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1]],
    "O": [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]],
    "P": [[1, 1, 1, 0], [1, 0, 0, 1], [1, 1, 1, 0], [1, 0, 0, 0], [1, 0, 0, 0]],
    "Q": [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1]],
    "R": [[1, 1, 1, 0], [1, 0, 0, 1], [1, 1, 1, 0], [1, 0, 1, 0], [1, 0, 0, 1]],
    "S": [[0, 1, 1, 1], [1, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 1], [1, 1, 1, 0]],
    "T": [[1, 1, 1, 1], [0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0]],
    "U": [[1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]],
    "V": [[1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0]],
    "W": [[1, 0, 0, 1], [1, 0, 0, 1], [1, 0, 1, 1], [1, 1, 1, 1], [1, 0, 0, 1]],
    "X": [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]],
    "Y": [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
    "Z": [[1, 1, 1, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [1, 1, 1, 1]],
}


@dataclass(frozen=True)
class AssetSpec:
    name: str
    kind: str
    width: int
    height: int
    matrix: list[list[int]] | None = None
    cell: int = 0
    pad_x: float = 0
    pad_y: float = 0
    radius: float = 0


def centered_pad(width: int, matrix: list[list[int]], cell: int) -> float:
    return (width - len(matrix[0]) * cell) / 2


def build_asset_specs() -> list[AssetSpec]:
    specs = [
        AssetSpec("bg_off_450", "background", 450, 450),
        AssetSpec("mask_450", "mask", 450, 450),
    ]

    specs.extend(
        AssetSpec(
            f"num_{digit}",
            "glyph",
            60,
            84,
            matrix,
            CONFIG["num_cell"],
            CONFIG["num_pad_x"],
            CONFIG["num_pad_y"],
            CONFIG["dot_radius_on"],
        )
        for digit, matrix in DIGIT_GLYPHS.items()
    )

    symbol_sizes = {
        "colon": (20, 84),
        "dash": (40, 84),
        "dot": (20, 84),
        "percent": (60, 84),
    }
    specs.extend(
        AssetSpec(
            f"num_{name}",
            "glyph",
            width,
            height,
            matrix,
            CONFIG["num_cell"],
            centered_pad(width, matrix, CONFIG["num_cell"]),
            CONFIG["num_pad_y"],
            CONFIG["dot_radius_on"],
        )
        for name, matrix in SYMBOL_GLYPHS.items()
        for width, height in [symbol_sizes[name]]
    )

    specs.append(AssetSpec("num_space", "space", 30, 84))

    specs.extend(
        AssetSpec(
            f"label_{letter}",
            "glyph",
            50,
            60,
            matrix,
            CONFIG["label_cell"],
            CONFIG["label_pad_x"],
            CONFIG["label_pad_y"],
            CONFIG["dot_radius_on"],
        )
        for letter, matrix in LABEL_GLYPHS.items()
    )
    return specs


ASSET_SPECS = build_asset_specs()
EXPECTED_PNG_ASSETS = [f"{spec.name}.png" for spec in ASSET_SPECS]
EXPECTED_SVG_ASSETS = [f"{spec.name}.svg" for spec in ASSET_SPECS]
EXPECTED_ASSETS = EXPECTED_PNG_ASSETS


def scale_color(color: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return color


def draw_dot(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, color: tuple[int, int, int, int], scale: int) -> None:
    draw.ellipse(
        [
            (cx - radius) * scale,
            (cy - radius) * scale,
            (cx + radius) * scale,
            (cy + radius) * scale,
        ],
        fill=scale_color(color),
    )


def downsample(image: Image.Image, width: int, height: int) -> Image.Image:
    return image.resize((width, height), Image.Resampling.LANCZOS)


def iter_watch_dots() -> list[tuple[int, int]]:
    dots = []
    cell = CONFIG["cell"]
    for row in range(CONFIG["grid"]):
        for col in range(CONFIG["grid"]):
            cx = col * cell + cell / 2
            cy = row * cell + cell / 2
            dots.append((int(cx), int(cy)))
    return dots


WATCH_DOTS = iter_watch_dots()


def draw_off_dot(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: int) -> None:
    draw_dot(draw, cx, cy, CONFIG["dot_radius_off_edge"], CONFIG["off_dot_edge_color_rgb"], scale)
    draw_dot(draw, cx, cy, CONFIG["dot_radius_off"], CONFIG["off_dot_color_rgb"], scale)


def render_png_background() -> Image.Image:
    width = height = CONFIG["canvas_size"]
    scale = CONFIG["aa_scale"]
    image = Image.new("RGBA", (width * scale, height * scale), CONFIG["bg_color_rgb"])
    draw = ImageDraw.Draw(image, "RGBA")
    for cx, cy in WATCH_DOTS:
        draw_off_dot(draw, cx, cy, scale)
    return downsample(image, width, height)


def render_png_mask() -> Image.Image:
    width = height = CONFIG["canvas_size"]
    scale = CONFIG["aa_scale"]
    image = Image.new("RGBA", (width * scale, height * scale), CONFIG["black_rgb"])
    draw = ImageDraw.Draw(image, "RGBA")
    for cx, cy in WATCH_DOTS:
        draw_dot(draw, cx, cy, CONFIG["dot_radius_off_edge"], CONFIG["transparent_rgb"], scale)
    return downsample(image, width, height)


def render_png_glyph(spec: AssetSpec) -> Image.Image:
    scale = CONFIG["aa_scale"]
    image = Image.new("RGBA", (spec.width * scale, spec.height * scale), CONFIG["transparent_rgb"])
    draw = ImageDraw.Draw(image, "RGBA")
    assert spec.matrix is not None
    for row, values in enumerate(spec.matrix):
        for col, value in enumerate(values):
            if value:
                cx = spec.pad_x + col * spec.cell + spec.cell / 2
                cy = spec.pad_y + row * spec.cell + spec.cell / 2
                draw_dot(draw, cx, cy, spec.radius, CONFIG["on_dot_color_rgb"], scale)
    return downsample(image, spec.width, spec.height)


def render_png_space(spec: AssetSpec) -> Image.Image:
    return Image.new("RGBA", (spec.width, spec.height), CONFIG["transparent_rgb"])


def render_png_asset(spec: AssetSpec) -> Image.Image:
    if spec.kind == "background":
        return render_png_background()
    if spec.kind == "mask":
        return render_png_mask()
    if spec.kind == "space":
        return render_png_space(spec)
    return render_png_glyph(spec)


def svg_root(width: int, height: int) -> ET.Element:
    return ET.Element(
        f"{{{SVG_NS}}}svg",
        {
            "width": str(width),
            "height": str(height),
            "viewBox": f"0 0 {width} {height}",
        },
    )


def append_circle(parent: ET.Element, cx: float, cy: float, radius: float, fill: str) -> None:
    ET.SubElement(
        parent,
        f"{{{SVG_NS}}}circle",
        {
            "cx": f"{cx:g}",
            "cy": f"{cy:g}",
            "r": f"{radius:g}",
            "fill": fill,
        },
    )


def append_rect(parent: ET.Element, width: int, height: int, fill: str, extra: dict[str, str] | None = None) -> ET.Element:
    attrs = {"width": str(width), "height": str(height), "fill": fill}
    if extra:
        attrs.update(extra)
    return ET.SubElement(parent, f"{{{SVG_NS}}}rect", attrs)


def append_off_dot(parent: ET.Element, cx: float, cy: float) -> None:
    append_circle(parent, cx, cy, CONFIG["dot_radius_off_edge"], CONFIG["off_dot_edge_color_hex"])
    append_circle(parent, cx, cy, CONFIG["dot_radius_off"], CONFIG["off_dot_color_hex"])


def render_svg_background(spec: AssetSpec) -> ET.ElementTree:
    root = svg_root(spec.width, spec.height)
    append_rect(root, spec.width, spec.height, CONFIG["bg_color_hex"])
    for cx, cy in WATCH_DOTS:
        append_off_dot(root, cx, cy)
    return ET.ElementTree(root)


def render_svg_mask(spec: AssetSpec) -> ET.ElementTree:
    root = svg_root(spec.width, spec.height)
    defs = ET.SubElement(root, f"{{{SVG_NS}}}defs")
    mask = ET.SubElement(defs, f"{{{SVG_NS}}}mask", {"id": "led-holes"})
    append_rect(mask, spec.width, spec.height, "white")
    for cx, cy in WATCH_DOTS:
        append_circle(mask, cx, cy, CONFIG["dot_radius_off_edge"], "black")
    append_rect(root, spec.width, spec.height, CONFIG["black_hex"], {"mask": "url(#led-holes)"})
    return ET.ElementTree(root)


def render_svg_glyph(spec: AssetSpec) -> ET.ElementTree:
    root = svg_root(spec.width, spec.height)
    assert spec.matrix is not None
    for row, values in enumerate(spec.matrix):
        for col, value in enumerate(values):
            if value:
                cx = spec.pad_x + col * spec.cell + spec.cell / 2
                cy = spec.pad_y + row * spec.cell + spec.cell / 2
                append_circle(root, cx, cy, spec.radius, CONFIG["on_dot_color_hex"])
    return ET.ElementTree(root)


def render_svg_space(spec: AssetSpec) -> ET.ElementTree:
    return ET.ElementTree(svg_root(spec.width, spec.height))


def render_svg_asset(spec: AssetSpec) -> ET.ElementTree:
    if spec.kind == "background":
        return render_svg_background(spec)
    if spec.kind == "mask":
        return render_svg_mask(spec)
    if spec.kind == "space":
        return render_svg_space(spec)
    return render_svg_glyph(spec)


def write_png_assets(output_dir: Path) -> list[Path]:
    png_dir = output_dir / "png"
    png_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for spec in ASSET_SPECS:
        path = png_dir / f"{spec.name}.png"
        render_png_asset(spec).save(path)
        paths.append(path)
    return paths


def write_svg_assets(output_dir: Path) -> list[Path]:
    svg_dir = output_dir / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)
    ET.register_namespace("", SVG_NS)
    paths = []
    for spec in ASSET_SPECS:
        path = svg_dir / f"{spec.name}.svg"
        render_svg_asset(spec).write(path, encoding="utf-8", xml_declaration=True)
        paths.append(path)
    return paths


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate LED dot-matrix watch face assets.")
    parser.add_argument("--format", choices=("png", "svg", "all"), default="png")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    generated = []
    if args.format in ("png", "all"):
        generated.extend(write_png_assets(args.output_dir))
    if args.format in ("svg", "all"):
        generated.extend(write_svg_assets(args.output_dir))
    print(f"Generated {len(generated)} asset files in {args.output_dir}")


if __name__ == "__main__":
    main()
