# -*- coding: utf-8 -*-
"""
AI 智能客服 API
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
from openai import OpenAI
from config import settings

router = APIRouter()

# 配置 Gemini
if settings.AI_SERVICE_TYPE == "gemini":
    genai.configure(api_key=settings.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# 配置 DeepSeek (OpenAI 兼容)
deepseek_client = None
if settings.AI_SERVICE_TYPE == "deepseek":
    deepseek_client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL
    )

SYSTEM_PROMPT = """
你现在是“青岛单人自助租衣小程序”的官方智能客服。
请根据以下业务规则回答用户问题：
1. 租赁时长：统一固定24小时，不支持自定义时长。
2. 时间计算：租赁开始时间为用户点击「我已取衣」时间，到期时间为取衣时间+24小时。
3. 预定流程：用户需先选择使用日期，系统筛选该日期可预约衣服。
4. 价格：单品按标价；3件特惠套餐固定69.9元/24小时。
5. 押金：单品按件收取，套餐按3件押金叠加收取。店主核验无误后一键原路退还。
6. 取消规则：未取衣可全额退款。
7. 门锁：支付成功后系统自动下发TTLock开门密码。
8. 逾期：超过24小时未还为逾期，由店主根据时长手动扣除押金。

你的语气应该是热情、专业且简洁的。如果用户的问题超出了租衣业务范围，请委婉地告知。
"""

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    AI 聊天接口 (支持 Gemini 和 DeepSeek)
    """
    # 检查是否配置了 API Key，未配置则返回模拟
    has_gemini = settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key"
    has_deepseek = settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_API_KEY != "your-deepseek-api-key"

    if not has_gemini and not has_deepseek:
        return {
            "code": 0,
            "message": "success",
            "data": {
                "reply": f"（模拟客服）您好！关于“{request.message}”，我们的租赁规则是统一24小时，套餐3件69.9元。请记得先选日期哦！"
            }
        }

    try:
        if settings.AI_SERVICE_TYPE == "deepseek" and has_deepseek:
            # DeepSeek 调用
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": request.message}
                ],
                stream=False
            )
            reply = response.choices[0].message.content
        else:
            # Gemini 调用
            chat_session = gemini_model.start_chat(history=[])
            full_prompt = f"{SYSTEM_PROMPT}\n\n用户说：{request.message}"
            response = chat_session.send_message(full_prompt)
            reply = response.text
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "reply": reply
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服务异常: {str(e)}")
