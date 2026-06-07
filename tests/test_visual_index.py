"""Unit test for the MaxSim scoring core (no model load)."""

import sys
from pathlib import Path

import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.visual_index import maxsim


def test_maxsim_prefers_page_containing_query_directions():
    # query: two orthogonal token directions
    query = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    page_match = torch.tensor([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]])  # covers both
    page_partial = torch.tensor([[1.0, 0.0], [1.0, 0.0]])  # covers one
    scores = maxsim(query, [page_match, page_partial])
    assert scores[0] == pytest.approx(2.0)  # 1.0 + 1.0
    assert scores[1] == pytest.approx(1.0)  # 1.0 + 0.0
    assert scores[0] > scores[1]


def test_maxsim_handles_fp16_pages():
    query = torch.tensor([[1.0, 0.0]])
    page = torch.tensor([[1.0, 0.0]], dtype=torch.float16)
    assert maxsim(query, [page])[0] == pytest.approx(1.0)
