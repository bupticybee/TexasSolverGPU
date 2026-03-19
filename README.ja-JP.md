# TexasSolver GPU

[![release](https://img.shields.io/github/v/release/bupticybee/TexasSolverGPU?label=release)](https://github.com/bupticybee/TexasSolverGPU/releases)
[![license](https://img.shields.io/badge/license-EULA-orange)](./EULA.md)
[![discord](https://img.shields.io/badge/discord-join%20chat-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/RtyD4vRy2e)

[English](./README.md) | [简体中文](./README.zh-CN.md) | README 日本語 | [한국어](./README.ko-KR.md) | [Español](./README.es-ES.md) | [Русский](./README.ru-RU.md)

<p align="center">
  <img src="./assets/images/logo-solid.png" alt="TexasSolver GPU logo" width="220" />
</p>

TexasSolver GPU は、従来の CPU 中心の solver ワークフローより大幅に高速なローカル解析を目指した、GPU 活用型テキサスホールデムソルバーの Windows 向け公開リリースリポジトリです。

## 概要

TexasSolver GPU は、NVIDIA GPU を搭載した Windows 環境でのローカル解析向けに作られています。従来の TexasSolver 系 CPU ベースの解析フローと比べて、GPU デスクトップ runtime により、より高速な solve と反復作業を目指しています。デスクトップアプリにはネイティブ solver runtime と GUI が含まれており、次のような用途に使えます。

- ツリー構築とクイックスタート解析
- 複数ボードの一括計算
- ノードロック検証
- 戦略結果の閲覧と練習

このリポジトリは公開配布用であり、非公開の `gpu_solver` ソース本体は含みません。

## GPU を使う理由

- GPU アクセラレーションにより、多くのローカル解析ワークロードで solve 時間を大きく短縮できます。
- 高速な反復により、ツリー構築、バッチ solve、ノードロック検証がより実用的になります。
- NVIDIA GPU を使う Windows ユーザー向けに、従来の TexasSolver 系列を高性能化した発展版として位置付けています。

## スクリーンショット

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

## ダウンロード

Windows ビルドは [GitHub Releases](https://github.com/bupticybee/TexasSolverGPU/releases) から取得してください。

現在の公開バージョン:

- バージョン: `v0.1.0`
- プラットフォーム: `windows-x64`

## 同梱ファイル

各 Windows パッケージには以下が含まれます。

- `TexasSolverGpu.exe`
- `TexasSolverGpu_131.exe`
- `TexasSolverGpu_legacy_126.exe`
- `WebView2Loader.dll`
- `quick_start/`
- `ranges/`

推奨起動順:

1. `TexasSolverGpu.exe`
2. `TexasSolverGpu_131.exe`
3. `TexasSolverGpu_legacy_126.exe`

## 必要環境

- Windows 10 / Windows 11 64-bit
- NVIDIA GPU
- WebView2 Runtime

## Viewer

戦略ビューアは [viewer/viewer.py](./viewer/viewer.py) に Python ソースとして含まれています。

```powershell
python viewer/viewer.py --file your_result.json
```

詳細は [viewer/README.md](./viewer/README.md) を参照してください。

## コミュニティ

- Discord: https://discord.com/invite/RtyD4vRy2e

## 注意

- 公開リポジトリであっても、非公開の `gpu_solver` ソースがオープンソースになるわけではありません。
- このリポジトリはバイナリ配布、メタデータ、スクリーンショット、補助ツール専用です。
- 内部 solver 実装やビルドシステム、非公開ツールは公開されません。
- 配布に関する注意は [EULA.md](./EULA.md) を確認してください。
