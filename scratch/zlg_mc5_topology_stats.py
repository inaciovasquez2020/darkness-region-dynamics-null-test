#!/usr/bin/env python3
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

URL = 'https://raw.githubusercontent.com/usnistgov/Circuits/master/data/topologies/topologies_k5.txt'
EXPECTED_BLOB_SHA = '597223d8709eda00c4728ecb304ba827cc1faa86'
GATE_RE = re.compile(r'\(A(\d+)\s+([^:]+?)\s*:\s*([^\)]+?)\)')


def git_blob_sha(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f'blob {len(data)}\0'.encode())
    h.update(data)
    return h.hexdigest()


def side_mask(s: str) -> int:
    s = s.strip()
    if s == 'L':
        return 0
    m = 0
    for tok in s.split():
        m |= 1 << int(tok)
    return m


def parse(line: str):
    gates = []
    for idx, left, right in GATE_RE.findall(line):
        gates.append((int(idx), side_mask(left), side_mask(right)))
    assert len(gates) == 5 and [g[0] for g in gates] == list(range(5)), line
    return [(l, r) for _, l, r in gates]


def reuse_rank(pair):
    l, r = pair
    if l == 0 and r == 0:
        return 0
    if l == 0 or r == 0 or l == r:
        return 1
    return 2


def sinks(gates):
    used = set()
    for j, (l, r) in enumerate(gates):
        for i in range(j):
            if ((l | r) >> i) & 1:
                used.add(i)
    return [i for i in range(5) if i not in used]


def ancestors_of(gates, root):
    seen = set()
    stack = [root]
    while stack:
        j = stack.pop()
        l, r = gates[j]
        for i in range(j):
            if ((l | r) >> i) & 1 and i not in seen:
                seen.add(i)
                stack.append(i)
    return seen


def depth(gates):
    d = [1] * 5
    for j, (l, r) in enumerate(gates):
        parents = [i for i in range(j) if ((l | r) >> i) & 1]
        if parents:
            d[j] = 1 + max(d[i] for i in parents)
    return max(d)


def main():
    data = urllib.request.urlopen(URL, timeout=30).read()
    sha = git_blob_sha(data)
    assert sha == EXPECTED_BLOB_SHA, (sha, EXPECTED_BLOB_SHA)
    lines = [x for x in data.decode().splitlines() if x.strip()]
    assert len(lines) == 3170, len(lines)

    last_rank = Counter()
    last_union = Counter()
    sink_count = Counter()
    min_sink_rank = Counter()
    all_sinks_rank2 = 0
    unique_sink_rank = Counter()
    last_ancestor_count = Counter()
    depths = Counter()
    hard_examples = []

    for line_no, line in enumerate(lines, 1):
        g = parse(line)
        lr = reuse_rank(g[4])
        last_rank[lr] += 1
        last_union[(g[4][0] | g[4][1]).bit_count()] += 1
        ss = sinks(g)
        sink_count[len(ss)] += 1
        sr = [reuse_rank(g[i]) for i in ss]
        min_sink_rank[min(sr)] += 1
        if all(x == 2 for x in sr):
            all_sinks_rank2 += 1
            if len(hard_examples) < 20:
                hard_examples.append({'line': line_no, 'sinks': ss, 'topology': line})
        if len(ss) == 1:
            unique_sink_rank[sr[0]] += 1
        last_ancestor_count[len(ancestors_of(g, 4))] += 1
        depths[depth(g)] += 1

    out = {
        'source': {'url': URL, 'git_blob_sha': sha, 'topologies': len(lines)},
        'last_gate_reuse_rank': dict(sorted(last_rank.items())),
        'last_gate_prior_support_size': dict(sorted(last_union.items())),
        'sink_count': dict(sorted(sink_count.items())),
        'minimum_sink_reuse_rank': dict(sorted(min_sink_rank.items())),
        'all_sinks_reuse_rank_2': all_sinks_rank2,
        'unique_sink_reuse_rank': dict(sorted(unique_sink_rank.items())),
        'last_gate_ancestor_count': dict(sorted(last_ancestor_count.items())),
        'depth': dict(sorted(depths.items())),
        'hard_examples_first_20': hard_examples,
    }
    Path('/tmp/zlg_mc5_topology_stats.json').write_text(json.dumps(out, indent=2) + '\n')
    print('ZLG_MC5_TOPOLOGY_STATS_BEGIN')
    print(json.dumps(out, sort_keys=True))
    print('ZLG_MC5_TOPOLOGY_STATS_END')


if __name__ == '__main__':
    main()
