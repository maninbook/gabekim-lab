# 인간 정신물리학 — 개념 그래프 코드

정신물리학 핵심 개념을 그리는 파이썬 스크립트. 교과서 정의를 그대로 사용:

- 페흐너 법칙:  S = k·ln(I / I0)
- 베버의 법칙:  ΔI = c·I  (베버 비율 c 일정)
- 심리측정함수(2AFC):  P(x) = 0.5 + 0.5·Φ((x−μ)/σ) — 역치(μ)에서 75%
- 스테어케이스:  2-down / 1-up 적응법

## 실행
```bash
pip install numpy matplotlib seaborn
python psychophysics_plots.py   # ./psychophysics_plots_out/ 에 PNG 생성
```

`cones_schematic()`(원추세포 S/M/L)는 대칭 가우시안 **개략도**라 기본 비활성.
