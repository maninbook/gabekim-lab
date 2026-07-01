#!/usr/bin/env python3
"""FBref 한국 대표팀 Scores & Fixtures(수동 수집)를 정리해 korea_matches.csv 생성.

출처: FBref Korea Republic (squad 473f0fbf)
- 벤투: 2022 시즌 페이지(2022 월드컵 사이클, 2019-09 ~ 2022-12)
- 홍명보 2기: 2026 시즌 페이지에서 2024-09 이후만 (이전은 클린스만/임시감독 → 제외)

컬럼: date, coach, comp, venue, gf, ga, result, opponent, poss, formation
poss(점유율)는 FBref가 일부 경기만 제공 → 없으면 None.
"""
import csv
from pathlib import Path

# (date, comp, venue, gf, ga, opponent, poss, formation)
# comp: WCQ | Friendly | WorldCup
bento = [
    ("2019-09-10", "WCQ", "Away", 2, 0, "Turkmenistan", None, "4-1-4-1"),
    ("2019-10-10", "WCQ", "Home", 8, 0, "Sri Lanka", None, "4-1-4-1"),
    ("2019-10-15", "WCQ", "Away", 0, 0, "Korea DPR", None, "4-1-3-2"),
    ("2019-11-14", "WCQ", "Away", 0, 0, "Lebanon", None, "4-2-2-2"),
    ("2021-06-05", "WCQ", "Home", 5, 0, "Turkmenistan", None, "3-4-3"),
    ("2021-06-09", "WCQ", "Away", 5, 0, "Sri Lanka", None, "4-1-4-1"),
    ("2021-06-13", "WCQ", "Home", 2, 1, "Lebanon", None, "4-2-3-1"),
    ("2021-09-02", "WCQ", "Home", 0, 0, "Iraq", None, "4-1-4-1"),
    ("2021-09-07", "WCQ", "Home", 1, 0, "Lebanon", None, "4-1-4-1"),
    ("2021-10-07", "WCQ", "Home", 2, 1, "Syria", None, "4-2-3-1"),
    ("2021-10-12", "WCQ", "Away", 1, 1, "IR Iran", None, "4-1-4-1"),
    ("2021-11-11", "WCQ", "Home", 1, 0, "UAE", None, "4-1-4-1"),
    ("2021-11-16", "WCQ", "Away", 3, 0, "Iraq", None, "4-2-3-1"),
    ("2022-01-15", "Friendly", "Neutral", 5, 1, "Iceland", None, "4-2-3-1"),
    ("2022-01-21", "Friendly", "Neutral", 4, 0, "Moldova", None, "4-2-3-1"),
    ("2022-01-27", "WCQ", "Away", 1, 0, "Lebanon", None, "4-1-3-2"),
    ("2022-02-01", "WCQ", "Neutral", 2, 0, "Syria", None, "4-1-3-2"),
    ("2022-03-24", "WCQ", "Home", 2, 0, "IR Iran", None, "4-1-4-1"),
    ("2022-03-29", "WCQ", "Away", 0, 1, "UAE", None, "4-1-3-2"),
    ("2022-06-02", "Friendly", "Neutral", 1, 5, "Brazil", None, "4-1-4-1"),
    ("2022-06-06", "Friendly", "Neutral", 2, 0, "Chile", None, "4-4-1-1"),
    ("2022-06-10", "Friendly", "Neutral", 2, 2, "Paraguay", None, "4-1-4-1"),
    ("2022-06-14", "Friendly", "Neutral", 4, 1, "Egypt", None, "4-1-4-1"),
    ("2022-09-23", "Friendly", "Neutral", 2, 2, "Costa Rica", None, "4-1-4-1"),
    ("2022-09-27", "Friendly", "Neutral", 1, 0, "Cameroon", None, "4-4-1-1"),
    ("2022-11-11", "Friendly", "Neutral", 1, 0, "Iceland", None, "4-2-2-2"),
    ("2022-11-24", "WorldCup", "Neutral", 0, 0, "Uruguay", 44, "4-2-3-1"),
    ("2022-11-28", "WorldCup", "Neutral", 2, 3, "Ghana", 63, "4-2-3-1"),
    ("2022-12-02", "WorldCup", "Neutral", 2, 1, "Portugal", 39, "4-1-4-1"),
    ("2022-12-05", "WorldCup", "Neutral", 1, 4, "Brazil", 47, "4-2-2-2"),
]

# 홍명보 2기: 2024-09 이후만 (그 이전 2026페이지 경기는 클린스만/임시 → 제외)
hong = [
    ("2024-09-05", "WCQ", "Home", 0, 0, "Palestine", 75, "4-2-3-1"),
    ("2024-09-10", "WCQ", "Away", 3, 1, "Oman", 66, "4-2-3-1"),
    ("2024-10-10", "WCQ", "Away", 2, 0, "Jordan", 75, "4-2-3-1"),
    ("2024-10-15", "WCQ", "Home", 3, 2, "Iraq", 76, "4-2-3-1"),
    ("2024-11-14", "WCQ", "Away", 3, 1, "Kuwait", 75, "4-2-3-1"),
    ("2024-11-19", "WCQ", "Neutral", 1, 1, "Palestine", 74, "4-2-3-1"),
    ("2025-03-20", "WCQ", "Home", 1, 1, "Oman", 63, "4-2-3-1"),
    ("2025-03-25", "WCQ", "Home", 1, 1, "Jordan", 75, "4-2-3-1"),
    ("2025-06-05", "WCQ", "Away", 2, 0, "Iraq", 76, "4-2-3-1"),
    ("2025-06-10", "WCQ", "Home", 4, 0, "Kuwait", 74, "4-2-3-1"),
    ("2026-03-28", "Friendly", "Neutral", 0, 4, "Cote d'Ivoire", None, "3-4-3"),
    ("2026-03-31", "Friendly", "Away", 0, 1, "Austria", None, "3-4-3"),
    ("2026-05-30", "Friendly", "Neutral", 5, 0, "Trinidad & Tobago", None, "3-4-3"),
    ("2026-06-03", "Friendly", "Neutral", 1, 0, "El Salvador", None, "3-4-3"),
    ("2026-06-11", "WorldCup", "Neutral", 2, 1, "Czechia", 62, "3-4-3"),
    ("2026-06-18", "WorldCup", "Neutral", 0, 1, "Mexico", 58, "3-4-3"),
    ("2026-06-24", "WorldCup", "Neutral", 0, 1, "South Africa", 69, "3-4-3"),
]


def result(gf, ga):
    return "W" if gf > ga else ("D" if gf == ga else "L")


def main():
    out = Path(__file__).parent / "korea_matches.csv"
    rows = []
    for coach, data in (("Bento", bento), ("Hong", hong)):
        for date, comp, venue, gf, ga, opp, poss, form in data:
            rows.append({
                "date": date, "coach": coach, "comp": comp, "venue": venue,
                "gf": gf, "ga": ga, "result": result(gf, ga),
                "opponent": opp, "poss": poss if poss is not None else "",
                "formation": form,
            })
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"저장: {out}  (총 {len(rows)}경기: 벤투 {len(bento)}, 홍명보 {len(hong)})")


if __name__ == "__main__":
    main()
