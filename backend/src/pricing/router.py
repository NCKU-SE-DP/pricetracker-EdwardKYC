from fastapi import APIRouter, Query , HTTPException, status
from fastapi import APIRouter, Query , HTTPException, status
from .config import pricing_config
import requests
import logging
from requests.exceptions import RequestException
from sentry_sdk import capture_exception
import logging
from requests.exceptions import RequestException
from sentry_sdk import capture_exception
router = APIRouter(
    prefix="/prices",
    tags=["Prices"],
    responses={404: {"description": "Not found"}},
)
from ..logger.base import logger
from ..error import handle_request_exception

@router.get("/necessities-price")
def get_necessities_prices(
        category=Query(None), commodity=Query(None)
):
    try:
        logger.info(f"Received request for necessities prices with category: {category}, commodity: {commodity}")
        response = requests.get(
            pricing_config.NECESSITIES_PRICE_API_URL,
            params={"CategoryName": category, "Name": commodity},
        )
        response.raise_for_status()
        logger.info("API request successful. Parsing response.")
        return response.json()

    except Exception as e:
        handle_request_exception(e, "fetching necessities prices")