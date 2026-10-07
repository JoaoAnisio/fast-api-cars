from fastapi import APIRouter

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def function_orders():
    return {"message": "Orders route"}