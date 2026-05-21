from pathlib import Path
import runpy
import xml.etree.ElementTree as ET

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_assets.py"
SVG_NS = "http://www.w3.org/2000/svg"
PERCENT_GLYPH = [
    [1, 1, 0, 0, 1],
    [1, 1, 0, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 1, 0, 1, 1],
    [1, 0, 0, 1, 1],
]


def load_generator() -> dict:
    return runpy.run_path(str(SCRIPT_PATH))


def test_project_scaffold_files_exist() -> None:
    assert (PROJECT_ROOT / "docs" / "watchface_asset_spec.md").is_file()
    assert SCRIPT_PATH.is_file()


def test_expected_asset_manifests_match_spec() -> None:
    namespace = load_generator()

    assert len(namespace["EXPECTED_PNG_ASSETS"]) == 43
    assert len(namespace["EXPECTED_SVG_ASSETS"]) == 43
    assert len(namespace["EXPECTED_GLOW_PNG_ASSETS"]) == 41
    assert len(namespace["EXPECTED_GLOW_SVG_ASSETS"]) == 41
    assert namespace["EXPECTED_ASSETS"] == namespace["EXPECTED_PNG_ASSETS"]

    png_stems = {Path(name).stem for name in namespace["EXPECTED_PNG_ASSETS"]}
    svg_stems = {Path(name).stem for name in namespace["EXPECTED_SVG_ASSETS"]}
    glow_png_stems = {Path(name).stem.removesuffix("_glow") for name in namespace["EXPECTED_GLOW_PNG_ASSETS"]}
    glow_svg_stems = {Path(name).stem.removesuffix("_glow") for name in namespace["EXPECTED_GLOW_SVG_ASSETS"]}
    assert png_stems == svg_stems
    assert glow_png_stems == glow_svg_stems
    assert glow_png_stems == png_stems - {"bg_off_450", "mask_450"}

    for name in ["bg_off_450", "mask_450", "num_0", "num_colon", "num_space", "label_Z"]:
        assert f"{name}.png" in namespace["EXPECTED_PNG_ASSETS"]
        assert f"{name}.svg" in namespace["EXPECTED_SVG_ASSETS"]

    for name in ["num_0", "num_colon", "num_percent", "num_space", "label_Z"]:
        assert f"{name}_glow.png" in namespace["EXPECTED_GLOW_PNG_ASSETS"]
        assert f"{name}_glow.svg" in namespace["EXPECTED_GLOW_SVG_ASSETS"]
    assert "bg_off_450_glow.png" not in namespace["EXPECTED_GLOW_PNG_ASSETS"]
    assert "mask_450_glow.svg" not in namespace["EXPECTED_GLOW_SVG_ASSETS"]


def test_asset_dimensions_match_spec() -> None:
    namespace = load_generator()
    dimensions = {spec.name: (spec.width, spec.height) for spec in namespace["ASSET_SPECS"]}

    assert dimensions["bg_off_450"] == (450, 450)
    assert dimensions["mask_450"] == (450, 450)
    assert dimensions["num_colon"] == (20, 84)
    assert dimensions["num_dash"] == (40, 84)
    assert dimensions["num_dot"] == (20, 84)
    assert dimensions["num_percent"] == (60, 84)
    assert dimensions["num_space"] == (30, 84)

    for digit in range(10):
        assert dimensions[f"num_{digit}"] == (60, 84)
    for code in range(ord("A"), ord("Z") + 1):
        assert dimensions[f"label_{chr(code)}"] == (50, 60)

    assert len(namespace["WATCH_DOTS"]) == 45 * 45


def test_percent_glyph_matches_selected_matrix() -> None:
    namespace = load_generator()

    assert namespace["SYMBOL_GLYPHS"]["percent"] == PERCENT_GLYPH


def test_label_specs_share_background_grid() -> None:
    namespace = load_generator()
    cell = namespace["CONFIG"]["cell"]
    label_specs = [spec for spec in namespace["ASSET_SPECS"] if spec.name.startswith("label_")]

    assert label_specs
    for spec in label_specs:
        assert spec.matrix is not None
        assert spec.cell == cell
        assert spec.pad_x == cell / 2
        assert spec.pad_y == cell / 2
        assert spec.width == len(spec.matrix[0]) * cell + 2 * spec.pad_x
        assert spec.height == len(spec.matrix) * cell + 2 * spec.pad_y


def test_generate_png_assets(tmp_path: Path) -> None:
    namespace = load_generator()
    namespace["main"](["--format", "png", "--output-dir", str(tmp_path)])

    png_files = sorted((tmp_path / "png").glob("*.png"))
    assert len(png_files) == 43
    assert not list(tmp_path.glob("*.png"))

    expected_sizes = {
        "bg_off_450.png": (450, 450),
        "mask_450.png": (450, 450),
        "num_8.png": (60, 84),
        "num_colon.png": (20, 84),
        "num_space.png": (30, 84),
        "label_A.png": (50, 60),
    }
    for filename, size in expected_sizes.items():
        with Image.open(tmp_path / "png" / filename) as image:
            assert image.size == size
            assert image.mode == "RGBA"

    with Image.open(tmp_path / "png" / "num_space.png") as image:
        assert image.getchannel("A").getextrema() == (0, 0)

    with Image.open(tmp_path / "png" / "num_8.png") as image:
        assert image.getchannel("A").getextrema()[1] > 0

    with Image.open(tmp_path / "png" / "label_A.png") as image:
        assert image.getchannel("A").getextrema()[1] > 0

    with Image.open(tmp_path / "png" / "bg_off_450.png") as image:
        assert image.getpixel((0, 0)) == (0, 0, 0, 255)
        assert image.getpixel((5, 5)) != (0, 0, 0, 255)

    with Image.open(tmp_path / "png" / "mask_450.png") as image:
        assert image.getpixel((5, 5))[3] == 0
        assert image.getpixel((225, 225))[3] == 0
        assert image.getpixel((0, 0))[3] == 255


def test_generate_svg_assets(tmp_path: Path) -> None:
    namespace = load_generator()
    namespace["main"](["--format", "svg", "--output-dir", str(tmp_path)])

    svg_files = sorted((tmp_path / "svg").glob("*.svg"))
    assert len(svg_files) == 43
    assert not list(tmp_path.glob("*.svg"))

    num_8_root = ET.parse(tmp_path / "svg" / "num_8.svg").getroot()
    assert num_8_root.tag == f"{{{SVG_NS}}}svg"
    assert num_8_root.attrib["width"] == "60"
    assert num_8_root.attrib["height"] == "84"
    assert num_8_root.attrib["viewBox"] == "0 0 60 84"
    num_8_circles = num_8_root.findall(f".//{{{SVG_NS}}}circle")
    assert len(num_8_circles) == sum(sum(row) for row in namespace["DIGIT_GLYPHS"]["8"])

    percent_root = ET.parse(tmp_path / "svg" / "num_percent.svg").getroot()
    assert percent_root.attrib["width"] == "60"
    assert percent_root.attrib["height"] == "84"
    assert percent_root.attrib["viewBox"] == "0 0 60 84"
    percent_circles = percent_root.findall(f".//{{{SVG_NS}}}circle")
    assert len(percent_circles) == sum(sum(row) for row in PERCENT_GLYPH)

    label_a_root = ET.parse(tmp_path / "svg" / "label_A.svg").getroot()
    assert label_a_root.attrib["width"] == "50"
    assert label_a_root.attrib["height"] == "60"
    assert label_a_root.attrib["viewBox"] == "0 0 50 60"
    for circle in label_a_root.findall(f".//{{{SVG_NS}}}circle"):
        assert float(circle.attrib["cx"]) % 10 == 0
        assert float(circle.attrib["cy"]) % 10 == 0

    space_root = ET.parse(tmp_path / "svg" / "num_space.svg").getroot()
    assert space_root.attrib["width"] == "30"
    assert space_root.attrib["height"] == "84"
    assert not space_root.findall(f".//{{{SVG_NS}}}circle")

    bg_root = ET.parse(tmp_path / "svg" / "bg_off_450.svg").getroot()
    assert bg_root.attrib["width"] == "450"
    assert bg_root.attrib["height"] == "450"
    assert bg_root.findall(f".//{{{SVG_NS}}}rect")
    assert len(bg_root.findall(f".//{{{SVG_NS}}}circle")) == len(namespace["WATCH_DOTS"]) * 2

    mask_root = ET.parse(tmp_path / "svg" / "mask_450.svg").getroot()
    assert mask_root.attrib["width"] == "450"
    assert mask_root.attrib["height"] == "450"
    assert mask_root.findall(f".//{{{SVG_NS}}}defs")
    assert mask_root.findall(f".//{{{SVG_NS}}}mask")
    assert len(mask_root.findall(f".//{{{SVG_NS}}}circle")) == len(namespace["WATCH_DOTS"])


def test_generate_glow_assets(tmp_path: Path) -> None:
    namespace = load_generator()
    namespace["main"](["--format", "glow", "--output-dir", str(tmp_path)])

    glow_png_files = sorted((tmp_path / "png_glow").glob("*.png"))
    glow_svg_files = sorted((tmp_path / "svg_glow").glob("*.svg"))
    assert len(glow_png_files) == 41
    assert len(glow_svg_files) == 41
    assert not list(tmp_path.glob("*.png"))
    assert not list(tmp_path.glob("*.svg"))
    assert not (tmp_path / "png").exists()
    assert not (tmp_path / "svg").exists()

    expected_png_sizes = {
        "num_8_glow.png": (60, 84),
        "num_colon_glow.png": (20, 84),
        "num_space_glow.png": (30, 84),
        "label_A_glow.png": (50, 60),
    }
    for filename, size in expected_png_sizes.items():
        with Image.open(tmp_path / "png_glow" / filename) as image:
            assert image.size == size
            assert image.mode == "RGBA"

    with Image.open(tmp_path / "png_glow" / "num_space_glow.png") as image:
        assert image.getchannel("A").getextrema() == (0, 0)

    with Image.open(tmp_path / "png_glow" / "num_8_glow.png") as image:
        assert image.getchannel("A").getextrema()[1] > 0

    with Image.open(tmp_path / "png_glow" / "label_A_glow.png") as image:
        assert image.getchannel("A").getextrema()[1] > 0

    num_8_root = ET.parse(tmp_path / "svg_glow" / "num_8_glow.svg").getroot()
    assert num_8_root.attrib["width"] == "60"
    assert num_8_root.attrib["height"] == "84"
    assert num_8_root.attrib["viewBox"] == "0 0 60 84"
    assert num_8_root.findall(f".//{{{SVG_NS}}}defs")
    assert num_8_root.findall(f".//{{{SVG_NS}}}filter")
    assert num_8_root.findall(f".//{{{SVG_NS}}}feGaussianBlur")
    assert len(num_8_root.findall(f".//{{{SVG_NS}}}circle")) == sum(sum(row) for row in namespace["DIGIT_GLYPHS"]["8"])

    space_root = ET.parse(tmp_path / "svg_glow" / "num_space_glow.svg").getroot()
    assert space_root.attrib["width"] == "30"
    assert space_root.attrib["height"] == "84"
    assert space_root.attrib["viewBox"] == "0 0 30 84"
    assert not space_root.findall(f".//{{{SVG_NS}}}circle")

    label_a_root = ET.parse(tmp_path / "svg_glow" / "label_A_glow.svg").getroot()
    assert label_a_root.attrib["width"] == "50"
    assert label_a_root.attrib["height"] == "60"
    assert label_a_root.attrib["viewBox"] == "0 0 50 60"


def test_generate_all_assets(tmp_path: Path) -> None:
    namespace = load_generator()
    namespace["main"](["--format", "all", "--output-dir", str(tmp_path)])

    assert len(list((tmp_path / "png").glob("*.png"))) == 43
    assert len(list((tmp_path / "svg").glob("*.svg"))) == 43
    assert len(list((tmp_path / "png_glow").glob("*.png"))) == 41
    assert len(list((tmp_path / "svg_glow").glob("*.svg"))) == 41
    assert not list(tmp_path.glob("*.png"))
    assert not list(tmp_path.glob("*.svg"))
