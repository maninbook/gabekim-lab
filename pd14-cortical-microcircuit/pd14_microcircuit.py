#!/usr/bin/env python3
"""PD14(Potjans & Diesmann, 2014) 대뇌피질 마이크로회로 모델 — 축소·설명용 재구현.

원 논문(Potjans TC, Diesmann M. "The Cell-Type Specific Cortical Microcircuit:
Relating Structure and Activity in a Full-Scale Spiking Network Model." Cerebral
Cortex, 2014)은 1mm² 감각피질 조각을 뉴런 약 7만7천 개·시냅스 약 3억 개로
재현하는 스파이킹 신경망 모델이다.

이 스크립트는 그 모델의 **핵심 아이디어**(층별 8개 세포군, 층내·층간
연결 구조, LIF 뉴런, 외부 입력)를 노트북/랩톱에서 몇 초 안에 돌아가도록
크게 축소해 재구현한 것이다.

⚠️ 중요: 여기 쓰인 뉴런 수·연결 확률·가중치는 원 논문의 정확한 발표
수치가 아니라, 논문이 설명하는 정성적 구조(L4가 주 입력층, L2/3→L5
피드포워드, L6→L4 피드백, E:I ≈ 4:1 등)를 본떠 만든 **예시값**이다.
정확한 재현이 아니라 "왜 이런 구조를 만들면 이런 활동 패턴이 나오는가"를
직접 눈으로 확인해보기 위한 학습용 축소 모델임을 밝혀둔다.

필요: numpy, pandas, matplotlib, seaborn
실행: python pd14_microcircuit.py   ->  ./pd14_plots_out/*.png
"""
from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

OUTDIR = Path(__file__).parent / "pd14_plots_out"

# ── 8개 세포군: 층(L2/3, L4, L5, L6) × 흥분성/억제성(E/I) ──────────
POPULATIONS = ["L23E", "L23I", "L4E", "L4I", "L5E", "L5I", "L6E", "L6I"]

# 세포군별 뉴런 수 (예시 비율 — 실제 논문 값이 아님).
# L2/3·L4가 가장 크고, E:I ≈ 4:1 — 실제 피질의 대략적 특징을 반영한 근사치.
SIZES = {
    "L23E": 400, "L23I": 100,
    "L4E": 400, "L4I": 100,
    "L5E": 200, "L5I": 50,
    "L6E": 200, "L6I": 50,
}

rng = np.random.default_rng(42)


def build_network():
    """뉴런 인덱스, 세포군 라벨 배열, 연결 확률 행렬(8×8)을 만든다."""
    n_total = sum(SIZES.values())
    pop_of = np.empty(n_total, dtype=object)
    offsets = {}
    idx = 0
    for p in POPULATIONS:
        offsets[p] = (idx, idx + SIZES[p])
        pop_of[idx: idx + SIZES[p]] = p
        idx += SIZES[p]

    # 연결 확률 행렬 P[source][target] — 예시값.
    # 대각(층내 재귀연결)은 높고, 특정 층간 경로(L4E→L23E 피드포워드,
    # L23E→L5E, L6E→L4E 피드백)만 의도적으로 강조했다.
    P = pd.DataFrame(0.01, index=POPULATIONS, columns=POPULATIONS)
    for p in POPULATIONS:
        P.loc[p, p] = 0.15  # 층내 재귀연결
    # 같은 층 내 E<->I 상호연결도 강하게
    for layer in ["L23", "L4", "L5", "L6"]:
        e, i = f"{layer}E", f"{layer}I"
        P.loc[e, i] = P.loc[i, e] = P.loc[i, i] = 0.15
    # 정성적으로 알려진 층간 경로 (예시 강도)
    P.loc["L4E", "L23E"] = 0.15   # L4 -> L2/3 피드포워드 (주 입력 경로)
    P.loc["L4E", "L23I"] = 0.10
    P.loc["L23E", "L5E"] = 0.10   # L2/3 -> L5 피드포워드
    P.loc["L6E", "L4E"] = 0.05    # L6 -> L4 피드백
    P.loc["L5E", "L6E"] = 0.05    # L5 -> L6

    return n_total, pop_of, offsets, P


def connectivity_matrix(n_total, pop_of, offsets, P):
    """뉴런×뉴런 가중치 행렬(부호 포함) 생성. 억제성 시냅스는 흥분성보다
    g배 강하게 — 균형 흥분-억제 네트워크에서 흔히 쓰는 관례."""
    J_exc = 0.15   # 흥분성 시냅스 가중치 (mV, 편의상 임의 단위)
    g = 4.0        # 억제:흥분 강도 비율
    W = np.zeros((n_total, n_total), dtype=np.float32)
    for src in POPULATIONS:
        s0, s1 = offsets[src]
        weight = -g * J_exc if src.endswith("I") else J_exc
        for tgt in POPULATIONS:
            p = P.loc[src, tgt]
            if p <= 0:
                continue
            t0, t1 = offsets[tgt]
            n_src, n_tgt = s1 - s0, t1 - t0
            mask = rng.random((n_src, n_tgt)) < p
            W[s0:s1, t0:t1] += mask * weight
    return W


def simulate(n_total, pop_of, W, T_ms=500.0, dt=0.1, seed=1):
    """LIF(leaky integrate-and-fire) 뉴런 네트워크를 오일러법으로 시뮬레이션."""
    r = np.random.default_rng(seed)
    n_steps = int(T_ms / dt)

    V_rest, V_reset, V_th = -65.0, -65.0, -50.0
    tau_m, tau_ref = 10.0, 2.0

    # 외부(배경) 입력: L4는 주 입력층이라 더 강한 구동 전류를 준다.
    # (단일 뉴런 기준 사전 튜닝: 비L4 mu=3.5 -> 약 4Hz, L4 mu=5.0 -> 약 8Hz)
    mu_ext = np.where(np.char.startswith(pop_of.astype(str), "L4"), 5.0, 3.5)
    sigma_ext = 2.2

    V = np.full(n_total, V_rest, dtype=np.float32)
    refractory = np.zeros(n_total, dtype=np.float32)
    spikes_prev = np.zeros(n_total, dtype=np.float32)

    spike_times, spike_ids = [], []

    for step in range(n_steps):
        t = step * dt
        syn_input = spikes_prev @ W  # (n_total,) 이전 스텝 스파이크가 만드는 시냅스 전류

        noise = r.normal(0, sigma_ext, n_total) * np.sqrt(dt)
        dV = (-(V - V_rest) + mu_ext + syn_input) / tau_m * dt + noise
        active = refractory <= 0
        V[active] += dV[active]
        refractory[~active] -= dt

        fired = active & (V >= V_th)
        if fired.any():
            ids = np.nonzero(fired)[0]
            spike_times.extend([t] * len(ids))
            spike_ids.extend(ids.tolist())
            V[fired] = V_reset
            refractory[fired] = tau_ref

        spikes_prev = fired.astype(np.float32)

    return pd.DataFrame({"t": spike_times, "neuron": spike_ids}), n_steps * dt


def style():
    sns.set_theme(style="white", font="AppleGothic")
    mpl.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 140, "savefig.bbox": "tight",
        "axes.unicode_minus": False,
        "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlepad": 14,
        "axes.labelsize": 11, "font.size": 10.5,
    })


def plot_raster(spikes, pop_of, offsets, save=True):
    fig, ax = plt.subplots(figsize=(9, 5))
    palette = sns.color_palette("husl", len(POPULATIONS))
    for color, pop in zip(palette, POPULATIONS):
        s0, s1 = offsets[pop]
        sub = spikes[(spikes.neuron >= s0) & (spikes.neuron < s1)]
        ax.scatter(sub.t, sub.neuron, s=2, color=color, label=pop, alpha=0.7)
    for pop in POPULATIONS:
        s0, _ = offsets[pop]
        ax.axhline(s0, color="#e5e7eb", lw=0.8, zorder=0)
    ax.set_xlabel("시간 (ms)")
    ax.set_ylabel("뉴런 번호 (세포군별)")
    ax.set_title("PD14 축소 모델 — 스파이크 래스터", loc="left")
    ax.legend(loc="upper right", markerscale=4, fontsize=8, ncol=2, frameon=False)
    sns.despine(ax=ax)
    plt.tight_layout()
    return _save(fig, "raster", save)


def plot_firing_rates(spikes, pop_of, offsets, T_ms, save=True):
    rates = []
    for pop in POPULATIONS:
        s0, s1 = offsets[pop]
        n = s1 - s0
        cnt = ((spikes.neuron >= s0) & (spikes.neuron < s1)).sum()
        rates.append(cnt / n / (T_ms / 1000.0))
    df = pd.DataFrame({"population": POPULATIONS, "rate": rates})
    df["layer"] = df.population.str[:-1]
    df["type"] = df.population.str[-1].map({"E": "흥분성", "I": "억제성"})

    fig, ax = plt.subplots(figsize=(7, 4.2))
    sns.barplot(data=df, x="layer", y="rate", hue="type",
                palette={"흥분성": "#2563eb", "억제성": "#ef4444"}, ax=ax)
    ax.set_xlabel(""); ax.set_ylabel("평균 발화율 (Hz)")
    ax.set_title("세포군별 평균 발화율", loc="left")
    ax.legend(title="", loc="upper right", frameon=False)
    sns.despine(ax=ax)
    plt.tight_layout()
    return _save(fig, "firing_rates", save)


def plot_connectivity(P, save=True):
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    hm = sns.heatmap(P.astype(float), annot=True, fmt=".2f", cmap="crest",
                      ax=ax, linewidths=0.5, cbar=True)
    # 세로로 회전된 한글 컬러바 라벨은 깨져 보여서, 가로 제목으로 대체.
    cbar = hm.collections[0].colorbar
    cbar.ax.set_title("연결\n확률", fontsize=10, pad=10)
    ax.set_xlabel("대상 세포군(target)")
    ax.set_ylabel("출발 세포군(source)")
    ax.set_title("세포군 간 연결 확률 (예시값)", loc="left")
    plt.tight_layout()
    return _save(fig, "connectivity", save)


def _save(fig, name, save):
    if save:
        OUTDIR.mkdir(exist_ok=True)
        path = OUTDIR / f"{name}.png"
        fig.savefig(path)
        plt.close(fig)
        print(f"저장: {path}")
        return path
    return fig


if __name__ == "__main__":
    style()
    n_total, pop_of, offsets, P = build_network()
    print(f"뉴런 수: {n_total} (원 논문 축소 버전, 예시 비율)")
    W = connectivity_matrix(n_total, pop_of, offsets, P)
    spikes, T_ms = simulate(n_total, pop_of, W)
    print(f"총 스파이크 수: {len(spikes)}  (시뮬레이션 {T_ms:.0f}ms)")

    plot_connectivity(P)
    plot_raster(spikes, pop_of, offsets)
    plot_firing_rates(spikes, pop_of, offsets, T_ms)
    print("완료. PNG:", OUTDIR)
