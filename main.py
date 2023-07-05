from fastapi import FastAPI
from app.controllers import user_controller, payment_controller, repayment_controller, transaction_controller
import uvicorn
from app import scheduler
app = FastAPI()

# Include routers
app.include_router(user_controller.router, prefix="/api", tags=["users"])
app.include_router(payment_controller.router, prefix="/api", tags=["payments"])
app.include_router(repayment_controller.router, prefix="/api", tags=["repayments"])
app.include_router(transaction_controller.router, prefix="/api", tags=["transactions"])

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8088, reload=True, access_log=True)



