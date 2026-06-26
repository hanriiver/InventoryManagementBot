from app.models.item import Item
from app.schemas.kakao import simple_text_response


def build_inventory_response(items: list[Item]) -> dict:
    if not items:
        text = "📦 등록된 품목이 없습니다."
    else:
        text = "📦 현재 재고 현황\n" + "─" * 20 + "\n"
        for item in items:
            status = "✅" if item.current_quantity > item.min_quantity else "⚠️"
            text += f"{status} {item.name}: {item.current_quantity}{item.unit or ''}\n"

    quick_replies = [
        {"label": "⚠️ 부족 재고만 보기", "action": "message", "messageText": "부족재고조회"},
        {"label": "📋 발주 목록", "action": "message", "messageText": "발주목록"},
        {"label": "✏️ 마감 입력", "action": "message", "messageText": "마감입력시작"},
    ]
    return simple_text_response(text, quick_replies)


def build_low_stock_response(items: list[Item]) -> dict:
    if not items:
        text = "✅ 부족한 재고가 없습니다."
    else:
        text = "⚠️ 부족 재고 목록\n" + "─" * 20 + "\n"
        for item in items:
            text += f"⚠️ {item.name}: {item.current_quantity}{item.unit or ''} (기준: {item.min_quantity}{item.unit or ''})\n"

    quick_replies = [
        {"label": "📋 발주 목록 생성", "action": "message", "messageText": "발주목록"},
        {"label": "📦 전체 재고 보기", "action": "message", "messageText": "재고조회"},
    ]
    return simple_text_response(text, quick_replies)


def build_closing_input_response(favorite_items: list[Item]) -> dict:
    quick_replies = [
        {
            "label": item.name,
            "action": "block",
            "blockId": "수량입력블록",
            "extra": {"item_id": item.id},
        }
        for item in favorite_items[:9]
    ]
    quick_replies.append(
        {"label": "✅ 입력 완료", "action": "message", "messageText": "마감완료"}
    )
    return simple_text_response(
        "📝 마감 재고 입력\n어떤 품목을 입력할까요?", quick_replies
    )


def build_order_list_response(orders, items_by_id: dict[int, Item]) -> dict:
    if not orders:
        text = "📋 발주할 품목이 없습니다."
    else:
        text = "📋 발주 목록\n" + "─" * 20 + "\n"
        for order in orders:
            item = items_by_id.get(order.item_id)
            name = item.name if item else f"품목#{order.item_id}"
            unit = item.unit if item else ""
            text += f"• {name}: {order.order_quantity}{unit or ''}\n"

    quick_replies = [
        {"label": "📦 전체 재고 보기", "action": "message", "messageText": "재고조회"},
    ]
    return simple_text_response(text, quick_replies)
