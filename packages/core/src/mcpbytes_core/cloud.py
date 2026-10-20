"""Optional client of the hosted MCPBytes API: runs a tool on MCPBytes GPUs and charges prepaid credits.

Used only when the user asks for the cloud explicitly. Needs MCPBYTES_API_KEY (https://console.mcpbytes.com/keys);
MCPBYTES_API_URL overrides the endpoint. Standard library only. REST contract: https://mcpbytes.com/docs.
"""

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .errors import ToolError

FINAL = {"succeeded", "failed", "canceled", "expired"}
AGENT = "mcpbytes-tools/0.1"


class Cloud:
    def __init__(self, key=None, api=None):
        self.key = key or os.environ.get("MCPBYTES_API_KEY")
        if not self.key:
            raise ToolError("api_key_missing", "cloud mode needs an MCPBytes API key",
                            "set MCPBYTES_API_KEY; create a key at https://console.mcpbytes.com/keys")
        self.api = (api or os.environ.get("MCPBYTES_API_URL") or "https://api.mcpbytes.com").rstrip("/")

    def _send(self, request, timeout=300):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            try:
                error = json.load(e).get("error") or {}
            except ValueError:
                error = {}
            retry = e.headers.get("Retry-After")
            hint = error.get("hint") or (f"retry after {retry} s" if retry else None)
            raise ToolError(error.get("code") or f"http_{e.code}", error.get("message") or str(e.reason), hint) from None
        except urllib.error.URLError as e:
            raise ToolError("unreachable", f"cannot reach {self.api}: {e.reason}") from None

    def call(self, method, path, body=None, headers=None):
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(self.api + path, data=data, method=method, headers={
            "Authorization": f"Bearer {self.key}", "User-Agent": AGENT,
            **({"Content-Type": "application/json"} if data is not None else {}), **(headers or {})})
        return json.loads(self._send(request))

    def upload(self, path):
        """upload_id for a local file; an identical file this account stored recently is reused without a PUT."""
        data = Path(path).read_bytes()
        upload = self.call("POST", "/v1/uploads", {"filename": Path(path).name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        if not upload.get("reused"):
            # The upload URL carries its own token: no API key on this request.
            self._send(urllib.request.Request(upload["url"], data=data, method="PUT",
                                              headers={"Content-Type": "application/octet-stream", "User-Agent": AGENT}), timeout=600)
        return upload["upload_id"]

    def start(self, tool, options, idempotency_key, upload_id=None):
        """Create a job. Replaying the same key and request returns the original job instead of charging again."""
        body = {"options": options, **({"upload_id": upload_id} if upload_id else {})}
        return self.call("POST", f"/v1/tools/{urllib.parse.quote(tool)}/jobs", body, {"Idempotency-Key": idempotency_key})

    def wait(self, job, progress=None):
        delay = 2.0
        while job["status"] not in FINAL:
            if progress:
                progress(job)
            time.sleep(delay)
            delay = min(delay * 1.5, 10.0)
            job = self.call("GET", f"/v1/jobs/{urllib.parse.quote(job['id'])}")
        if job["status"] != "succeeded":
            error = job.get("error") or {}
            raise ToolError(error.get("code") or job["status"], error.get("message") or f"job {job['id']} {job['status']}", error.get("hint"))
        return job

    def download(self, job, out):
        out = Path(out)
        saved = []
        for file in (job.get("result") or {}).get("files", []):
            target = out / file["name"]  # the API validates names: one or two safe segments
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self._send(urllib.request.Request(file["url"], headers={"User-Agent": AGENT}), timeout=600)
            if file.get("sha256") and hashlib.sha256(data).hexdigest() != file["sha256"]:
                raise ToolError("download_corrupt", f"{file['name']} does not match its published SHA-256", "download again")
            target.write_bytes(data)
            saved.append(target)
        return saved
