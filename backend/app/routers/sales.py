from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional
from datetime import date, datetime
import csv
import io
from ..database import get_db
from ..models.po import PO, DeletedPO
from ..models.product import Product
from ..models.customer import Customer
from ..schemas import po as po_schema
from .auth import get_current_user
from ..utils.delivery_calculator import calculate_delivery_date

router = APIRouter()


@router.get("/po", response_model=List[po_schema.POResponse])
async def get_pos(
    skip: int = 0,
    limit: int = 30,
    po_number: Optional[str] = None,
    customer_name: Optional[str] = None,
    product_code: Optional[str] = None,
    delivery_date_from: Optional[date] = None,
    delivery_date_to: Optional[date] = None,
    is_delivered: Optional[bool] = Query(False, description="配送済みフラグ（デフォルトfalse=未配送のみ表示）"),
    sort_by: Optional[str] = Query("timestamp_desc", description="ソート順: timestamp_desc, timestamp_asc, delivery_date_asc, delivery_date_desc"),
    db: Session = Depends(get_db)
):
    """
    PO一覧を取得（検索機能付き）
    - デフォルトでは配送済みでないものだけを表示
    - 登録時間の降順でソート（最新が上）
    """
    # JOINを使用してProduct、Customerと結合し、必要なフィールドを選択
    query = db.query(
        PO,
        Product.product_code,
        Customer.customer_name
    ).join(Product, PO.product_id == Product.product_id).join(Customer, Product.customer_id == Customer.customer_id)

    # 配送済みフィルター
    query = query.filter(PO.is_delivered == is_delivered)

    # PO番号での検索（部分一致）
    if po_number:
        query = query.filter(PO.po_number.like(f"%{po_number}%"))

    # 顧客名での検索（部分一致）
    if customer_name:
        query = query.filter(Customer.customer_name.like(f"%{customer_name}%"))

    # 製品コードでの検索（部分一致）
    if product_code:
        query = query.filter(Product.product_code.like(f"%{product_code}%"))

    # 納期範囲での検索
    if delivery_date_from:
        query = query.filter(PO.delivery_date >= delivery_date_from)
    if delivery_date_to:
        query = query.filter(PO.delivery_date <= delivery_date_to)

    # ソート
    if sort_by == "timestamp_desc":
        query = query.order_by(desc(PO.timestamp))
    elif sort_by == "timestamp_asc":
        query = query.order_by(asc(PO.timestamp))
    elif sort_by == "delivery_date_asc":
        query = query.order_by(asc(PO.delivery_date))
    elif sort_by == "delivery_date_desc":
        query = query.order_by(desc(PO.delivery_date))
    else:
        # デフォルトは登録時間の降順
        query = query.order_by(desc(PO.timestamp))

    results = query.offset(skip).limit(limit).all()

    # POオブジェクトに追加データを設定
    pos = []
    for po, product_code, customer_name in results:
        po_dict = po.__dict__.copy()
        po_dict['product_code'] = product_code
        po_dict['customer_name'] = customer_name
        pos.append(po_dict)

    return pos


@router.post("/po", response_model=po_schema.POResponse)
async def create_po(
    po: po_schema.POCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    PO登録
    """
    po_data = po.model_dump()
    po_data['user'] = current_user['username']
    db_po = PO(**po_data)
    db.add(db_po)
    db.commit()
    db.refresh(db_po)
    return db_po


@router.put("/po/{po_id}", response_model=po_schema.POResponse)
async def update_po(
    po_id: int,
    po: po_schema.POUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    PO更新
    """
    db_po = db.query(PO).filter(PO.po_id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="PO not found")

    for key, value in po.model_dump(exclude_unset=True).items():
        setattr(db_po, key, value)

    db_po.user = current_user['username']
    db.commit()
    db.refresh(db_po)
    return db_po


@router.delete("/po/{po_id}")
async def delete_po(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    PO削除（DeletedPOテーブルに移動）
    """
    db_po = db.query(PO).filter(PO.po_id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="PO not found")

    # DeletedPOテーブルにデータを移動
    deleted_po = DeletedPO(
        po_id=db_po.po_id,
        po_number=db_po.po_number,
        product_id=db_po.product_id,
        delivery_date=db_po.delivery_date,
        date_receive_po=db_po.date_receive_po,
        po_quantity=db_po.po_quantity,
        is_delivered=db_po.is_delivered,
        original_timestamp=db_po.timestamp,
        original_user=db_po.user,
        deleted_by_user=current_user['username']
    )
    db.add(deleted_po)

    # 元のPOを削除
    db.delete(db_po)
    db.commit()

    return {"message": "PO deleted successfully", "po_id": po_id}


@router.get("/po/deleted", response_model=List[po_schema.DeletedPOResponse])
async def get_deleted_pos(
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """
    削除されたPO一覧を取得
    - 削除時間の降順でソート（最新が上）
    """
    deleted_pos = db.query(DeletedPO).order_by(desc(DeletedPO.deleted_timestamp)).offset(skip).limit(limit).all()
    return deleted_pos


@router.post("/po/csv/validate")
async def validate_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    CSVファイルをアップロードしてバリデーション
    - 製品コード、顧客名の存在チェック
    - データ型の検証
    - エラーがある行をハイライト

    CSVフォーマット（ヘッダーなし、6カラム固定）:
    po_number,product_code,customer_name,po_quantity,date_receive_po,delivery_date
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSVファイルのみアップロード可能です")

    try:
        # CSVファイルを読み込み
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')  # BOM対応
        csv_file = io.StringIO(decoded)
        csv_reader = csv.reader(csv_file)

        validated_data = []
        row_number = 0

        # カラムの定義（ヘッダーなしの場合の順序）
        column_names = ['po_number', 'product_code', 'customer_name', 'po_quantity', 'date_receive_po', 'delivery_date']

        for row in csv_reader:
            row_number += 1

            # 空行をスキップ
            if not row or all(cell.strip() == '' for cell in row):
                continue

            # カラム数チェック
            if len(row) != 6:
                raise HTTPException(
                    status_code=400,
                    detail=f"行{row_number}: カラム数が不正です（期待: 6カラム、実際: {len(row)}カラム）\n"
                           f"フォーマット: po_number,product_code,customer_name,po_quantity,date_receive_po,delivery_date"
                )

            errors = {}
            validated_row = {
                'row_number': row_number,
                'po_number': row[0].strip() if len(row) > 0 else '',
                'product_code': row[1].strip() if len(row) > 1 else '',
                'customer_name': row[2].strip() if len(row) > 2 else '',
                'po_quantity': row[3].strip() if len(row) > 3 else '',
                'date_receive_po': row[4].strip() if len(row) > 4 else '',
                'delivery_date': row[5].strip() if len(row) > 5 else '',
            }

            # 1. 必須フィールドチェック
            for field in column_names:
                if not validated_row[field]:
                    errors[field] = f"{field}が空です"

            # 2. 製品コードの存在チェック
            product = None
            if validated_row['product_code']:
                product = db.query(Product).filter(
                    Product.product_code == validated_row['product_code']
                ).first()
                if not product:
                    errors['product_code'] = "製品コードがデータベースに存在しません"
                else:
                    validated_row['product_id'] = product.product_id

            # 3. 顧客名の存在チェック（製品に紐づく顧客と一致するか）
            if validated_row['customer_name'] and product:
                customer = db.query(Customer).filter(
                    Customer.customer_id == product.customer_id
                ).first()
                if not customer:
                    errors['customer_name'] = "顧客がデータベースに存在しません"
                elif customer.customer_name != validated_row['customer_name']:
                    errors['customer_name'] = f"製品コードの顧客名が一致しません（正: {customer.customer_name}）"
            elif validated_row['customer_name']:
                # 製品がない場合は顧客名だけでも検証
                customer = db.query(Customer).filter(
                    Customer.customer_name == validated_row['customer_name']
                ).first()
                if not customer:
                    errors['customer_name'] = "顧客名がデータベースに存在しません"

            # 4. 数量の検証
            if validated_row['po_quantity']:
                try:
                    quantity = int(validated_row['po_quantity'])
                    if quantity <= 0:
                        errors['po_quantity'] = "数量は1以上の整数である必要があります"
                    validated_row['po_quantity_int'] = quantity
                except ValueError:
                    errors['po_quantity'] = "数量は整数である必要があります"

            # 5. 日付の検証（複数フォーマットに対応、DD/MM/YYYYを優先）
            date_formats = [
                '%d/%m/%Y',      # 10/11/2025 (DD/MM/YYYY) - 優先フォーマット
                '%Y-%m-%d',      # 2025-11-10
                '%m/%d/%Y',      # 11/10/2025
                '%Y/%m/%d',      # 2025/11/10
            ]

            for date_field in ['date_receive_po', 'delivery_date']:
                if validated_row[date_field]:
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(validated_row[date_field], fmt).date()
                            # YYYY-MM-DD形式に統一
                            validated_row[f'{date_field}_parsed'] = str(parsed_date)
                            break
                        except ValueError:
                            continue

                    if not parsed_date:
                        errors[date_field] = f"日付形式が不正です（対応形式: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD）"

            validated_row['errors'] = errors
            validated_row['has_errors'] = len(errors) > 0
            validated_data.append(validated_row)

        return {
            "success": True,
            "data": validated_data,
            "total_rows": len(validated_data),
            "error_rows": sum(1 for row in validated_data if row['has_errors'])
        }

    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="CSVファイルのエンコーディングが不正です（UTF-8を使用してください）")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"CSVファイルの処理中にエラーが発生しました: {str(e)}"
        print(f"CSV処理エラー: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=error_detail)


@router.post("/po/clipboard/validate")
async def validate_clipboard_data(
    request: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    クリップボードから貼り付けられたデータをバリデーション
    - 製品コード、顧客名の存在チェック
    - データ型の検証
    - エラーがある行をハイライト

    リクエストボディ: { "data": [ {...row_data...}, ... ] }
    """
    try:
        data = request.get('data', [])
        validated_data = []

        for row in data:
            errors = {}
            validated_row = {
                'row_number': row.get('row_number', 0),
                'po_number': row.get('po_number', '').strip(),
                'product_code': row.get('product_code', '').strip(),
                'customer_name': row.get('customer_name', '').strip(),
                'po_quantity': row.get('po_quantity', '').strip(),
                'date_receive_po': row.get('date_receive_po', '').strip(),
                'delivery_date': row.get('delivery_date', '').strip(),
            }

            # 1. 必須フィールドチェック
            column_names = ['po_number', 'product_code', 'customer_name', 'po_quantity', 'date_receive_po', 'delivery_date']
            for field in column_names:
                if not validated_row[field]:
                    errors[field] = f"{field}が空です"

            # 2. 製品コードの存在チェック
            product = None
            validated_row['product_id'] = None  # デフォルト値を初期化
            if validated_row['product_code']:
                product = db.query(Product).filter(
                    Product.product_code == validated_row['product_code']
                ).first()
                if not product:
                    errors['product_code'] = "製品コードがデータベースに存在しません"
                else:
                    validated_row['product_id'] = product.product_id

            # 3. 顧客名の存在チェック（製品に紐づく顧客と一致するか）
            if validated_row['customer_name'] and product:
                customer = db.query(Customer).filter(
                    Customer.customer_id == product.customer_id
                ).first()
                if not customer:
                    errors['customer_name'] = "顧客がデータベースに存在しません"
                elif customer.customer_name != validated_row['customer_name']:
                    errors['customer_name'] = f"製品コードの顧客名が一致しません（正: {customer.customer_name}）"
            elif validated_row['customer_name']:
                # 製品がない場合は顧客名だけでも検証
                customer = db.query(Customer).filter(
                    Customer.customer_name == validated_row['customer_name']
                ).first()
                if not customer:
                    errors['customer_name'] = "顧客名がデータベースに存在しません"

            # 4. 数量の検証
            if validated_row['po_quantity']:
                try:
                    quantity = int(validated_row['po_quantity'])
                    if quantity <= 0:
                        errors['po_quantity'] = "数量は1以上の整数である必要があります"
                    validated_row['po_quantity_int'] = quantity
                except ValueError:
                    errors['po_quantity'] = "数量は整数である必要があります"

            # 5. 日付の検証（複数フォーマットに対応、DD/MM/YYYYを優先）
            date_formats = [
                '%d/%m/%Y',      # 10/11/2025 (DD/MM/YYYY) - 優先フォーマット
                '%Y-%m-%d',      # 2025-11-10
                '%m/%d/%Y',      # 11/10/2025
                '%Y/%m/%d',      # 2025/11/10
            ]

            for date_field in ['date_receive_po', 'delivery_date']:
                if validated_row[date_field]:
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(validated_row[date_field], fmt).date()
                            # YYYY-MM-DD形式に統一
                            validated_row[date_field] = str(parsed_date)
                            break
                        except ValueError:
                            continue

                    if not parsed_date:
                        errors[date_field] = f"日付形式が不正です（対応形式: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD）"

            validated_row['errors'] = errors
            validated_row['has_errors'] = len(errors) > 0
            validated_data.append(validated_row)

        return {
            "success": True,
            "data": validated_data,
            "total_rows": len(validated_data),
            "error_rows": sum(1 for row in validated_data if row['has_errors'])
        }

    except Exception as e:
        import traceback
        error_detail = f"データの処理中にエラーが発生しました: {str(e)}"
        print(f"クリップボードデータ処理エラー: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=error_detail)


@router.post("/po/csv/import")
async def import_csv(
    validated_data: List[dict],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    バリデーション済みのCSV/クリップボードデータを一括登録
    """
    try:
        created_pos = []
        error_count = 0

        for row in validated_data:
            # エラーがある行はスキップ
            if row.get('has_errors', False):
                error_count += 1
                continue

            # 必須フィールドのチェック
            if not row.get('product_id'):
                error_count += 1
                print(f"Warning: Skipping row {row.get('row_number')} - product_id is missing")
                continue

            # POを作成
            # 日付がすでにYYYY-MM-DD形式の文字列の場合と、date型の場合に対応
            date_receive_po = row['date_receive_po']
            delivery_date = row['delivery_date']

            if isinstance(date_receive_po, str):
                date_receive_po = datetime.strptime(date_receive_po, '%Y-%m-%d').date()
            if isinstance(delivery_date, str):
                delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()

            po_data = {
                'po_number': row['po_number'],
                'product_id': row['product_id'],
                'po_quantity': row.get('po_quantity_int'),
                'date_receive_po': date_receive_po,
                'delivery_date': delivery_date,
                'is_delivered': False,
                'user': current_user['username']
            }

            print(f"Creating PO: {po_data}")

            db_po = PO(**po_data)
            db.add(db_po)
            created_pos.append(po_data)

        db.commit()

        return {
            "success": True,
            "created_count": len(created_pos),
            "skipped_count": error_count,
            "message": f"{len(created_pos)}件のPOを登録しました（{error_count}件はエラーのためスキップ）"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"一括登録中にエラーが発生しました: {str(e)}")


@router.post("/po/calculate-delivery")
async def calculate_po_delivery(
    request: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    POの納期を計算

    リクエストボディ:
    {
        "product_id": int,
        "po_quantity": int,
        "start_date": "YYYY-MM-DD"  # PO受領日
    }

    レスポンス:
    {
        "delivery_date": "YYYY-MM-DD",
        "total_days": int,
        "processes": [
            {
                "process_no": int,
                "process_name": str,
                "process_type": "DAY" | "SPM",
                "days": int,
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "rough_cycletime": float,
                "production_limit": int | null
            },
            ...
        ],
        "start_date": "YYYY-MM-DD",
        "po_quantity": int,
        "product_id": int
    }
    """
    try:
        product_id = request.get('product_id')
        po_quantity = request.get('po_quantity')
        start_date_str = request.get('start_date')

        # バリデーション
        if not product_id:
            raise HTTPException(status_code=400, detail="product_id is required")
        if not po_quantity or po_quantity <= 0:
            raise HTTPException(status_code=400, detail="po_quantity must be greater than 0")
        if not start_date_str:
            raise HTTPException(status_code=400, detail="start_date is required")

        # 日付をパース
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date must be in YYYY-MM-DD format")

        # 製品の存在確認
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 納期を計算
        result = calculate_delivery_date(
            db=db,
            product_id=product_id,
            po_quantity=po_quantity,
            start_date=start_date
        )

        # 日付をISO形式の文字列に変換
        result['delivery_date'] = result['delivery_date'].isoformat()
        result['start_date'] = result['start_date'].isoformat()
        for process in result['processes']:
            process['start_date'] = process['start_date'].isoformat()
            process['end_date'] = process['end_date'].isoformat()

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = f"納期計算中にエラーが発生しました: {str(e)}"
        print(f"納期計算エラー: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail)
