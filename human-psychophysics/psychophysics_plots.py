#!/usr/bin/env python3
"""정신물리학 개념 그래프 — seaborn 기반, 공식을 그림에 명시.

공식(교과서 정의):
  · 베버의 법칙 :  ΔI = c · I                     (Weber 비율 c 일정)
  · 페흐너 법칙 :  S  = k · ln(I / I0)            (베버 법칙을 적분 → 로그 인코딩)
  · 심리측정함수:  P(x) = γ + (1−γ)·Φ((x−μ)/σ),  2AFC면 γ=0.5 → 역치(μ)에서 75%
  · 스테어케이스:  2-down / 1-up 적응법           (≈70.7% 지점으로 수렴)

수식은 matplotlib mathtext($…$)로 그려 한글 폰트와 무관하게 깨지지 않음.

실행:  python psychophysics_plots.py      →  ./psychophysics_plots_out/*.png
필요:  numpy pandas matplotlib seaborn
"""
from __future__ import annotations
import math
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

OUTDIR = Path(__file__).parent / "psychophysics_plots_out"
PALETTE = "colorblind"          # seaborn 팔레트


def setup() -> None:
    sns.set_theme(style="whitegrid", context="notebook",
                  font="AppleGothic", palette=PALETTE)
    mpl.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 140, "savefig.bbox": "tight",
        "axes.unicode_minus": False,
        "axes.titlesize": 15, "axes.titleweight": "bold", "axes.titlepad": 14,
        "axes.labelsize": 12, "mathtext.fontset": "cm",
    })


def Phi(z):
    """표준정규 누적분포함수 Φ (scipy 없이)."""
    z = np.asarray(z, dtype=float)
    return 0.5 * (1.0 + np.vectorize(math.erf)(z / np.sqrt(2.0)))


def _formula(ax, text, xy=(0.04, 0.9)):
    """공식을 축 좌상단에 박스로 표기."""
    ax.text(*xy, text, transform=ax.transAxes, fontsize=15, va="top",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#d1d5db"))


def _save(fig, name):
    OUTDIR.mkdir(exist_ok=True)
    path = OUTDIR / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    print(f"저장: {path}")
    return path


# ── 1. 베버의 법칙 + 페흐너 법칙 ──────────────────────────────
def weber_fechner():
    c, k, I0 = 0.15, 1.0, 1.0
    pal = sns.color_palette(PALETTE)
    I = np.linspace(1, 100, 400)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.6))

    # (A) 베버: JND = c·I  — 기준이 커질수록 JND도 커짐
    sns.lineplot(data=pd.DataFrame({"I": I, "JND": c * I}),
                 x="I", y="JND", ax=a1, color=pal[0], lw=2.8)
    for Ib in (20, 70):                       # 두 기준점의 JND 크기 비교
        a1.vlines(Ib, 0, c * Ib, color=pal[3], lw=2)
        a1.scatter([Ib], [c * Ib], color=pal[3], s=55, zorder=5)
        a1.annotate(f"기준 {Ib} → JND {c*Ib:.1f}", (Ib, c * Ib),
                    textcoords="offset points", xytext=(8, 10),
                    ha="left", fontsize=10, color="#4b5563")
    a1.set_xlabel("기준 자극 세기  I"); a1.set_ylabel("JND  ΔI")
    a1.set_title("베버의 법칙", loc="left")
    _formula(a1, r"$\Delta I = c\,I$")

    # (B) 페흐너: S = k·ln(I/I0) — 자극이 2배씩 커질 때 지각은 '일정량'씩 증가
    sns.lineplot(data=pd.DataFrame({"I": I, "S": k * np.log(I / I0)}),
                 x="I", y="S", ax=a2, color=pal[0], lw=2.8)
    doubles = I0 * 2.0 ** np.arange(1, 7)     # 2,4,8,16,32,64 (등비)
    Sd = k * np.log(doubles / I0)
    a2.scatter(doubles, Sd, color=pal[1], s=55, zorder=5)
    for xi, yi in zip(doubles, Sd):
        a2.hlines(yi, 0, xi, color=pal[1], lw=1, ls=":", alpha=0.6)
    a2.set_xlabel("물리 자극 세기  I"); a2.set_ylabel("지각 신호  S")
    a2.set_title("페흐너 법칙 (로그 인코딩)", loc="left")
    a2.text(0.97, 0.30, "자극이 2배씩 늘 때\n지각은 일정량씩만 증가",
            transform=a2.transAxes, ha="right", fontsize=10, color="#4b5563")
    _formula(a2, r"$S = k\,\ln(I/I_0)$")

    fig.tight_layout()
    return _save(fig, "weber_fechner")


# ── 2. 심리측정 함수 (2AFC) ──────────────────────────────────
def psychometric(n_trials=40, seed=1):
    mu, sigma = 0.0, 1.0
    pal = sns.color_palette(PALETTE)

    x = np.linspace(-3, 3, 400)
    curve = pd.DataFrame({"x": x, "P": 0.5 + 0.5 * Phi((x - mu) / sigma)})

    rng = np.random.default_rng(seed)
    xs = np.linspace(-2.4, 2.4, 9)
    p_true = 0.5 + 0.5 * Phi((xs - mu) / sigma)
    data = pd.DataFrame({"x": xs, "P": rng.binomial(n_trials, p_true) / n_trials})

    fig, ax = plt.subplots(figsize=(8.4, 5))
    sns.lineplot(data=curve, x="x", y="P", ax=ax, color=pal[0], lw=2.8,
                 label="심리측정 곡선 (누적 정규)")
    sns.scatterplot(data=data, x="x", y="P", ax=ax, color=pal[1], s=90,
                    edgecolor="white", linewidth=1, zorder=5,
                    label=f"관측 정답률 ({n_trials}회/점)")

    ax.axhline(0.75, color="#9ca3af", ls="--", lw=1)
    ax.axhline(0.5, color="#d1d5db", ls=":", lw=1)
    ax.axvline(mu, color="#9ca3af", ls="--", lw=1)
    ax.annotate("역치 (75%) = PSE, x=μ", (mu, 0.75), textcoords="offset points",
                xytext=(12, -4), fontsize=10, color="#4b5563")
    ax.annotate("우연 수준 0.5", (-2.9, 0.5), textcoords="offset points",
                xytext=(0, 6), fontsize=9, color="#9ca3af")
    # 민감도: 곡선이 가파를수록(σ 작을수록) 민감
    ax.annotate("", (mu + sigma, 0.5 + 0.5 * float(Phi(1))), (mu, 0.75),
                arrowprops=dict(arrowstyle="<->", color=pal[3], lw=1.5))
    ax.text(mu + sigma * 0.55, 0.70, "기울기 ∝ 민감도\n(σ 작을수록 가파름)",
            fontsize=10, color=pal[3])

    ax.set_ylim(0.42, 1.02)
    ax.set_xlabel("자극 강도  x"); ax.set_ylabel("정답률  P(correct)")
    ax.set_title("심리측정 함수 (2AFC)", loc="left")
    ax.legend(loc="lower right", frameon=False)
    _formula(ax, r"$P(x)=0.5+0.5\,\Phi\!\left(\frac{x-\mu}{\sigma}\right)$",
             xy=(0.04, 0.97))

    fig.tight_layout()
    return _save(fig, "psychometric")


# ── 3. 스테어케이스 (2-down / 1-up) ──────────────────────────
def staircase(n=45, step=0.35, seed=7):
    mu, sigma = 0.0, 1.0
    pal = sns.color_palette(PALETTE)

    def p_correct(v):
        return float(0.5 + 0.5 * Phi((v - mu) / sigma))

    rng = np.random.default_rng(seed)
    v, streak, prev = 2.6, 0, 0
    traj, revs = [], []
    for t in range(n):
        traj.append(v)
        hit = rng.random() < p_correct(v)
        d = 0
        if hit:
            streak += 1
            if streak >= 2:           # 2연속 정답 → 어렵게(강도↓)
                v -= step; streak = 0; d = -1
        else:                          # 오답 → 쉽게(강도↑)
            v += step; streak = 0; d = 1
        if d and prev and d != prev:
            revs.append(t)
        if d:
            prev = d
        v = max(v, -1.2)

    df = pd.DataFrame({"trial": range(len(traj)), "intensity": traj})
    thr = (df.loc[revs[2:], "intensity"].mean()
           if len(revs) > 3 else df["intensity"].tail(10).mean())

    fig, ax = plt.subplots(figsize=(9, 4.4))
    sns.lineplot(data=df, x="trial", y="intensity", ax=ax,
                 color=pal[0], lw=1.8, marker="o", markersize=6)
    sns.scatterplot(x=list(revs), y=df.loc[revs, "intensity"].tolist(), ax=ax,
                    color=pal[1], s=90, zorder=5, label="반전(reversal)")
    ax.axhline(thr, color="#9ca3af", ls="--", lw=1.4)
    ax.text(len(traj) - 1, thr + 0.09, f"추정 역치 ≈ {thr:.2f}",
            ha="right", fontsize=11, color="#4b5563")
    ax.set_xlabel("시행 번호"); ax.set_ylabel("자극 강도")
    ax.set_title("스테어케이스 (2-down / 1-up)", loc="left")
    ax.legend(loc="upper right", frameon=False)
    _formula(ax, "정답 2연속 → 강도↓\n오답 1회 → 강도↑", xy=(0.63, 0.42))

    fig.tight_layout()
    return _save(fig, "staircase")


if __name__ == "__main__":
    setup()
    weber_fechner()
    psychometric()
    staircase()
    print("완료. PNG:", OUTDIR)
