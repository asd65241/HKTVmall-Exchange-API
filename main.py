from typing import Optional

from fastapi import FastAPI

from schema import Query
from core import HKTVmallToolkit as Toolkit

app = FastAPI(
    title="HKTVmall Exchange Sales API",
    description="This API used to interact with the HKTVmall Exchange backend",
    version="1.0.1",
    contact={
        "name": "Tom Mong from Stocksgram",
        "url": "https://stocksgram.com",
        "email": "tom@stocksgram.com",
    },
    docs_url='/'
)

@app.get("/sales/nday/{nday}")
def get_Sales_with_nday(nday: int):
    """
    Get the sales of nday before today
    """
    tkit = Toolkit()

    results = tkit.getSalesND(nday)
    return results

@app.post("/sales/nday/{nday}")
async def get_Sales_with_nday_with_login(nday: int, q: Query):
    """
    Get the sales of nday before today
    """
    if q == None:
        tkit = Toolkit()
    else:
        tkit = Toolkit(username=q.username,pwd=q.password,merchant=q.merchant)

    results = tkit.getSalesND(nday)
    return results


@app.get("/sales/date/{date}")
def get_Sales_with_date(date: str):
    """
    Get the sales of a particular day
    """
    tkit = Toolkit()

    results = tkit.getSales(date)
    return results

@app.post("/sales/date/{date}")
async def get_Sales_with_date_with_login(date: int, q: Query):
    """
    Get the sales of a particular day
    """
    if q == None:
        tkit = Toolkit()
    else:
        tkit = Toolkit(username=q.username,pwd=q.password,merchant=q.merchant)

    results = tkit.getSales(date)
    return results
