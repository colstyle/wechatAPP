# -*- coding: utf-8 -*-
"""
微信支付 V3 工具类框架
"""
import time
import uuid
import json
import base64
from typing import Optional, Dict, Any
from config import settings

class WeChatPayV3:
    def __init__(self):
        self.mchid = settings.WECHAT_PAY_MCH_ID
        self.appid = settings.WECHAT_APP_ID
        self.serial_no = settings.WECHAT_PAY_SERIAL_NO
        self.private_key = settings.WECHAT_PAY_PRIVATE_KEY
        self.api_v3_key = settings.WECHAT_PAY_APIV3_KEY
        
    def _generate_signature(self, method: str, url: str, timestamp: int, nonce_str: str, body: str = "") -> str:
        """
        生成 V3 签名
        """
        # 签名串：HTTP方法\nURL\n时间戳\n随机串\n请求报文主体\n
        sign_str = f"{method}\n{url}\n{timestamp}\n{nonce_str}\n{body}\n"
        
        # 实际开发中需要使用私钥进行加密：
        # key = serialization.load_pem_private_key(self.private_key.encode(), password=None)
        # signature = key.sign(sign_str.encode(), padding.PKCS1v15(), hashes.SHA256())
        # return base64.b64encode(signature).decode()
        
        return "MOCK_SIGNATURE"

    def _get_auth_header(self, method: str, url: str, body: str = "") -> str:
        """
        生成 Authorization 头
        """
        timestamp = int(time.time())
        nonce_str = uuid.uuid4().hex.upper()
        signature = self._generate_signature(method, url, timestamp, nonce_str, body)
        
        auth_header = (
            f'WECHATPAY2-SHA256-RSA2048 '
            f'mchid="{self.mchid}",'
            f'nonce_str="{nonce_str}",'
            f'signature="{signature}",'
            f'timestamp="{timestamp}",'
            f'serial_no="{self.serial_no}"'
        )
        return auth_header

    def create_order(self, order_no: str, amount: int, description: str, openid: str) -> Dict[str, Any]:
        """
        创建预支付订单 (JSAPI)
        """
        url = "/v3/pay/transactions/jsapi"
        body = {
            "appid": self.appid,
            "mchid": self.mchid,
            "description": description,
            "out_trade_no": order_no,
            "notify_url": "https://your-domain.com/api/order/pay/notify",
            "amount": {"total": amount, "currency": "CNY"},
            "payer": {"openid": openid}
        }
        
        # 实际开发中调用 requests.post(url, json=body, headers=headers)
        # 这里返回模拟数据供前端测试流程
        
        timestamp = str(int(time.time()))
        nonce_str = uuid.uuid4().hex
        prepay_id = f"wx{uuid.uuid4().hex[:20]}"
        
        # 这里的签名是前端 wx.requestPayment 需要的支付签名
        pay_sign = self._generate_signature("GET", prepay_id, int(timestamp), nonce_str)

        return {
            "timeStamp": timestamp,
            "nonceStr": nonce_str,
            "package": f"prepay_id={prepay_id}",
            "signType": "RSA",
            "paySign": pay_sign
        }

    def refund(self, out_trade_no: str, out_refund_no: str, refund_amount: int, total_amount: int, reason: str = "") -> Dict[str, Any]:
        """
        申请退款
        """
        url = "/v3/refund/domestic/refunds"
        body = {
            "out_trade_no": out_trade_no,
            "out_refund_no": out_refund_no,
            "reason": reason,
            "amount": {
                "refund": refund_amount,
                "total": total_amount,
                "currency": "CNY"
            }
        }
        
        # 实际开发中调用 requests.post(url, json=body, headers=headers)
        
        return {
            "refund_id": f"ref{uuid.uuid4().hex[:20]}",
            "out_refund_no": out_refund_no,
            "status": "SUCCESS"
        }

wechat_pay = WeChatPayV3()
