from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.kakao import KakaoRequest, simple_text_response
from app.services import inventory, report

router = APIRouter(prefix="/kakao", tags=["kakao"])


@router.post("/webhook")
async def kakao_webhook(payload: KakaoRequest, db: AsyncSession = Depends(get_db)):
    intent_name = payload.intent.name if payload.intent else None
    utterance = payload.userRequest.utterance if payload.userRequest else ""

    if intent_name == "재고_조회" or utterance == "재고조회":
        items = await inventory.get_all_inventory(db)
        return report.build_inventory_response(items)

    if intent_name == "부족_재고_조회" or utterance == "부족재고조회":
        items = await inventory.get_low_stock_items(db)
        return report.build_low_stock_response(items)

    if intent_name == "마감_입력_시작" or utterance == "마감입력시작":
        favorites = await inventory.get_favorite_items(db)
        return report.build_closing_input_response(favorites)

    if intent_name == "품목_수량_입력":
        action_params = payload.action.params if payload.action else {}
        client_extra = payload.action.clientExtra if payload.action else {}
        item_id = None
        if client_extra and "item_id" in client_extra:
            item_id = int(client_extra["item_id"])
        quantity_str = (action_params or {}).get("quantity")
        if item_id is not None and quantity_str is not None:
            item = await inventory.set_item_quantity(db, item_id, int(quantity_str))
            return simple_text_response(
                f"✅ {item.name} 재고를 {item.current_quantity}{item.unit or ''}로 입력했습니다."
            )
        return simple_text_response("수량 입력 정보를 확인하지 못했습니다. 다시 시도해주세요.")

    if utterance and "," in utterance:
        updated, not_found = await inventory.bulk_update_inventory(db, utterance)
        lines = [f"✅ {item.name}: {item.current_quantity}{item.unit or ''}" for item in updated]
        if not_found:
            lines.append("⚠️ 찾을 수 없는 품목: " + ", ".join(not_found))
        text = "마감 입력 완료\n" + "\n".join(lines) if lines else "입력된 품목을 찾을 수 없습니다."
        return simple_text_response(text)

    if intent_name == "발주_목록_조회" or utterance == "발주목록":
        await inventory.generate_order_list(db)
        orders = await inventory.get_pending_orders(db)
        items = await inventory.get_all_inventory(db)
        items_by_id = {item.id: item for item in items}
        return report.build_order_list_response(orders, items_by_id)

    if intent_name == "발주_완료":
        action_params = payload.action.params if payload.action else {}
        order_id = (action_params or {}).get("order_id")
        if order_id is not None:
            order = await inventory.complete_order(db, int(order_id))
            return simple_text_response(f"✅ 발주 #{order.id} 입고 완료 처리되었습니다.")
        return simple_text_response("발주 정보를 확인하지 못했습니다.")

    return simple_text_response(
        "무엇을 도와드릴까요?",
        [
            {"label": "📦 재고 조회", "action": "message", "messageText": "재고조회"},
            {"label": "✏️ 마감 입력", "action": "message", "messageText": "마감입력시작"},
        ],
    )
