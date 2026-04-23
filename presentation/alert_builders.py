from __future__ import annotations

from market_primitives.common import (
    BreakerBlock,
    EqualLiquidityLevel,
    FairValueGap,
    InvertedFVG,
    KeyLevel,
    LiquiditySweep,
    OrderBlock,
    PDZone,
    SMTDivergence,
    StructureBreak,
    SwingPoint,
    VolumeSignal,
    fmt_price,
    ts_utc,
)
from strategies.types import EntrySetup

from .types import AlertPayload


def build_primitive_alerts(
    *,
    swings: list[SwingPoint],
    sweeps: list[LiquiditySweep],
    raids: list[LiquiditySweep],
    structure_breaks: list[StructureBreak],
    fvgs: list[FairValueGap],
    ifvgs: list[InvertedFVG],
    order_blocks: list[OrderBlock],
    breaker_blocks: list[BreakerBlock],
    equal_highs: list[EqualLiquidityLevel],
    equal_lows: list[EqualLiquidityLevel],
    key_levels: list[KeyLevel],
    volume_signals: list[VolumeSignal],
    pd_zones: list[PDZone],
    smt_divergences: list[SMTDivergence],
) -> list[AlertPayload]:
    alerts: list[AlertPayload] = []
    alerts.extend(from_swing(swing) for swing in swings)
    alerts.extend(from_sweep(sweep, "Sweeps") for sweep in sweeps)
    alerts.extend(from_sweep(sweep, "Liquidity") for sweep in raids)
    alerts.extend(from_structure_break(structure) for structure in structure_breaks)
    alerts.extend(from_fvg(fvg) for fvg in fvgs if not fvg.invalidated)
    alerts.extend(from_ifvg(ifvg) for ifvg in ifvgs)
    alerts.extend(from_order_block(order_block) for order_block in order_blocks)
    alerts.extend(from_breaker_block(block) for block in breaker_blocks)
    alerts.extend(from_equal_level(level, "EQH") for level in equal_highs)
    alerts.extend(from_equal_level(level, "EQL") for level in equal_lows)
    alerts.extend(from_key_level(level) for level in key_levels)
    alerts.extend(from_volume_signal(signal) for signal in volume_signals)
    alerts.extend(from_pd_zone(zone) for zone in pd_zones)
    alerts.extend(from_smt_divergence(divergence) for divergence in smt_divergences)
    return alerts


def from_swing(swing: SwingPoint) -> AlertPayload:
    label = "Swing High" if swing.direction == "high" else "Swing Low"
    direction = "Bearish" if swing.direction == "high" else "Bullish"
    return AlertPayload(
        symbol=swing.symbol,
        timeframe=swing.timeframe,
        pattern="Swings",
        alert_kind="primitive",
        detail=f"SWING: {ts_utc(swing.timestamp)} | {fmt_price(swing.level)} | {label}",
        direction=direction,
        timestamp=swing.timestamp,
        level=swing.level,
    )


def from_sweep(sweep: LiquiditySweep, pattern: str) -> AlertPayload:
    direction = "Bullish" if sweep.direction == "bullish" else "Bearish"
    label = "SSL taken and reclaimed" if sweep.direction == "bullish" else "BSL taken and reclaimed"
    prefix = "LIQUIDITY RAID" if pattern == "Liquidity" else "SWEEP"
    return AlertPayload(
        symbol=sweep.symbol,
        timeframe=sweep.timeframe,
        pattern=pattern,
        alert_kind="primitive",
        detail=f"{prefix}: {ts_utc(sweep.timestamp)} | {fmt_price(sweep.liquidity_level)} | {direction} {label}",
        direction=direction,
        timestamp=sweep.timestamp,
        level=sweep.liquidity_level,
        sweep_level=sweep.liquidity_level,
        metadata=dict(sweep.metadata),
    )


def from_structure_break(structure: StructureBreak) -> AlertPayload:
    pattern = "CHoCH" if structure.break_type == "CHOCH" else structure.break_type
    direction = "Bullish" if structure.direction == "bullish" else "Bearish"
    return AlertPayload(
        symbol=structure.symbol,
        timeframe=structure.timeframe,
        pattern=pattern,
        alert_kind="primitive",
        detail=f"{pattern}: {ts_utc(structure.timestamp)} | {fmt_price(structure.broken_level)} | {direction} {pattern}",
        direction=direction,
        timestamp=structure.timestamp,
        level=structure.broken_level,
        structure_level=structure.broken_level,
        metadata=dict(structure.metadata),
    )


def from_fvg(fvg: FairValueGap) -> AlertPayload:
    direction = "Bullish" if fvg.direction == "bullish" else "Bearish"
    suffix = "[ACTIVE]" if not fvg.mitigated else "[RETESTED]"
    return AlertPayload(
        symbol=fvg.symbol,
        timeframe=fvg.timeframe,
        pattern="FVG",
        alert_kind="primitive",
        detail=f"FVG: {ts_utc(fvg.created_at)} | {fmt_price(fvg.gap_low)} - {fmt_price(fvg.gap_high)} | {direction} {suffix}",
        direction=direction,
        timestamp=fvg.mitigated_at or fvg.created_at,
        gap_low=fvg.gap_low,
        gap_high=fvg.gap_high,
        metadata=dict(fvg.metadata),
    )


def from_ifvg(ifvg: InvertedFVG) -> AlertPayload:
    direction = "Bullish" if ifvg.direction == "bullish" else "Bearish"
    return AlertPayload(
        symbol=ifvg.symbol,
        timeframe=ifvg.timeframe,
        pattern="IFVG",
        alert_kind="primitive",
        detail=f"IFVG: {ts_utc(ifvg.timestamp)} | {fmt_price(ifvg.zone_low)} - {fmt_price(ifvg.zone_high)} | {direction} inversion retest",
        direction=direction,
        timestamp=ifvg.timestamp,
        gap_low=ifvg.zone_low,
        gap_high=ifvg.zone_high,
        metadata=dict(ifvg.metadata),
    )


def from_order_block(block: OrderBlock) -> AlertPayload:
    direction = "Bullish" if block.direction == "bullish" else "Bearish"
    return AlertPayload(
        symbol=block.symbol,
        timeframe=block.timeframe,
        pattern="OB",
        alert_kind="primitive",
        detail=f"OB: {ts_utc(block.origin_time)} | {fmt_price(block.zone_low)} - {fmt_price(block.zone_high)} | {direction} Order Block",
        direction=direction,
        timestamp=block.timestamp,
        ob_low=block.zone_low,
        ob_high=block.zone_high,
        metadata=dict(block.metadata),
    )


def from_breaker_block(block: BreakerBlock) -> AlertPayload:
    direction = "Bullish" if block.direction == "bullish" else "Bearish"
    return AlertPayload(
        symbol=block.symbol,
        timeframe=block.timeframe,
        pattern="Breaker",
        alert_kind="primitive",
        detail=f"BREAKER: {ts_utc(block.origin_time)} | {fmt_price(block.zone_low)} - {fmt_price(block.zone_high)} | {direction} Breaker",
        direction=direction,
        timestamp=block.timestamp,
        ob_low=block.zone_low,
        ob_high=block.zone_high,
        metadata=dict(block.metadata),
    )


def from_equal_level(level: EqualLiquidityLevel, pattern: str) -> AlertPayload:
    direction = "Bearish" if pattern == "EQH" else "Bullish"
    label = "Equal Highs - BSL above" if pattern == "EQH" else "Equal Lows - SSL below"
    return AlertPayload(
        symbol=level.symbol,
        timeframe=level.timeframe,
        pattern=pattern,
        alert_kind="primitive",
        detail=f"{pattern}: {ts_utc(level.timestamp)} | {fmt_price(level.level)} | {label} ({level.touches} touches)",
        direction=direction,
        timestamp=level.timestamp,
        level=level.level,
    )


def from_key_level(level: KeyLevel) -> AlertPayload:
    direction = "Bullish" if level.direction == "bullish" else "Bearish"
    return AlertPayload(
        symbol=level.symbol,
        timeframe=level.timeframe,
        pattern="KL",
        alert_kind="primitive",
        detail=f"KEY LEVEL: {ts_utc(level.timestamp)} | {fmt_price(level.level)} | {level.touches} touches ({level.bias})",
        direction=direction,
        timestamp=level.timestamp,
        level=level.level,
    )


def from_volume_signal(signal: VolumeSignal) -> AlertPayload:
    direction = "Bullish" if signal.direction == "bullish" else "Bearish"
    if signal.signal_type == "spike":
        usd_volume = signal.metadata.get("usd_volume", 0.0)
        volume_text = f"${usd_volume/1_000_000:.1f}M" if usd_volume >= 1_000_000 else f"${usd_volume/1_000:.0f}K"
        detail = f"VOLUME: {ts_utc(signal.timestamp)} | {volume_text} | {signal.metadata.get('tier', 'Notable')} {direction}"
        pattern = "Volume"
    else:
        detail = f"VP: {ts_utc(signal.timestamp)} | POC {fmt_price(signal.level)} | Price at high-volume node"
        pattern = "VP"
    return AlertPayload(
        symbol=signal.symbol,
        timeframe=signal.timeframe,
        pattern=pattern,
        alert_kind="primitive",
        detail=detail,
        direction=direction,
        timestamp=signal.timestamp,
        level=signal.level,
        metadata=dict(signal.metadata),
    )


def from_pd_zone(zone: PDZone) -> AlertPayload:
    detail_map = {
        "ote_discount": f"OTE ZONE: {ts_utc(zone.timestamp)} | {fmt_price(zone.zone_low)} - {fmt_price(zone.zone_high)} | Bullish OTE",
        "ote_premium": f"OTE ZONE: {ts_utc(zone.timestamp)} | {fmt_price(zone.zone_low)} - {fmt_price(zone.zone_high)} | Bearish OTE",
        "premium": f"PREMIUM: {ts_utc(zone.timestamp)} | EQ {fmt_price(zone.equilibrium)} | Above equilibrium",
        "discount": f"DISCOUNT: {ts_utc(zone.timestamp)} | EQ {fmt_price(zone.equilibrium)} | Below equilibrium",
    }
    direction = "Premium" if "premium" in zone.kind else "Discount"
    return AlertPayload(
        symbol=zone.symbol,
        timeframe=zone.timeframe,
        pattern="PD",
        alert_kind="primitive",
        detail=detail_map[zone.kind],
        direction=direction,
        timestamp=zone.timestamp,
        level=zone.equilibrium,
        metadata=dict(zone.metadata),
    )


def from_smt_divergence(divergence: SMTDivergence) -> AlertPayload:
    direction = "Bullish" if divergence.direction == "bullish" else "Bearish"
    return AlertPayload(
        symbol=divergence.symbol,
        timeframe=divergence.timeframe,
        pattern="SMT",
        alert_kind="primitive",
        detail=(
            f"SMT {direction}: {divergence.symbol} {fmt_price(divergence.primary_level)} / "
            f"{divergence.secondary_symbol} {fmt_price(divergence.secondary_level)} - divergence"
        ),
        direction=direction,
        timestamp=divergence.timestamp,
        level=divergence.primary_level,
        metadata=dict(divergence.metadata),
    )


def from_entry_setup(setup: EntrySetup) -> AlertPayload:
    direction = "Bullish" if setup.direction == "long" else "Bearish"
    return AlertPayload(
        symbol=setup.symbol,
        timeframe=setup.timeframe,
        pattern=setup.model_name,
        alert_kind="strategy",
        detail="",
        direction=direction,
        trade_direction=setup.direction,
        timestamp=setup.timestamp,
        score=setup.score,
        level=setup.structure_level or setup.sweep_level,
        entry_low=setup.entry_low,
        entry_high=setup.entry_high,
        invalidation=setup.invalidation,
        sweep_level=setup.sweep_level,
        structure_level=setup.structure_level,
        context_timeframe=setup.context_timeframe,
        status=setup.status,
        reason=setup.reason,
        components=setup.components,
        metadata=dict(setup.metadata),
    )


__all__ = [
    "AlertPayload",
    "build_primitive_alerts",
    "from_entry_setup",
]
