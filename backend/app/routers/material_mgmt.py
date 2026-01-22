from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import List
from datetime import datetime
from ..database import get_db
from ..models.material_management import (
    MaterialType,
    MaterialForm,
    MaterialSpec,
    MaterialItem,
    MaterialLot,
    MaterialTransaction,
    MaterialStockSnapshot,
)
from ..models.factory import Factory
from ..models.supplier import Supplier
from ..schemas import material_management as schema
from .auth import get_current_user

router = APIRouter()


# ==================== Material Types ====================
@router.get("/material-types", response_model=List[schema.MaterialTypeResponse])
async def get_material_types(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all material types"""
    query = db.query(MaterialType)
    if search:
        query = query.filter(MaterialType.material_name.contains(search))
    query = query.order_by(MaterialType.material_type_id.desc())
    return query.offset(skip).limit(limit).all()


@router.post("/material-types", response_model=schema.MaterialTypeResponse)
async def create_material_type(
    material_type: schema.MaterialTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new material type"""
    data = material_type.model_dump()
    data['user'] = current_user['username']
    db_item = MaterialType(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/material-types/{material_type_id}", response_model=schema.MaterialTypeResponse)
async def update_material_type(
    material_type_id: int,
    material_type: schema.MaterialTypeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a material type"""
    db_item = db.query(MaterialType).filter(MaterialType.material_type_id == material_type_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material type not found")

    for key, value in material_type.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db_item.user = current_user['username']
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/material-types/{material_type_id}")
async def delete_material_type(
    material_type_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a material type"""
    db_item = db.query(MaterialType).filter(MaterialType.material_type_id == material_type_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material type not found")

    # Check for related specs
    specs_count = db.query(MaterialSpec).filter(MaterialSpec.material_type_id == material_type_id).count()
    if specs_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete material type with associated specs")

    db.delete(db_item)
    db.commit()
    return {"message": "Material type deleted successfully"}


# ==================== Material Forms ====================
@router.get("/material-forms", response_model=List[schema.MaterialFormResponse])
async def get_material_forms(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all material forms"""
    return db.query(MaterialForm).order_by(MaterialForm.material_form_id).all()


@router.post("/material-forms", response_model=schema.MaterialFormResponse)
async def create_material_form(
    material_form: schema.MaterialFormCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new material form"""
    existing = db.query(MaterialForm).filter(MaterialForm.material_form_code == material_form.material_form_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Material form code already exists")

    data = material_form.model_dump()
    data['user'] = current_user['username']
    db_item = MaterialForm(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/material-forms/{material_form_id}", response_model=schema.MaterialFormResponse)
async def update_material_form(
    material_form_id: int,
    material_form: schema.MaterialFormUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a material form"""
    db_item = db.query(MaterialForm).filter(MaterialForm.material_form_id == material_form_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material form not found")

    for key, value in material_form.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db_item.user = current_user['username']
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/material-forms/{material_form_id}")
async def delete_material_form(
    material_form_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a material form"""
    db_item = db.query(MaterialForm).filter(MaterialForm.material_form_id == material_form_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material form not found")

    # Check for related specs
    specs_count = db.query(MaterialSpec).filter(MaterialSpec.material_form_id == material_form_id).count()
    if specs_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete material form with associated specs")

    db.delete(db_item)
    db.commit()
    return {"message": "Material form deleted successfully"}


# ==================== Material Specs ====================
@router.get("/material-specs", response_model=List[schema.MaterialSpecWithDetails])
async def get_material_specs(
    skip: int = 0,
    limit: int = 100,
    material_type_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all material specs with details"""
    query = db.query(MaterialSpec)
    if material_type_id:
        query = query.filter(MaterialSpec.material_type_id == material_type_id)
    query = query.order_by(MaterialSpec.material_spec_id.desc())
    specs = query.offset(skip).limit(limit).all()

    result = []
    for s in specs:
        material_type = db.query(MaterialType).filter(MaterialType.material_type_id == s.material_type_id).first()
        material_form = db.query(MaterialForm).filter(MaterialForm.material_form_id == s.material_form_id).first()
        result.append({
            **s.__dict__,
            "material_name": material_type.material_name if material_type else None,
            "form_name": material_form.form_name if material_form else None,
        })
    return result


@router.post("/material-specs", response_model=schema.MaterialSpecResponse)
async def create_material_spec(
    spec: schema.MaterialSpecCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new material spec"""
    data = spec.model_dump()
    data['user'] = current_user['username']
    db_item = MaterialSpec(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/material-specs/{material_spec_id}", response_model=schema.MaterialSpecResponse)
async def update_material_spec(
    material_spec_id: int,
    spec: schema.MaterialSpecUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a material spec"""
    db_item = db.query(MaterialSpec).filter(MaterialSpec.material_spec_id == material_spec_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material spec not found")

    for key, value in spec.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db_item.user = current_user['username']
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/material-specs/{material_spec_id}")
async def delete_material_spec(
    material_spec_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a material spec"""
    db_item = db.query(MaterialSpec).filter(MaterialSpec.material_spec_id == material_spec_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material spec not found")

    # Check for related items
    items_count = db.query(MaterialItem).filter(MaterialItem.material_spec_id == material_spec_id).count()
    if items_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete spec with associated items")

    db.delete(db_item)
    db.commit()
    return {"message": "Material spec deleted successfully"}


# ==================== Material Items ====================
@router.get("/material-items", response_model=List[schema.MaterialItemWithDetails])
async def get_material_items(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all material items with details"""
    query = db.query(MaterialItem)
    if search:
        query = query.filter(MaterialItem.material_code.contains(search))
    query = query.order_by(MaterialItem.timestamp.desc())
    items = query.offset(skip).limit(limit).all()

    result = []
    for item in items:
        spec = db.query(MaterialSpec).filter(MaterialSpec.material_spec_id == item.material_spec_id).first()
        material_type = None
        material_form = None
        if spec:
            material_type = db.query(MaterialType).filter(MaterialType.material_type_id == spec.material_type_id).first()
            material_form = db.query(MaterialForm).filter(MaterialForm.material_form_id == spec.material_form_id).first()

        result.append({
            **item.__dict__,
            "material_name": material_type.material_name if material_type else None,
            "form_name": material_form.form_name if material_form else None,
            "thickness_mm": spec.thickness_mm if spec else None,
            "width_mm": spec.width_mm if spec else None,
            "length_mm": spec.length_mm if spec else None,
        })
    return result


@router.post("/material-items", response_model=schema.MaterialItemResponse)
async def create_material_item(
    item: schema.MaterialItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new material item"""
    existing = db.query(MaterialItem).filter(MaterialItem.material_code == item.material_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Material code already exists")

    data = item.model_dump()
    data['user'] = current_user['username']
    db_item = MaterialItem(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/material-items/{material_code}", response_model=schema.MaterialItemResponse)
async def update_material_item(
    material_code: str,
    item: schema.MaterialItemUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a material item"""
    db_item = db.query(MaterialItem).filter(MaterialItem.material_code == material_code).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material item not found")

    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db_item.user = current_user['username']
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/material-items/{material_code}")
async def delete_material_item(
    material_code: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a material item"""
    db_item = db.query(MaterialItem).filter(MaterialItem.material_code == material_code).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material item not found")

    # Check for related lots
    lots_count = db.query(MaterialLot).filter(MaterialLot.material_code == material_code).count()
    if lots_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete item with associated lots")

    db.delete(db_item)
    db.commit()
    return {"message": "Material item deleted successfully"}


# ==================== Material Lots ====================
@router.get("/material-lots", response_model=List[schema.MaterialLotWithDetails])
async def get_material_lots(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    material_code: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all material lots with details"""
    query = db.query(MaterialLot)
    if search:
        query = query.filter(MaterialLot.lot_no.contains(search))
    if material_code:
        query = query.filter(MaterialLot.material_code == material_code)
    query = query.order_by(MaterialLot.lot_id.desc())
    lots = query.offset(skip).limit(limit).all()

    result = []
    for lot in lots:
        supplier = db.query(Supplier).filter(Supplier.supplier_id == lot.supplier_id).first() if lot.supplier_id else None
        item = db.query(MaterialItem).filter(MaterialItem.material_code == lot.material_code).first()
        spec = None
        material_type = None
        if item:
            spec = db.query(MaterialSpec).filter(MaterialSpec.material_spec_id == item.material_spec_id).first()
            if spec:
                material_type = db.query(MaterialType).filter(MaterialType.material_type_id == spec.material_type_id).first()

        result.append({
            **lot.__dict__,
            "supplier_name": supplier.supplier_name if supplier else None,
            "material_name": material_type.material_name if material_type else None,
            "description": item.description if item else None,
        })
    return result


@router.post("/material-lots", response_model=schema.MaterialLotResponse)
async def create_material_lot(
    lot: schema.MaterialLotCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new material lot"""
    data = lot.model_dump()
    data['user'] = current_user['username']
    db_item = MaterialLot(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/material-lots/{lot_id}", response_model=schema.MaterialLotResponse)
async def update_material_lot(
    lot_id: int,
    lot: schema.MaterialLotUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a material lot"""
    db_item = db.query(MaterialLot).filter(MaterialLot.lot_id == lot_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material lot not found")

    for key, value in lot.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db_item.user = current_user['username']
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/material-lots/{lot_id}")
async def delete_material_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a material lot"""
    db_item = db.query(MaterialLot).filter(MaterialLot.lot_id == lot_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Material lot not found")

    # Check for related transactions
    tx_count = db.query(MaterialTransaction).filter(MaterialTransaction.lot_id == lot_id).count()
    if tx_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete lot with associated transactions")

    db.delete(db_item)
    db.commit()
    return {"message": "Material lot deleted successfully"}


# ==================== Material Transactions ====================
@router.get("/material-transactions", response_model=List[schema.MaterialTransactionWithDetails])
async def get_material_transactions(
    skip: int = 0,
    limit: int = 100,
    lot_id: int = None,
    factory_id: int = None,
    transaction_type: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all material transactions with details"""
    query = db.query(MaterialTransaction)
    if lot_id:
        query = query.filter(MaterialTransaction.lot_id == lot_id)
    if factory_id:
        query = query.filter(MaterialTransaction.factory_id == factory_id)
    if transaction_type:
        query = query.filter(MaterialTransaction.transaction_type == transaction_type)
    query = query.order_by(MaterialTransaction.transaction_date.desc())
    transactions = query.offset(skip).limit(limit).all()

    result = []
    for tx in transactions:
        lot = db.query(MaterialLot).filter(MaterialLot.lot_id == tx.lot_id).first()
        factory = db.query(Factory).filter(Factory.factory_id == tx.factory_id).first()
        material_item = None
        material_type = None
        if lot:
            material_item = db.query(MaterialItem).filter(MaterialItem.material_code == lot.material_code).first()
            if material_item:
                spec = db.query(MaterialSpec).filter(MaterialSpec.material_spec_id == material_item.material_spec_id).first()
                if spec:
                    material_type = db.query(MaterialType).filter(MaterialType.material_type_id == spec.material_type_id).first()

        result.append({
            **tx.__dict__,
            "lot_no": lot.lot_no if lot else None,
            "material_code": lot.material_code if lot else None,
            "material_name": material_type.material_name if material_type else None,
            "factory_name": factory.factory_name if factory else None,
        })
    return result


@router.post("/material-transactions", response_model=schema.MaterialTransactionResponse)
async def create_material_transaction(
    transaction: schema.MaterialTransactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new material transaction and update stock snapshot"""
    data = transaction.model_dump()
    data['user'] = current_user['username']
    if not data.get('transaction_date'):
        data['transaction_date'] = datetime.now()

    # Create transaction
    db_tx = MaterialTransaction(**data)
    db.add(db_tx)

    # Update stock snapshot
    lot_id = data['lot_id']
    factory_id = data['factory_id']
    tx_type = data['transaction_type']

    snapshot = db.query(MaterialStockSnapshot).filter(
        MaterialStockSnapshot.lot_id == lot_id,
        MaterialStockSnapshot.factory_id == factory_id
    ).first()

    if not snapshot:
        snapshot = MaterialStockSnapshot(
            lot_id=lot_id,
            factory_id=factory_id,
            sheet_qty=0,
            coil_qty=0,
            weight_kg=0,
            user=current_user['username']
        )
        db.add(snapshot)

    # Calculate new quantities
    multiplier = 1 if tx_type == "IN" else -1
    snapshot.sheet_qty = (snapshot.sheet_qty or 0) + (data.get('sheet_qty', 0) or 0) * multiplier
    snapshot.coil_qty = (snapshot.coil_qty or 0) + (data.get('coil_qty', 0) or 0) * multiplier
    snapshot.weight_kg = (snapshot.weight_kg or 0) + (data.get('weight_kg', 0) or 0) * multiplier
    snapshot.user = current_user['username']

    db.commit()
    db.refresh(db_tx)
    return db_tx


@router.get("/material-transactions/by-lot/{lot_id}", response_model=List[schema.MaterialTransactionWithDetails])
async def get_transactions_by_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all transactions for a specific lot"""
    return await get_material_transactions(lot_id=lot_id, db=db, current_user=current_user)


# ==================== Material Stock ====================
@router.get("/material-stock", response_model=List[schema.MaterialStockWithDetails])
async def get_material_stock(
    factory_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current material stock with details"""
    query = db.query(MaterialStockSnapshot)
    if factory_id:
        query = query.filter(MaterialStockSnapshot.factory_id == factory_id)
    snapshots = query.all()

    result = []
    for snap in snapshots:
        lot = db.query(MaterialLot).filter(MaterialLot.lot_id == snap.lot_id).first()
        factory = db.query(Factory).filter(Factory.factory_id == snap.factory_id).first()
        supplier = None
        material_item = None
        material_type = None

        if lot:
            supplier = db.query(Supplier).filter(Supplier.supplier_id == lot.supplier_id).first() if lot.supplier_id else None
            material_item = db.query(MaterialItem).filter(MaterialItem.material_code == lot.material_code).first()
            if material_item:
                spec = db.query(MaterialSpec).filter(MaterialSpec.material_spec_id == material_item.material_spec_id).first()
                if spec:
                    material_type = db.query(MaterialType).filter(MaterialType.material_type_id == spec.material_type_id).first()

        result.append({
            **snap.__dict__,
            "lot_no": lot.lot_no if lot else None,
            "material_code": lot.material_code if lot else None,
            "material_name": material_type.material_name if material_type else None,
            "factory_name": factory.factory_name if factory else None,
            "supplier_name": supplier.supplier_name if supplier else None,
        })
    return result


@router.get("/material-stock/by-lot/{lot_id}", response_model=List[schema.MaterialStockWithDetails])
async def get_stock_by_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get stock for a specific lot across all factories"""
    query = db.query(MaterialStockSnapshot).filter(MaterialStockSnapshot.lot_id == lot_id)
    snapshots = query.all()

    result = []
    for snap in snapshots:
        lot = db.query(MaterialLot).filter(MaterialLot.lot_id == snap.lot_id).first()
        factory = db.query(Factory).filter(Factory.factory_id == snap.factory_id).first()
        supplier = None
        material_item = None
        material_type = None

        if lot:
            supplier = db.query(Supplier).filter(Supplier.supplier_id == lot.supplier_id).first() if lot.supplier_id else None
            material_item = db.query(MaterialItem).filter(MaterialItem.material_code == lot.material_code).first()
            if material_item:
                spec = db.query(MaterialSpec).filter(MaterialSpec.material_spec_id == material_item.material_spec_id).first()
                if spec:
                    material_type = db.query(MaterialType).filter(MaterialType.material_type_id == spec.material_type_id).first()

        result.append({
            **snap.__dict__,
            "lot_no": lot.lot_no if lot else None,
            "material_code": lot.material_code if lot else None,
            "material_name": material_type.material_name if material_type else None,
            "factory_name": factory.factory_name if factory else None,
            "supplier_name": supplier.supplier_name if supplier else None,
        })
    return result


# ==================== Autocomplete Endpoints ====================
@router.get("/autocomplete/material-types")
async def autocomplete_material_types(
    search: str = "",
    db: Session = Depends(get_db)
):
    """Autocomplete for material types"""
    query = db.query(MaterialType.material_type_id, MaterialType.material_name)
    if search:
        query = query.filter(MaterialType.material_name.contains(search))
    types = query.limit(20).all()
    return [{"id": t.material_type_id, "name": t.material_name} for t in types]


@router.get("/autocomplete/material-items")
async def autocomplete_material_items(
    search: str = "",
    db: Session = Depends(get_db)
):
    """Autocomplete for material items"""
    query = db.query(MaterialItem.material_code, MaterialItem.description)
    if search:
        query = query.filter(MaterialItem.material_code.contains(search))
    items = query.limit(20).all()
    return [{"material_code": i.material_code, "description": i.description} for i in items]


@router.get("/autocomplete/material-lots")
async def autocomplete_material_lots(
    search: str = "",
    material_code: str = None,
    db: Session = Depends(get_db)
):
    """Autocomplete for material lots"""
    query = db.query(MaterialLot.lot_id, MaterialLot.lot_no, MaterialLot.material_code)
    if material_code:
        query = query.filter(MaterialLot.material_code == material_code)
    if search:
        query = query.filter(MaterialLot.lot_no.contains(search))
    lots = query.limit(20).all()
    return [{"id": l.lot_id, "lot_no": l.lot_no, "material_code": l.material_code} for l in lots]
