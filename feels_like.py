"""체감온도 계산식 (기상청 공식) + 안양대 캠퍼스 보정."""
from __future__ import annotations

import math
from dataclasses import dataclass

import config


def wind_chill(temp_c: float, wind_ms: float) -> float:
    """기상청 겨울철 체감온도 (바람냉각지수).

    적용 조건: 기온 10°C 이하, 풍속 1.3m/s(4.8km/h) 이상. 그 밖에는 기온 그대로.
    """
    v = wind_ms * 3.6  # km/h
    if temp_c > 10 or v < 4.8:
        return temp_c
    v16 = v ** 0.16
    return 13.12 + 0.6215 * temp_c - 11.37 * v16 + 0.3965 * v16 * temp_c


def _wet_bulb_stull(temp_c: float, rh: float) -> float:
    """Stull(2011) 습구온도 근사식 — 기상청 여름철 체감온도 계산에 사용."""
    return (
        temp_c * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(temp_c + rh)
        - math.atan(rh - 1.67633)
        + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh)
        - 4.686035
    )


def summer_feels_like(temp_c: float, rh: float) -> float:
    """기상청 여름철 체감온도 (기온·습도 기반)."""
    tw = _wet_bulb_stull(temp_c, rh)
    return (
        -0.2442 + 0.55399 * tw + 0.45535 * temp_c
        - 0.0022 * tw ** 2 + 0.00278 * tw * temp_c + 3.0
    )


def feels_like(temp_c: float, wind_ms: float, rh: float) -> float:
    """기온 구간에 맞는 기상청 체감온도식을 골라 계산."""
    if temp_c <= 10:
        return wind_chill(temp_c, wind_ms)
    if temp_c >= 25:
        return summer_feels_like(temp_c, rh)
    return temp_c


@dataclass
class CampusFeel:
    app_temp: float          # 일반 날씨 앱 기온
    campus_temp: float       # 고도 보정한 캠퍼스 기온
    campus_wind: float       # 바람길 보정한 캠퍼스 풍속
    feels: float             # 캠퍼스 체감온도 (개인 민감도 전)
    personal: float          # 개인 민감도까지 반영한 최종 체감온도
    altitude_delta: float    # 고도 보정량 (°C)
    wind_delta: float        # 바람 보정량 (°C)
    sensitivity_delta: float # 개인 보정량 (°C)


def campus_feels_like(
    temp_c: float,
    wind_ms: float,
    rh: float,
    source_elevation_m: float,
    sensitivity: str = "보통",
) -> CampusFeel:
    """일반 예보값 → 안양대 언덕 위 캠퍼스 체감온도.

    1) 고도 보정: 예보 지점과 캠퍼스의 고도 차 × 기온감률
    2) 바람 보정: 언덕·건물 사이 바람길로 풍속 증가 → 체감온도 재계산
    3) 개인 보정: 추위 민감도
    """
    altitude_delta = -(config.CAMPUS_ELEVATION_M - source_elevation_m) * config.LAPSE_RATE_C_PER_M
    campus_temp = temp_c + altitude_delta
    campus_wind = wind_ms * config.CAMPUS_WIND_FACTOR

    no_extra_wind = feels_like(campus_temp, wind_ms, rh)
    feels = feels_like(campus_temp, campus_wind, rh)
    wind_delta = feels - no_extra_wind

    sens = config.SENSITIVITY_OFFSET.get(sensitivity, 0.0)
    return CampusFeel(
        app_temp=temp_c,
        campus_temp=campus_temp,
        campus_wind=campus_wind,
        feels=feels,
        personal=feels + sens,
        altitude_delta=altitude_delta,
        wind_delta=wind_delta,
        sensitivity_delta=sens,
    )
