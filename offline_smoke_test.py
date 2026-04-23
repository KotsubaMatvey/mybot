import asyncio
import io
import os
import tempfile
from dataclasses import dataclass, field
from types import SimpleNamespace

import database
import handlers
import handlers.charts as handler_charts
import onboarding
import payment_flow


@dataclass
class DummyMessage:
    text: str = ""
    replies: list = field(default_factory=list)
    deleted: bool = False

    async def reply_text(self, text, **kwargs):
        self.replies.append(("text", text, kwargs))
        return DummyMessage(text=text)

    async def reply_photo(self, photo=None, caption=None, **kwargs):
        self.replies.append(("photo", caption, kwargs))
        return DummyMessage(text=caption or "")

    async def delete(self):
        self.deleted = True


@dataclass
class DummyBot:
    sent: list = field(default_factory=list)

    async def send_message(self, chat_id, text, **kwargs):
        self.sent.append(("message", chat_id, text, kwargs))
        return DummyMessage(text=text)

    async def send_photo(self, chat_id, photo=None, caption=None, **kwargs):
        self.sent.append(("photo", chat_id, caption, kwargs))
        return DummyMessage(text=caption or "")


@dataclass
class DummyCallbackQuery:
    data: str
    from_user: SimpleNamespace
    message: DummyMessage = field(default_factory=DummyMessage)
    answers: list = field(default_factory=list)
    edits: list = field(default_factory=list)

    async def answer(self, text=None, show_alert=False):
        self.answers.append((text, show_alert))

    async def edit_message_text(self, text, **kwargs):
        self.edits.append(("text", text, kwargs))

    async def edit_message_reply_markup(self, reply_markup=None):
        self.edits.append(("markup", reply_markup, {}))


def make_update(user_id: int, text: str = ""):
    return SimpleNamespace(
        effective_user=SimpleNamespace(id=user_id),
        message=DummyMessage(text=text),
        callback_query=None,
    )


def make_context():
    return SimpleNamespace(bot=DummyBot(), args=[])


def sample_candles(n: int = 80, base: float = 100.0):
    candles = []
    price = base
    for i in range(n):
        drift = 0.15 if i % 7 < 4 else -0.08
        open_ = price
        close = price + drift
        high = max(open_, close) + 0.4
        low = min(open_, close) - 0.35
        candles.append({
            "time": 1_700_000_000_000 + i * 60_000,
            "open": round(open_, 4),
            "high": round(high, 4),
            "low": round(low, 4),
            "close": round(close, 4),
            "volume": 100 + i,
        })
        price = close
    return candles


async def main():
    tmpdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    original_db_path = database.DB_PATH
    original_send_payment_screen = payment_flow.send_payment_screen
    original_get_cached_candles = handler_charts.get_cached_candles
    original_get_cached_patterns = handler_charts.get_cached_patterns
    original_generate_chart = handler_charts.generate_chart
    original_get_user = handler_charts.get_user

    results = []
    try:
        database.DB_PATH = os.path.join(tmpdir.name, "test_users.db")
        database.init_db()

        payment_calls = []

        async def fake_send_payment_screen(user_id, context, update=None, expired=False):
            payment_calls.append((user_id, expired))
            target = update.message if update else None
            if target:
                await target.reply_text("PAYMENT_SCREEN")
            else:
                await context.bot.send_message(user_id, "PAYMENT_SCREEN")

        payment_flow.send_payment_screen = fake_send_payment_screen

        # Scenario 1: unsubscribed user goes to payment screen.
        update = make_update(101)
        context = make_context()
        await handlers.start(update, context)
        results.append(("start_unsubscribed_payment", bool(payment_calls and payment_calls[-1][0] == 101)))

        # Scenario 2: subscribed user with incomplete setup goes into onboarding, not dashboard.
        database.upsert_user(202)
        database.set_subscription(202, 30)
        update = make_update(202)
        context = make_context()
        await handlers.start(update, context)
        setup_prompt_seen = any("Setup Preferences" in reply[1] for reply in update.message.replies if reply[0] == "text")
        results.append(("start_subscribed_incomplete_setup", onboarding.is_active(202) and setup_prompt_seen))

        # Scenario 3: completed setup can render status/dashboard.
        database.save_preferences(202, {"BTCUSDT"}, {"BOS"}, {"1h"})
        update = make_update(202)
        context = make_context()
        await handlers.status_cmd(update, context)
        dashboard_seen = any("ICT Crypto Alerts" in reply[1] for reply in update.message.replies if reply[0] == "text")
        results.append(("status_completed_setup", dashboard_seen))

        # Scenario 4: outdated payment callback is rejected.
        database.upsert_user(303, invoice_id=999)
        query = DummyCallbackQuery("check_pay_111", from_user=SimpleNamespace(id=303))
        consumed = await payment_flow.handle_callback(303, "check_pay_111", query, make_context())
        results.append(("payment_outdated_invoice", consumed and query.answers and "outdated" in (query.answers[-1][0] or "").lower()))

        # Scenario 5: chart callback with missing user state should not crash.
        handler_charts.get_cached_candles = lambda symbol, tf: sample_candles()
        handler_charts.get_cached_patterns = lambda symbol, tf: []

        async def fake_generate_chart(candles, patterns, symbol, tf):
            return io.BytesIO(b"fake-chart")

        handler_charts.generate_chart = fake_generate_chart
        handler_charts.get_user = lambda user_id: None

        update = SimpleNamespace(
            callback_query=DummyCallbackQuery("chart_BTCUSDT_1h", from_user=SimpleNamespace(id=404))
        )
        context = make_context()
        await handlers.handle_chart_callback(update, context)
        sent_photo = any(reply[0] == "photo" for reply in update.callback_query.message.replies)
        results.append(("chart_callback_missing_user_safe", sent_photo))

    finally:
        database.DB_PATH = original_db_path
        payment_flow.send_payment_screen = original_send_payment_screen
        handler_charts.get_cached_candles = original_get_cached_candles
        handler_charts.get_cached_patterns = original_get_cached_patterns
        handler_charts.generate_chart = original_generate_chart
        handler_charts.get_user = original_get_user
        tmpdir.cleanup()

    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print("Offline smoke test results:")
    for name, ok in results:
        print(f" - {name}: {'PASS' if ok else 'FAIL'}")
    print(f"Summary: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
