from __future__ import annotations

from typing import Any, Dict, List

from bheshajpatro.eclipse.models import EclipseYearReport


def build_graphics_payload(report: EclipseYearReport) -> Dict[str, Any]:
    timeline: List[Dict[str, Any]] = []

    for event in report.events:
        timeline.append(
            {
                "date": event.global_date,
                "kind": event.kind,
                "eclipse_type": event.eclipse_type,
                "visible": event.visible,
                "title": event.title,
            }
        )

    return {
        "timeline": timeline,
    }