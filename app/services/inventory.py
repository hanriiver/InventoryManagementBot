import re
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_log import InventoryLog, Order
from app.models.item import Item

BULK_ENTRY_PATTERN = re.compile(r"([^\d,]+?)\s*(\d+)\s*(?:,|$)")


async def get_all_inventory(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item).order_by(Item.category, Item.name))
    return list(result.scalars().all())


async def get_inventory_by_category(db: AsyncSession, category: str) -> list[Item]:
    result = await db.execute(
        select(Item).where(Item.category == category).order_by(Item.name)
    )
    return list(result.scalars().all())


async def get_favorite_items(db: AsyncSession) -> list[Item]:
    result = await db.execute(
        select(Item).where(Item.is_favorite.is_(True)).order_by(Item.name)
    )
    return list(result.scalars().all())


async def get_low_stock_items(db: AsyncSession) -> list[Item]:
    result = await db.execute(select(Item).order_by(Item.category, Item.name))
    items = result.scalars().all()
    return [item for item in items if item.current_quantity <= item.min_quantity]


async def get_item_by_name(db: AsyncSession, name: str) -> Item | None:
    result = await db.execute(select(Item).where(Item.name == name))
    return result.scalar_one_or_none()


async def _log_change(
    db: AsyncSession,
    item: Item,
    change_type: str,
    before_quantity: int,
    note: str,
) -> None:
    db.add(
        InventoryLog(
            item_id=item.id,
            change_type=change_type,
            before_quantity=before_quantity,
            after_quantity=item.current_quantity,
            note=note,
        )
    )


async def set_item_quantity(
    db: AsyncSession, item_id: int, quantity: int, note: str = "마감입력"
) -> Item:
    item = await db.get(Item, item_id)
    if item is None:
        raise ValueError(f"Item {item_id} not found")
    before = item.current_quantity
    item.current_quantity = quantity
    await _log_change(db, item, "set", before, note)
    await db.commit()
    return item


async def add_item_quantity(
    db: AsyncSession, item_id: int, quantity: int, note: str = "입고"
) -> Item:
    item = await db.get(Item, item_id)
    if item is None:
        raise ValueError(f"Item {item_id} not found")
    before = item.current_quantity
    item.current_quantity += quantity
    await _log_change(db, item, "add", before, note)
    await db.commit()
    return item


def parse_bulk_input(text_input: str) -> list[tuple[str, int]]:
    parsed: list[tuple[str, int]] = []
    for chunk in text_input.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        match = re.match(r"^(.+?)\s+(\d+)$", chunk)
        if match:
            name = match.group(1).strip()
            quantity = int(match.group(2))
            parsed.append((name, quantity))
    return parsed


async def bulk_update_inventory(
    db: AsyncSession, text_input: str
) -> tuple[list[Item], list[str]]:
    updated: list[Item] = []
    not_found: list[str] = []
    for name, quantity in parse_bulk_input(text_input):
        item = await get_item_by_name(db, name)
        if item is None:
            not_found.append(name)
            continue
        before = item.current_quantity
        item.current_quantity = quantity
        await _log_change(db, item, "set", before, "마감입력(일괄)")
        updated.append(item)
    await db.commit()
    return updated, not_found


async def generate_order_list(db: AsyncSession) -> list[Order]:
    low_stock_items = await get_low_stock_items(db)
    orders: list[Order] = []
    for item in low_stock_items:
        existing = await db.execute(
            select(Order).where(Order.item_id == item.id, Order.status == "pending")
        )
        if existing.scalar_one_or_none() is not None:
            continue
        order_quantity = max(item.min_quantity * 2 - item.current_quantity, 1)
        order = Order(item_id=item.id, order_quantity=order_quantity, status="pending")
        db.add(order)
        orders.append(order)
    await db.commit()
    return orders


async def get_pending_orders(db: AsyncSession) -> list[Order]:
    result = await db.execute(
        select(Order).where(Order.status == "pending").order_by(Order.created_at)
    )
    return list(result.scalars().all())


async def get_weekly_consumption(db: AsyncSession, days: int = 7) -> dict[int, int]:
    since = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(InventoryLog).where(InventoryLog.created_at >= since)
    )
    consumption: dict[int, int] = {}
    for log in result.scalars().all():
        delta = log.before_quantity - log.after_quantity
        if delta > 0:
            consumption[log.item_id] = consumption.get(log.item_id, 0) + delta
    return consumption


async def complete_order(db: AsyncSession, order_id: int) -> Order:
    from datetime import datetime

    order = await db.get(Order, order_id)
    if order is None:
        raise ValueError(f"Order {order_id} not found")
    await add_item_quantity(db, order.item_id, order.order_quantity, note="발주입고")
    order.status = "completed"
    order.completed_at = datetime.utcnow()
    await db.commit()
    return order
