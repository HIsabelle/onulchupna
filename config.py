"""오늘춥나?? 설정값.

캠퍼스 보정 계수는 '추정값'입니다. 실측(휴대용 온도계·풍속계로 캠퍼스와
안양 AWS 지점을 동시에 측정)을 하면 아래 숫자만 바꾸면 됩니다.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_env(path: Path = BASE_DIR / ".env"):
    """.env 파일의 KEY=VALUE 를 환경변수로 (이미 설정된 값은 유지)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            if value.strip():
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

DATA_DIR = BASE_DIR / "data"
MODEL_PATH = DATA_DIR / "outfit_model.joblib"
FEEDBACK_PATH = DATA_DIR / "feedback.csv"

# 안양대학교 안양캠퍼스 (경기도 안양시 만안구 삼덕로37번길 22)
CAMPUS_NAME = "안양대학교 안양캠퍼스"
CAMPUS_LAT = 37.3916
CAMPUS_LON = 126.9195
CAMPUS_ELEVATION_M = 90.0      # 캠퍼스(언덕 위) 해발고도 추정값 — 실측 후 수정

# '일반 날씨 앱' 기준 지점: 안양시청(동안구) — 날씨 앱이 보여주는 온도의 기준
APP_REF_LAT = 37.3943
APP_REF_LON = 126.9568

# 기상청 예보 기준 고도 (안양 시가지 평지 추정값) — Open-Meteo는 응답의 격자 고도를 사용
KMA_SOURCE_ELEVATION_M = 40.0

# 기상청 단기예보 격자 좌표 (안양시 만안구)
KMA_NX = 59
KMA_NY = 123

# 기온감률: 고도 100m 올라갈 때마다 약 0.65°C 하강
LAPSE_RATE_C_PER_M = 0.0065

# 언덕·건물 사이 바람길 효과: 일반 예보 풍속 대비 캠퍼스 풍속 배율 (추정값)
CAMPUS_WIND_FACTOR = 1.3

# "나는 추위를..." 개인 민감도 보정 (°C, 체감온도에 더함)
SENSITIVITY_OFFSET = {
    "많이 타요": -2.0,
    "보통": 0.0,
    "안 타요": +2.0,
}

# 캠퍼스에 머무는 시간 프리셋 (시작시, 종료시)
SCHEDULE_PRESETS = {
    "오전만 (09~12시)": (9, 12),
    "09:00 ~ 18:00": (9, 18),
    "야간까지 (09~22시)": (9, 22),
}
