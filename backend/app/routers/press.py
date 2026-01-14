from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import traceback
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
    try:
        query = db.query(
            Process.process_id,
            Process.product_id,
            Process.process_no,
            ProcessNameType.process_name,
            Process.rough_cycletime,
            Process.setup_time,
            Process.production_limit,
            Process.cavity,
            Process.timestamp,
            Process.user,
            Customer.customer_name,
            Product.product_code
        ).join(
            ProcessNameType, Process.process_name_id == ProcessNameType.process_name_id
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
                "cavity": p.cavity,
                "timestamp": p.timestamp,
                "user": p.user,
                "customer_name": p.customer_name,
                "product_code": p.product_code
            })

        return result
    except Exception as e:
        print(f"Error in get_processes: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/process-table")
async def get_process_table(
    db: Session = Depends(get_db)
):
    """
    工程表を取得（製品ごとに工程1〜20を横に並べて表示）
    N+1クエリ問題を解消: 1回のJOINクエリで全データ取得
    """
    try:
        # 1回のクエリで全データを取得（N+1問題解消）
        query = db.query(
            Product.product_id,
            Product.product_code,
            Customer.customer_name,
            Process.process_no,
            ProcessNameType.process_name,
            Process.rough_cycletime
        ).join(
            Customer, Product.customer_id == Customer.customer_id
        ).join(
            Process, Product.product_id == Process.product_id
        ).join(
            ProcessNameType, Process.process_name_id == ProcessNameType.process_name_id
        ).filter(
            Product.is_active == True,
            Process.process_no != None,
            Process.process_no <= 20
        ).order_by(Product.product_id, Process.process_no).all()

        # Pythonで製品ごとにグループ化
        product_map = {}
        for row in query:
            product_id = row.product_id

            if product_id not in product_map:
                product_map[product_id] = {
                    "product_id": product_id,
                    "customer_name": row.customer_name,
                    "product_code": row.product_code,
                }
                # 工程1〜20のフィールドを初期化
                for i in range(1, 21):
                    product_map[product_id][f"process_{i}"] = ""
                    product_map[product_id][f"rough_cycletime_{i}"] = None

            # 工程名とrough_cycletimeをセット
            if row.process_no is not None:
                product_map[product_id][f"process_{row.process_no}"] = row.process_name or ""
                product_map[product_id][f"rough_cycletime_{row.process_no}"] = row.rough_cycletime

        return list(product_map.values())
    except Exception as e:
        print(f"Error in get_process_table: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/processes", response_model=process_schema.ProcessResponse)
async def create_process(
    process: process_schema.ProcessCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    工程登録
    """
    # Validate process_name exists in ProcessNameType and get the ID
    name_type = db.query(ProcessNameType).filter(
        ProcessNameType.process_name == process.process_name
    ).first()

    if not name_type:
        raise HTTPException(status_code=400, detail="Invalid process name. Please select from the master list.")

    process_data = process.model_dump()
    # Replace process_name with process_name_id
    del process_data['process_name']
    process_data['process_name_id'] = name_type.process_name_id
    process_data['user'] = current_user['username']

    db_process = Process(**process_data)
    db.add(db_process)
    db.commit()
    db.refresh(db_process)

    # Return with process_name for frontend compatibility
    return {
        "process_id": db_process.process_id,
        "product_id": db_process.product_id,
        "process_no": db_process.process_no,
        "process_name": name_type.process_name,
        "rough_cycletime": db_process.rough_cycletime,
        "setup_time": db_process.setup_time,
        "production_limit": db_process.production_limit,
        "cavity": db_process.cavity,
        "timestamp": db_process.timestamp,
        "user": db_process.user
    }


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
        raise HTTPException(status_code=404, detail="Process not found")

    update_data = process.model_dump(exclude_unset=True, exclude_none=False)

    # Validate process_name if it's being updated and convert to process_name_id
    name_type = None
    if 'process_name' in update_data:
        name_type = db.query(ProcessNameType).filter(
            ProcessNameType.process_name == update_data['process_name']
        ).first()

        if not name_type:
            raise HTTPException(status_code=400, detail="Invalid process name. Please select from the master list.")

        # Replace process_name with process_name_id
        del update_data['process_name']
        update_data['process_name_id'] = name_type.process_name_id

    update_data['user'] = current_user['username']

    for key, value in update_data.items():
        setattr(db_process, key, value)

    db.commit()
    db.refresh(db_process)

    # Get the process_name for the response
    if not name_type:
        name_type = db.query(ProcessNameType).filter(
            ProcessNameType.process_name_id == db_process.process_name_id
        ).first()

    return {
        "process_id": db_process.process_id,
        "product_id": db_process.product_id,
        "process_no": db_process.process_no,
        "process_name": name_type.process_name if name_type else "",
        "rough_cycletime": db_process.rough_cycletime,
        "setup_time": db_process.setup_time,
        "production_limit": db_process.production_limit,
        "cavity": db_process.cavity,
        "timestamp": db_process.timestamp,
        "user": db_process.user
    }


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
