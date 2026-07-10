from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from database import engine, Base, get_db
from models import ParkingModel
from schemas import ParkingCreate

app = FastAPI()

Base.metadata.create_all(bind=engine)


def response(status_code, message, error, data, path):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/parking-slots", status_code=201)
def create_parking(
    parking: ParkingCreate,
    request: Request,
    db: Session = Depends(get_db)
):

    new_slot = ParkingModel(
        slot_code=parking.slot_code,
        zone_name=parking.zone_name,
        max_weight=parking.max_weight,
        is_available=parking.is_available
    )

    try:
        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)

        return response(
            201,
            "Thêm vị trí đỗ xe thành công",
            None,
            {
                "id": new_slot.id,
                "slot_code": new_slot.slot_code,
                "zone_name": new_slot.zone_name,
                "max_weight": new_slot.max_weight,
                "is_available": new_slot.is_available
            },
            request.url.path
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="slot_code already exists"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )


@app.get("/parking-slots")
def get_all_parking(
    request: Request,
    db: Session = Depends(get_db)
):

    parking_list = db.query(ParkingModel).all()

    result = []

    for item in parking_list:
        result.append({
            "id": item.id,
            "slot_code": item.slot_code,
            "zone_name": item.zone_name,
            "max_weight": item.max_weight,
            "is_available": item.is_available
        })

    return response(
        200,
        "Lấy danh sách vị trí đỗ xe thành công",
        None,
        result,
        request.url.path
    )


@app.get("/parking-slots/{slot_id}")
def get_parking(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    parking = db.query(ParkingModel).filter(
        ParkingModel.id == slot_id
    ).first()

    if parking is None:
        raise HTTPException(
            status_code=404,
            detail="Parking slot not found"
        )

    return response(
        200,
        "Lấy thông tin vị trí đỗ xe thành công",
        None,
        {
            "id": parking.id,
            "slot_code": parking.slot_code,
            "zone_name": parking.zone_name,
            "max_weight": parking.max_weight,
            "is_available": parking.is_available
        },
        request.url.path
    )
