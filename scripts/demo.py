"""Capture real curl exchanges, with only credential text masked in artifacts."""
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.seed import TENANTS, stable_id

BASE_URL = "http://127.0.0.1:8000"
records = []


def exchange(label, tenant=0, message=None, session_id=None, path="/chat", expected=200):
    key = TENANTS[tenant][2] if tenant is not None else "unknown-local-demo-key"
    masked_key = f"demo_{TENANTS[tenant][1]}_****" if tenant is not None else "unknown_****"
    args = ["curl", "--silent", "--show-error", "--max-time", "20", "-X",
            "POST" if message else "GET", f"{BASE_URL}{path}", "-H", f"X-API-Key: {key}"]
    payload = None
    if message:
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id
        args += ["-H", "Content-Type: application/json", "--data-binary", "@-"]
    result = subprocess.run(args + ["--write-out", "\n%{http_code}"],
                            input=json.dumps(payload) if payload else None,
                            capture_output=True, text=True, check=True, cwd=ROOT)
    body, status = result.stdout.rsplit("\n", 1)
    response = json.loads(body)
    assert int(status) == expected, (label, status, response)
    safe_args = [arg.replace(key, masked_key) for arg in args]
    if payload:
        safe_args[-2:] = ["--data-binary", json.dumps(payload)]
    command = shlex.join(safe_args + ["--write-out", "\n%{http_code}"])
    record = {"label": label, "tenant": TENANTS[tenant][0] if tenant is not None else "Unknown key",
              "masked_key": masked_key, "request": payload, "path": path,
              "status": int(status), "response": response, "command": command}
    records.append(record)
    print(f"{label}: HTTP {status}")
    return response


def main():
    (ROOT / "output").mkdir(exist_ok=True)
    totals = exchange("Acme — totals", message="totals last 7 days")
    assert totals["rows"][0]["posts"] == 21
    top = exchange("Acme — top posts", message="top posts on instagram last 7 days")
    exchange("Acme — platform follow-up", message="what about tiktok?", session_id=top["session_id"])
    exchange("Acme — date follow-up", message="and last month?", session_id=top["session_id"])
    bluebird = exchange("Bluebird — engagement rate", tenant=1,
                        message="engagement rate by platform last month")
    exchange("Bluebird — follower growth", tenant=1, message="follower growth this week")
    exchange("Acme — posting time", message="best posting weekday and hour last month")
    exchange("Acme — comparison", message="compare instagram vs tiktok last month")
    exchange("Acme — worst posts", message="worst posts last 7 days")
    exchange("Acme — local pgvector help", message="what can you answer?")
    exchange("Acme cannot read Bluebird history", path=f"/sessions/{bluebird['session_id']}", expected=404)
    exchange("Unknown key is rejected", tenant=None, message="totals last 7 days", expected=401)
    exchange("Acme — six-message follow-up history", path=f"/sessions/{top['session_id']}")
    for record in records:
        if record["request"] and record["status"] == 200:
            slug = "acme" if record["tenant"] == "Acme Coffee" else "bluebird"
            assert all(row["tenant_id"] == str(stable_id(slug)) for row in record["response"]["rows"])
    (ROOT / "output/demo_records.json").write_text(json.dumps(records, indent=2) + "\n")
    parts = ["# Real curl demo transcript\n",
             "Personal portfolio demo by Zhuangyi Qiu. Rule-based mode and synthetic data. "
             "All requests below were executed by curl against the live local FastAPI server. "
             "Only API-key text in displayed commands is masked. Responses are complete. "
             "The fixed analytics clock is 2026-11-10 12:00 UTC.\n"]
    for index, record in enumerate(records, 1):
        parts += [f"## {index}. {record['label']}\n", "```sh\n" + record["command"] + "\n```\n",
                  f"HTTP {record['status']}\n", "```json\n" + json.dumps(record["response"], indent=2) + "\n```\n"]
    (ROOT / "output/demo_transcript.md").write_text("\n".join(parts))


if __name__ == "__main__":
    main()
