from typing import Any

from pydantic import BaseModel


class KakaoIntent(BaseModel):
    id: str | None = None
    name: str | None = None


class KakaoUserRequestUser(BaseModel):
    id: str | None = None


class KakaoUserRequest(BaseModel):
    utterance: str | None = None
    user: KakaoUserRequestUser | None = None
    params: dict[str, Any] | None = None


class KakaoAction(BaseModel):
    name: str | None = None
    clientExtra: dict[str, Any] | None = None
    params: dict[str, Any] | None = None


class KakaoRequest(BaseModel):
    intent: KakaoIntent | None = None
    userRequest: KakaoUserRequest | None = None
    bot: dict[str, Any] | None = None
    action: KakaoAction | None = None


def simple_text_response(text: str, quick_replies: list[dict] | None = None) -> dict:
    response: dict[str, Any] = {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
        },
    }
    if quick_replies:
        response["template"]["quickReplies"] = quick_replies[:10]
    return response
