// 서버 없이 브라우저만으로 동작하는 버전 (GitHub Pages · index.html 더블클릭).
// service.py 와 같은 결과 형태를 만들어 화면 코드가 그대로 쓰도록 합니다.
// 기상청 API·네이버 쇼핑·학생 제보 통계는 서버(비밀 키·저장소)가 필요해 여기선 빠집니다.
const Standalone = (() => {
  const M = window.ONULCHUPNA;          // model.js (python web_export.py 로 생성)
  const C = M.config;
  const WEEKDAYS = "일월화수목금토";
  const FB_KEY = "onulchupna-feedback";
  let fc = null;

  // ---------- 시간 (항상 한국 시간 기준) ----------
  function kstNow() {
    const s = new Date().toLocaleString("sv-SE", { timeZone: "Asia/Seoul" }); // 2026-11-15 18:37:00
    const [d, t] = s.split(" ");
    const [hh, mm] = t.split(":").map(Number);
    return { date: d, hour: hh, minute: mm };
  }
  function addDays(dateStr, n) {
    const [y, m, d] = dateStr.split("-").map(Number);
    return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10);
  }
  function dateLabel(dateStr) {
    const [y, m, d] = dateStr.split("-").map(Number);
    return `${m}월 ${d}일 (${WEEKDAYS[new Date(Date.UTC(y, m - 1, d)).getUTCDay()]})`;
  }

  // ---------- 체감온도 (feels_like.py 와 같은 식) ----------
  function windChill(t, w) {
    const v = w * 3.6;
    if (t > 10 || v < 4.8) return t;
    const v16 = v ** 0.16;
    return 13.12 + 0.6215 * t - 11.37 * v16 + 0.3965 * v16 * t;
  }
  function summerFeels(t, rh) {
    const tw = t * Math.atan(0.151977 * Math.sqrt(rh + 8.313659)) + Math.atan(t + rh) - Math.atan(rh - 1.67633)
      + 0.00391838 * rh ** 1.5 * Math.atan(0.023101 * rh) - 4.686035;
    return -0.2442 + 0.55399 * tw + 0.45535 * t - 0.0022 * tw * tw + 0.00278 * tw * t + 3.0;
  }
  function feelsLike(t, w, rh) {
    if (t <= 10) return windChill(t, w);
    if (t >= 25) return summerFeels(t, rh);
    return t;
  }
  function campusFeel(t, w, rh, srcElev, sens) {
    const altitude = -(C.campus_elevation - srcElev) * C.lapse;
    const ct = t + altitude, cw = w * C.wind_factor;
    const f = feelsLike(ct, cw, rh);
    const s = C.sensitivity[sens] ?? 0;
    return { app: t, campusTemp: ct, campusWind: cw, feels: f, personal: f + s,
             altitude, wind: f - feelsLike(ct, w, rh), sens: s };
  }

  // ---------- AI 모델 (Random Forest 추론) ----------
  function predict(x) {
    const proba = new Array(M.classes.length).fill(0);
    for (const tr of M.trees) {
      let n = 0;
      while (tr.f[n] !== -1) n = x[tr.f[n]] <= tr.t[n] ? tr.l[n] : tr.r[n];
      tr.v[n].forEach((p, i) => (proba[i] += p));
    }
    return M.classes[proba.indexOf(Math.max(...proba))];
  }

  // ---------- 날씨 ----------
  function demoForecast() {
    const mean = [-2.4, 0.4, 5.7, 12.5, 17.8, 22.2, 25.0, 25.7, 21.2, 14.8, 7.2, 0.4];
    const today = kstNow().date, rows = [];
    for (let d = 0; d < 3; d++) {
      const date = addDays(today, d), m = +date.slice(5, 7);
      for (let h = 0; h < 24; h++) rows.push({
        date, hour: h, temp: +(mean[m - 1] + 4.5 * Math.sin((h - 9) / 24 * 2 * Math.PI)).toFixed(1),
        wind: +(2.5 + 1.5 * Math.sin(h / 24 * 2 * Math.PI)).toFixed(1), humidity: 55, pop: 10 });
    }
    return { hourly: rows, source: "데모 데이터(오프라인)", elevation: C.default_source_elevation };
  }
  async function forecast() {
    if (fc && Date.now() - fc.at < 600000) return fc;
    try {
      const q = new URLSearchParams({
        latitude: C.app_ref[0], longitude: C.app_ref[1],
        hourly: "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability",
        wind_speed_unit: "ms", timezone: "Asia/Seoul", forecast_days: 3 });
      const js = await (await fetch("https://api.open-meteo.com/v1/forecast?" + q)).json();
      const h = js.hourly;
      fc = { hourly: h.time.map((t, i) => ({
              date: t.slice(0, 10), hour: +t.slice(11, 13), temp: h.temperature_2m[i] ?? 0,
              wind: h.wind_speed_10m[i] ?? 0, humidity: h.relative_humidity_2m[i] ?? 50,
              pop: h.precipitation_probability[i] ?? 0 })),
             source: "Open-Meteo 예보", elevation: js.elevation ?? C.default_source_elevation };
    } catch (e) {
      fc = demoForecast();
    }
    fc.at = Date.now();
    return fc;
  }

  // ---------- 체감 제보 (이 기기 브라우저에만 저장) ----------
  function readFb() {
    try { return JSON.parse(localStorage.getItem(FB_KEY) || "[]"); } catch { return []; }
  }
  function stats() {
    const today = kstNow().date;
    const fb = readFb().filter((r) => r.date === today);
    const total = fb.length, choices = ["추워요", "적당해요", "더워요"];
    const counts = Object.fromEntries(choices.map((c) => [c, fb.filter((r) => r.feedback === c).length]));
    const recent = fb.slice(-3).reverse().map((r) => {
      const mins = Math.floor((Date.now() - r.at) / 60000);
      const top = C.levels[r.worn_level].categories["상의"][0];
      return { text: `${top} 입었는데 ${r.feedback}`,
               ago: mins < 1 ? "방금" : mins < 60 ? `${mins}분 전` : `${Math.floor(mins / 60)}시간 전` };
    });
    return { total, counts, recent, local: true,
             pct: Object.fromEntries(choices.map((c) => [c, total ? Math.round(100 * counts[c] / total) : 0])) };
  }

  // ---------- service.py 와 같은 응답 ----------
  async function home() {
    const f = await forecast(), now = kstNow();
    const cur = f.hourly.find((r) => r.date === now.date && r.hour === now.hour) || f.hourly[0];
    const ampm = now.hour < 12 ? "오전" : "오후";
    return {
      campus: C.campus,
      now_label: `${dateLabel(now.date)} ${ampm} ${now.hour % 12 || 12}:${String(now.minute).padStart(2, "0")}`,
      app_temp: Math.round(cur.temp), app_label: f.source, source: f.source,
      errors: ["웹 체험판이에요. 서버 없이 브라우저에서 계산하며, 기상청 실데이터·학생 제보 모으기는 로컬 실행 버전에서 지원돼요."],
      schedules: Object.keys(C.schedules), sensitivities: Object.keys(C.sensitivity),
      levels: C.levels.map((l) => ({ level: l.level, name: l.name, items: Object.values(l.categories).flat() })),
      stats: stats(),
      data: { elevation: C.campus_elevation, wind_factor: C.wind_factor },
    };
  }

  async function analyze({ day, schedule, sensitivity }) {
    const f = await forecast(), now = kstNow();
    const target = day === "오늘" ? now.date : addDays(now.date, 1);
    const [sh, eh] = C.schedules[schedule] || [9, 18];
    let sel = f.hourly.filter((r) => r.date === target && r.hour >= sh && r.hour <= eh);
    if (day === "오늘") sel = sel.filter((r) => r.hour >= now.hour);
    if (!sel.length) return { error: "선택한 시간대의 예보가 없어요. 오늘 일정이 이미 끝났다면 '내일'을 선택하세요." };

    const sensCode = Object.keys(C.sensitivity).indexOf(sensitivity);
    const month = +target.slice(5, 7);
    const hours = sel.map((r) => {
      const cf = campusFeel(r.temp, r.wind, r.humidity, f.elevation, sensitivity);
      const x = [cf.campusTemp, cf.campusWind, r.humidity, cf.personal, r.hour, month, sensCode, r.pop];
      return { hour: r.hour, app: r.temp, wind: r.wind, pop: r.pop, feels: cf.personal, level: predict(x), cf };
    });

    const worst = hours.reduce((a, b) => (b.level > a.level || (b.level === a.level && b.feels < a.feels) ? b : a));
    const cf = worst.cf, lv = C.levels[worst.level];
    const levels = hours.map((h) => h.level);
    const layering = Math.max(...levels) - Math.min(...levels) >= 2;
    const rainMax = Math.max(...hours.map((h) => h.pop));

    const cats = {};
    for (const [k, v] of Object.entries(lv.categories)) cats[k] = [...v];
    if (rainMax >= 60) for (const [k, extra] of Object.entries(C.rain_extra))
      cats[k] = [...extra, ...cats[k].filter((i) => i !== "샌들" && i !== "슬리퍼")];

    let tip;
    if (rainMax >= 60) tip = `강수확률이 최대 ${Math.round(rainMax)}%예요. 우산을 꼭 챙기세요.`;
    else if (layering) tip = "일교차가 커요. 벗기 쉬운 겉옷으로 겹쳐 입고 낮에는 한 겹 벗으세요.";
    else if (cf.wind <= -1) tip = "건물 사이 바람이 강해요. 목을 감싸는 옷이 체감온도를 크게 올려줘요.";
    else tip = "실내 강의실은 따뜻하니 안에 너무 두껍게 입기보다 겉옷으로 조절하세요.";

    const diff = Math.round(cf.app - cf.personal);
    const head = diff >= 1 ? `날씨앱만 보고 얇게 입으면 후회해요! 언덕 위 캠퍼스는 날씨앱보다 ${diff}° 더 춥게 느껴져요. `
      : diff <= -1 ? `오늘 캠퍼스는 날씨앱보다 ${-diff}° 덜 춥게 느껴져요. ` : "오늘 캠퍼스 체감은 날씨앱과 비슷해요. ";
    const comment = `${head}${worst.hour}시가 체감 ${Math.round(cf.personal)}°로 가장 추우니 ${cats["상의"][0]}에 ${cats["의류 잡화"][0]}까지 챙기세요.`;

    const chart = hours.length <= 6 ? hours : hours.filter((_, i) => i % 3 === 0 || i === hours.length - 1);
    const minFeels = Math.min(...hours.map((h) => h.feels));
    const last = hours[hours.length - 1];
    const warning = hours.length >= 2 && last.feels <= minFeels && hours[0].feels - last.feels >= 3
      ? `${last.hour}시 이후 기온 급하강 주의` : null;
    const st = stats();
    const sgn = (v) => (v >= 0 ? "+" : "") + v.toFixed(1) + "°";

    return {
      source: f.source, errors: [], date_label: dateLabel(target), schedule, end_hour: eh,
      steps: {
        weather: `${Math.round(hours[0].app)}° · ${hours[0].wind.toFixed(1)}m/s`,
        altitude: sgn(cf.altitude), wind: sgn(cf.wind),
        feedback: `${st.total}건 반영`, sensitivity: sgn(cf.sens),
      },
      result: {
        hour: worst.hour, feels: Math.round(+cf.personal.toFixed(1)), app: Math.round(cf.app), diff,
        altitude: +cf.altitude.toFixed(1), wind: +cf.wind.toFixed(1), sensitivity: +cf.sens.toFixed(1),
        level: lv.level, level_name: lv.name,
        categories: Object.entries(cats).map(([name, items]) => ({
          name, emoji: C.category_emoji[name],
          items: items.map((i) => ({ name: i, emoji: C.item_emoji[i] || "👕" })) })),
        comment, tip, model: "RandomForest (웹)", feedback_total: st.total,
      },
      hourly: chart.map((h) => ({ hour: h.hour, app: +h.app.toFixed(1), feels: +h.feels.toFixed(1) })),
      warning, stats: st,
    };
  }

  async function feedback({ worn_level, feedback }) {
    const fb = readFb();
    fb.push({ worn_level, feedback, date: kstNow().date, at: Date.now() });
    try { localStorage.setItem(FB_KEY, JSON.stringify(fb.slice(-200))); } catch {}
    return stats();
  }

  async function products(item) {
    const links = {};
    for (const [site, url] of Object.entries(C.search_links)) links[site] = url.replace("{q}", encodeURIComponent(item));
    return { products: [], links };
  }

  return { home, analyze, feedback, products };
})();
