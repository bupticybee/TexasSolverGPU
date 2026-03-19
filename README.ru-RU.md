# TexasSolver GPU

[![release](https://img.shields.io/github/v/release/bupticybee/TexasSolverGPU?label=release)](https://github.com/bupticybee/TexasSolverGPU/releases)
[![license](https://img.shields.io/badge/license-EULA-orange)](./EULA.md)
[![discord](https://img.shields.io/badge/discord-join%20chat-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/RtyD4vRy2e)

[English](./README.md) | [简体中文](./README.zh-CN.md) | [日本語](./README.ja-JP.md) | [한국어](./README.ko-KR.md) | [Español](./README.es-ES.md) | README Русский

<p align="center">
  <img src="./assets/images/logo-solid.png" alt="TexasSolver GPU logo" width="220" />
</p>

TexasSolver GPU - это публичный репозиторий дистрибуции Windows-версии GPU-ускоренного солвера для Texas Hold'em, рассчитанного на заметно более быструю локальную работу по сравнению с прежними CPU-ориентированными solver workflow.

## О проекте

TexasSolver GPU предназначен для локального анализа в Windows на машинах с NVIDIA GPU. По сравнению с прежними TexasSolver-подобными workflow, ориентированными в основном на CPU, этот GPU desktop runtime делает упор на намного более быстрые локальные расчеты и более быструю итерацию. Настольное приложение объединяет нативные solver runtime и GUI, чтобы вы могли:

- строить деревья и запускать быстрые расчеты
- пакетно решать несколько бордов
- анализировать сценарии node lock
- изучать результаты стратегии и тренироваться против них

Этот репозиторий предназначен только для публичной дистрибуции. Приватный исходный код `gpu_solver` здесь не публикуется.

## Почему GPU

- GPU-ускорение заметно сокращает время расчета для многих локальных сценариев анализа.
- Более быстрая итерация делает построение деревьев, batch solving и эксперименты с node lock намного практичнее.
- Для пользователей Windows с NVIDIA GPU этот проект можно считать высокопроизводительным развитием более ранней линейки TexasSolver.

## Скриншоты

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

## Скачать

Скачивайте Windows-сборки из [GitHub Releases](https://github.com/bupticybee/TexasSolverGPU/releases).

Текущий публичный релиз:

- Версия: `v0.1.0`
- Платформа: `windows-x64`

## Файлы рантайма

Каждый Windows-пакет включает:

- `TexasSolverGpu.exe`
- `TexasSolverGpu_131.exe`
- `TexasSolverGpu_legacy_126.exe`
- `WebView2Loader.dll`
- `quick_start/`
- `ranges/`

Рекомендуемый порядок запуска:

1. `TexasSolverGpu.exe`
2. `TexasSolverGpu_131.exe`
3. `TexasSolverGpu_legacy_126.exe`

## Требования

- Windows 10 или Windows 11, 64-bit
- NVIDIA GPU
- Установленный WebView2 Runtime

## Viewer

Средство просмотра стратегий распространяется как Python-скрипт: [viewer/viewer.py](./viewer/viewer.py).

```powershell
python viewer/viewer.py --file your_result.json
```

Подробности смотрите в [viewer/README.md](./viewer/README.md).

## Сообщество

- Discord: https://discord.com/invite/RtyD4vRy2e

## Notice

- Публичный репозиторий не означает, что приватный исходный код `gpu_solver` стал open source.
- Этот репозиторий предназначен только для распространения бинарных файлов, метаданных, скриншотов и вспомогательных инструментов.
- Внутренняя реализация solver, build-системы и приватные инструменты здесь не публикуются.
- См. [EULA.md](./EULA.md) для условий распространения.
