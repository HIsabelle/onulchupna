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
| `static/index.html` | 예선 자료 화면 구상 그대로: 시작 → AI 분석 중 → 결과 |

## AI 동작 방식

1. **체감온도 계산**: 예보 기온 → 고도차 × 0.65°C/100m 보정 → 캠퍼스 풍속(×1.3)으로 기상청 체감온도식 재계산 → 추위 민감도(±2°C)
2. **옷차림 분류**: 캠퍼스 기온·풍속·습도·체감·시각·월·민감도·강수확률 → 8단계 중 하나
3. **학습 데이터**: 초기에는 '기온별 옷차림 표' 규칙 라벨(사람별 편차를 노이즈로 반영).
   학생이 "이렇게 입었는데 추워요/더워요"를 제보하면 라벨을 한 단계 고쳐 5배 가중치로 재학습
   → 제보가 쌓일수록 규칙이 아닌 **실제 안양대 학생 체감**을 학습합니다.

> 현재 정확도(약 81%)는 규칙 라벨 기준이라 참고용입니다. 본선 검증(7/10)은
> 실제 사용자 5명의 제보로 다시 측정해야 의미가 있습니다.

## 시연 팁

- `http://localhost:5000/#analyze` 로 열면 바로 분석 화면부터 시작 (녹화용)
- '하교 시간 알림'은 브라우저 알림이라 탭이 열려 있어야 울립니다
- 로그인은 '사용자 정보 수집 안 함' 범위에 따라 넣지 않았습니다

## 실측으로 바꿔야 할 값 (`config.py`)

- `CAMPUS_ELEVATION_M` (현재 90m 추정), `KMA_SOURCE_ELEVATION_M` (40m 추정)
- `CAMPUS_WIND_FACTOR` (1.3 추정) — 캠퍼스와 평지에서 동시에 풍속을 재서 비율 계산
- 기상청 AWS 2025년 자료: 기상자료개방포털에서 CSV 내려받아 `python train.py --aws 파일.csv`
