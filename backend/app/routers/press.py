from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models.process import Process, ProcessNameType
from ..models.product import Product
from ..models.customer import Customer
from ..schemas import process as process_schema
from .auth import get_current_user

router = APIRouter()


@router.get("/processes", response_model=List[process_schema.ProcessWithDetailsResponse])
async def get_processes(
    product_id: int = None,
    customer_name: str = None,
    product_code: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    工程一覧を取得（顧客名、製品コード含む）
    customer_name, product_codeで検索可能
    """
    query = db.query(
        Process.process_id,
        Process.product_id,
        Process.process_no,
        Process.process_name,
        Process.rough_cycletime,
        Process.setup_time,
        Process.production_limit,
        Process.timestamp,
        Process.user,
        Customer.customer_name,
        Product.product_code
    ).join(
        Product, Process.product_id == Product.product_id
    ).join(
        Customer, Product.customer_id == Customer.customer_id
    )

    if product_id:
        query = query.filter(Process.product_id == product_id)
    
    if customer_name:
        query = query.filter(Customer.customer_name.contains(customer_name))
    
    if product_code:
        query = query.filter(Product.product_code.contains(product_code))

    processes = query.order_by(Process.timestamp.desc()).offset(skip).limit(limit).all()

    # Convert to dict for response
    result = []
    for p in processes:
        result.append({
            "process_id": p.process_id,
            "product_id": p.product_id,
            "process_no": p.process_no,
            "process_name": p.process_name,
            "rough_cycletime": p.rough_cycletime,
            "setup_time": p.setup_time,
            "production_limit": p.production_limit,
            "timestamp": p.timestamp,
            "user": p.user,
            "customer_name": p.customer_name,
            "product_code": p.product_code
        })

    return result


@router.get("/process-table")
async def get_process_table(
    db: Session = Depends(get_db)
):
    """
    工程表を取得（製品ごとに工程1〜20を横に並べて表示）
    """
    # 製品ごとに工程をグループ化
    products = db.query(
        Product.product_id,
        Product.product_code,
        Customer.customer_name
    ).join(
        Customer, Product.customer_id == Customer.customer_id
    ).filter(
        Product.is_active == True
    ).all()

    result = []
    for product in products:
        # この製品の工程を取得
        processes = db.query(Process).filter(
            Process.product_id == product.product_id
        ).order_by(Process.process_no).all()

        # 工程がない製品はスキップ
        if not processes:
            continue

        # 工程を工程番号ごとに整理（最大20工程）
        process_map = {}
        for proc in processes:
            if proc.process_no <= 20:
                process_map[proc.process_no] = proc.process_name

        product_row = {
            "product_id": product.product_id,
            "customer_name": product.customer_name,
            "product_code": product.product_code,
        }

        # 工程1〜20のフィールドを追加
        for i in range(1, 21):
            product_row[f"process_{i}"] = process_map.get(i, "")

        result.append(product_row)

    return result


@router.post("/processes", response_model=process_schema.ProcessResponse)
async def create_process(
    process: process_schema.ProcessCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    工程登録
    """
    # Validate process_name exists in ProcessNameType
    name_type = db.query(ProcessNameType).filter(
        ProcessNameType.process_name == process.process_name
    ).first()

    if not name_type:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid process name. Please select from the master list.")

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
    工程更新
    """
    db_process = db.query(Process).filter(Process.process_id == process_id).first()
    if not db_process:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Process not found")

    update_data = process.model_dump(exclude_unset=True, exclude_none=False)
    
    # Validate process_name if it's being updated
    if 'process_name' in update_data:
        name_type = db.query(ProcessNameType).filter(
            ProcessNameType.process_name == update_data['process_name']
        ).first()

        if not name_type:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Invalid process name. Please select from the master list.")

    update_data['user'] = current_user['username']

    for key, value in update_data.items():
        setattr(db_process, key, value)

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
    工程削除
    """
    db_process = db.query(Process).filter(Process.process_id == process_id).first()
    if not db_process:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Process not found")

    db.delete(db_process)
    db.commit()
    return {"message": "Process deleted successfully"}


@router.get("/process-name-types", response_model=List[process_schema.ProcessNameTypeResponse])
async def get_process_name_types(
    db: Session = Depends(get_db)
):
    """
    工程名タイプ一覧を取得
    """
    process_types = db.query(ProcessNameType).all()
    return process_types


@router.get("/process-name-type/{process_name:path}")
async def get_process_name_type(
    process_name: str,
    db: Session = Depends(get_db)
):
    """
    工程名から工程タイプ（SPM/DAY）を取得
    """
    process_type = db.query(ProcessNameType).filter(
        ProcessNameType.process_name == process_name
    ).first()

    if process_type:
        return {
            "process_name": process_type.process_name,
            "day_or_spm": process_type.day_or_spm,
            "type_label": "SPM" if process_type.day_or_spm else "DAY"
        }

    # マスターにない場合はデフォルトを返す
    return {
        "process_name": process_name,
        "day_or_spm": None,
        "type_label": "サイクルタイム"
    }


@router.get("/autocomplete/process-names")
async def autocomplete_process_names(
    search: str = "",
    db: Session = Depends(get_db)
):
    """
    工程名のオートコンプリート用エンドポイント
    """
    query = db.query(ProcessNameType)

    if search:
        query = query.filter(ProcessNameType.process_name.like(f"%{search}%"))

    process_types = query.all()

    # AutocompleteInputコンポーネントの形式に合わせる
    return [
        {
            "id": pt.process_name_id,
            "name": pt.process_name,
            "process_name": pt.process_name
        }
        for pt in process_types
    ]
