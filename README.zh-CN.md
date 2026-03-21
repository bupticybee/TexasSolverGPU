# TexasSolver GPU

[![release](https://img.shields.io/github/v/release/bupticybee/TexasSolverGPU?label=release)](https://github.com/bupticybee/TexasSolverGPU/releases)
[![license](https://img.shields.io/badge/license-EULA-orange)](./EULA.md)
[![discord](https://img.shields.io/badge/discord-join%20chat-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/RtyD4vRy2e)

[English](./README.md) | README 简体中文 | [日本語](./README.ja-JP.md) | [한국어](./README.ko-KR.md) | [Español](./README.es-ES.md) | [Русский](./README.ru-RU.md)

<p align="center">
  <img src="./assets/images/logo-solid.png" alt="TexasSolver GPU logo" width="220" />
</p>

TexasSolver GPU 是一个面向 Windows 的德州扑克 GPU 求解器发布仓库，目标是相比以往偏 CPU 的求解流程带来明显更快的本地求解速度。

## 项目介绍

TexasSolver GPU 面向搭载 NVIDIA GPU 的 Windows 本地研究场景。相比以往 TexasSolver 风格、偏 CPU 的求解流程，这个 GPU 桌面版本更强调更快的本地求解和更高效的迭代体验。桌面应用将原生求解运行时和 GUI 打包在一起，可以用于：

- 构建博弈树并快速开始求解
- 对多个牌面进行批量求解
- 进行节点锁定分析
- 查看策略结果并进行对练

这个仓库只是公开分发仓库，不包含私有的 `gpu_solver` 主源码。

## 为什么使用 GPU

- GPU 加速能显著缩短很多本地求解任务的耗时。
- 更快的迭代速度让建树、批量求解和节点锁定实验都更实用。
- 对于使用 NVIDIA 显卡的 Windows 用户，这个项目可以看作是 TexasSolver 路线上的高性能演进版本。

## 界面截图

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

## 下载

Windows 发布包请从 [GitHub Releases](https://github.com/bupticybee/TexasSolverGPU/releases) 下载。

当前公开版本：

- 版本：`v0.2.0`
- 平台：`windows-x64`

## 运行文件

每个 Windows 发布包中包含：

- `TexasSolverGpu.exe`
- `TexasSolverGpu_131.exe`
- `TexasSolverGpu_legacy_126.exe`
- `WebView2Loader.dll`
- `quick_start/`
- `ranges/`

建议启动顺序：

1. `TexasSolverGpu.exe`
2. `TexasSolverGpu_131.exe`
3. `TexasSolverGpu_legacy_126.exe`

## 环境要求

- Windows 10 / Windows 11 64 位
- NVIDIA GPU
- 已安装 WebView2 Runtime

## Viewer

策略查看器以 Python 源码形式提供，位于 [viewer/viewer.py](./viewer/viewer.py)。

```powershell
python viewer/viewer.py --file your_result.json
```

详情见 [viewer/README.md](./viewer/README.md)。

## 社区

- Discord: https://discord.com/invite/RtyD4vRy2e

## 说明

- 公开仓库不代表私有 `gpu_solver` 主源码开源。
- 这个仓库只用于二进制分发、元数据、截图和辅助工具。
- 内部求解实现、构建系统和私有工具不会在这里公开。
- 分发说明见 [EULA.md](./EULA.md)。
