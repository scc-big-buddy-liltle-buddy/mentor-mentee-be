# global_matching.py
"""
Global optimisation of mentor–mentee assignments.

This module replaces the sequential (greedy) assignment in *matching.py* with a
minimum‑cost‑flow solver from **OR‑Tools** so that the **sum of match scores is
maximised** while each mentor receives at most `max_group_size` mentees.

Public function
---------------
>>> from global_matching import generate_global_match
>>> match = generate_global_match(mentees, mentors)

The returned object is the same *Match* schema used throughout the existing
codebase, so no downstream changes are required.

Requirements
------------
* ortools>=9.8  (add to requirements.txt)

If OR‑Tools cannot be imported, a clear RuntimeError is raised.
"""

from __future__ import annotations

import datetime
import math
import uuid
from typing import List, Optional

try:
    from ortools.graph import pywrapgraph  # type: ignore
except ImportError as exc:  # pragma: no cover – handled at runtime
    raise RuntimeError(
        "OR‑Tools is required for the global optimiser.  Install with:  pip install ortools"
    ) from exc

from app.models import Group, Match, MatchMentee, Mentee, Mentor
from app.utils.matching import calculateMatchingRate

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_flow_model(
    mentees: List[Mentee],
    mentors: List[Mentor],
    max_group_size: int,
) -> pywrapgraph.SimpleMinCostFlow:
    """Return a fully‑populated min‑cost flow network."""

    n_mentees = len(mentees)
    n_mentors = len(mentors)

    SRC = 0
    SINK = n_mentees + n_mentors + 1
    SCALE = 1000  # convert float scores → int costs

    mcf = pywrapgraph.SimpleMinCostFlow()

    # Source → mentee vertices
    for i in range(n_mentees):
        mcf.AddArcWithCapacityAndUnitCost(SRC, i + 1, 1, 0)

    # Mentee → mentor arcs (cost = −score)
    for i, mentee in enumerate(mentees):
        for j, mentor in enumerate(mentors):
            cost = int(-round(calculateMatchingRate(mentee, mentor) * SCALE))
            mcf.AddArcWithCapacityAndUnitCost(i + 1, n_mentees + j + 1, 1, cost)

    # Mentor → sink arcs (capacity = max_group_size)
    for j in range(n_mentors):
        mcf.AddArcWithCapacityAndUnitCost(n_mentees + j + 1, SINK, max_group_size, 0)

    # Supplies
    mcf.SetNodeSupply(SRC, n_mentees)
    mcf.SetNodeSupply(SINK, -n_mentees)

    return mcf


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_global_match(
    mentees: List[Mentee],
    mentors: List[Mentor],
    *,
    match_name: Optional[str] = None,
) -> Match:
    """Return a *Match* whose total matching score is globally optimal."""

    if not mentors:
        raise ValueError("Mentor list cannot be empty")
    if not mentees:
        raise ValueError("Mentee list cannot be empty")

    max_group_size = math.ceil(len(mentees) / len(mentors))
    flow = _build_flow_model(mentees, mentors, max_group_size)

    if flow.Solve() != flow.OPTIMAL:
        raise RuntimeError("OR‑Tools failed to find an optimal assignment")

    # Convert solver output → groups
    groups: List[Group] = [
        {
            "id": str(idx),
            "mentorId": mentor.id,
            "mentees": [],
        }
        for idx, mentor in enumerate(mentors)
    ]

    n_mentees = len(mentees)

    for arc in range(flow.NumArcs()):
        if flow.Flow(arc) == 0:
            continue

        tail, head = flow.Tail(arc), flow.Head(arc)
        if 1 <= tail <= n_mentees and n_mentees < head < n_mentees + len(mentors) + 1:
            mentee_idx = tail - 1
            mentor_idx = head - n_mentees - 1

            mentee = mentees[mentee_idx]
            mentor = mentors[mentor_idx]

            groups[mentor_idx]["mentees"].append(
                MatchMentee(
                    menteeId=mentee.id,
                    menteeName=mentee.fullName,
                    matchRate=calculateMatchingRate(mentee, mentor),
                )
            )

    # ----------------------------- wrap as Match --------------------------- #
    match = Match(
        uid=str(uuid.uuid4()),
        createdAt=datetime.datetime.now().isoformat(timespec="seconds"),
        matchName=match_name or f"Global Match {datetime.date.today()}",
        groups=[Group(**g) for g in groups],
    )

    return match
