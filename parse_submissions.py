"""Parse the bundled -ec submission volumes into a structured corpus with a
per-record language profile (script / register / vocabulary signals).

Input : submissions/md/*-ec.md   (only these — see note below)
Output: submissions/corpus.jsonl  (one record per individual submission)

Why -ec only: each individual submission is delimited by
  立法會CB(3){paper}/2026({seq})號文件
In the -ec bundles that line separates records. In the -c org files the SAME
string recurs mid-body as a page footer, so splitting them would be wrong.
The OCR'd union file is uncorrected and is a -c file anyway, so it's excluded.

Language fields are SIGNALS, not verdicts: simplified script / mainland
vocabulary / absent Cantonese flag *possible* non-local or templated origin and
only gain weight when they stack with each other and with near-duplicate
clustering. Report them as 疑似 with the ratio shown, never as proof.

ponytail: simp detection is a curated marker-set heuristic (dependency-free,
directionally right, ratio surfaced for transparency). Upgrade path: OpenCC
t2s/s2t roundtrip if the marker set proves too crude.
"""
import re, json, glob, os

MD_DIR = "submissions/md"
OUT = "submissions/corpus.jsonl"

DELIM = re.compile(r"立法會CB\(3\)(\d+)/2026\((\d+)\)號文件")
# 小組委員會 {name}於{YYYY}年{M}月{D}日提交的意見書 {body...}
SUBMITTER = re.compile(
    r"小組委員會\s*(?P<name>.+?)於(?P<y>\d{4})年(?P<m>\d{1,2})月(?P<d>\d{1,2})日提交的意見書\s*"
)
HONORIFICS = ("先生", "小姐", "女士", "醫生", "教授", "博士", "太太")
HAN = re.compile(r"[一-鿿]")
LATIN = re.compile(r"[A-Za-z]")

# Common simplified-only characters likely to surface in these texts. Not
# exhaustive — a ratio flag, not a converter. (繁 in comments for reference.)
# NOTE excluded: 台 只 余 — valid in Traditional too, they fire as false positives.
SIMP_MARKERS = frozenset(
    "网约车这个们来对时间题应该实国华东书见观风飞马师务试验关门开间阳医药钱铁"
    "长两广严丽举义乐习乡买乱产亲从众优传价体债储兰兴养内册写军农冻击划刘则"
    "创删别剧劝动励劳势区协单卖卫却厂历压县参双发变叙叠号叹只台叶吗员听启"
    "呐呒周咏响哑哓哔哕哗哙哜哝哟唛唢唤啧啬啭啮啰啴啸喷喽喾嗫嗬嗳嘘嘤嘱噜团园"
    "图圆国圣场坏块坚坛坜坝坞坟垦垩垫垲垴埘埙埚堑堕墙壮声壳壶处备复够头夸夺奁"
    "妆妇妈姗娄娅娆娇娈娱娲娴婳婴婶媪嫒嫔嫱嬷孙学孪宁宝实宠审宪宫宽宾对寻导寿"
    "将尔尘尝尜尴尽层屃屉届属屡屦岁岂岖岗岘岙岚岛岭岽岿峄峡峣峤峥峦崂崃崄崭嵘"
    "嵚嵛巅巩巯币帅师帏帐帜带帧帮帱帻帼幂幞广庄庆庐庑库应庙庞废廪开异弃张弥弪"
    "弯归录彝彦彻征径徕忆忏忾怀态怂怃怄怅怆怜总怼怿恋恳恶恸恹恺恻恼恽悦悫悬悭"
    "悯惊惧惨惩惫惬惭惮惯愠愦愿慑慭懑懒懔戆戋戏戗战戬户扎扑扦执扩扪扫扬扰抚抛"
    "国买卖东车书见观长门问间样还过这进远连边对会团办亿"
)
CANTONESE = ("嘅", "咗", "喺", "啲", "嗰", "冇", "佢哋", "乜嘢", "嚟", "喇", "嘞", "啩")
EN_TOK = re.compile(r"[A-Za-z][A-Za-z'-]+")
# Tokens that are NOT vernacular code-mixing: topic/brand nouns everyone cites,
# document-citation + email-header boilerplate, and English function words
# (a run of these means a quoted English sentence, not Cantonese code-mixing).
EN_STOP = frozenset((
    "uber tesla didi grab app apps gps ai api mtr kmb taxi octopus whatsapp"
    " hk hong kong china prc"
    " sc subleg legco gov lc cb paper no docx pdf page lcpaper bills ord reg"
    " utc gmt beijing chongqing urumqi am pm mon tue wed thu fri sat sun"
    " the of to for is and are a an in on at be by or as it we you they i this"
    " that with not but"
).split())
# Vocabulary tells: term choice that leaks origin even inside Traditional text
MAINLAND_LEX = ("出租车", "出租車", "师傅", "師傅", "打车", "打車", "网约", "约车")


def lang_profile(text):
    han = HAN.findall(text)
    n_han = len(han) or 1
    simp = sum(c in SIMP_MARKERS for c in han)
    canto = sum(text.count(p) for p in CANTONESE)
    mainland = sum(text.count(w) for w in MAINLAND_LEX)
    has_trad = bool(re.search(r"[網約車這個們來對時間國華東書見觀]", text))
    n_latin = len(LATIN.findall(text))
    if len(han) == 0 and n_latin > 0:
        lang = "en"
    elif n_latin > len(han):
        lang = "mixed"
    else:
        lang = "zh"
    simp_ratio = simp / n_han
    # Intrasentential English woven into a Traditional matrix = HK Cantonese
    # vernacular fluency (call車 / 個app / 揸車chok). Excludes brand/topic nouns,
    # citation+email boilerplate, and English function words (a quoted English
    # sentence ≠ code-mixing). A simplified matrix is gated out: there a loanword
    # like taxi服务 is mainland borrowing, not the HK register the user means.
    codemix = [t for t in (w.lower() for w in EN_TOK.findall(text))
               if t not in EN_STOP]
    return {
        "n_han": len(han),
        "simp_ratio": round(simp_ratio, 4),
        "cantonese_score": canto,
        "mainland_lexicon": mainland,
        "codemix_score": len(codemix),
        "code_mixing": len(han) >= 6 and simp_ratio < 0.05 and len(codemix) >= 1,
        # weakest signal: only a substantial simp chunk inside a Traditional doc
        # is a real paste seam; a stray char or two is OCR/typo noise.
        "mixed_script": simp_ratio >= 0.08 and has_trad,
        "lang": lang,
    }


def split_name(raw):
    raw = raw.strip()
    for h in HONORIFICS:
        if raw.endswith(h):
            return raw[: -len(h)].strip(), h
    return raw, ""


def parse_file(path):
    text = open(path, encoding="utf-8").read()
    src = os.path.basename(path)
    records = []
    matches = list(DELIM.finditer(text))
    for i, m in enumerate(matches):
        paper, seq = m.group(1), m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        sm = SUBMITTER.search(chunk)
        if sm:
            name, honorific = split_name(sm.group("name"))
            date = f"{sm.group('y')}-{int(sm.group('m')):02d}-{int(sm.group('d')):02d}"
            body = chunk[sm.end():].strip()
        else:
            name, honorific, date, body = "", "", "", chunk
        rec = {
            "paper": f"CB(3){paper}/2026",
            "seq": int(seq),
            "name": name,
            "honorific": honorific,
            "date": date,
            "source": src,
            "n_chars": len(body),
            "body": body,
            **lang_profile(body),
        }
        records.append(rec)
    return records


def main():
    all_recs = []
    for path in sorted(glob.glob(f"{MD_DIR}/*-ec.md")):
        all_recs.extend(parse_file(path))
    with open(OUT, "w", encoding="utf-8") as f:
        for r in all_recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    n = len(all_recs)
    named = sum(1 for r in all_recs if r["name"])
    simp = sum(1 for r in all_recs if r["simp_ratio"] >= 0.10)
    canto = sum(1 for r in all_recs if r["cantonese_score"] >= 3)
    codemix = sum(1 for r in all_recs if r["code_mixing"])
    canto_or_mix = sum(1 for r in all_recs if r["cantonese_score"] >= 3 or r["code_mixing"])
    mainland = sum(1 for r in all_recs if r["mainland_lexicon"] > 0)
    mixed = sum(1 for r in all_recs if r["mixed_script"])
    en = sum(1 for r in all_recs if r["lang"] != "zh")
    print(f"WROTE {OUT}: {n} records, {named} with a parsed name")
    print(f"  simplified-leaning (simp_ratio≥0.10): {simp}")
    print(f"  Cantonese register (score≥3):         {canto}")
    print(f"  EN code-mixing in Trad matrix:        {codemix}")
    print(f"  local vernacular (Cantonese OR mix):  {canto_or_mix}")
    print(f"  mainland vocabulary present:          {mainland}")
    print(f"  mixed script (paste-seam signal):     {mixed}")
    print(f"  non-zh (en/mixed):                    {en}")


def demo():
    """ponytail self-check: parsing + language signals must hold."""
    trad = lang_profile("網約車嘅數量唔夠，呢個係市民嘅需求")  # HK Cantonese, traditional
    assert trad["cantonese_score"] >= 2, trad
    assert trad["simp_ratio"] == 0.0, trad
    assert trad["code_mixing"] is False, trad  # no English → not code-mixing
    simp = lang_profile("网约车的数量不够，这个是市民的需求")  # simplified
    assert simp["simp_ratio"] > 0.3, simp
    assert simp["cantonese_score"] == 0, simp
    mix = lang_profile("call車費太貴，個app好user-friendly但10000個牌實在太少")  # Trad + EN code-mix
    assert mix["code_mixing"] is True, mix
    assert mix["codemix_score"] >= 2, mix  # call, user-friendly (app is a brand-stop)
    loan = lang_profile("香港的taxi服务太差，应该开放")  # simplified matrix + loanword
    assert loan["code_mixing"] is False, loan  # gated out: not the HK register
    brand = lang_profile("我每日都用Uber返工，好方便")  # only a brand name, no code-mix
    assert brand["code_mixing"] is False, brand
    n, h = split_name("袁天賦先生")
    assert (n, h) == ("袁天賦", "先生"), (n, h)
    n2, h2 = split_name("CLARKE Martin")
    assert (n2, h2) == ("CLARKE Martin", ""), (n2, h2)
    # delimiter + submitter line parse end-to-end
    sample = ("立法會CB(3)662/2026(101)號文件\n\n與規管網約車服務有關的4項附屬法例"
              "小組委員會 袁天賦先生於2026年6月9日提交的意見書 正文內容測試。")
    import tempfile
    p = os.path.join(tempfile.mkdtemp(), "x-ec.md")
    open(p, "w", encoding="utf-8").write(sample)
    recs = parse_file(p)
    assert len(recs) == 1 and recs[0]["name"] == "袁天賦" and recs[0]["seq"] == 101, recs
    assert recs[0]["date"] == "2026-06-09" and recs[0]["body"] == "正文內容測試。", recs
    print("demo OK")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        demo()
    else:
        main()
