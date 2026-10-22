"""
Baixa o calendário público de contribuições — sem token, sem API GraphQL.
O GitHub serve o mesmo fragmento HTML que a página de perfil usa em
https://github.com/users/<usuario>/contributions

Uso:  python scripts/fetch_contributions.py
      python scripts/fetch_contributions.py --demo   # dados falsos p/ testar offline
Saída: data/contributions.json
"""
import json
import random
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from config import USERNAME

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"


def fetch_days(username: str) -> list[dict]:
    import requests
    from bs4 import BeautifulSoup

    url = f"https://github.com/users/{username}/contributions"
    r = requests.get(url, timeout=30, headers={"User-Agent": "profile-readme-bot"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # contagens ficam nos tooltips: "5 contributions on May 3rd." / "No contributions on ..."
    counts = {}
    for tip in soup.select("tool-tip[for]"):
        m = re.match(r"\s*(No|[\d,]+)\s+contribution", tip.get_text())
        if m:
            counts[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))

    days = []
    for td in soup.select("[data-date]"):
        d = td.get("data-date")
        level = int(td.get("data-level", 0))
        if td.has_attr("data-count"):           # marcação antiga
            count = int(td["data-count"])
        else:
            count = counts.get(td.get("id"), 0 if level == 0 else None)
            if count is None:
                count = level                    # fallback: sem tooltip
        days.append({"date": d, "count": count, "level": level})
    if not days:
        raise SystemExit(f"nenhum dia encontrado em {url} — o usuário '{username}' existe?")
    days.sort(key=lambda x: x["date"])
    return days


def demo_days() -> list[dict]:
    random.seed(7)
    end = date.today()
    start = end - timedelta(days=end.weekday() + 1 + 52 * 7)  # começa num domingo
    days = []
    d = start
    while d <= end:
        busy = 0.55 + 0.35 * (d.weekday() < 5)
        c = 0 if random.random() > busy else int(random.expovariate(1 / 6)) + 1
        days.append({"date": d.isoformat(), "count": c, "level": 0})
        d += timedelta(days=1)
    nz = sorted(x["count"] for x in days if x["count"])
    q = [nz[int(len(nz) * p)] for p in (0.25, 0.5, 0.75)]
    for x in days:
        c = x["count"]
        x["level"] = 0 if c == 0 else 1 + sum(c > t for t in q)
    return days


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    # sequência atual: termina hoje, ou ontem se hoje ainda está zerado
    current = 0
    tail = days[::-1]
    if tail and tail[0]["count"] == 0:
        tail = tail[1:]
    for d in tail:
        if not d["count"]:
            break
        current += 1
    best = max(days, key=lambda d: d["count"])
    months = defaultdict(int)
    for d in days:
        months[d["date"][:7]] += d["count"]
    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": dict(sorted(months.items())),
    }


def main():
    demo = "--demo" in sys.argv
    days = demo_days() if demo else fetch_days(USERNAME)
    data = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "demo": demo,
        "stats": stats(days),
        "days": days,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    s = data["stats"]
    print(f"salvo: {OUT} — {len(days)} dias, {s['total']} contribuições, sequência atual {s['current_streak']}")


if __name__ == "__main__":
    main()
