"""Snapshot: save and compare CSV snapshots for regression tracking."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


class SnapshotError(Exception):
    pass


@dataclass
class Snapshot:
    name: str
    path: str
    headers: List[str]
    row_count: int
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    checksum: str = ""


def _snapshot_path(store_dir: str, name: str) -> str:
    return os.path.join(store_dir, f"{name}.snapshot.json")


def save_snapshot(store_dir: str, snapshot: Snapshot) -> None:
    os.makedirs(store_dir, exist_ok=True)
    target = _snapshot_path(store_dir, snapshot.name)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(snapshot.__dict__, f, indent=2)


def load_snapshot(store_dir: str, name: str) -> Snapshot:
    target = _snapshot_path(store_dir, name)
    if not os.path.exists(target):
        raise SnapshotError(f"Snapshot '{name}' not found in {store_dir}")
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Snapshot(**data)


def list_snapshots(store_dir: str) -> List[str]:
    if not os.path.isdir(store_dir):
        return []
    return [
        f.replace(".snapshot.json", "")
        for f in os.listdir(store_dir)
        if f.endswith(".snapshot.json")
    ]


def delete_snapshot(store_dir: str, name: str) -> None:
    target = _snapshot_path(store_dir, name)
    if not os.path.exists(target):
        raise SnapshotError(f"Snapshot '{name}' not found")
    os.remove(target)


def snapshot_from_rows(
    name: str,
    path: str,
    headers: List[str],
    rows: List[Dict[str, str]],
    checksum: str = "",
) -> Snapshot:
    return Snapshot(
        name=name,
        path=path,
        headers=headers,
        row_count=len(rows),
        checksum=checksum,
    )
