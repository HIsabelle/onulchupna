"""시간대별 날씨 예보 가져오기.

우선순위:
  1) 기상청 — 공공데이터포털(KMA_API_KEY) 또는 기상청 API허브(KMA_APIHUB_KEY)
     · 단기예보(getVilageFcst): 시간대별 기온·풍속·습도·강수확률
     · 초단기실황(getUltraSrtNcst): 지금 이 시각 관측값
  2) Open-Meteo (무료, 키 불필요)
  3) 네트워크가 안 되면 시연용 데모 데이터
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional
from urllib.parse import unquote

import pandas as pd
import requests

import config

COLUMNS = ["time", "temp", "wind", "humidity", "pop"]

DATA_GO_KR = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
APIHUB = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0"


@dataclass
class Forecast:
    hourly: pd.DataFrame
    source: str
    source_elevation: float
    now: Optional[dict] = None              # 초단기실황 {temp, wind, humidity, time}
    errors: list = field(default_factory=list)


# ---------------- 기상청 ----------------

def _kma_endpoint():
    """(기본 URL, 인증 파라미터 dict) — 설정된 키 종류에 따라."""
    if os.environ.get("KMA_API_KEY"):
        # 포털의 '인코딩 키'를 넣어도 동작하도록 한 번 디코딩 (requests가 다시 인코딩함)
        return DATA_GO_KR, {"serviceKey": unquote(os.environ["KMA_API_KEY"].strip())}
    if os.environ.get("KMA_APIHUB_KEY"):
        return APIHUB, {"authKey": os.environ["KMA_APIHUB_KEY"].strip()}
    return None, None


def _kma_call(op: str, base_date: str, base_time: str) -> list:
    url, auth = _kma_endpoint()
    resp = requests.get(
        f"{url}/{op}",
        params={**auth, "pageNo": 1, "numOfRows": 1000, "dataType": "JSON",
                "base_date": base_date, "base_time": base_time,
                "nx": config.KMA_NX, "ny": config.KMA_NY},
        timeout=10,
    )
    if resp.status_code != 200:
        # URL에 인증키가 들어 있으므로 상태 코드만 노출
        raise RuntimeError(f"HTTP {resp.status_code} (인증키·활용신청 승인 여부를 확인하세요)")
    try:
        js = resp.json()
    except ValueError:
        # 키 오류 등은 XML로 옴 (예: SERVICE_KEY_IS_NOT_REGISTERED_ERROR)
        raise RuntimeError(f"기상청 응답 오류: {resp.text[:200]}")
    header = js["response"]["header"]
    if header["resultCode"] != "00":
        raise RuntimeError(f"기상청 오류 {header['resultCode']}: {header['resultMsg']}")
    return js["response"]["body"]["items"]["item"]


def _vilage_base(now: datetime):
    """단기예보 발표시각(02,05,...,23시, 발표 10분 후 조회 가능) 중 가장 최근 것."""
    for h in (23, 20, 17, 14, 11, 8, 5, 2):
        if now >= now.replace(hour=h, minute=10, second=0, microsecond=0):
            return now.strftime("%Y%m%d"), f"{h:02d}00"
    return (now - timedelta(days=1)).strftime("%Y%m%d"), "2300"


def _ncst_base(now: datetime):
    """초단기실황: 매시 정각 자료가 약 40분 이후 제공."""
    t = now - timedelta(minutes=40)
    return t.strftime("%Y%m%d"), t.strftime("%H00")


def fetch_kma_forecast() -> pd.DataFrame:
    items = _kma_call("getVilageFcst", *_vilage_base(datetime.now()))
    keymap = {"TMP": "temp", "WSD": "wind", "REH": "humidity", "POP": "pop"}
    rows = {}
    for it in items:
        col = keymap.get(it["category"])
        if col:
            t = datetime.strptime(it["fcstDate"] + it["fcstTime"], "%Y%m%d%H%M")
            rows.setdefault(t, {"time": t})[col] = float(it["fcstValue"])
    df = pd.DataFrame(sorted(rows.values(), key=lambda r: r["time"]))
    return df[COLUMNS].dropna()


def fetch_kma_now() -> dict:
    base_date, base_time = _ncst_base(datetime.now())
    items = _kma_call("getUltraSrtNcst", base_date, base_time)
    v = {it["category"]: float(it["obsrValue"]) for it in items}
    return {
        "temp": v["T1H"], "wind": v.get("WSD", 0.0), "humidity": v.get("REH", 50.0),
        "time": datetime.strptime(base_date + base_time, "%Y%m%d%H%M"),
    }


# ---------------- 대체 소스 ----------------

def fetch_open_meteo():
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            # 캠퍼스가 아니라 '날씨 앱 기준 지점'(동안구) 예보를 받아 캠퍼스로 보정
            "latitude": config.APP_REF_LAT, "longitude": config.APP_REF_LON,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability",
            "wind_speed_unit": "ms", "timezone": "Asia/Seoul", "forecast_days": 3,
        },
        timeout=10,
    )
    resp.raise_for_status()
    js = resp.json()
    h = js["hourly"]
    df = pd.DataFrame({
        "time": pd.to_datetime(h["time"]),
        "temp": h["temperature_2m"],
        "wind": h["wind_speed_10m"],
        "humidity": h["relative_humidity_2m"],
        "pop": h["precipitation_probability"],
    })
    return df.fillna(0), float(js.get("elevation", config.KMA_SOURCE_ELEVATION_M))


def demo_forecast(start: date) -> pd.DataFrame:
    """인터넷이 없을 때 시연용 데이터 (월별 평년기온 + 일교차 곡선)."""
    monthly_mean = [-2.4, 0.4, 5.7, 12.5, 17.8, 22.2, 25.0, 25.7, 21.2, 14.8, 7.2, 0.4]
    rows = []
    for d in range(3):
        day = start + timedelta(days=d)
        mean = monthly_mean[day.month - 1]
        for hour in range(24):
            rows.append({
                "time": datetime(day.year, day.month, day.day, hour),
                "temp": round(mean + 4.5 * math.sin((hour - 9) / 24 * 2 * math.pi), 1),
                "wind": round(2.5 + 1.5 * math.sin(hour / 24 * 2 * math.pi), 1),
                "humidity": 55.0,
                "pop": 10.0,
            })
    return pd.DataFrame(rows)


def get_forecast() -> Forecast:
    errors = []
    if _kma_endpoint()[0]:
        try:
            fc = Forecast(fetch_kma_forecast(), "기상청 단기예보", config.KMA_SOURCE_ELEVATION_M)
            try:
                fc.now = fetch_kma_now()
            except Exception as e:
                fc.errors.append(f"초단기실황 실패: {e}")
            return fc
        except Exception as e:
            errors.append(f"기상청 단기예보 실패 → 대체 소스 사용: {e}")
    else:
        errors.append("기상청 API 키가 없어 Open-Meteo를 사용합니다 (.env에 KMA_API_KEY 설정).")
    try:
        df, elev = fetch_open_meteo()
        return Forecast(df, "Open-Meteo 예보", elev, errors=errors)
    except Exception as e:
        errors.append(f"Open-Meteo 실패: {e}")
        return Forecast(demo_forecast(date.today()), "데모 데이터(오프라인)",
                        config.KMA_SOURCE_ELEVATION_M, errors=errors)
