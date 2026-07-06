from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Any

app = FastAPI()

# PHẦN 1
# Luồng dữ liệu:
# Client gửi Request
#      ↓
# API xử lý nghiệp vụ
#      ↓
# Nếu thành công --> trả 6 trường JSON
# Nếu Validation/HTTP/Runtime Error
# --> Global Exception Handler bắt lỗi
# --> Chuẩn hóa thành JSON gồm:
# statusCode, message, data, error, timestamp, path

orders_db = [
    {"id": 1, "code": "SP001", "status": "PENDING"},
    {"id": 2, "code": "SP002", "status": "DELIVERED"}
]


class StandardResponse(BaseModel):
    statusCode: int
    message: str
    data: Any | None = None
    error: Any | None = None
    timestamp: str
    path: str


def success_response(request: Request, data: Any, message: str):
    return StandardResponse(
        statusCode=200,
        message=message,
        data=data,
        error=None,
        timestamp=datetime.now().isoformat(),
        path=request.url.path
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": "Request failed",
            "data": None,
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "statusCode": 422,
            "message": "Validation Error",
            "data": None,
            "error": exc.errors(),
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "statusCode": 500,
            "message": "Internal Server Error",
            "data": None,
            "error": "Đã xảy ra lỗi hệ thống.",
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )


@app.delete("/orders/{order_id}",response_model=StandardResponse,status_code=status.HTTP_200_OK)
def cancel_order(order_id: int, request: Request):
    for order in orders_db:

        if order["id"] == order_id:

            if order["status"] == "DELIVERED":
                raise HTTPException(
                    status_code=400,
                    detail="Không thể hủy đơn hàng đã giao."
                )

            order["status"] = "CANCELLED"

            return success_response(request,order,"Hủy đơn hàng thành công.")

    raise HTTPException(status_code=404,detail="Không tìm thấy đơn hàng.")