# Order Blocks and Breakers

## Order Block Definition

Bullish OB:

- Last down-close candle before bullish MSS/BOS/displacement.
- Body zone is between close and open of that down-close candle.
- Mean threshold is midpoint of open and close.

Bearish OB:

- Last up-close candle before bearish MSS/BOS/displacement.
- Body zone is between open and close of that up-close candle.
- Mean threshold is midpoint of open and close.

When there is a same-color candle series before impulse, prefer the largest-body candle in the immediate pre-displacement group. Do not scan arbitrarily far back.

Suggested metadata:

- `direction`
- `zone_low`
- `zone_high`
- `open`
- `close`
- `high`
- `low`
- `origin_time`
- `mean_threshold`
- `validated`
- `invalidated`
- `mitigated`
- `validation_time`
- `invalidation_time`

## Validation

Bullish OB validation:

- Price closes above OB high, or bullish structure break confirms.

Bearish OB validation:

- Price closes below OB low, or bearish structure break confirms.

## Invalidation

Use close-through mean threshold as the conservative invalidation rule.

Bullish OB invalidation:

- Candle closes below mean threshold.

Bearish OB invalidation:

- Candle closes above mean threshold.

Wick-only probes are not enough for invalidation unless a stricter optional mode is explicitly enabled.

## Breaker Blocks

Breaker is a failed OB, not a random broken range.

Bullish Breaker:

- Source is bearish OB or bearish manipulation context.
- Sell-side liquidity is taken.
- Price breaks upward through structure.
- Failed bearish block becomes support.

Bearish Breaker:

- Source is bullish OB or bullish manipulation context.
- Buy-side liquidity is taken.
- Price breaks downward through structure.
- Failed bullish block becomes resistance.

Suggested metadata:

- `source_order_block_time`
- `source_order_block_direction`
- `direction`
- `zone_low`
- `zone_high`
- `origin_time`
- `sweep_time`
- `trigger_time`
- `retested`
- `failed_ob_confirmed`

## Rejection Cases

Reject or penalize:

- Breaker without source OB.
- Breaker without sweep or opposite structure break.
- OB invalidation by wick-only move when conservative mean-threshold mode is used.
