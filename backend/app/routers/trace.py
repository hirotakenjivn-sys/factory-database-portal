from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from ..database import get_db
from ..models.trace import StampTrace, OutsourceTrace
from ..models.product import Product
from ..models.customer import Customer
from ..models.lot import Lot
from ..models.po import PO
from ..models.process import Process
from ..models.employee import Employee
from ..models.supplier import Supplier
from ..schemas.trace import (
    TraceDetailResponse,
    TraceSearchRequest,
    StampTraceResponse,
    OutsourceTraceResponse,
    StampTraceCreate,
)

router = APIRouter()


@router.post("/search", response_model=TraceDetailResponse)
async def search_trace(
    request: TraceSearchRequest,
    db: Session = Depends(get_db)
):
    """
    トレース情報を検索する

    Parameters:
    - search_type: 'product' (製品番号), 'lot' (ロット番号), 'po' (PO番号)
    - search_value: 検索値
    """

    # 検索タイプに応じてLot/Product/POを取得
    lot = None
    product = None
    po = None
    customer = None

    if request.search_type == "product":
        # 製品コードから製品を検索
        product = db.query(Product).join(
            Customer, Product.customer_id == Customer.customer_id
        ).filter(Product.product_code == request.search_value).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        customer = product.customer

        # この製品に関連するトレースを取得（最初のロットを使用）
        stamp_trace = db.query(StampTrace).join(
            Lot, StampTrace.lot_id == Lot.lot_id
        ).filter(Lot.product_id == product.product_id).first()

        if stamp_trace:
            lot = stamp_trace.lot
            if stamp_trace.po_id:
                po = db.query(PO).filter(PO.po_id == stamp_trace.po_id).first()

    elif request.search_type == "lot":
        # ロット番号からロットを検索
        lot = db.query(Lot).join(
            Product, Lot.product_id == Product.product_id
        ).join(
            Customer, Product.customer_id == Customer.customer_id
        ).filter(Lot.lot_number == request.search_value).first()

        if not lot:
            raise HTTPException(status_code=404, detail="Lot not found")

        product = lot.product
        customer = product.customer

        # このロットに関連するPOを取得（もしあれば）
        stamp_trace = db.query(StampTrace).filter(
            StampTrace.lot_id == lot.lot_id,
            StampTrace.po_id != None
        ).first()

        if stamp_trace and stamp_trace.po_id:
            po = db.query(PO).filter(PO.po_id == stamp_trace.po_id).first()

    elif request.search_type == "po":
        # PO番号からPOを検索
        po = db.query(PO).join(
            Product, PO.product_id == Product.product_id
        ).join(
            Customer, Product.customer_id == Customer.customer_id
        ).filter(PO.po_number == request.search_value).first()

        if not po:
            raise HTTPException(status_code=404, detail="PO not found")

        product = po.product
        customer = product.customer

        # このPOに関連するロットを取得
        stamp_trace = db.query(StampTrace).filter(
            StampTrace.po_id == po.po_id
        ).join(Lot, StampTrace.lot_id == Lot.lot_id).first()

        if stamp_trace:
            lot = stamp_trace.lot

    else:
        raise HTTPException(status_code=400, detail="Invalid search type")

    # トレースが見つからない場合
    if not lot:
        raise HTTPException(status_code=404, detail="Trace data not found")

    # 内製トレースを取得
    stamp_traces_query = db.query(StampTrace).filter(
        StampTrace.lot_id == lot.lot_id
    )

    # POが指定されている場合は、そのPOに関連するトレースのみ取得
    if po:
        stamp_traces_query = stamp_traces_query.filter(
            or_(StampTrace.po_id == po.po_id, StampTrace.po_id == None)
        )

    stamp_traces = stamp_traces_query.options(
        joinedload(StampTrace.employee),
        joinedload(StampTrace.process)
    ).all()

    # 外注トレースを取得
    outsource_traces_query = db.query(OutsourceTrace).filter(
        OutsourceTrace.lot_id == lot.lot_id
    )

    if po:
        outsource_traces_query = outsource_traces_query.filter(
            or_(OutsourceTrace.po_id == po.po_id, OutsourceTrace.po_id == None)
        )

    outsource_traces = outsource_traces_query.options(
        joinedload(OutsourceTrace.supplier),
        joinedload(OutsourceTrace.process)
    ).all()

    # レスポンスの整形
    stamp_trace_responses = []
    for st in stamp_traces:
        stamp_trace_responses.append(StampTraceResponse(
            stamp_trace_id=st.stamp_trace_id,
            lot_id=st.lot_id,
            process_id=st.process_id,
            po_id=st.po_id,
            employee_id=st.employee_id,
            ok_quantity=st.ok_quantity,
            ng_quantity=st.ng_quantity,
            result=st.result,
            date=st.date,
            note=st.note,
            timestamp=st.timestamp,
            user=st.user,
            employee_name=st.employee.name if st.employee else None,
            process_name=st.process.process_name if st.process else None
        ))

    outsource_trace_responses = []
    for ot in outsource_traces:
        outsource_trace_responses.append(OutsourceTraceResponse(
            outsource_trace_id=ot.outsource_trace_id,
            lot_id=ot.lot_id,
            process_id=ot.process_id,
            po_id=ot.po_id,
            supplier_id=ot.supplier_id,
            ok_quantity=ot.ok_quantity,
            ng_quantity=ot.ng_quantity,
            date=ot.date,
            note=ot.note,
            timestamp=ot.timestamp,
            user=ot.user,
            supplier_name=ot.supplier.supplier_name if ot.supplier else None,
            process_name=ot.process.process_name if ot.process else None
        ))

    return TraceDetailResponse(
        product_code=product.product_code,
        product_id=product.product_id,
        customer_name=customer.customer_name,
        lot_number=lot.lot_number,
        lot_id=lot.lot_id,
        po_number=po.po_number if po else "",
        po_id=po.po_id if po else 0,
        delivery_date=po.delivery_date if po else date.today(),
        po_quantity=po.po_quantity if po else 0,
        stamp_traces=stamp_trace_responses,
        outsource_traces=outsource_trace_responses
    )


@router.post("/stamp-trace", response_model=StampTraceResponse)
async def create_stamp_trace(
    trace: StampTraceCreate,
    db: Session = Depends(get_db)
):
    """
    内製トレースを登録する
    """
    # 新しいトレースを作成
    new_trace = StampTrace(
        lot_id=trace.lot_id,
        process_id=trace.process_id,
        po_id=trace.po_id,
        employee_id=trace.employee_id,
        ok_quantity=trace.ok_quantity,
        ng_quantity=trace.ng_quantity,
        result=trace.result,
        date=trace.date,
        note=trace.note,
        user=trace.user or "system"
    )

    db.add(new_trace)
    db.commit()
    db.refresh(new_trace)

    # 関連データを取得してレスポンスを作成
    trace_with_relations = db.query(StampTrace).filter(
        StampTrace.stamp_trace_id == new_trace.stamp_trace_id
    ).options(
        joinedload(StampTrace.employee),
        joinedload(StampTrace.process)
    ).first()

    return StampTraceResponse(
        stamp_trace_id=trace_with_relations.stamp_trace_id,
        lot_id=trace_with_relations.lot_id,
        process_id=trace_with_relations.process_id,
        po_id=trace_with_relations.po_id,
        employee_id=trace_with_relations.employee_id,
        ok_quantity=trace_with_relations.ok_quantity,
        ng_quantity=trace_with_relations.ng_quantity,
        result=trace_with_relations.result,
        date=trace_with_relations.date,
        note=trace_with_relations.note,
        timestamp=trace_with_relations.timestamp,
        user=trace_with_relations.user,
        employee_name=trace_with_relations.employee.name if trace_with_relations.employee else None,
        process_name=trace_with_relations.process.process_name if trace_with_relations.process else None
    )


class StampTraceSimpleRequest(BaseModel):
    product_id: int
    lot_number: str
    process_id: int
    employee_id: int
    ok_quantity: int
    ng_quantity: int
    result: str
    date: date
    note: Optional[str] = None


@router.post("/stamp-trace-simple")
async def create_stamp_trace_simple(
    request: StampTraceSimpleRequest,
    db: Session = Depends(get_db)
):
    """
    シンプルな内製トレース登録（POなし）
    製品ID、ロット番号、工程IDから直接トレースを登録
    """
    # ロットを取得または作成
    lot = db.query(Lot).filter(
        Lot.lot_number == request.lot_number,
        Lot.product_id == request.product_id
    ).first()

    if not lot:
        # 新しいロットを作成
        try:
            lot = Lot(
                lot_number=request.lot_number,
                product_id=request.product_id,
                date_created=request.date,
                user="system"
            )
            db.add(lot)
            db.commit()
            db.refresh(lot)
        except Exception as e:
            # ロット作成に失敗した場合（重複など）、ロールバックして再取得
            db.rollback()
            # 別のトランザクションで既に作成された可能性があるため再検索
            lot = db.query(Lot).filter(
                Lot.lot_number == request.lot_number,
                Lot.product_id == request.product_id
            ).first()
            
            # それでも見つからない場合は、lot_numberのみで検索
            if not lot:
                lot = db.query(Lot).filter(
                    Lot.lot_number == request.lot_number
                ).first()
            
            # まだ見つからない場合はエラーを返す
            if not lot:
                raise HTTPException(
                    status_code=400,
                    detail=f"ロット '{request.lot_number}' の作成に失敗しました: {str(e)}"
                )

    # 工程情報を取得してdoneフラグを判定
    process = db.query(Process).filter(Process.process_id == request.process_id).first()
    is_done = False
    if process:
        process_name_upper = process.process_name.upper()
        if ("PACKING" in process_name_upper or "梱包" in process_name_upper) and request.result == "pass":
            is_done = True

    # トレースを作成
    new_trace = StampTrace(
        lot_id=lot.lot_id,
        process_id=request.process_id,
        po_id=None,  # POなし
        employee_id=request.employee_id,
        ok_quantity=request.ok_quantity,
        ng_quantity=request.ng_quantity,
        result=request.result,
        date=request.date,
        note=request.note,
        user="system",
        done=is_done
    )

    db.add(new_trace)
    db.commit()
    db.refresh(new_trace)

    return {"message": "Stamp trace created successfully", "stamp_trace_id": new_trace.stamp_trace_id}


class OutsourceTraceSimpleRequest(BaseModel):
    product_id: int
    lot_number: str
    process_id: int
    supplier_name: str
    ok_quantity: int
    ng_quantity: int
    date: date
    note: Optional[str] = None


@router.post("/outsource-trace-simple")
async def create_outsource_trace_simple(
    request: OutsourceTraceSimpleRequest,
    db: Session = Depends(get_db)
):
    """
    シンプルな委託トレース登録（POなし）
    製品ID、ロット番号、工程ID、サプライヤー名から直接トレースを登録
    """
    # ロットを取得または作成
    lot = db.query(Lot).filter(
        Lot.lot_number == request.lot_number,
        Lot.product_id == request.product_id
    ).first()

    if not lot:
        # 新しいロットを作成
        lot = Lot(
            lot_number=request.lot_number,
            product_id=request.product_id,
            date_created=request.date,
            user="system"
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)

    # サプライヤーを取得
    supplier = db.query(Supplier).filter(
        Supplier.supplier_name == request.supplier_name
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=400,
            detail=f"サプライヤー '{request.supplier_name}' が見つかりません。サプライヤーマスタに登録してください。"
        )

    # トレースを作成
    new_trace = OutsourceTrace(
        lot_id=lot.lot_id,
        process_id=request.process_id,
        po_id=None,  # POなし
        supplier_id=supplier.supplier_id,
        ok_quantity=request.ok_quantity,
        ng_quantity=request.ng_quantity,
        date=request.date,
        note=request.note,
        user="system"
    )

    db.add(new_trace)
    db.commit()
    db.refresh(new_trace)

    return {"message": "Outsource trace created successfully", "outsource_trace_id": new_trace.outsource_trace_id}


@router.get("/stamp-traces")
async def get_stamp_traces(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """内製トレース一覧を取得（詳細情報含む）"""
    stamp_traces = db.query(StampTrace).options(
        joinedload(StampTrace.employee),
        joinedload(StampTrace.process),
        joinedload(StampTrace.po),
        joinedload(StampTrace.lot).joinedload(Lot.product)
    ).order_by(desc(StampTrace.date), desc(StampTrace.stamp_trace_id)).offset(skip).limit(limit).all()

    responses = []
    for st in stamp_traces:
        responses.append({
            "stamp_trace_id": st.stamp_trace_id,
            "lot_id": st.lot_id,
            "process_id": st.process_id,
            "po_id": st.po_id,
            "employee_id": st.employee_id,
            "ok_quantity": st.ok_quantity,
            "ng_quantity": st.ng_quantity,
            "result": st.result,
            "date": st.date,
            "note": st.note,
            "timestamp": st.timestamp,
            "user": st.user,
            "employee_name": st.employee.name if st.employee else None,
            "process_name": st.process.process_name if st.process else None,
            "po_number": st.po.po_number if st.po else None,
            "lot_number": st.lot.lot_number if st.lot else None,
            "product_code": st.lot.product.product_code if st.lot and st.lot.product else None,
            "done": st.done
        })

    return responses


@router.get("/outsource-traces")
async def get_outsource_traces(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """外注トレース一覧を取得（詳細情報含む）"""
    outsource_traces = db.query(OutsourceTrace).options(
        joinedload(OutsourceTrace.supplier),
        joinedload(OutsourceTrace.process),
        joinedload(OutsourceTrace.po),
        joinedload(OutsourceTrace.lot).joinedload(Lot.product)
    ).order_by(desc(OutsourceTrace.date), desc(OutsourceTrace.outsource_trace_id)).offset(skip).limit(limit).all()

    responses = []
    for ot in outsource_traces:
        responses.append({
            "outsource_trace_id": ot.outsource_trace_id,
            "lot_id": ot.lot_id,
            "process_id": ot.process_id,
            "po_id": ot.po_id,
            "supplier_id": ot.supplier_id,
            "ok_quantity": ot.ok_quantity,
            "ng_quantity": ot.ng_quantity,
            "date": ot.date,
            "note": ot.note,
            "timestamp": ot.timestamp,
            "user": ot.user,
            "supplier_name": ot.supplier.supplier_name if ot.supplier else None,
            "process_name": ot.process.process_name if ot.process else None,
            "po_number": ot.po.po_number if ot.po else None,
            "lot_number": ot.lot.lot_number if ot.lot else None,
            "product_code": ot.lot.product.product_code if ot.lot and ot.lot.product else None
        })

    return responses


@router.get("/incomplete-traces")
async def get_incomplete_traces(
    product_code: Optional[str] = None,
    process_id: Optional[int] = None,
    lot_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    梱包未完了トレース（done = false）を取得
    
    Parameters:
    - product_code: 製品コードでフィルタ（オプション）
    - process_id: 工程IDでフィルタ（オプション）
    - lot_number: ロット番号でフィルタ（オプション）
    
    Returns:
    - 未完了トレースのリスト
    """
    query = db.query(StampTrace).filter(
        StampTrace.done == False
    ).options(
        joinedload(StampTrace.employee),
        joinedload(StampTrace.process),
        joinedload(StampTrace.lot).joinedload(Lot.product).joinedload(Product.customer)
    )
    
    # 製品コードでフィルタ
    if product_code:
        query = query.join(Lot).join(Product).filter(
            Product.product_code == product_code
        )
    
    # 工程IDでフィルタ
    if process_id:
        query = query.filter(StampTrace.process_id == process_id)
    
    # ロット番号でフィルタ
    if lot_number:
        query = query.join(Lot).filter(Lot.lot_number == lot_number)
    
    # 最新順にソート
    traces = query.order_by(desc(StampTrace.timestamp)).all()
    
    responses = []
    for st in traces:
        product = None
        customer_name = None
        if st.lot and st.lot.product:
            product = st.lot.product
            if product.customer:
                customer_name = product.customer.customer_name
        
        responses.append({
            "stamp_trace_id": st.stamp_trace_id,
            "timestamp": st.timestamp,
            "product_code": product.product_code if product else None,
            "lot_number": st.lot.lot_number if st.lot else None,
            "process_name": st.process.process_name if st.process else None,
            "employee_name": st.employee.name if st.employee else None,
            "ok_quantity": st.ok_quantity,
            "ng_quantity": st.ng_quantity,
            "result": st.result,
            "note": st.note,
            "customer_name": customer_name,
            "date": st.date
        })
    
    return responses

