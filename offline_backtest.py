from scanner import (
    _collect_swings,
    detect_bos,
    detect_sweeps,
    detect_liquidity_raids,
    detect_key_levels,
    detect_volume_profile,
)


def mk_candle(ts, open_, high, low, close, volume=100.0):
    return {
        "time": ts,
        "open": float(open_),
        "high": float(high),
        "low": float(low),
        "close": float(close),
        "volume": float(volume),
    }


def build_wave(base_ts, centers, width=0.8, volume=100.0):
    candles = []
    for i, center in enumerate(centers):
        open_ = center - 0.2
        close = center + 0.2
        high = center + width
        low = center - width
        candles.append(mk_candle(base_ts + i * 60_000, open_, high, low, close, volume + (i % 4) * 10))
    return candles


def filler(base_ts, n=30, anchor=100.0):
    seq = []
    for i in range(n):
        delta = [0.0, 0.4, -0.2, 0.3, -0.3][i % 5]
        seq.append(anchor + delta)
    return build_wave(base_ts, seq, width=0.45, volume=90.0)


def scenario_bos_bullish():
    ts = 1_700_000_000_000
    candles = filler(ts, 30, 100.0)
    tail = build_wave(
        ts + len(candles) * 60_000,
        [100.0, 102.0, 105.0, 102.0, 100.0, 101.0, 103.0, 101.5, 100.5, 101.5, 106.2, 105.9],
        width=0.9,
        volume=140.0,
    )
    candles.extend(tail)
    candles.append(mk_candle(ts + len(candles) * 60_000, 105.9, 106.4, 105.4, 106.0, 150.0))  # forming candle
    return candles


def scenario_sweep_bearish():
    ts = 1_700_000_000_000
    candles = filler(ts, 30, 100.0)
    tail = build_wave(
        ts + len(candles) * 60_000,
        [100.0, 102.0, 105.0, 102.0, 100.0, 101.0, 103.0, 101.5, 100.5, 101.5],
        width=0.9,
        volume=140.0,
    )
    candles.extend(tail)
    ts2 = ts + len(candles) * 60_000
    candles.append(mk_candle(ts2, 104.1, 107.0, 103.0, 103.4, 180.0))  # last closed candle sweeps above SH, closes back below
    candles.append(mk_candle(ts2 + 60_000, 103.4, 103.8, 103.0, 103.5, 120.0))  # forming candle
    return candles


def scenario_liquidity_bullish():
    ts = 1_700_000_000_000
    candles = filler(ts, 30, 99.5)
    tail = build_wave(
        ts + len(candles) * 60_000,
        [100.0, 98.0, 95.0, 98.0, 100.0, 99.0, 97.0, 99.0, 100.0, 98.5],
        width=0.9,
        volume=130.0,
    )
    candles.extend(tail)
    ts2 = ts + len(candles) * 60_000
    candles.append(mk_candle(ts2, 95.2, 98.2, 93.6, 96.8, 260.0))  # raid below recent SSL, close back above
    candles.append(mk_candle(ts2 + 60_000, 96.8, 97.1, 96.2, 96.7, 120.0))
    return candles


def scenario_key_level():
    ts = 1_700_000_000_000
    candles = filler(ts, 25, 101.0)
    tail = build_wave(
        ts + len(candles) * 60_000,
        [100.0, 102.0, 105.0, 102.0, 100.0, 101.0, 104.9, 102.0, 100.5, 101.5, 105.1, 102.2, 101.0, 105.02, 105.78],
        width=0.85,
        volume=140.0,
    )
    candles.extend(tail)
    candles.append(mk_candle(ts + len(candles) * 60_000, 105.7, 106.0, 105.5, 105.8, 130.0))
    return candles


def scenario_volume_profile():
    ts = 1_700_000_000_000
    candles = []
    centers = [100.0, 100.1, 99.9, 100.2, 100.0, 100.05] * 8 + [101.8, 102.0, 99.0, 99.2, 100.08, 100.12]
    for i, center in enumerate(centers):
        vol = 300.0 if 99.95 <= center <= 100.15 else 80.0
        candles.extend(build_wave(ts + len(candles) * 60_000, [center], width=0.35, volume=vol))
    candles.append(mk_candle(ts + len(candles) * 60_000, 100.12, 100.3, 99.9, 100.1, 320.0))
    return candles


SCENARIOS = [
    ("BOS", detect_bos, scenario_bos_bullish),
    ("Sweeps", detect_sweeps, scenario_sweep_bearish),
    ("Liquidity", detect_liquidity_raids, scenario_liquidity_bullish),
    ("KL", detect_key_levels, scenario_key_level),
    ("VP", detect_volume_profile, scenario_volume_profile),
]


def main():
    print("Offline detector regression results:")
    passed = 0
    for expected, detector, scenario in SCENARIOS:
        candles = scenario()
        hits = detector(candles)
        matched = any(hit.get("type") == expected for hit in hits)
        print(f" - {expected}: {'PASS' if matched else 'FAIL'} | hits={len(hits)}")
        if expected == "BOS":
            closed = candles[:-1]
            sh, sl = _collect_swings(closed[-35:])
            print(f"   debug last_close={closed[-1]['close']:.2f} last_sh={(sh[-1]['level'] if sh else None)} last_sl={(sl[-1]['level'] if sl else None)}")
        if expected in ("Sweeps", "Liquidity"):
            lookback = candles[-31:-2] if expected == "Sweeps" else candles[-35:-2]
            sh, sl = _collect_swings(lookback)
            last_closed = candles[-2]
            print(f"   debug last_closed=H{last_closed['high']:.2f}/L{last_closed['low']:.2f}/C{last_closed['close']:.2f} sh={(sh[-1]['level'] if sh else None)} sl={(sl[-1]['level'] if sl else None)}")
        if expected == "KL":
            closed = candles[:-1]
            sh, sl = _collect_swings(closed[-60:])
            print(f"   debug swings highs={[round(x['level'],2) for x in sh[-5:]]} lows={[round(x['level'],2) for x in sl[-5:]]} current={closed[-1]['close']:.2f}")
        for hit in hits[:3]:
            print(f"   {hit.get('detail', '')}")
        passed += int(matched)
    total = len(SCENARIOS)
    print(f"Summary: {passed}/{total} scenarios matched expected detector output")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
