# MCPBytes tools

Open-source, run-it-yourself versions of the [MCPBytes](https://mcpbytes.com) tools. Each tool is a
Python package with a command line and an MCP server. It runs on your own hardware, or on MCPBytes
GPUs for credits when you pass `--cloud` with an API key.

| Package | What it does | Runs on |
|---|---|---|
| [`mcpbytes-pixel-sprite`](https://github.com/MCPBytes/mcpbytes-pixel-sprite) | 32×32 pixel-art character sprite sheets with walk animations and Godot/Unity exports | NVIDIA GPU (CUDA), or `--cloud` |
| [`mcpbytes-image-to-3d`](https://github.com/MCPBytes/mcpbytes-image-to-3d) | A textured 3D model (GLB) from one image: a harness around Tencent's Hunyuan3D 2.1 | NVIDIA GPU (CUDA, 32 GB or more), or `--cloud` |
| [`mcpbytes-core`](packages/core) | Shared runtime: pinned Hugging Face model downloads, the cloud client | — |

```bash
uvx --torch-backend=auto mcpbytes-pixel-sprite generate "a forest ranger with a green hood"
uvx --python 3.12 --torch-backend=auto mcpbytes-image-to-3d chair.jpg
```

Model weights are never bundled: each tool downloads them from their publishers, at pinned commits or
checksums, under their publishers' licences.

## Development

Each tool lives in its own repository and is checked out here as a submodule under `packages/`, next to the shared
`mcpbytes-core`, so clone with `--recursive` (or run `git submodule update --init` in an existing clone):

```bash
git clone --recursive https://github.com/MCPBytes/tools
uv sync                # Python 3.11–3.13; CUDA 12.8 PyTorch on Windows and Linux
uv run pytest
```

`packages/image-to-3d` is not a workspace member: Hunyuan3D 2.1's code needs older ML libraries than pixel-sprite,
so it has its own environment (`cd packages/image-to-3d && uv run --with pytest pytest`).

## Licence

The code is licensed under the [GNU Affero General Public License v3.0 only](LICENSE). Files copied into
a tool's outputs carry their own permissive licence, stated in that package's `NOTICE`; vendored third-party
code keeps its own licence (`mcpbytes-image-to-3d` includes Tencent's Hunyuan3D 2.1 code, under the Tencent
Hunyuan 3D 2.1 Community License Agreement). What the tools generate is yours.
