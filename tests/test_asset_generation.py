from pathlib import Path
import runpy


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_scaffold_files_exist() -> None:
    assert (PROJECT_ROOT / "docs" / "watchface_asset_spec.md").is_file()
    assert (PROJECT_ROOT / "scripts" / "generate_assets.py").is_file()


def test_expected_asset_manifest_matches_spec() -> None:
    namespace = runpy.run_path(str(PROJECT_ROOT / "scripts" / "generate_assets.py"))

    assert len(namespace["EXPECTED_ASSETS"]) == 43
    assert "bg_off_450.png" in namespace["EXPECTED_ASSETS"]
    assert "mask_450.png" in namespace["EXPECTED_ASSETS"]
    assert "num_space.png" in namespace["EXPECTED_ASSETS"]
    assert "label_Z.png" in namespace["EXPECTED_ASSETS"]
