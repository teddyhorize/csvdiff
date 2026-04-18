"""CLI helpers for the sampling feature."""

from __future__ import annotations

import argparse
from typing import List, Dict

from csvdiff.sampling import SamplingOptions, SamplingError, sample_pair


def register_sampling_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("sampling")
    grp.add_argument(
        "--sample-n",
        type=int,
        default=None,
        metavar="N",
        help="Randomly sample N rows from each file before diffing.",
    )
    grp.add_argument(
        "--sample-fraction",
        type=float,
        default=None,
        metavar="F",
        help="Randomly sample a fraction (0–1] of rows from each file.",
    )
    grp.add_argument(
        "--sample-seed",
        type=int,
        default=None,
        metavar="SEED",
        help="Random seed for reproducible sampling.",
    )
    grp.add_argument(
        "--sample-systematic",
        action="store_true",
        default=False,
        help="Use systematic (evenly spaced) sampling instead of random.",
    )


def sampling_options_from_args(args: argparse.Namespace) -> SamplingOptions | None:
    if args.sample_n is None and args.sample_fraction is None:
        return None
    return SamplingOptions(
        n=args.sample_n,
        fraction=args.sample_fraction,
        seed=args.sample_seed,
        systematic=args.sample_systematic,
    )


def maybe_apply_sampling(
    rows_a: List[Dict[str, str]],
    rows_b: List[Dict[str, str]],
    args: argparse.Namespace,
) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    opts = sampling_options_from_args(args)
    if opts is None:
        return rows_a, rows_b
    try:
        return sample_pair(rows_a, rows_b, opts)
    except SamplingError as exc:
        raise SystemExit(f"Sampling error: {exc}") from exc
