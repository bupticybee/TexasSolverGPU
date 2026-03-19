# TexasSolver GPU

[![release](https://img.shields.io/github/v/release/bupticybee/TexasSolverGPU?label=release)](https://github.com/bupticybee/TexasSolverGPU/releases)
[![license](https://img.shields.io/badge/license-EULA-orange)](./EULA.md)
[![discord](https://img.shields.io/badge/discord-join%20chat-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/RtyD4vRy2e)

README English | [简体中文](./README.zh-CN.md) | [日本語](./README.ja-JP.md) | [한국어](./README.ko-KR.md) | [Español](./README.es-ES.md)

<p align="center">
  <img src="./assets/images/logo-solid.png" alt="TexasSolver GPU logo" width="220" />
</p>

TexasSolver GPU is a Windows desktop release repository for a GPU-accelerated Texas Hold'em solver.

## Introduction

TexasSolver GPU is built for practical local study on Windows with an NVIDIA GPU. The desktop app bundles native solver runtimes together with a GUI so you can:

- build trees and run quick-start studies
- batch solve multiple boards
- inspect node-lock scenarios
- explore and practice against strategy outputs

This repository is the public distribution repository only. It does not contain the private `gpu_solver` source tree.

## Screenshots

### Quick Start

![TexasSolver GPU quick start page](./assets/images/quick-start-page.png)

### Tree Construction

![TexasSolver GPU tree construction page](./assets/images/tree-construction-page.png)

### Batch Solving

![TexasSolver GPU batch solving page](./assets/images/batch-solving-page.png)

### Node Lock

![TexasSolver GPU node lock page](./assets/images/node-lock-page.png)

### Play Against Strategy

![TexasSolver GPU play against strategy page](./assets/images/play-against-strategy.png)

## Download

Download Windows builds from [GitHub Releases](https://github.com/bupticybee/TexasSolverGPU/releases).

Current public release:

- Version: `v0.1.0`
- Platform: `windows-x64`

## Runtime Files

Each Windows bundle includes:

- `TexasSolverGpu.exe`
- `TexasSolverGpu_131.exe`
- `TexasSolverGpu_legacy_126.exe`
- `WebView2Loader.dll`
- `quick_start/`
- `ranges/`

Recommended startup order:

1. `TexasSolverGpu.exe`
2. `TexasSolverGpu_131.exe`
3. `TexasSolverGpu_legacy_126.exe`

## Requirements

- Windows 10 or Windows 11, 64-bit
- NVIDIA GPU
- WebView2 Runtime installed

## Viewer

The strategy viewer is distributed as Python source in [viewer/viewer.py](./viewer/viewer.py).

```powershell
python viewer/viewer.py --file your_result.json
```

See [viewer/README.md](./viewer/README.md) for details.

## Community

- Discord: https://discord.com/invite/RtyD4vRy2e

## Notice

- Public repo does not mean the private `gpu_solver` source code is open source.
- This repo is for binary distribution, metadata, screenshots, and helper tools only.
- Internal solver implementation, build systems, and private tooling are not published here.
- See [EULA.md](./EULA.md) for the distribution notice.
