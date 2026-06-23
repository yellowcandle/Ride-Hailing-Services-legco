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
import json, re, random, zlib

CORPUS = "submissions/corpus.jsonl"
OUT = "submissions/text_findings.json"
K = 96            # minhash signature length
PRIME = (1 << 61) - 1
SIM = 0.45        # Jaccard estimate at/above this = same template skeleton
NGRAM = 4

WS = re.compile(r"\s+")
# Forwarded-email envelope + timezone footer: shared metadata, not the writer's
# content. Strip so two unrelated forwards don't cluster on their headers.
ENVELOPE = re.compile(
    r"寄件者:.*?(?=主旨|主題|致[:：]|$)"
    r"|已傳送:.*?(?:UTC[^)]*\)|\n)"
    r"|收件者:.*?(?:\n|$)",
    re.S)


def shingles(body):
    s = WS.sub("", ENVELOPE.sub("", body))
    return {zlib.crc32(s[i:i + NGRAM].encode()) for i in range(len(s) - NGRAM + 1)}


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
    findings = {"batches": batches, "clusters": cl_out,
                "n_records": len(recs), "n_in_clusters": templated,
                "n_clusters": len(cl_out)}
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
    print("demo OK")


if __name__ == "__main__":
    import sys
    demo() if "--demo" in sys.argv else main()
