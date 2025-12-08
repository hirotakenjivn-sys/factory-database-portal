from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import date
from ..database import get_db
from ..models.process import Process
from ..models.product import Product
from ..models.customer import Customer
from ..schemas import process as process_schema
from .auth import get_current_user

router = APIRouter()


@router.get("/processes", response_model=List[process_schema.ProcessWithDetailsResponse])
async def get_processes(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    工程一覧を取得（検索機能付き）
    - product_idで製品の工程を絞り込み
    - searchで製品コードまたは顧客名で検索
    """
    # JOINを使用してProduct、Customerと結合
    query = db.query(
        Process,
        Product.product_code,
        Customer.customer_name
    ).join(Product, Process.product_id == Product.product_id).join(Customer, Product.customer_id == Customer.customer_id)

    # 製品IDでフィルタ
    if product_id:
        query = query.filter(Process.product_id == product_id)

    # 製品コードまたは顧客名で検索
    if search:
        query = query.filter(
            (Product.product_code.like(f"%{search}%")) |
            (Customer.customer_name.like(f"%{search}%"))
        )

    # 工程番号順でソート
    query = query.order_by(Product.product_id, Process.process_no)

    results = query.offset(skip).limit(limit).all()

    # データを整形
    processes = []
    for process, product_code, customer_name in results:
        process_dict = process.__dict__.copy()
        process_dict['product_code'] = product_code
        process_dict['customer_name'] = customer_name
        processes.append(process_dict)

    return processes


@router.get("/processes/{process_id}", response_model=process_schema.ProcessWithDetailsResponse)
async def get_process(
    process_id: int,
    db: Session = Depends(get_db)
):
    """
    指定した工程の詳細を取得
    """
    result = db.query(
        Process,
        Product.product_code,
        Customer.customer_name
    ).join(Product, Process.product_id == Product.product_id).join(Customer, Product.customer_id == Customer.customer_id).filter(Process.process_id == process_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Process not found")

    process, product_code, customer_name = result
    process_dict = process.__dict__.copy()
    process_dict['product_code'] = product_code
    process_dict['customer_name'] = customer_name

    return process_dict


@router.post("/processes", response_model=process_schema.ProcessResponse)
async def create_process(
    process: process_schema.ProcessCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    工程を登録
    """
    # 製品の存在確認
    product = db.query(Product).filter(Product.product_id == process.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 同じ製品の同じ工程番号が既に存在するか確認
    existing_process = db.query(Process).filter(
        Process.product_id == process.product_id,
        Process.process_no == process.process_no
    ).first()
    if existing_process:
        raise HTTPException(
            status_code=400,
            detail=f"Process No.{process.process_no} already exists for this product"
        )

    process_data = process.model_dump()
    process_data['user'] = current_user['username']
    db_process = Process(**process_data)
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process


@router.put("/processes/{process_id}", response_model=process_schema.ProcessResponse)
async def update_process(
    process_id: int,
    process: process_schema.ProcessUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    工程を更新
    """
    db_process = db.query(Process).filter(Process.process_id == process_id).first()
    if not db_process:
        raise HTTPException(status_code=404, detail="Process not found")

    # 更新データを適用
    for key, value in process.model_dump(exclude_unset=True).items():
        if key != 'user':  # userは別で設定
            setattr(db_process, key, value)

    db_process.user = current_user['username']
    db.commit()
    db.refresh(db_process)
    return db_process


@router.delete("/processes/{process_id}")
async def delete_process(
    process_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    工程を削除
    """
    db_process = db.query(Process).filter(Process.process_id == process_id).first()
    if not db_process:
        raise HTTPException(status_code=404, detail="Process not found")

    db.delete(db_process)
    db.commit()

    return {"message": "Process deleted successfully", "process_id": process_id}


@router.get("/list", response_model=List[process_schema.ProcessResponse])
async def get_all_processes(
    db: Session = Depends(get_db)
):
    """
    全工程を取得（シンプルな一覧）
    """
    processes = db.query(Process).order_by(Process.product_id, Process.process_no).all()
    return processes


@router.get("/products/{product_id}/processes", response_model=List[process_schema.ProcessResponse])
async def get_product_processes(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    指定した製品の全工程を取得（工程番号順）
    """
    # 製品の存在確認
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 工程を工程番号順で取得
    processes = db.query(Process).filter(
        Process.product_id == product_id
    ).order_by(Process.process_no).all()

    return processes
