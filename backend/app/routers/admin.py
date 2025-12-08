from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db, engine
from ..models.production_schedule import ProductionSchedule
from sqlalchemy import inspect

router = APIRouter()


@router.post("/create-production-schedule-table")
async def create_production_schedule_table(db: Session = Depends(get_db)):
    """
    production_scheduleテーブルを作成する管理用エンドポイント
    """
    try:
        # テーブルが既に存在するか確認
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if 'production_schedule' in existing_tables:
            return {
                "status": "exists",
                "message": "production_scheduleテーブルは既に存在します",
                "table_name": "production_schedule"
            }

        # テーブルを作成
        ProductionSchedule.__table__.create(engine, checkfirst=True)

        # 作成されたか確認
        inspector = inspect(engine)
        if 'production_schedule' in inspector.get_table_names():
            columns = inspector.get_columns('production_schedule')
            return {
                "status": "created",
                "message": "production_scheduleテーブルを作成しました",
                "table_name": "production_schedule",
                "columns": [col['name'] for col in columns]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="テーブルの作成に失敗しました"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"エラーが発生しました: {str(e)}"
        )


@router.get("/check-tables")
async def check_tables():
    """
    データベース内のテーブル一覧を取得
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        return {
            "status": "success",
            "tables": tables,
            "count": len(tables),
            "has_production_schedule": "production_schedule" in tables
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"エラーが発生しました: {str(e)}"
        )


@router.post("/insert-press-machines")
async def insert_press_machines(db: Session = Depends(get_db)):
    """
    PRESS機のマスタデータを登録
    """
    from ..models.factory import MachineList

    try:
        # 既存のPRESS機を確認
        existing_press = db.query(MachineList).filter(
            MachineList.machine_type == 'PRESS'
        ).all()

        # PRESS機の番号リスト
        press_machines = [
            'PRESS-001', 'PRESS-002', 'PRESS-003', 'PRESS-004',
            'PRESS-005', 'PRESS-006', 'PRESS-007', 'PRESS-008',
            'PRESS-S001', 'PRESS-S002', 'PRESS-S003', 'PRESS-S004'
        ]

        existing_machine_nos = [m.machine_no for m in existing_press]

        # 未登録のPRESS機を追加
        added = []
        for machine_no in press_machines:
            if machine_no not in existing_machine_nos:
                new_machine = MachineList(
                    factory_id=1,
                    machine_no=machine_no,
                    machine_type='PRESS',
                    user='admin'
                )
                db.add(new_machine)
                added.append(machine_no)

        db.commit()

        # 登録後のPRESS機数を確認
        total_press = db.query(MachineList).filter(
            MachineList.machine_type == 'PRESS'
        ).count()

        return {
            "status": "success",
            "message": f"PRESS機を登録しました",
            "existing_count": len(existing_machine_nos),
            "added_count": len(added),
            "added_machines": added,
            "total_press_machines": total_press
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"エラーが発生しました: {str(e)}"
        )


@router.get("/check-press-machines")
async def check_press_machines(db: Session = Depends(get_db)):
    """
    PRESS機の登録状況を確認
    """
    from ..models.factory import MachineList

    try:
        press_machines = db.query(MachineList).filter(
            MachineList.machine_type == 'PRESS'
        ).all()

        return {
            "status": "success",
            "count": len(press_machines),
            "machines": [
                {
                    "machine_list_id": m.machine_list_id,
                    "machine_no": m.machine_no,
                    "factory_id": m.factory_id,
                    "machine_type": m.machine_type
                }
                for m in press_machines
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"エラーが発生しました: {str(e)}"
        )
