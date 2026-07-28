# C++ 스터디 02 — 변수, 자료형, sizeof, 형변환, 스코프

홍정모 교수님의 [코테용 C++ 핵심 정리 무료 강의](https://www.youtube.com/watch?v=UqCZda8DLGc)를 따라 공부한 두 번째 실습 코드.

- 정적 타입과 변수-메모리 관계
- `sizeof`(값이 아니라 타입의 고정 크기)
- `float`/`double`, `char`/문자열 배열 구분
- 형변환(narrowing conversion) — 반올림이 아니라 0 방향 버림(truncation)
- 기본 연산자, `bool`의 `boolalpha` 스트림 포맷
- 블록 스코프와 섀도잉(shadowing)

원본 실습 코드의 주석 그대로 남겨뒀고(궁금했던 점 표시 포함), 다음 두 가지는 직접 컴파일해서 확인한 뒤 블로그 글에서 바로잡았다:

- `i = 986.654;` → **986** (987 아님 — truncation은 반올림이 아니라 버림)
- `sizeof(f)`를 두 번째 줄에서 복붙 실수로 그대로 씀 — `sizeof(d)`는 8바이트(4바이트 아님)

## 실행
```bash
clang++ -std=c++17 main.cpp -o main && ./main
```

정리 글: [GabeKim 블로그 — C++ 스터디 02](https://gabekim.vercel.app/blog/study_c_plus_plus_02)
