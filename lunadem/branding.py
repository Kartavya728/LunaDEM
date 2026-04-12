"""Shared creator metadata and plot credit helpers."""

from __future__ import annotations

from typing import Any

CREATOR_GITHUB_ID = "Kartavya728"
CREATOR_NAME = "Kartavya Mahesh Suryawanshi"


def add_matplotlib_credit(figure: Any) -> None:
    """Stamp a subtle creator credit in the bottom-right corner."""
    figure.text(
        0.995,
        0.015,
        CREATOR_GITHUB_ID,
        ha="right",
        va="bottom",
        fontsize=8,
        alpha=0.3,
    )


def add_plotly_credit(figure: Any) -> None:
    """Stamp a subtle creator credit in the bottom-right corner."""
    figure.add_annotation(
        text=CREATOR_GITHUB_ID,
        xref="paper",
        yref="paper",
        x=0.995,
        y=0.01,
        xanchor="right",
        yanchor="bottom",
        showarrow=False,
        opacity=0.3,
        font={"size": 10},
    )
