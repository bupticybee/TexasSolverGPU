# TexasSolver GPU

[![release](https://img.shields.io/github/v/release/bupticybee/TexasSolverGPU?label=release)](https://github.com/bupticybee/TexasSolverGPU/releases)
[![license](https://img.shields.io/badge/license-EULA-orange)](./EULA.md)
[![discord](https://img.shields.io/badge/discord-join%20chat-5865F2?logo=discord&logoColor=white)](https://discord.com/invite/RtyD4vRy2e)

[English](./README.md) | [简体中文](./README.zh-CN.md) | [日本語](./README.ja-JP.md) | [한국어](./README.ko-KR.md) | README Español | [Русский](./README.ru-RU.md)

<p align="center">
  <img src="./assets/images/logo-solid.png" alt="TexasSolver GPU logo" width="220" />
</p>

TexasSolver GPU es el repositorio público de distribución para la versión de Windows de un solver de Texas Hold'em acelerado por GPU, pensado para resolver mucho más rápido que los flujos anteriores centrados en CPU.

## Introducción

TexasSolver GPU está pensado para estudio local en Windows con una GPU NVIDIA. En comparación con los flujos anteriores de estilo TexasSolver más centrados en CPU, este runtime de escritorio con GPU busca ofrecer resoluciones locales mucho más rápidas y una iteración más ágil. La aplicación de escritorio incluye runtimes nativos del solver y una GUI para:

- construir árboles y empezar estudios rápidos
- resolver varios boards por lotes
- analizar escenarios con node lock
- explorar resultados y practicar contra estrategias

Este repositorio es solo para distribución pública. No contiene el árbol fuente privado de `gpu_solver`.

## Por que GPU

- La aceleración por GPU reduce de forma importante el tiempo de cálculo en muchas cargas de trabajo locales.
- Una iteración más rápida hace mucho más práctico construir árboles, resolver por lotes y probar escenarios con node lock.
- Para usuarios de Windows con GPU NVIDIA, este proyecto representa la evolución de alto rendimiento de la línea TexasSolver anterior.

## Capturas

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

## Descarga

Descarga las builds de Windows desde [GitHub Releases](https://github.com/bupticybee/TexasSolverGPU/releases).

Versión pública actual:

- Versión: `v0.1.0`
- Plataforma: `windows-x64`

## Archivos incluidos

Cada paquete de Windows incluye:

- `TexasSolverGpu.exe`
- `TexasSolverGpu_131.exe`
- `TexasSolverGpu_legacy_126.exe`
- `WebView2Loader.dll`
- `quick_start/`
- `ranges/`

Orden recomendado de inicio:

1. `TexasSolverGpu.exe`
2. `TexasSolverGpu_131.exe`
3. `TexasSolverGpu_legacy_126.exe`

## Requisitos

- Windows 10 o Windows 11 de 64 bits
- GPU NVIDIA
- WebView2 Runtime instalado

## Viewer

El visor de estrategias se distribuye como código Python en [viewer/viewer.py](./viewer/viewer.py).

```powershell
python viewer/viewer.py --file your_result.json
```

Consulta [viewer/README.md](./viewer/README.md) para más detalles.

## Comunidad

- Discord: https://discord.com/invite/RtyD4vRy2e

## Aviso

- Que el repositorio sea público no significa que el código fuente privado de `gpu_solver` sea open source.
- Este repositorio es solo para distribución binaria, metadatos, capturas y herramientas auxiliares.
- La implementación interna del solver, el sistema de build y las herramientas privadas no se publican aquí.
- Consulta [EULA.md](./EULA.md) para el aviso de distribución.
