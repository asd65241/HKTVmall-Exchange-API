from typing import Optional

from fastapi import FastAPI, HTTPException

from schema import Query
from core import HKTVmallToolkit as Toolkit

app = FastAPI(
    title="HKTVmall Exchange Sales API",
    description="This API used to interact with the HKTVmall Exchange backend",
    version="1.2.0",
    contact={
        "name": "Tom Mong from Stocksgram",
        "url": "https://stocksgram.com",
        "email": "tom@stocksgram.com",
    },
    docs_url='/'
)

@app.post("/sales/nday/{nday}")
async def get_Sales_with_nday_with_login(nday: int, q: Query):
    """
    Get the sales of nday before today
    """
    try:
        tkit = Toolkit(username=q.username,pwd=q.password,merchant=q.merchant)

        results = tkit.getSalesND(nday)
        return results
    except Exception as msg:
        raise HTTPException(status_code=500, detail=repr(msg))

@app.post("/sales/date/{date}")
async def get_Sales_with_date_with_login(date: int, q: Query):
    """
    Get the sales of a particular day
    """
    try:
        tkit = Toolkit(username=q.username,pwd=q.password,merchant=q.merchant)

        results = tkit.getSales(date)
        return results
    except Exception as msg:
        raise HTTPException(status_code=500, detail=repr(msg))

# Deprecidated 

# @app.get("/sales/nday/{nday}")
# def get_Sales_with_nday(nday: int):
#     """
#     Get the sales of nday before today
#     """
#     try:
#         tkit = Toolkit()

#         results = tkit.getSalesND(nday)
#         return results
#     except Exception as msg:
#         raise HTTPException(status_code=500, detail=repr(msg))


# @app.get("/sales/date/{date}")
# def get_Sales_with_date(date: str):
#     """
#     Get the sales of a particular day
#     """
#     try:
#         tkit = Toolkit()

#         results = tkit.getSales(date)
#         return results
#     except Exception as msg:
#         raise HTTPException(status_code=500, detail=repr(msg))
