# LED WatchFace

用于 Samsung Watch Face Studio / Wear OS 的 LED 点阵表盘素材生成项目。

项目通过 Python 脚本批量生成透明 PNG 和 SVG 素材，供 WFS Bitmap Font、背景图和遮罩图使用。详细规格见 [docs/watchface_asset_spec.md](docs/watchface_asset_spec.md)。

## 环境要求

- Python 3.10+
- uv

本项目使用 uv 管理依赖，依赖定义在 [pyproject.toml](pyproject.toml)，锁文件为 [uv.lock](uv.lock)。

## 安装依赖

```bash
uv sync
```

## 生成素材

默认生成 PNG：

```bash
uv run python scripts/generate_assets.py
```

显式生成 PNG：

```bash
uv run python scripts/generate_assets.py --format png
```

生成 SVG：

```bash
uv run python scripts/generate_assets.py --format svg
```

生成 glow PNG 和 glow SVG：

```bash
uv run python scripts/generate_assets.py --format glow
```

同时生成 PNG、SVG、glow PNG 和 glow SVG：

```bash
uv run python scripts/generate_assets.py --format all
```

指定输出目录：

```bash
uv run python scripts/generate_assets.py --format all --output-dir assets_led
```

## 输出目录

生成文件按文件类型分组：

```text
assets_led/
├── png/
│   ├── bg_off_450.png
│   ├── mask_450.png
│   ├── num_0.png ~ num_9.png
│   ├── num_colon.png
│   ├── num_dash.png
│   ├── num_dot.png
│   ├── num_percent.png
│   ├── num_space.png
│   └── label_A.png ~ label_Z.png
├── png_glow/
│   ├── num_0_glow.png ~ num_9_glow.png
│   ├── num_colon_glow.png
│   ├── num_dash_glow.png
│   ├── num_dot_glow.png
│   ├── num_percent_glow.png
│   ├── num_space_glow.png
│   └── label_A_glow.png ~ label_Z_glow.png
├── svg/
│   ├── bg_off_450.svg
│   ├── mask_450.svg
│   ├── num_0.svg ~ num_9.svg
│   ├── num_colon.svg
│   ├── num_dash.svg
│   ├── num_dot.svg
│   ├── num_percent.svg
│   ├── num_space.svg
│   └── label_A.svg ~ label_Z.svg
└── svg_glow/
    ├── num_0_glow.svg ~ num_9_glow.svg
    ├── num_colon_glow.svg
    ├── num_dash_glow.svg
    ├── num_dot_glow.svg
    ├── num_percent_glow.svg
    ├── num_space_glow.svg
    └── label_A_glow.svg ~ label_Z_glow.svg
```

PNG 是 WFS Bitmap Font 的主交付格式；`png_glow/` 是叠加发光层的主交付格式。SVG 和 `svg_glow/` 作为预览、编辑和兼容性尝试的附加格式。

## 运行测试

```bash
uv run pytest
```

测试会验证素材清单、尺寸、PNG 透明通道、SVG XML 结构、glow 素材尺寸和 SVG blur filter，以及各格式是否输出到对应子目录。

## Git 说明

[assets_led/](assets_led/) 中的 PNG/SVG 素材会随源码一起提交，便于直接在 WFS 中使用。
