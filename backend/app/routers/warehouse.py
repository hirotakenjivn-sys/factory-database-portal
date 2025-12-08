from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import FinishedProduct, Product, Lot, Customer
from ..schemas import warehouse as schemas
from ..routers.auth import get_current_user

router = APIRouter()


@router.get("/finished-products", response_model=List[schemas.FinishedProductWithDetails])
async def get_finished_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """完成品一覧を取得"""
    finished_products = db.query(FinishedProduct)\
        .join(Product, FinishedProduct.product_id == Product.product_id)\
        .join(Lot, FinishedProduct.lot_id == Lot.lot_id)\
        .join(Customer, Product.customer_id == Customer.customer_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

    # データを整形
    result = []
    for fp in finished_products:
        result.append({
            "finished_product_id": fp.finished_product_id,
            "product_id": fp.product_id,
            "lot_id": fp.lot_id,
            "finished_quantity": fp.finished_quantity,
            "date_finished": fp.date_finished,
            "timestamp": fp.timestamp,
            "user": fp.user,
            "product_code": fp.product.product_code,
            "lot_number": fp.lot.lot_number,
            "customer_name": fp.product.customer.customer_name,
        })

    return result


@router.get("/finished-products/{finished_product_id}", response_model=schemas.FinishedProduct)
async def get_finished_product(
    finished_product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """完成品を1件取得"""
    finished_product = db.query(FinishedProduct)\
        .filter(FinishedProduct.finished_product_id == finished_product_id)\
        .first()

    if not finished_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finished product not found"
        )

    return finished_product


@router.post("/finished-products", response_model=schemas.FinishedProduct, status_code=status.HTTP_201_CREATED)
async def create_finished_product(
    finished_product_data: schemas.FinishedProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """完成品を登録"""
    # 製品とロットの存在確認
    product = db.query(Product).filter(Product.product_id == finished_product_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    lot = db.query(Lot).filter(Lot.lot_id == finished_product_data.lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lot not found"
        )

    new_finished_product = FinishedProduct(
        **finished_product_data.dict(),
        user=current_user["username"]
    )

    db.add(new_finished_product)
    db.commit()
    db.refresh(new_finished_product)

    return new_finished_product


@router.put("/finished-products/{finished_product_id}", response_model=schemas.FinishedProduct)
async def update_finished_product(
    finished_product_id: int,
    finished_product_data: schemas.FinishedProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """完成品を更新"""
    finished_product = db.query(FinishedProduct)\
        .filter(FinishedProduct.finished_product_id == finished_product_id)\
        .first()

    if not finished_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finished product not found"
        )

    # 更新データを適用
    update_data = finished_product_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(finished_product, key, value)

    finished_product.user = current_user["username"]

    db.commit()
    db.refresh(finished_product)

    return finished_product


@router.delete("/finished-products/{finished_product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finished_product(
    finished_product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """完成品を削除"""
    finished_product = db.query(FinishedProduct)\
        .filter(FinishedProduct.finished_product_id == finished_product_id)\
        .first()

    if not finished_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finished product not found"
        )

    db.delete(finished_product)
    db.commit()

    return None
