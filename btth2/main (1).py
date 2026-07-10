from fastapi import FastAPI, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import SmartHomePlanCreate, SmartHomePlanResponse
from crud import create_plan, get_plans, get_plan
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()


def response(status_code, message, error, data, path):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/smart-home-plans", status_code=201)
def add_plan(
    plan: SmartHomePlanCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        new_plan = create_plan(db, plan)

        return response(
            201,
            "Thêm gói thiết bị thành công",
            None,
            SmartHomePlanResponse.model_validate(new_plan).model_dump(),
            str(request.url.path)
        )

    except HTTPException as e:
        return response(
            e.status_code,
            e.detail,
            "Bad Request",
            None,
            str(request.url.path)
        )


@app.get("/smart-home-plans")
def all_plans(
    request: Request,
    db: Session = Depends(get_db)
):
    plans = get_plans(db)

    data = [
        SmartHomePlanResponse.model_validate(plan).model_dump()
        for plan in plans
    ]

    return response(
        200,
        "Lấy danh sách thành công",
        None,
        data,
        str(request.url.path)
    )


@app.get("/smart-home-plans/{plan_id}")
def detail_plan(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        plan = get_plan(db, plan_id)

        return response(
            200,
            "Lấy thông tin thành công",
            None,
            SmartHomePlanResponse.model_validate(plan).model_dump(),
            str(request.url.path)
        )

    except HTTPException as e:
        return response(
            e.status_code,
            e.detail,
            "Not Found",
            None,
            str(request.url.path)
        )