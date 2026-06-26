import httpx

from app.core.config import settings
from app.db.database import async_session
from app.services import inventory, report


async def send_push_message(user_id: str, text: str) -> None:
    if not (settings.kakao_channel_token and settings.kakao_push_api_url and user_id):
        return
    headers = {"Authorization": f"Bearer {settings.kakao_channel_token}"}
    payload = {
        "receiver_uuids": [user_id],
        "template_object": {"object_type": "text", "text": text},
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        await client.post(settings.kakao_push_api_url, json=payload, headers=headers)


async def send_low_stock_alert() -> None:
    async with async_session() as db:
        items = await inventory.get_low_stock_items(db)
    if not items:
        return
    lines = [f"⚠️ {item.name}: {item.current_quantity}{item.unit or ''}" for item in items]
    text = "📦 부족 재고 알림\n" + "\n".join(lines)
    await send_push_message(settings.admin_user_id, text)


async def send_weekly_report() -> None:
    async with async_session() as db:
        consumption = await inventory.get_weekly_consumption(db)
        items = await inventory.get_all_inventory(db)
    items_by_id = {item.id: item for item in items}
    text = report.build_weekly_report_text(consumption, items_by_id)
    await send_push_message(settings.admin_user_id, text)
