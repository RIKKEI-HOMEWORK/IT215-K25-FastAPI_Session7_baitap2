from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RequestValidationError
from datetime import datetime

orders_db = [
    {"id": 1, "code": "SP001", "status": "PENDING"},
    {"id": 2, "code": "SP002", "status": "DELIVERED"}
]

api = FastAPI()

@api.exception_handler(Exception)
async def exeption_handler(request: Request, ext: Exception):
    return JSONResponse(
        status_code= 500,
        content={
            'statusCode' : 500,
            'message' : 'Runtime error',
            'data' : None,
            'error' : 'Runtime error',
            'timestamp' : datetime.now().isoformat(),
            'path' : str(request.url.path)
        }
    )

@api.exception_handler(HTTPException)
async def httpexception_handler(request: Request, ext: HTTPException):
    return JSONResponse(
        status_code=ext.status_code,
        content={
            'statusCode' : ext.status_code,
            'message' : 'Bad request',
            'data' : None,
            'error' : 'Bad request',
            'timestamp' : datetime.now().isoformat(),
            'path' : str(request.url.path)
        }
    )

@api.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, ext: RequestValidationError):
    return JSONResponse(
        status_code=ext.status_code,
        content={
            'statusCode' : ext.status_code,
            'message' : 'Validation error',
            'data' : None,
            'error' : 'Validation error',
            'timestamp' : datetime.now().isoformat(),
            'path' : str(request.url.path)
        }
    )

@api.delete('/orders/{order_id}')
def delete_order(order_id: int):
    for order in orders_db:
        if order['id'] == order_id:

            if order['status'] == 'DELIVERED':
                raise HTTPException(
                    status_code=400,
                    detail='Bad request'
                )
            
            order['status'] = 'CANCELLED'
            return {
                "statusCode": 200,
                "message": "Order cancelled successfully",
                "data": order,
                "error": None,
                "timestamp": datetime.now().isoformat(),
                "path": f"/orders/{order_id}"
            }
    raise HTTPException(
        status_code=404,
        detail='Not found'
    )

            
