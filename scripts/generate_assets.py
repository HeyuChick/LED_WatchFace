from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "assets_led"

EXPECTED_ASSETS = [
    "bg_off_450.png",
    "mask_450.png",
    *[f"num_{digit}.png" for digit in range(10)],
    "num_colon.png",
    "num_dash.png",
    "num_dot.png",
    "num_percent.png",
    "num_space.png",
    *[f"label_{chr(code)}.png" for code in range(ord("A"), ord("Z") + 1)],
]


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Asset output directory ready: {OUTPUT_DIR}")
    print(f"Expected asset count: {len(EXPECTED_ASSETS)}")


if __name__ == "__main__":
    main()
