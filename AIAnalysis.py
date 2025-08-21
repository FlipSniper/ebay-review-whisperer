import os
import re
import pandas as pd
from rapidfuzz import fuzz
from transformers import pipeline

# ========= Config =========
CSV_PATH = "test.csv"

HARD_NEGATIVE_ISSUES = {
    "Fake or counterfeit",
    "Faulty functionality",
    "Missing parts",
    "Wrong item",
    "Misleading description",   # treated as hard neg if explicitly present
    "Damaged product (severe)"  # we tag severity
}

POSITIVE_ISSUES = {
    "Good experience", "Fast delivery", "Well packaged", "Accurate description",
    "Great value", "Responsive seller", "High quality", "Good product",
    "Helpful seller", "Issue resolved", "Trustworthy seller", "Great communication"
}

POSITIVE_WORDS = {
    "great","excellent","happy","recommend","fast shipping","good price","love",
    "satisfied","perfect","awesome","wonderful","smooth transaction","very good",
    "looks new","like new","no scratches","no scratch","no cracks","no crack"
}

# ========= Load =========
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(os.path.abspath(CSV_PATH))

df = pd.read_csv(CSV_PATH)
req = {"comment","rating_type"}
if not req.issubset(df.columns):
    raise ValueError(f"CSV must include {req}")

# normalize comments
def normalize_quotes(s: str) -> str:
    return (s.replace("“","\"").replace("”","\"")
             .replace("’","'").replace("‘","'")
             .replace("–","-").replace("—","-"))

df["comment"] = df["comment"].fillna("").astype(str).map(normalize_quotes)
df = df[~df["comment"].str.strip().str.lower().isin({"ok","fine","good","meh","nice","cool"})].copy()

# ========= Categories / Keywords =========
ISSUE_CATEGORIES = [
    "Late delivery","Wrong item","Overpriced","Fake or counterfeit",
    "Damaged product","Missing parts","Poor customer service",
    "Good experience","Fast delivery","Well packaged","Accurate description",
    "Great value","Responsive seller","High quality","Misleading description",
    "Faulty functionality","Good product","Helpful seller","Issue resolved",
    "Trustworthy seller","Great communication"
]

ISSUE_KEYWORDS = {
    # negatives
    "Late delivery": ["late delivery","arrived late","delayed","slow shipping","shipping delay","later than scheduled"],
    "Wrong item": ["wrong item","incorrect item","not what i ordered","different item","description doesn’t match","description doesn't match"],
    "Overpriced": ["overpriced","too expensive","pricey","cost too much","high price"],
    "Fake or counterfeit": ["fake","counterfeit","not genuine","knockoff","imitation"],
    "Damaged product": ["damaged","broken","defective","faulty","scratches","scratched","scuff","scuffed",
                        "crack","cracked","shattered","chips","chipped","knicks","nicks"],
    "Missing parts": ["missing parts","incomplete","parts not included","missing sim tray","no sim tray"],
    "Poor customer service": ["poor service","bad support","unhelpful","rude seller","no response","slow response"],

    # positives / neutrals
    "Good experience": ["good experience","happy","satisfied","recommend","perfect","awesome","wonderful"],
    "Fast delivery": ["fast delivery","quick shipping","arrived quickly","super quick","came quickly"],
    "Well packaged": ["well packaged","secure packaging","nicely packed","good packaging"],
    "Accurate description": ["accurate description","as described","matched listing","true to description"],
    "Great value": ["great value","good value","worth the money","good deal","reasonable price"],
    "Responsive seller": ["responsive seller","quick reply","helpful seller","good communication","kept me informed","very fast response","understanding"],
    "High quality": ["high quality","premium","well made","quality perfect"],
    "Misleading description": ["misleading","not as described","description not accurate","listed wrong"],
    "Faulty functionality": ["doesn't work","not working","faulty functionality","esim was broken","won't turn on","won’t turn on"],
    "Good product": ["great condition","looks like new","like new","looks new","very clean"],
    "Helpful seller": ["helpful","responsive","understanding"],
    "Issue resolved": ["resolved the issue","gave refund","took care of it","refund issued"],
    "Trustworthy seller": ["trustworthy","reliable","very trustworthy"],
    "Great communication": ["kept me informed","great communication","good communication"]
}

# modifiers for damage severity
SEVERE_MODS = {"excessive","large","deep","pronounced","many","a lot","tons","way more","significant","big","heavy"}
MINOR_MODS  = {"tiny","small","minor","light","hairline","couple","few","not visible","barely visible","only"}

# ========= Helpers =========
def has_negation_window(text: str, kw: str, max_gap=3) -> bool:
    """
    Detect negation within a small window before keyword.
    Catches: 'no scratches', 'not scratched', 'never any scratches', 'without scratches'
    """
    pattern = rf"\b(?:no|not|never|without)\b(?:\W+\w+){{0,{max_gap}}}?\W*\b{re.escape(kw)}\b"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def fuzzy_hit(text: str, kw: str, threshold=95) -> bool:
    return fuzz.partial_ratio(kw, text) >= threshold

def detect_damage_with_severity(text: str, original_rating: str) -> str | None:
    t = text.lower()
    any_damage_word = False
    severe_hint = False
    minor_hint = False

    for kw in ISSUE_KEYWORDS["Damaged product"]:
        if has_negation_window(t, kw):  # e.g., "no scratches"
            continue
        if fuzzy_hit(t, kw):
            any_damage_word = True

    if not any_damage_word:
        return None

    # severity cues
    for mod in SEVERE_MODS:
        if mod in t:
            severe_hint = True; break
    for mod in MINOR_MODS:
        if mod in t:
            minor_hint = True

    # cracked/shattered are always severe
    if any(w in t for w in ["crack","cracked","shatter","shattered","chip","chipped"]):
        severe_hint = True

    # if user rated Positive and damage is minor → don't tag as damage
    if original_rating.lower() == "positive" and not severe_hint:
        return None

    return "Damaged product (severe)" if severe_hint else "Damaged product"

def match_issues_rule_based(text: str, original_rating: str, threshold=95) -> list[str]:
    t = text.lower()
    issues = set()

    # Special-case damage with severity
    dmg = detect_damage_with_severity(text, original_rating)
    if dmg:
        issues.add(dmg)

    # Generic keyword matching with negation guard
    for issue, kws in ISSUE_KEYWORDS.items():
        if issue.startswith("Damaged product"):
            continue  # handled above
        for kw in kws:
            if has_negation_window(t, kw):
                continue
            if fuzzy_hit(t, kw, threshold=threshold):
                issues.add(issue); break

    # Conflict cleanup: Accurate vs Misleading
    if "Accurate description" in issues and "Misleading description" in issues:
        if re.search(r"\bmisleading\b|\bnot as described\b|\bdescription (?:not|isn't|isn’t) accurate\b", t):
            issues.discard("Accurate description")
        else:
            issues.discard("Misleading description")

    # If positive wording is strong, prefer positive product tags
    if any(pw in t for pw in POSITIVE_WORDS):
        issues.add("Good product")

    return sorted(issues)

# zero-shot fallback (multi-label)
zsc = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def ai_fallback(text: str, min_conf=0.70, topk=3) -> list[str]:
    if not text.strip():
        return []
    res = zsc(text, ISSUE_CATEGORIES, multi_label=True)
    labels = []
    for lbl, score in zip(res["labels"], res["scores"]):
        if score >= min_conf:
            labels.append(lbl)
        if len(labels) >= topk:
            break
    return labels

def finalize_issues(text: str, original_rating: str) -> list[str]:
    rb = set(match_issues_rule_based(text, original_rating))
    if not rb:
        ai = set(ai_fallback(text))
    else:
        # Only let AI add *non-contradictory* extras
        ai = set(ai_fallback(text)) - {"Misleading description"} if "Accurate description" in rb else set(ai_fallback(text))
    issues = rb | ai

    # If “Damaged product (severe)” and “Damaged product” both present → keep severe only
    if "Damaged product (severe)" in issues and "Damaged product" in issues:
        issues.discard("Damaged product")

    # Re-run description conflict in case AI added the other side
    if "Accurate description" in issues and "Misleading description" in issues:
        t = text.lower()
        if re.search(r"\bmisleading\b|\bnot as described\b", t):
            issues.discard("Accurate description")
        else:
            issues.discard("Misleading description")

    return sorted(issues)

def override_sentiment(comment: str, issues: list[str], rating_type: str) -> str:
    t = comment.lower()
    has_hard_neg = any(i in HARD_NEGATIVE_ISSUES for i in issues)
    has_pos_issue = any(i in POSITIVE_ISSUES for i in issues)
    has_pos_words = any(pw in t for pw in POSITIVE_WORDS)

    # Late delivery alone shouldn't flip a positive rating
    only_late = issues == ["Late delivery"] or set(issues) == {"Late delivery"}

    # If rating is positive and there’s no hard negative → POSITIVE
    if rating_type.lower() == "positive" and not has_hard_neg:
        return "POSITIVE"

    # Strong positive wording + no hard negative → POSITIVE
    if has_pos_words and not has_hard_neg:
        return "POSITIVE"

    # Late delivery alone → keep original (often Positive/Neutral)
    if only_late and rating_type.lower() != "negative":
        return rating_type.upper()

    # Any hard negative → NEGATIVE
    if has_hard_neg:
        return "NEGATIVE"

    # Otherwise lean on original rating or positive issues
    if has_pos_issue and rating_type.lower() != "negative":
        return "POSITIVE"

    return rating_type.upper()

# ========= Apply =========
def apply_row(row):
    comment = (row["comment"] or "").strip()
    rating = (row["rating_type"] or "").strip()
    if not comment:
        return pd.Series([[], rating.upper() or "NEUTRAL"])
    issues = finalize_issues(comment, rating)
    sentiment = override_sentiment(comment, issues, rating)
    return pd.Series([issues, sentiment])

df[["issues", "final_sentiment"]] = df.apply(apply_row, axis=1)

# ========= Output =========
summary = (
    df.explode("issues")
      .groupby(["issues","final_sentiment"])
      .size()
      .reset_index(name="count")
      .sort_values("count", ascending=False)
)

print("📊 Issue Sentiment Summary:")
print(summary)

print("\n🚨 All NEGATIVE Reviews:")
neg = df[df["final_sentiment"]=="NEGATIVE"].copy()
neg["issues"] = neg["issues"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
print(neg[["comment","issues"]].to_string(index=False))

out_path = os.path.abspath("negative_reviews.csv")
neg.to_csv(out_path, index=False)
print(f"\n💾 Negative reviews exported to {out_path}")
