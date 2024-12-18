from fastapi import APIRouter, Query , HTTPException, status
from .config import pricing_config
import requests
from requests.exceptions import RequestException
from sentry_sdk import capture_exception
router = APIRouter(
    prefix="/prices",
    tags=["Prices"],
    responses={404: {"description": "Not found"}},
)

@router.get("/necessities-price")
def get_necessities_prices(
        category=Query(None), commodity=Query(None)
):
    try:
        # 發送 GET 請求至 API
        response = requests.get(
            pricing_config.NECESSITIES_PRICE_API_URL,
            params={"CategoryName": category, "Name": commodity},
        )

        # 檢查 API 回應狀態碼是否為 2xx
        response.raise_for_status()

        # 回傳 API 的 JSON 結果
        return response.json()

    except RequestException as e:
        # 捕捉請求相關的錯誤（如連線失敗、超時等）
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the necessities prices. Please try again later.",
        )
    except ValueError as e:
        # 捕捉 JSON 解析錯誤
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the API response. Please try again later.",
        )
    except Exception as e:
        # 捕捉其他未知錯誤
        capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )