"""Textual-analysis findings over submissions/corpus.jsonl.

Two outputs, both written to submissions/text_findings.json (+ printed):
  1. Per-batch language profile (662/673/688/710): local-vernacular vs
     simplified / mainland-vocabulary shares.
  2. Near-duplicate template clusters via MinHash on char 4-grams — quantifies
     the "templated letter" campaigns ANALYSIS.md currently counts by hand, and
     fingerprints each cluster by the language signals (organic = Cantonese /
     code-mix; templated-astroturf = simplified / mainland vocab).

Stdlib only, deterministic (fixed seeds; crc32 shingle hashing). ponytail:
MinHash not exact Jaccard — fine for near-dup detection at ~1k docs; exact
pairwise is the upgrade if a cluster boundary is ever disputed.
"""
import json, re, random, zlib, math
from collections import defaultdict, Counter

CORPUS = "submissions/corpus.jsonl"
OUT = "submissions/text_findings.json"
K = 96            # minhash signature length
PRIME = (1 << 61) - 1
SIM = 0.45        # Jaccard estimate at/above this = same template skeleton
NGRAM = 4

# Soft (TF-IDF cosine) pass: catches PARAPHRASED templates — shared argument
# skeletons reworded enough to slip past the near-identical MinHash bar (the
# blind spot §6.2 names: "a reworded template won't register"). Cosine over
# idf-weighted char-4-grams links docs that reuse distinctive phrasing without
# being copies. SOFT_PICK is the reported threshold; SOFT_SIMS is the honesty
# knob — we print cluster counts across it so the cut isn't a hidden choice.
SOFT_PICK = 0.35
SOFT_SIMS = (0.25, 0.35, 0.45)
DF_HI = 0.6       # drop char-4-grams in >60% of docs: punctuation-level noise,
                  # tiny idf anyway, and their huge postings dominate cost.

WS = re.compile(r"\s+")
# Forwarded-email envelope + timezone footer: shared metadata, not the writer's
# content. Strip so two unrelated forwards don't cluster on their headers.
ENVELOPE = re.compile(
    r"寄件者:.*?(?=主旨|主題|致[:：]|$)"
    r"|已傳送:.*?(?:UTC[^)]*\)|\n)"
    r"|收件者:.*?(?:\n|$)",
    re.S)


def clean(body):
    return WS.sub("", ENVELOPE.sub("", body))


def shingles(body):
    s = clean(body)
    return {zlib.crc32(s[i:i + NGRAM].encode()) for i in range(len(s) - NGRAM + 1)}


def gramset(s):                                    # string char-4-grams (cleaned text)
    return {s[i:i + NGRAM] for i in range(len(s) - NGRAM + 1)}


def signature(sh, coeffs):
    if not sh:
        return None
    return tuple(min((a * x + b) % PRIME for x in sh) for a, b in coeffs)


def cluster(recs, coeffs):
    sigs = {}
    for i, r in enumerate(recs):
        sh = shingles(r["body"])
        if len(sh) >= 8:                      # skip near-empty bodies
            sigs[i] = signature(sh, coeffs)
    ids = list(sigs)
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    # LSH banding to avoid the full O(n^2): many narrow bands = sensitive to
    # looser (≈0.45) template matches; the SIM check below removes false collisions.
    BANDS, ROWS = 48, K // 48
    from collections import defaultdict
    buckets = defaultdict(list)
    for i in ids:
        sig = sigs[i]
        for b in range(BANDS):
            buckets[(b, sig[b * ROWS:(b + 1) * ROWS])].append(i)
    for members in buckets.values():
        for a in range(len(members)):
            for c in range(a + 1, len(members)):
                i, j = members[a], members[c]
                if find(i) == find(j):
                    continue
                est = sum(x == y for x, y in zip(sigs[i], sigs[j])) / K
                if est >= SIM:
                    parent[find(i)] = find(j)
    groups = defaultdict(list)
    for i in ids:
        groups[find(i)].append(i)
    return [g for g in groups.values() if len(g) >= 3]


def union_find(n):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return find, union, parent


def tfidf_vectors(bodies):
    # Binary tf (presence) — petitions are short; a repeated phrase shouldn't
    # outweigh the skeleton. idf crushes common grams; drop df<2 (no sharing
    # possible) and df>DF_HI*N (noise). L2-normalise so dot == cosine.
    grams = [gramset(clean(b)) for b in bodies]
    df = Counter(g for gs in grams for g in gs)
    n = len(bodies)
    keep = {g: math.log(n / d) for g, d in df.items() if 2 <= d <= DF_HI * n}
    vecs = []
    for gs in grams:
        w = {g: keep[g] for g in gs if g in keep}
        norm = math.sqrt(sum(v * v for v in w.values())) or 1.0
        vecs.append({g: v / norm for g, v in w.items()})
    return vecs


def cosine_pairs(vecs):
    # Exact sparse cosine via inverted index — only docs sharing a kept gram are
    # compared, so cost is Σ_g C(df_g,2), not O(n²). Returns {(i<j): cosine}.
    inv = defaultdict(list)
    for i, v in enumerate(vecs):
        for g, w in v.items():
            inv[g].append((i, w))
    dot = defaultdict(float)
    for postings in inv.values():
        for a in range(len(postings)):
            ia, wa = postings[a]
            for b in range(a + 1, len(postings)):
                ib, wb = postings[b]
                dot[(ia, ib) if ia < ib else (ib, ia)] += wa * wb
    return dot


def soft_cluster(dot, n, sim):
    find, union, _ = union_find(n)
    for (i, j), c in dot.items():
        if c >= sim:
            union(i, j)
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)
    return [g for g in groups.values() if len(g) >= 3]


def stitch(grams):
    # Greedily glue overlapping 4-grams (share 3 chars) into readable phrases.
    # ponytail: greedy/first-match, so branchy templates may merge oddly — it's
    # a human-readable label for the shared frame, not a canonical reconstruction.
    grams = set(grams)
    by_prefix = defaultdict(list)
    for g in grams:
        by_prefix[g[:3]].append(g)
    used, out = set(), []
    for g in sorted(grams):
        if g in used:
            continue
        s = g
        used.add(g)
        while True:
            nxt = [x for x in by_prefix.get(s[-3:], ()) if x not in used]
            if not nxt:
                break
            used.add(nxt[0])
            s += nxt[0][-1]
        out.append(s)
    out.sort(key=len, reverse=True)
    return out


def frame_phrases(members, k=3, frac=0.6):
    # The shared talking-point: 4-grams present in ≥frac of members, stitched.
    grams = [gramset(clean(m["body"])) for m in members]
    need = max(2, round(frac * len(members)))
    common = Counter(g for gs in grams for g in gs)
    shared = [g for g, c in common.items() if c >= need]
    out = [p for p in stitch(shared) if len(p) >= NGRAM + 2]
    return [(p[:36] + "…") if len(p) > 37 else p for p in out[:k]]   # label, not paragraph


def main():
    recs = [json.loads(l) for l in open(CORPUS, encoding="utf-8")]
    rng = random.Random(42)
    coeffs = [(rng.randrange(1, PRIME), rng.randrange(0, PRIME)) for _ in range(K)]

    # 1. per-batch language profile
    batches = {}
    for r in recs:
        b = re.search(r"CB\(3\)(\d+)", r["paper"]).group(1)
        d = batches.setdefault(b, {"n": 0, "vernacular": 0, "simp": 0, "mainland": 0, "en": 0})
        d["n"] += 1
        if r["cantonese_score"] >= 3 or r["code_mixing"]:
            d["vernacular"] += 1
        if r["simp_ratio"] >= 0.10:
            d["simp"] += 1
        if r["mainland_lexicon"] > 0:
            d["mainland"] += 1
        if r["lang"] != "zh":
            d["en"] += 1

    # 2. near-duplicate template clusters
    clusters = cluster(recs, coeffs)
    cl_out = []
    for g in sorted(clusters, key=len, reverse=True):
        members = [recs[i] for i in g]
        vern = sum(1 for m in members if m["cantonese_score"] >= 3 or m["code_mixing"])
        simp = sum(1 for m in members if m["simp_ratio"] >= 0.10)
        mainland = sum(1 for m in members if m["mainland_lexicon"] > 0)
        papers = sorted({m["paper"] for m in members})
        cl_out.append({
            "size": len(g),
            "papers": papers,
            "vernacular": vern, "simp": simp, "mainland": mainland,
            "sample": members[0]["body"][:80],
        })

    templated = sum(c["size"] for c in cl_out)

    # 3. soft (paraphrase) template families — TF-IDF char-4-gram cosine
    n = len(recs)
    minhash_idx = {i for g in clusters for i in g}
    dot = cosine_pairs(tfidf_vectors([r["body"] for r in recs]))
    sensitivity = {}
    for s in SOFT_SIMS:
        gs = soft_cluster(dot, n, s)
        sensitivity[s] = {"clusters": len(gs), "docs": sum(len(g) for g in gs)}
    soft_out = []
    for g in sorted(soft_cluster(dot, n, SOFT_PICK), key=len, reverse=True):
        members = [recs[i] for i in g]
        dates = sorted(m["date"] for m in members if m.get("date"))
        day = Counter(d for d in dates).most_common(1)
        soft_out.append({
            "size": len(g),
            "papers": sorted({m["paper"] for m in members}),
            "vernacular": sum(1 for m in members if m["cantonese_score"] >= 3 or m["code_mixing"]),
            "simp": sum(1 for m in members if m["simp_ratio"] >= 0.10),
            "mainland": sum(1 for m in members if m["mainland_lexicon"] > 0),
            "new_vs_minhash": sum(1 for i in g if i not in minhash_idx),
            "date_span": [dates[0], dates[-1]] if dates else None,
            "peak_day": list(day[0]) if day else None,
            "frame": frame_phrases(members),
            "sample": members[0]["body"][:80],
        })
    soft_docs = sum(c["size"] for c in soft_out)

    findings = {"batches": batches, "clusters": cl_out,
                "n_records": n, "n_in_clusters": templated,
                "n_clusters": len(cl_out),
                "soft_pick": SOFT_PICK, "soft_sensitivity": sensitivity,
                "soft_clusters": soft_out, "n_in_soft_clusters": soft_docs}
    json.dump(findings, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"records: {len(recs)}")
    print("\nper-batch language profile:")
    print(f"  {'batch':9} {'n':>4} {'vernacular':>11} {'simp≥.10':>9} {'mainland':>9} {'en/mix':>7}")
    for b in sorted(batches):
        d = batches[b]
        print(f"  CB(3){b:5} {d['n']:>4} {d['vernacular']:>6} ({d['vernacular']*100//d['n']:>2}%) "
              f"{d['simp']:>8} {d['mainland']:>9} {d['en']:>7}")
    print(f"\nnear-duplicate clusters (≥3, Jaccard≥{SIM}): {len(cl_out)} clusters, "
          f"{templated} submissions ({templated*100//len(recs)}%)")
    for c in cl_out[:12]:
        print(f"  size {c['size']:>3}  vern={c['vernacular']:>2} simp={c['simp']:>2} "
              f"mainland={c['mainland']:>2}  {c['papers']}  | {c['sample'][:42]}")

    print(f"\nsoft paraphrase families (cosine threshold sensitivity):")
    for s in SOFT_SIMS:
        d = sensitivity[s]
        print(f"  cos≥{s}: {d['clusters']:>3} families, {d['docs']:>4} docs "
              f"({d['docs']*100//n}%)")
    print(f"\nfamilies at picked cos≥{SOFT_PICK}: {len(soft_out)} families, "
          f"{soft_docs} docs ({soft_docs*100//n}%); "
          f"{sum(c['new_vs_minhash'] for c in soft_out)} not caught by MinHash")
    for c in soft_out[:12]:
        span = "–".join(c["date_span"]) if c["date_span"] else "?"
        peak = f"{c['peak_day'][0]}×{c['peak_day'][1]}" if c["peak_day"] else "?"
        print(f"  size {c['size']:>3} (+{c['new_vs_minhash']} new)  vern={c['vernacular']:>2} "
              f"simp={c['simp']:>2} mainland={c['mainland']:>2}  {span} peak {peak}")
        print(f"        frame: {' / '.join(c['frame']) or '(diffuse)'}")
    print(f"WROTE {OUT}")


def demo():
    a = "我支持放寬網約車牌照數量上限至三萬個以滿足市民需求" * 3
    b = a.replace("三萬", "兩萬")            # near-identical template
    c = "的士服務質素低劣司機拒載兜路必須嚴格規管白牌車保障乘客" * 3  # different
    rng = random.Random(1)
    coeffs = [(rng.randrange(1, PRIME), rng.randrange(0, PRIME)) for _ in range(K)]
    recs = [{"body": a, "cantonese_score": 0, "code_mixing": False, "simp_ratio": 0,
             "mainland_lexicon": 0}] * 1
    recs = [dict(body=x, cantonese_score=0, code_mixing=False, simp_ratio=0,
                 mainland_lexicon=0) for x in (a, b, c, a)]
    cl = cluster(recs, coeffs)
    assert len(cl) == 1, cl                  # a,b,a cluster; c excluded
    assert sorted(cl[0]) == [0, 1, 3], cl
    assert signature(shingles(c), coeffs) != signature(shingles(a), coeffs)

    # soft pass: three PARAPHRASES of one petition (reworded, words inserted) —
    # MinHash misses them (Jaccard too low), cosine groups them; an off-topic
    # doc stays out.
    base = "本人強烈反對政府批出一萬個網約車牌照，嚴重衝擊的士行業，懇請當局撤回建議"
    p1 = "本人強烈反對政府首階段批出一萬個網約車牌照，對的士行業造成嚴重衝擊，懇請當局盡快撤回有關建議"
    p2 = "本人在此強烈反對政府批出多達一萬個網約車牌照，嚴重衝擊現有的士行業，懇請當局撤回此建議"
    off = "網約車收費透明，乘客可預先知道車費，又不能拒載，服務遠勝現時的士。" * 2
    soft = [{"body": x} for x in (base, p1, p2, off)]
    dot = cosine_pairs(tfidf_vectors([s["body"] for s in soft]))
    grp = soft_cluster(dot, len(soft), SOFT_PICK)
    assert len(grp) == 1 and sorted(grp[0]) == [0, 1, 2], grp   # 3 paraphrases, off excluded
    assert frame_phrases([{"body": base}, {"body": p1}, {"body": p2}]), "should surface a shared frame"
    print("demo OK")


if __name__ == "__main__":
    import sys
    demo() if "--demo" in sys.argv else main()
