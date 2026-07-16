# PD14 대뇌피질 마이크로회로 — 축소 재구현

Potjans & Diesmann (2014)의 대뇌피질 마이크로회로 모델(PD14)의 핵심 구조를
파이썬(NumPy)만으로 축소 재구현한 학습용 코드.

⚠️ 원 논문의 정확한 발표 수치(뉴런 수·연결확률·가중치)가 아니라, 논문이
설명하는 정성적 구조(8개 세포군, L4 중심 입력, 층간 피드포워드/피드백,
E:I ≈ 4:1)를 본떠 만든 예시값입니다. 실제 재현이 아니라 학습·시각화 목적.

## 구성
- 8개 세포군: L2/3, L4, L5, L6 × 흥분성(E)/억제성(I)
- LIF(leaky integrate-and-fire) 뉴런, 오일러법 시뮬레이션
- 세포군별 연결 확률 행렬 + 배경 구동 전류(L4에 더 강한 입력)

## 실행
```bash
pip install numpy pandas matplotlib seaborn
python pd14_microcircuit.py   # ./pd14_plots_out/ 에 PNG 3개 생성
```

출력: 연결확률 히트맵, 스파이크 래스터, 세포군별 평균 발화율.

## 원 논문
Potjans TC, Diesmann M. (2014). *The Cell-Type Specific Cortical Microcircuit:
Relating Structure and Activity in a Full-Scale Spiking Network Model.*
Cerebral Cortex.
