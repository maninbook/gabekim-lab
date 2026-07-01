#!/usr/bin/env python3
"""정신물리학 개념 그래프 (직접 수정·실행용).

각 함수가 그래프 하나를 그려 PNG로 저장합니다. 공식은 교과서 정의를 그대로 사용:
- 페흐너 법칙:   S = k · ln(I / I0)
- 베버의 법칙:   ΔI = c · I          (베버 비율 c 일정)
- 심리측정함수:  P(x) = γ + (1-γ)·Φ((x-μ)/σ),  2AFC면 γ=0.5 → 역치(μ)에서 75%
- 스테어케이스:  2-down / 1-up 적응법 (~70.7% 지점으로 수렴)

실행:  python notebooks/psychophysics_plots.py
필요:  numpy, matplotlib, seaborn  (.venv에 이미 설치됨)
"""
from __future__ import annotations
import math
from pathlib import Path

import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

OUTDIR = Path(__file__).parent / "psychophysics_plots_out"
PAL = sns.color_palette("Set2")


def style() -> None:
    sns.set_theme(style="white", font="AppleGothic")
    mpl.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 140, "savefig.bbox": "tight",
        "axes.unicode_minus": False,
        "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlepad": 20,
        "axes.labelsize": 11, "axes.labelcolor": "#374151",
        "axes.edgecolor": "#e5e7eb",
        "xtick.color": "#6b7280", "ytick.color": "#6b7280",
        "font.size": 11, "legend.frameon": False,
    })


def _finish(ax, title, sub=None, grid="y"):
    ax.set_title(title, loc="left")
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9.5,
                color="#6b7280", va="bottom")
    ax.grid(axis=grid, color="#eef1f5", lw=1)
    ax.set_axisbelow(True)
    sns.despine(ax=ax)


# 정규분포 누적함수 Φ (scipy 없이)
def Phi(z):
    return 0.5 * (1 + np.vectorize(math.erf)(z / np.sqrt(2)))


def fechner_weber(save=True):
    """페흐너 로그 인코딩 + 베버의 법칙 (2패널)."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4))

    I = np.linspace(1, 100, 200)      # 물리 자극 세기 (I0 = 1)
    a1.plot(I, np.log(I), color=PAL[0], lw=2.6)
    a1.set_xlabel("물리 자극 세기 I")
    a1.set_ylabel("지각 신호 S = ln(I)")
    _finish(a1, "페흐너 법칙 (로그 인코딩)", "S = k·ln(I / I0)")

    c = 0.1                            # 베버 비율
    base = np.linspace(0, 100, 100)
    a2.plot(base, c * base, color=PAL[1], lw=2.6)
    a2.set_xlabel("기준 자극 세기 I")
    a2.set_ylabel("JND  ΔI")
    _finish(a2, "베버의 법칙", "ΔI = c·I  (c = 0.1)")

    fig.tight_layout()
    return _out(fig, "fechner_weber", save)


def psychometric(n_trials=50, seed=1, save=True):
    """심리측정 함수 (2AFC): P(x) = 0.5 + 0.5·Φ((x-μ)/σ)."""
    mu, sigma = 0.0, 1.0
    x = np.linspace(-3, 3, 200)
    P = 0.5 + 0.5 * Phi((x - mu) / sigma)

    rng = np.random.default_rng(seed)
    xs = np.linspace(-2.5, 2.5, 9)
    ps = 0.5 + 0.5 * Phi((xs - mu) / sigma)
    obs = rng.binomial(n_trials, ps) / n_trials   # 시행수 ↑ → 노이즈 ↓

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(x, P, color=PAL[0], lw=2.6, label="P(x) = 0.5 + 0.5·Φ((x-μ)/σ)")
    ax.scatter(xs, obs, color=PAL[2], s=55, zorder=5,
               edgecolor="white", linewidth=0.8, label=f"관측 ({n_trials}시행/점)")
    ax.axhline(0.75, color="#9ca3af", ls="--", lw=1)
    ax.axvline(mu, color="#9ca3af", ls="--", lw=1)
    ax.text(-2.9, 0.77, "역치(75%)", fontsize=9, color="#6b7280")
    ax.set_ylim(0.45, 1.02)
    ax.set_xlabel("자극 강도 x")
    ax.set_ylabel("정답률 P(correct)")
    ax.legend(loc="lower right")
    _finish(ax, "심리측정 함수 (2AFC)", "곡선 기울기 = 민감도")
    fig.tight_layout()
    return _out(fig, "psychometric", save)


def staircase(n=45, step=0.35, seed=7, save=True):
    """2-down / 1-up 스테어케이스: 역치로 수렴."""
    mu, sigma = 0.0, 1.0

    def p_correct(v):
        return 0.5 + 0.5 * float(Phi(np.array((v - mu) / sigma)))

    rng = np.random.default_rng(seed)
    v, streak, prev_dir = 2.6, 0, 0
    traj, revs = [], []
    for t in range(n):
        traj.append(v)
        hit = rng.random() < p_correct(v)
        d = 0
        if hit:
            streak += 1
            if streak >= 2:      # 2연속 정답 → 어렵게(강도↓)
                v -= step; streak = 0; d = -1
        else:                    # 오답 → 쉽게(강도↑)
            v += step; streak = 0; d = 1
        if d != 0 and prev_dir != 0 and d != prev_dir:
            revs.append(t)
        if d != 0:
            prev_dir = d
        v = max(v, -1.2)

    traj = np.array(traj)
    thr = traj[revs[2:]].mean() if len(revs) > 3 else traj[-10:].mean()

    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(range(len(traj)), traj, color=PAL[0], lw=1.8, marker="o", ms=4)
    ax.scatter(revs, traj[revs], color=PAL[1], s=60, zorder=5, label="반전(reversal)")
    ax.axhline(thr, color="#9ca3af", ls="--", lw=1.2)
    ax.text(len(traj) - 1, thr + 0.08, f"추정 역치 ≈ {thr:.2f}",
            ha="right", fontsize=9, color="#6b7280")
    ax.set_xlabel("시행 번호")
    ax.set_ylabel("자극 강도")
    ax.legend(loc="upper right")
    _finish(ax, "스테어케이스 절차", "정답 시 어렵게 · 오답 시 쉽게")
    fig.tight_layout()
    return _out(fig, "staircase", save)


def cones_schematic(save=True):
    """[개략도 — 정확한 스펙트럼 아님] S/M/L 원추세포 민감도.
    실제 원추 감도는 비대칭이라, 정확성이 필요하면 실측 원추 fundamentals
    (예: Stockman & Sharpe)을 CSV로 불러와 그리는 것을 권장.
    """
    wl = np.linspace(380, 700, 320)

    def g(mu, sd):
        return np.exp(-0.5 * ((wl - mu) / sd) ** 2)

    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    for mu, sd, col, lab in [(420, 28, "#3b6fd6", "S"),
                             (534, 38, "#3aa856", "M"),
                             (564, 42, "#d6453b", "L")]:
        ax.plot(wl, g(mu, sd), color=col, lw=2.3, label=lab)
        ax.fill_between(wl, g(mu, sd), color=col, alpha=0.12)
    ax.set_xlabel("파장 (nm)")
    ax.set_ylabel("상대 민감도")
    ax.set_yticks([])
    ax.legend(loc="upper right")
    _finish(ax, "원추세포 S/M/L 민감도 (개략도)", "※ 대칭 가우시안 근사 — 정확한 스펙트럼 아님")
    fig.tight_layout()
    return _out(fig, "cones_schematic", save)


def _out(fig, name, save):
    if save:
        OUTDIR.mkdir(exist_ok=True)
        path = OUTDIR / f"{name}.png"
        fig.savefig(path)
        print(f"저장: {path}")
        plt.close(fig)
        return path
    return fig


if __name__ == "__main__":
    style()
    fechner_weber()
    psychometric()
    staircase()
    # cones_schematic()  # 필요 시 주석 해제 (개략도)
    print("완료. PNG는", OUTDIR, "에 있습니다.")
