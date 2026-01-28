from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict, Counter
import math
import re
from typing import List, Tuple, Dict

def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()

@dataclass
class NGramConfig:
    n: int = 3
    add_k: float = 0.5  # smoothing

class NGramLM:
    """
    N-gram language model with add-k smoothing.
    Provides negative log-likelihood loss over a chunk.
    """
    def __init__(self, cfg: NGramConfig | None = None):
        self.cfg = cfg or NGramConfig()
        self.counts: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)
        self.context_totals: Dict[Tuple[str, ...], int] = defaultdict(int)
        self.vocab: Counter = Counter()

    def _contexts(self, tokens: List[str]) -> List[Tuple[Tuple[str, ...], str]]:
        n = self.cfg.n
        if len(tokens) < n:
            return []
        pairs = []
        for i in range(n - 1, len(tokens)):
            ctx = tuple(tokens[i - (n - 1): i])
            nxt = tokens[i]
            pairs.append((ctx, nxt))
        return pairs

    def update(self, text: str) -> None:
        toks = tokenize(text)
        for t in toks:
            self.vocab[t] += 1
        for ctx, nxt in self._contexts(toks):
            self.counts[ctx][nxt] += 1
            self.context_totals[ctx] += 1

    def nll_loss(self, text: str) -> float:
        toks = tokenize(text)
        pairs = self._contexts(toks)
        if not pairs:
            return 10.0  # conservative high loss for short chunks

        V = max(1, len(self.vocab))
        add_k = self.cfg.add_k

        total = 0.0
        for ctx, nxt in pairs:
            ctx_total = self.context_totals.get(ctx, 0)
            nxt_count = self.counts.get(ctx, Counter()).get(nxt, 0)
            prob = (nxt_count + add_k) / (ctx_total + add_k * V)
            prob = max(prob, 1e-12)
            total += -math.log(prob)

        return total / len(pairs)

    def perplexity(self, text: str) -> float:
        return math.exp(self.nll_loss(text))
