from __future__ import annotations

import argparse
import json

from .engine import NetOpsCommanderEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NetOps-Commander LLM scaffold CLI")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--vendor", required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--actor", default="netops_user")
    parser.add_argument(
        "--confirmed",
        action="store_true",
        help="Allow execution of high-risk/destructive changes after external multi-stage approval",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    engine = NetOpsCommanderEngine()
    result = engine.run(
        request_id=args.request_id,
        action=args.action,
        vendor=args.vendor,
        device=args.device,
        query=args.query,
        actor=args.actor,
        confirmed=args.confirmed,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
