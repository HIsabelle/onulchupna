# 오늘춥나?? — 안양대 캠퍼스 체감온도 & 옷차림 추천

2026 안양대학교 AI 경진대회 (AI26-016, 팀 환전)

날씨앱 온도(안양시 동안구 기준)를 **언덕 위 안양대 캠퍼스 체감온도**로 보정하고,
캠퍼스에 머무는 시간대 중 가장 추운 때를 기준으로 **옷차림을 추천**합니다.

## 다운로드하고 실행하기

### 0. 준비물 (처음 한 번)

- **Python 3.9 이상**: [python.org](https://www.python.org/downloads/)에서 설치
  - 설치 첫 화면에서 **"Add python.exe to PATH"를 꼭 체크**하세요.
  - 확인: 터미널(PowerShell)에서 `python --version` 입력 → `Python 3.x.x`가 나오면 OK
- **Git**(선택): [git-scm.com](https://git-scm.com/)
  - Git이 없으면 아래 '방법 B'처럼 ZIP으로 받으면 됩니다.

### 1. 코드 내려받기

**방법 A — Git 사용**
```powershell
git clone https://github.com/HIsabelle/onulchupna.git
cd onulchupna
```

**방법 B — ZIP 다운로드**
1. 깃허브 저장소 페이지에서 초록색 **`<> Code`** 버튼 → **Download ZIP**
2. 압축을 풀고, 풀린 폴더에서 빈 곳을 **우클릭 → "터미널에서 열기"** (또는 VSCode로 폴더를 열고 상단 메뉴 **터미널 → 새 터미널**)

### 2. 필요한 라이브러리 설치 (처음 한 번, 1~3분)

```powershell
pip install -r requirements.txt
```

### 3. AI 모델 학습 (처음 한 번, 약 10초)

```powershell
python train.py
```

`정확도 … 판단 기준 7/10 (70%) → 통과`가 나오면 완료입니다.
모델 파일(`data/outfit_model.joblib`)은 용량이 커서 깃허브에 올리지 않으므로, 받은 컴퓨터마다 한 번씩 실행해야 합니다.

### 4. 실행

```powershell
python server.py
```

`오늘춥나?? → http://localhost:5000`이 나오면 브라우저에서 **http://localhost:5000** 을 여세요.

- **끄기**: 터미널에서 `Ctrl + C`. 실행 중에는 그 터미널 창을 닫지 마세요.
- **다음부터는** 4번(`python server.py`)만 하면 됩니다.

### 자주 나는 문제

| 증상 | 해결 |
|---|---|
| `python`을 찾을 수 없음 | Python 설치 때 PATH 체크를 안 한 경우 → 재설치하며 체크, 또는 `py server.py` |
| `No module named 'flask'` 등 | 2번 `pip install -r requirements.txt`를 다시 실행 |
| `Address already in use` | 이미 서버가 켜져 있음 → 그냥 브라우저에서 열기 |
| 화면이 예전 그대로 | 서버를 껐다 켜고 브라우저에서 `Ctrl + F5` |
| 상단에 "기상청 API 키가 없어…" | 정상 동작입니다(Open-Meteo 사용). 기상청 값을 쓰려면 아래 API 키 설정 |

## 설치 없이 보기 — HTML 버전

파이썬 설치 없이 **`docs/index.html`을 더블클릭**하면 브라우저에서 바로 열립니다.
서버가 없으면 자동으로 '웹 체험판'으로 동작해요.

| 기능 | 서버 버전 (`python server.py`) | HTML 버전 (파일·GitHub Pages) |
|---|---|---|
| 날씨 | 기상청(키 있을 때) → Open-Meteo | Open-Meteo |
| 체감온도 계산 | ✅ | ✅ 같은 계산식 |
| AI 옷차림 모델 | Random Forest 200그루 | Random Forest 30그루 축소판 (정확도 비슷) |
| 쇼핑몰 예시 이미지 | 네이버 API 키 있으면 사진 | 검색 링크만 |
| 학생 체감 제보 | 모두의 제보를 모아 통계·재학습 | 이 기기 브라우저에만 저장 |

**GitHub Pages로 인터넷에 공개하기**: 저장소 Settings → Pages → Branch를 `main`, 폴더를 **`/docs`** 로 저장
→ 1~2분 뒤 `https://hisabelle.github.io/onulchupna/` 에서 누구나 접속 가능

## API 키 설정 (선택)

키가 없어도 실행됩니다. 기상청 실데이터·옷 예시 이미지를 쓰려면:

1. 폴더의 `.env.example`을 복사해 이름을 **`.env`** 로 바꾸기
2. 발급받은 키를 `=` 뒤에 붙여넣기 (예: `KMA_API_KEY=abcd1234...`)
3. 서버를 껐다 다시 켜기

> ⚠️ `.env`에는 비밀 키가 들어 있으므로 깃허브에 올리거나 메신저로 공유하지 마세요. (`.gitignore`로 업로드 제외되어 있음)


| 키 | 용도 | 발급처 | 없으면 |
|---|---|---|---|
| `KMA_API_KEY` | 기상청 단기예보 + 초단기실황 | data.go.kr '기상청_단기예보 조회서비스' (Decoding 키) | Open-Meteo 사용 |
| `KMA_APIHUB_KEY` | 위와 동일 (API허브 경로) | apihub.kma.go.kr | — |
| `NAVER_CLIENT_ID/SECRET` | 추천 옷 예시 이미지 | developers.naver.com 검색 API | 쇼핑몰 검색 링크만 표시 |
| `OPENAI_API_KEY` | 'AI 한마디' 문장 | platform.openai.com | 템플릿 문장 |

키가 없거나 틀리면 화면 상단에 이유가 표시되고 자동으로 대체 소스를 씁니다.
인터넷이 아예 없으면 데모 데이터로 동작하므로 시연이 끊기지 않습니다.

## 구조

| 파일 | 역할 |
|---|---|
| `config.py` | 캠퍼스 좌표·고도, 바람 배율, 민감도 보정 등 **조정 가능한 계수** |
| `weather.py` | 기상청 / Open-Meteo / 데모 예보 수집 |
| `feels_like.py` | 기상청 체감온도식(겨울 바람냉각, 여름 습도) + 캠퍼스 보정(고도·바람·개인) |
| `outfit.py` | 기온별 옷차림 8단계 × 상의·하의·신발·의류 잡화 |
| `model.py` | Random Forest / XGBoost 옷차림 분류, 학생 제보 반영 |
| `train.py` | 학습: `python train.py [--aws AWS.csv] [--model xgb]` |
| `service.py` | 화면용 계산 묶음 (분석 결과·제보 통계) |
| `server.py` | Flask 웹 서버 + API (`/api/home`, `/api/analyze`, `/api/feedback`, `/api/products`) |
| `docs/index.html` | 예선 자료 화면 구상 그대로: 시작 → AI 분석 중 → 결과 (서버·HTML 버전 공용) |
| `docs/standalone.js` | 서버 없이 브라우저에서 계산하는 HTML 버전 로직 |
| `docs/model.js` | HTML 버전용 작은 AI 모델 + 설정값 (`python web_export.py`로 생성) |
| `web_export.py` | 웹용 모델 내보내기 — `config.py`·`outfit.py`를 고쳤으면 다시 실행 |

## 사용하는 AI 모델

### 현재 모델: Random Forest 분류기 (scikit-learn)

결정트리 여러 개가 각자 옷차림 단계를 고르고, 다수결로 최종 결과를 정하는 머신러닝 모델입니다.
표 형태 데이터(기온·풍속 같은 숫자)에 강하고, 데이터가 적어도 안정적이며, 무료입니다.

| 항목 | 내용 |
|---|---|
| 종류 | 지도학습 · 다중 분류 (8단계) |
| 라이브러리 | scikit-learn `RandomForestClassifier` (선택: XGBoost `--model xgb`) |
| 크기 | 서버 버전 트리 200개 / HTML 버전 트리 30개 |
| 입력 (8개) | 캠퍼스 기온, 캠퍼스 풍속, 습도, 개인 체감온도, 시각, 월, 추위 민감도, 강수확률 |
| 출력 | 옷차림 단계 0(한여름)~7(한겨울) → 상의·하의·신발·의류 잡화 추천 |
| 학습 데이터 | 안양 기후를 흉내 낸 합성 날씨 6,000시간 × 민감도 3종 = 14,400건 (+ 기상청 AWS CSV 가능) |
| 라벨 | '기온별 옷차림 표' 규칙 + 사람마다 다른 체감(±1.2°C 노이즈) |
| 재학습 | 학생 제보 "이렇게 입었는데 추워요/더워요" → 라벨 한 단계 수정, 5배 가중치 |
| 성능 | 단계 정확히 일치 약 81%, ±1단계 이내 99.9% (검증 데이터 20%) |

> ⚠️ 현재 정확도는 **규칙으로 만든 라벨** 기준이라 참고용입니다. 본선 검증(7/10)은
> 실제 사용자 5명의 제보로 다시 측정해야 의미가 있습니다.

### 전체 처리 흐름

1. **날씨 수집**: 기상청 단기예보(또는 Open-Meteo) 시간대별 기온·풍속·습도·강수확률
2. **체감온도 계산** (AI 아님, 공식): 고도차 × 0.65°C/100m → 캠퍼스 풍속(×1.3)으로 기상청 체감온도식 재계산 → 추위 민감도(±2°C)
3. **옷차림 분류** (AI): 위 값을 Random Forest에 넣어 시간대별 단계 예측 → 가장 두껍게 입어야 하는 시간 기준으로 추천
4. **AI 한마디**: `OPENAI_API_KEY`가 있으면 GPT(gpt-4o-mini)가 문장 생성, 없으면 템플릿 문장

### 앞으로: Air Fit 모델로 교체 예정

예선 자료(6쪽)의 **Air Fit**(MIT 라이선스, GitHub 공개 코드)을 이용해 **새 모델을 학습**하고,
지금의 Random Forest 대신 옷차림 분류에 쓸 계획입니다.
교체할 곳은 `model.py` 한 파일입니다.

- `make_model()` — 모델 생성 (지금은 Random Forest)
- `train()` — 학습
- `predict_level()` — 예측 → `(단계 0~7, 확률)` 형태로만 돌려주면 화면·서버는 수정할 필요 없음

Air Fit 모델의 입력이 다르면 `make_row()`에서 입력 값을 맞춰 주면 됩니다.
MIT 라이선스이므로 사용 시 README에 출처(저장소 주소·저작권 표시)를 남겨야 합니다.

## 시연 팁

- 주소 끝에 `#analyze`를 붙여 열면 (예: `http://localhost:5000/#analyze`) 바로 분석 화면부터 시작 (녹화용)
- '하교 시간 알림'은 브라우저 알림이라 탭이 열려 있어야 울립니다
- 로그인은 '사용자 정보 수집 안 함' 범위에 따라 넣지 않았습니다

## 실측으로 바꿔야 할 값 (`config.py`)

- `CAMPUS_ELEVATION_M` (현재 90m 추정), `KMA_SOURCE_ELEVATION_M` (40m 추정)
- `CAMPUS_WIND_FACTOR` (1.3 추정) — 캠퍼스와 평지에서 동시에 풍속을 재서 비율 계산
- 기상청 AWS 2025년 자료: 기상자료개방포털에서 CSV 내려받아 `python train.py --aws 파일.csv`
