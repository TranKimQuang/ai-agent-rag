import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Download an official CSO CSV snapshot")
    parser.add_argument(
        "--url",
        default="https://cso.kmi.open.ac.uk/download/version-3.5/cso_v3.5.csv",
        help="Official CSO download endpoint",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/cso-source/cso-v3.5.csv"),
    )
    args = parser.parse_args()

    response = httpx.get(args.url, timeout=120, follow_redirects=True)
    response.raise_for_status()
    content = response.content
    if not content:
        raise RuntimeError("The CSO download returned an empty response")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(content)
    manifest = {
        "source_url": args.url,
        "resolved_url": str(response.url),
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "content_type": response.headers.get("content-type"),
        "content_disposition": response.headers.get("content-disposition"),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "output": args.output.as_posix(),
    }
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
