from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import BrokenMold, Process, Product
from ..schemas import mold as schemas
from ..routers.auth import get_current_user

router = APIRouter()


@router.get("/broken-molds", response_model=List[schemas.BrokenMoldWithDetails])
async def get_broken_molds(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """金型故障一覧を取得"""
    broken_molds = db.query(BrokenMold)\
        .join(Process, BrokenMold.process_id == Process.process_id)\
        .join(Product, Process.product_id == Product.product_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

    # データを整形
    result = []
    for bm in broken_molds:
        process = db.query(Process).filter(Process.process_id == bm.process_id).first()
        product = db.query(Product).filter(Product.product_id == process.product_id).first()

        result.append({
            "broken_mold_id": bm.broken_mold_id,
            "process_id": bm.process_id,
            "date_broken": bm.date_broken,
            "date_hope_repaired": bm.date_hope_repaired,
            "date_schedule_repaired": bm.date_schedule_repaired,
            "note": bm.note,
            "timestamp": bm.timestamp,
            "user": bm.user,
            "product_code": product.product_code,
            "process_name": process.process_name,
            "process_no": process.process_no,
        })

    return result


@router.get("/broken-molds/{broken_mold_id}", response_model=schemas.BrokenMold)
async def get_broken_mold(
    broken_mold_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """金型故障を1件取得"""
    broken_mold = db.query(BrokenMold)\
        .filter(BrokenMold.broken_mold_id == broken_mold_id)\
        .first()

    if not broken_mold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broken mold not found"
        )

    return broken_mold


@router.post("/broken-molds", response_model=schemas.BrokenMold, status_code=status.HTTP_201_CREATED)
async def create_broken_mold(
    broken_mold_data: schemas.BrokenMoldCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """金型故障を登録"""
    # 工程の存在確認
    process = db.query(Process).filter(Process.process_id == broken_mold_data.process_id).first()
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found"
        )

    new_broken_mold = BrokenMold(
        **broken_mold_data.dict(),
        user=current_user["username"]
    )

    db.add(new_broken_mold)
    db.commit()
    db.refresh(new_broken_mold)

    return new_broken_mold


@router.put("/broken-molds/{broken_mold_id}", response_model=schemas.BrokenMold)
async def update_broken_mold(
    broken_mold_id: int,
    broken_mold_data: schemas.BrokenMoldUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """金型故障を更新"""
    broken_mold = db.query(BrokenMold)\
        .filter(BrokenMold.broken_mold_id == broken_mold_id)\
        .first()

    if not broken_mold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broken mold not found"
        )

    # 更新データを適用
    update_data = broken_mold_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(broken_mold, key, value)

    broken_mold.user = current_user["username"]

    db.commit()
    db.refresh(broken_mold)

    return broken_mold


@router.delete("/broken-molds/{broken_mold_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_broken_mold(
    broken_mold_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """金型故障を削除"""
    broken_mold = db.query(BrokenMold)\
        .filter(BrokenMold.broken_mold_id == broken_mold_id)\
        .first()

    if not broken_mold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broken mold not found"
        )

    db.delete(broken_mold)
    db.commit()

    return None
