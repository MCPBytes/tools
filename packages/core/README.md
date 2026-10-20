# mcpbytes-core

The shared runtime of the [MCPBytes open-source tools](https://github.com/MCPBytes/tools): model files pinned to
Hugging Face commits and downloaded on demand into the standard Hugging Face cache, GPU checks, seeds derived the way
the hosted API derives them, and the client of the hosted MCPBytes API that a tool uses only when you pass `--cloud`.

You normally don't install it yourself: a tool package such as
[`mcpbytes-pixel-sprite`](https://pypi.org/project/mcpbytes-pixel-sprite/) depends on it.

## Licence

GNU AGPL v3.0 only. "MCPBytes" is a trade name of King Of The Hour, LLC; the licence grants no rights to it.
