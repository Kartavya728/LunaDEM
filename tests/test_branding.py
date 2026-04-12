from __future__ import annotations

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from lunadem.branding import (
    CREATOR_GITHUB_ID,
    CREATOR_NAME,
    add_matplotlib_credit,
    add_plotly_credit,
)


def test_add_matplotlib_credit_places_handle() -> None:
    fig, _ = plt.subplots()
    add_matplotlib_credit(fig)

    assert fig.texts
    assert fig.texts[-1].get_text() == CREATOR_GITHUB_ID
    assert fig.texts[-1].get_alpha() == 0.3
    plt.close(fig)


def test_add_plotly_credit_places_handle() -> None:
    figure = go.Figure()
    add_plotly_credit(figure)

    assert figure.layout.annotations
    assert figure.layout.annotations[-1].text == CREATOR_GITHUB_ID
    assert figure.layout.annotations[-1].opacity == 0.3


def test_creator_constants_are_stable() -> None:
    assert CREATOR_NAME == "Kartavya Mahesh Suryawanshi"
    assert CREATOR_GITHUB_ID == "Kartavya728"
