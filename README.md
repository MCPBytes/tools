# MCPBytes tools

Open-source, run-it-yourself versions of the [MCPBytes](https://mcpbytes.com) tools. Each tool is a
Python package with a command line and an MCP server. It runs on your own hardware, or on MCPBytes
GPUs for credits when you pass `--cloud` with an API key.

| Package | What it does | Runs on |
|---|---|---|
| [`mcpbytes-pixel-sprite`](packages/pixel-sprite) | 32×32 pixel-art character sprite sheets with walk animations and Godot/Unity exports | NVIDIA GPU (CUDA), or `--cloud` |
| [`mcpbytes-core`](packages/core) | Shared runtime: pinned Hugging Face model downloads, the cloud client | — |

```bash
uvx --torch-backend=auto mcpbytes-pixel-sprite generate "a forest ranger with a green hood"
```

Model weights are never bundled: each tool downloads them from Hugging Face at pinned commits, under
their publishers' licences.

## Development

```bash
uv sync                # Python 3.11–3.13; CUDA 12.8 PyTorch on Windows and Linux
uv run pytest
```

## Licence

The code is licensed under the [GNU Affero General Public License v3.0 only](LICENSE). Files copied into
a tool's outputs carry their own permissive licence, stated in that package's `NOTICE`; what the tools
generate is yours. "MCPBytes" is a trade name of King Of The Hour, LLC; the licence grants no rights to it.
