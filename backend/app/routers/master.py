from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.customer import Customer
from ..models.product import Product
from ..models.employee import Employee
from ..models.supplier import Supplier
from ..models.lot import Lot
from ..models.factory import Factory, MachineList, MachineType
from ..models.material import MaterialRate
from ..models.cycletime import Cycletime
from ..models.process import ProcessNameType, Process
from ..models.po import PO
from ..models.finished_product import FinishedProduct
from ..models.production_schedule import ProductionSchedule
from ..models.trace import StampTrace, OutsourceTrace
from ..models.mold import BrokenMold
from ..models.calendar import Calendar
from ..schemas import customer as customer_schema
from ..schemas import product as product_schema
from ..schemas import employee as employee_schema
from ..schemas import supplier as supplier_schema
from ..schemas import process as process_schema
from ..schemas import factory as factory_schema
from ..schemas import material as material_schema
from ..schemas import cycletime as cycletime_schema
from .auth import get_current_user
from ..utils.auth import get_password_hash, generate_strong_password

router = APIRouter()


# ==================== Table Counts ====================
@router.get("/table-counts")
async def get_table_counts(db: Session = Depends(get_db)):
    """Get record counts for all master tables"""
    return {
        "customers": db.query(Customer).count(),
        "products": db.query(Product).count(),
        "employees": db.query(Employee).count(),
        "suppliers": db.query(Supplier).count(),
        "process_name_types": db.query(ProcessNameType).count(),
        "material_rates": db.query(MaterialRate).count(),
        "machine_list": db.query(MachineList).count(),
        "cycletimes": db.query(Cycletime).count(),
        "calendar": db.query(Calendar).count(),
        "processes": db.query(Process).count(),
    }


# ==================== Customers ====================
@router.get("/customers", response_model=List[customer_schema.CustomerResponse])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    if search:
        query = query.filter(Customer.customer_name.contains(search))

    # 顧客IDの降順でソート
    query = query.order_by(Customer.customer_id.desc())
    customers = query.offset(skip).limit(limit).all()
    return customers


@router.post("/customers", response_model=customer_schema.CustomerResponse)
async def create_customer(
    customer: customer_schema.CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer_data = customer.model_dump()
    customer_data['user'] = current_user['username']
    db_customer = Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.put("/customers/{customer_id}", response_model=customer_schema.CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: customer_schema.CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in customer.model_dump(exclude_unset=True).items():
        setattr(db_customer, key, value)

    db_customer.user = current_user['username']
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 関連する製品があるかチェック
    products_count = db.query(Product).filter(Product.customer_id == customer_id).count()
    if products_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete customer with associated products")

    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted successfully"}


# ==================== Products ====================
@router.get("/products")
async def get_products(
    skip: int = 0,
    limit: int = 100,
    product_code: str = None,
    customer_name: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product).join(Customer, Product.customer_id == Customer.customer_id)

    # 製品コードで検索
    if product_code:
        query = query.filter(Product.product_code.contains(product_code))

    # 顧客名で検索
    if customer_name:
        query = query.filter(Customer.customer_name.contains(customer_name))

    # タイムスタンプの降順でソート
    query = query.order_by(Product.timestamp.desc())
    products = query.offset(skip).limit(limit).all()

    # データを整形して顧客名を含める
    result = []
    for p in products:
        result.append({
            "product_id": p.product_id,
            "product_code": p.product_code,
            "customer_id": p.customer_id,
            "customer_name": p.customer.customer_name if p.customer else None,
            "is_active": p.is_active,
            "timestamp": p.timestamp,
            "user": p.user
        })
    return result


@router.get("/products/by-code/{product_code}")
async def get_product_by_code(
    product_code: str,
    db: Session = Depends(get_db)
):
    """製品コードから製品情報と顧客名を取得"""
    product = db.query(Product).join(
        Customer, Product.customer_id == Customer.customer_id
    ).filter(
        Product.product_code == product_code,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "product_id": product.product_id,
        "product_code": product.product_code,
        "customer_id": product.customer_id,
        "customer_name": product.customer.customer_name if product.customer else None,
        "is_active": product.is_active
    }


@router.post("/products", response_model=product_schema.ProductResponse)
async def create_product(
    product: product_schema.ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    product_data = product.model_dump()
    product_data['user'] = current_user['username']
    db_product = Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/products/{product_id}", response_model=product_schema.ProductResponse)
async def update_product(
    product_id: int,
    product: product_schema.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)

    db_product.user = current_user['username']
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        db_product = db.query(Product).filter(Product.product_id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check for associated data
        # Lots
        lots_count = db.query(Lot).filter(Lot.product_id == product_id).count()
        if lots_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete product with associated lots")

        # Cycletime settings
        cycletime_count = db.query(Cycletime).filter(Cycletime.product_id == product_id).count()
        if cycletime_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete product with associated cycletime settings")

        # Material rates
        material_rates_count = db.query(MaterialRate).filter(MaterialRate.product_id == product_id).count()
        if material_rates_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete product with associated material rates")

        # Processes
        processes = db.query(Process).filter(Process.product_id == product_id).all()
        process_ids = [p.process_id for p in processes]
        if len(process_ids) > 0:
            # Check for data associated with processes
            # Production Schedule
            schedules_count = db.query(ProductionSchedule).filter(ProductionSchedule.process_id.in_(process_ids)).count()
            if schedules_count > 0:
                raise HTTPException(status_code=400, detail="Cannot delete product with associated production schedules")
            
            # Stamp Traces
            stamp_traces_count = db.query(StampTrace).filter(StampTrace.process_id.in_(process_ids)).count()
            if stamp_traces_count > 0:
                raise HTTPException(status_code=400, detail="Cannot delete product with associated stamp traces")
            
            # Outsource Traces
            outsource_traces_count = db.query(OutsourceTrace).filter(OutsourceTrace.process_id.in_(process_ids)).count()
            if outsource_traces_count > 0:
                raise HTTPException(status_code=400, detail="Cannot delete product with associated outsource traces")
            
            # Broken Molds
            broken_molds_count = db.query(BrokenMold).filter(BrokenMold.process_id.in_(process_ids)).count()
            if broken_molds_count > 0:
                raise HTTPException(status_code=400, detail="Cannot delete product with associated broken mold records")

            raise HTTPException(status_code=400, detail="Cannot delete product with associated processes")

        # POs
        pos_count = db.query(PO).filter(PO.product_id == product_id).count()
        if pos_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete product with associated POs")

        # Finished products
        finished_products_count = db.query(FinishedProduct).filter(FinishedProduct.product_id == product_id).count()
        if finished_products_count > 0:
            raise HTTPException(status_code=400, detail="Cannot delete product with associated finished products")

        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error during deletion: {str(e)}")


# ==================== Employees ====================
@router.get("/employees")
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    employee_no: str = None,
    name: str = None,
    has_password: bool = None,
    db: Session = Depends(get_db)
):
    query = db.query(Employee)

    # 従業員番号で検索
    if employee_no:
        query = query.filter(Employee.employee_no.contains(employee_no))

    # 名前で検索
    if name:
        query = query.filter(Employee.name.contains(name))

    # パスワード有無でフィルタ
    if has_password is True:
        query = query.filter(Employee.password_hash.isnot(None))

    # 従業員IDの降順でソート
    query = query.order_by(Employee.employee_id.desc())
    employees = query.offset(skip).limit(limit).all()

    # has_passwordフィールドを追加
    result = []
    for emp in employees:
        emp_dict = {
            "employee_id": emp.employee_id,
            "employee_no": emp.employee_no,
            "name": emp.name,
            "is_active": emp.is_active,
            "timestamp": emp.timestamp,
            "user": emp.user,
            "has_password": emp.password_hash is not None
        }
        result.append(emp_dict)
    return result


@router.post("/employees", response_model=employee_schema.EmployeeCreateResponse)
async def create_employee(
    employee: employee_schema.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    employee_data = employee.model_dump()
    create_password = employee_data.pop('create_password', True)
    employee_data['user'] = current_user['username']

    plain_password = None
    if create_password:
        # パスワード自動生成
        plain_password = generate_strong_password()
        hashed_password = get_password_hash(plain_password)
        employee_data['password_hash'] = hashed_password

    db_employee = Employee(**employee_data)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    # レスポンス用にパスワードをセット（DBオブジェクトには持たせない）
    response = employee_schema.EmployeeCreateResponse.model_validate(db_employee)
    if plain_password:
        response.generated_password = plain_password
    
    return response


@router.put("/employees/{employee_id}", response_model=employee_schema.EmployeeCreateResponse)
async def update_employee(
    employee_id: int,
    employee: employee_schema.EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """従業員情報を更新"""
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee_data = employee.model_dump(exclude_unset=True)
    create_password = employee_data.pop('create_password', False)

    plain_password = None
    if create_password:
        # パスワード自動生成
        plain_password = generate_strong_password()
        hashed_password = get_password_hash(plain_password)
        employee_data['password_hash'] = hashed_password

    for key, value in employee_data.items():
        setattr(db_employee, key, value)

    db_employee.user = current_user['username']
    db.commit()
    db.refresh(db_employee)

    # レスポンス作成
    response = employee_schema.EmployeeCreateResponse.model_validate(db_employee)
    if plain_password:
        response.generated_password = plain_password

    return response


@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """従業員を削除"""
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 関連する実績データがあるかチェック
    traces_count = db.query(StampTrace).filter(StampTrace.employee_id == employee_id).count()
    if traces_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete employee with associated production traces")

    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}


@router.post("/employees/{employee_id}/revoke-password")
async def revoke_employee_password(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """従業員のパスワードを削除（ログイン不可にする）"""
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not db_employee.password_hash:
        raise HTTPException(status_code=400, detail="Employee does not have a password")

    db_employee.password_hash = None
    db_employee.user = current_user['username']
    db.commit()
    return {"message": "Password revoked successfully"}


# ==================== Suppliers ====================
@router.get("/suppliers", response_model=List[supplier_schema.SupplierResponse])
async def get_suppliers(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Supplier)
    if search:
        query = query.filter(Supplier.supplier_name.contains(search))

    # 仕入先IDの降順でソート
    query = query.order_by(Supplier.supplier_id.desc())
    suppliers = query.offset(skip).limit(limit).all()
    return suppliers


@router.post("/suppliers", response_model=supplier_schema.SupplierResponse)
async def create_supplier(
    supplier: supplier_schema.SupplierCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    supplier_data = supplier.model_dump()
    supplier_data['user'] = current_user['username']
    db_supplier = Supplier(**supplier_data)
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


# ==================== Autocomplete Endpoints ====================
@router.get("/autocomplete/customers")
async def autocomplete_customers(
    search: str = "",
    db: Session = Depends(get_db)
):
    """顧客名のオートコンプリート用エンドポイント"""
    query = db.query(Customer.customer_id, Customer.customer_name).filter(
        Customer.is_active == True
    )
    if search:
        query = query.filter(Customer.customer_name.contains(search))
    customers = query.limit(20).all()
    return [{"id": c.customer_id, "name": c.customer_name} for c in customers]


@router.get("/autocomplete/products")
async def autocomplete_products(
    search: str = "",
    db: Session = Depends(get_db)
):
    """製品コードのオートコンプリート用エンドポイント（顧客名も含む）"""
    query = db.query(
        Product.product_id,
        Product.product_code,
        Customer.customer_name
    ).join(
        Customer, Product.customer_id == Customer.customer_id
    ).filter(
        Product.is_active == True
    )
    if search:
        query = query.filter(Product.product_code.contains(search))
    products = query.limit(20).all()
    return [{"id": p.product_id, "product_code": p.product_code, "customer_name": p.customer_name} for p in products]


@router.get("/autocomplete/employees")
async def autocomplete_employees(
    search: str = "",
    db: Session = Depends(get_db)
):
    """従業員名のオートコンプリート用エンドポイント"""
    query = db.query(Employee.employee_id, Employee.name).filter(
        Employee.is_active == True
    )
    if search:
        query = query.filter(Employee.name.contains(search))
    employees = query.limit(20).all()
    return [{"id": e.employee_id, "name": e.name} for e in employees]


@router.get("/autocomplete/suppliers")
async def autocomplete_suppliers(
    search: str = "",
    db: Session = Depends(get_db)
):
    """サプライヤー名のオートコンプリート用エンドポイント"""
    query = db.query(Supplier.supplier_id, Supplier.supplier_name).filter(
        Supplier.is_active == True
    )
    if search:
        query = query.filter(Supplier.supplier_name.contains(search))
    suppliers = query.limit(20).all()
    return [{"id": s.supplier_id, "name": s.supplier_name} for s in suppliers]


@router.get("/autocomplete/lots")
async def autocomplete_lots(
    search: str = "",
    product_id: int = None,
    db: Session = Depends(get_db)
):
    """ロット番号のオートコンプリート用エンドポイント"""
    query = db.query(Lot.lot_id, Lot.lot_number, Lot.product_id)

    if product_id:
        query = query.filter(Lot.product_id == product_id)

    if search:
        query = query.filter(Lot.lot_number.contains(search))

    lots = query.limit(20).all()
    return [{"id": l.lot_id, "number": l.lot_number, "product_id": l.product_id} for l in lots]


@router.get("/autocomplete/factories")
async def autocomplete_factories(
    search: str = "",
    db: Session = Depends(get_db)
):
    """工場のオートコンプリート用エンドポイント"""
    query = db.query(Factory.factory_id, Factory.factory_name)
    if search:
        query = query.filter(Factory.factory_name.contains(search))
    factories = query.limit(20).all()
    return [{"id": f.factory_id, "name": f.factory_name} for f in factories]


@router.get("/autocomplete/process-names")
async def autocomplete_process_names(
    search: str = "",
    db: Session = Depends(get_db)
):
    """工程名のオートコンプリート用エンドポイント（PRESS工程のみ）"""
    query = db.query(ProcessNameType.process_name).filter(
        ProcessNameType.process_name.contains("PRESS")
    )
    if search:
        query = query.filter(ProcessNameType.process_name.contains(search))
    process_names = query.limit(20).all()
    return [{"name": p.process_name} for p in process_names]


@router.get("/autocomplete/machines")
async def autocomplete_machines(
    search: str = "",
    machine_type: str = None,
    db: Session = Depends(get_db)
):
    """機械番号のオートコンプリート用エンドポイント"""
    query = db.query(
        MachineList.machine_no,
        Factory.factory_name
    ).join(
        Factory, MachineList.factory_id == Factory.factory_id
    ).outerjoin(
        MachineType, MachineList.machine_type_id == MachineType.machine_type_id
    )

    if machine_type:
        query = query.filter(MachineType.machine_type_name == machine_type)

    if search:
        query = query.filter(MachineList.machine_no.contains(search))

    machines = query.limit(20).all()
    return [{"machine_no": m.machine_no, "factory_name": m.factory_name, "display": f"{m.machine_no} ({m.factory_name})"} for m in machines]


# ==================== Process Names ====================
@router.get("/process-names", response_model=List[process_schema.ProcessNameTypeResponse])
async def get_process_names(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """工程名一覧を取得"""
    query = db.query(ProcessNameType)
    if search:
        query = query.filter(ProcessNameType.process_name.contains(search))
    query = query.order_by(ProcessNameType.process_name_id.desc())
    process_names = query.offset(skip).limit(limit).all()
    return process_names


@router.post("/process-names", response_model=process_schema.ProcessNameTypeResponse)
async def create_process_name(
    process_name: process_schema.ProcessNameTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """工程名を登録"""
    process_name_data = process_name.model_dump()
    process_name_data['user'] = current_user['username']
    db_process_name = ProcessNameType(**process_name_data)
    db.add(db_process_name)
    db.commit()
    db.refresh(db_process_name)
    return db_process_name


@router.put("/process-names/{process_name_id}", response_model=process_schema.ProcessNameTypeResponse)
async def update_process_name(
    process_name_id: int,
    process_name: process_schema.ProcessNameTypeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """工程名を更新"""
    db_process_name = db.query(ProcessNameType).filter(ProcessNameType.process_name_id == process_name_id).first()
    if not db_process_name:
        raise HTTPException(status_code=404, detail="Process name not found")

    for key, value in process_name.model_dump(exclude_unset=True).items():
        setattr(db_process_name, key, value)

    db_process_name.user = current_user['username']
    db.commit()
    db.refresh(db_process_name)
    return db_process_name


@router.delete("/process-names/{process_name_id}")
async def delete_process_name(
    process_name_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """工程名を削除"""
    db_process_name = db.query(ProcessNameType).filter(ProcessNameType.process_name_id == process_name_id).first()
    if not db_process_name:
        raise HTTPException(status_code=404, detail="Process name not found")

    db.delete(db_process_name)
    db.commit()
    return {"message": "Process name deleted successfully"}


# ==================== Material Rates ====================
@router.get("/material-rates", response_model=List[material_schema.MaterialRateWithDetails])
async def get_material_rates(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """材料レート一覧を取得"""
    query = db.query(MaterialRate).join(Product, MaterialRate.product_id == Product.product_id)
    if search:
        query = query.filter(Product.product_code.contains(search))
    material_rates = query.offset(skip).limit(limit).all()

    # データを整形
    result = []
    for mr in material_rates:
        result.append({
            "material_rate_id": mr.material_rate_id,
            "product_id": mr.product_id,
            "thickness": mr.thickness,
            "width": mr.width,
            "pitch": mr.pitch,
            "h": mr.h,
            "timestamp": mr.timestamp,
            "user": mr.user,
            "product_code": db.query(Product).filter(Product.product_id == mr.product_id).first().product_code,
        })
    return result


@router.post("/material-rates", response_model=material_schema.MaterialRateResponse)
async def create_material_rate(
    material_rate: material_schema.MaterialRateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """材料レートを登録"""
    material_rate_data = material_rate.model_dump()
    material_rate_data['user'] = current_user['username']
    db_material_rate = MaterialRate(**material_rate_data)
    db.add(db_material_rate)
    db.commit()
    db.refresh(db_material_rate)
    return db_material_rate


# ==================== Machine Types ====================
@router.get("/machine-types", response_model=List[factory_schema.MachineTypeResponse])
async def get_machine_types(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械種類一覧を取得"""
    query = db.query(MachineType)
    if search:
        query = query.filter(MachineType.machine_type_name.contains(search))
    machine_types = query.offset(skip).limit(limit).all()
    return machine_types


@router.post("/machine-types", response_model=factory_schema.MachineTypeResponse)
async def create_machine_type(
    machine_type: factory_schema.MachineTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械種類を登録"""
    machine_type_data = machine_type.model_dump()
    machine_type_data['user'] = current_user['username']
    db_machine_type = MachineType(**machine_type_data)
    db.add(db_machine_type)
    db.commit()
    db.refresh(db_machine_type)
    return db_machine_type


@router.put("/machine-types/{machine_type_id}", response_model=factory_schema.MachineTypeResponse)
async def update_machine_type(
    machine_type_id: int,
    machine_type: factory_schema.MachineTypeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械種類を更新"""
    db_machine_type = db.query(MachineType).filter(MachineType.machine_type_id == machine_type_id).first()
    if not db_machine_type:
        raise HTTPException(status_code=404, detail="Machine type not found")

    for key, value in machine_type.model_dump(exclude_unset=True).items():
        setattr(db_machine_type, key, value)

    db_machine_type.user = current_user['username']
    db.commit()
    db.refresh(db_machine_type)
    return db_machine_type


@router.delete("/machine-types/{machine_type_id}")
async def delete_machine_type(
    machine_type_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械種類を削除"""
    db_machine_type = db.query(MachineType).filter(MachineType.machine_type_id == machine_type_id).first()
    if not db_machine_type:
        raise HTTPException(status_code=404, detail="Machine type not found")

    db.delete(db_machine_type)
    db.commit()
    return {"message": "Machine type deleted successfully"}


# ==================== Machines ====================
@router.get("/machines", response_model=List[factory_schema.MachineListWithDetails])
async def get_machines(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械一覧を取得"""
    query = db.query(MachineList).outerjoin(Factory, MachineList.factory_id == Factory.factory_id).outerjoin(MachineType, MachineList.machine_type_id == MachineType.machine_type_id)
    if search:
        query = query.filter(MachineList.machine_no.contains(search))
    # 降順でソート
    query = query.order_by(MachineList.machine_list_id.desc())
    machines = query.offset(skip).limit(limit).all()

    # データを整形
    result = []
    for m in machines:
        factory = db.query(Factory).filter(Factory.factory_id == m.factory_id).first()
        machine_type = db.query(MachineType).filter(MachineType.machine_type_id == m.machine_type_id).first()
        result.append({
            "machine_list_id": m.machine_list_id,
            "factory_id": m.factory_id,
            "machine_no": m.machine_no,
            "machine_type_id": m.machine_type_id,
            "timestamp": m.timestamp,
            "user": m.user,
            "factory_name": factory.factory_name if factory else None,
            "machine_type_name": machine_type.machine_type_name if machine_type else None,
        })
    return result


@router.post("/machines")
async def create_machine(
    machine_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械を登録"""
    machine_no = machine_data.get("machine_no")
    machine_type_id = machine_data.get("machine_type_id")
    factory_id = machine_data.get("factory_id")

    if not machine_no:
        raise HTTPException(status_code=400, detail="machine_no is required")

    if not factory_id:
        raise HTTPException(status_code=400, detail="factory_id is required")

    # 機械を登録
    db_machine = MachineList(
        factory_id=factory_id,
        machine_no=machine_no,
        machine_type_id=machine_type_id,
        user=current_user['username']
    )
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


@router.put("/machines/{machine_list_id}")
async def update_machine(
    machine_list_id: int,
    machine_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械を更新"""
    machine = db.query(MachineList).filter(MachineList.machine_list_id == machine_list_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    machine_no = machine_data.get("machine_no")
    machine_type_id = machine_data.get("machine_type_id")
    factory_id = machine_data.get("factory_id")

    if machine_no:
        machine.machine_no = machine_no
    if machine_type_id is not None:
        machine.machine_type_id = machine_type_id
    if factory_id:
        machine.factory_id = factory_id
    machine.user = current_user['username']

    db.commit()
    db.refresh(machine)
    return machine


@router.delete("/machines/{machine_list_id}")
async def delete_machine(
    machine_list_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """機械を削除"""
    machine = db.query(MachineList).filter(MachineList.machine_list_id == machine_list_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    db.delete(machine)
    db.commit()
    return {"message": "Machine deleted successfully"}


# ==================== Cycletimes ====================
@router.get("/product/{product_id}/process-names")
async def get_product_process_names(
    product_id: int,
    db: Session = Depends(get_db)
):
    """製品に紐づく工程名一覧を取得（cycletime用）"""
    processes = db.query(
        Process.process_id,
        Process.process_no,
        Process.rough_cycletime,
        ProcessNameType.process_name
    ).join(
        ProcessNameType, Process.process_name_id == ProcessNameType.process_name_id
    ).filter(
        Process.product_id == product_id
    ).order_by(Process.process_no).all()

    return [{"process_id": p.process_id, "process_no": p.process_no, "process_name": p.process_name, "rough_cycletime": p.rough_cycletime} for p in processes]


@router.get("/cycletimes", response_model=List[cycletime_schema.CycletimeWithDetails])
async def get_cycletimes(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """サイクルタイム設定一覧を取得"""
    query = db.query(Cycletime).join(Product, Cycletime.product_id == Product.product_id)
    if search:
        query = query.filter(Product.product_code.contains(search))
    cycletime_list = query.offset(skip).limit(limit).all()

    # データを整形
    result = []
    for c in cycletime_list:
        result.append({
            "cycletime_id": c.cycletime_id,
            "product_id": c.product_id,
            "process_name": c.process_name,
            "press_no": c.press_no,
            "cycle_time": c.cycle_time,
            "timestamp": c.timestamp,
            "user": c.user,
            "product_code": db.query(Product).filter(Product.product_id == c.product_id).first().product_code,
        })
    return result


@router.post("/cycletimes", response_model=cycletime_schema.CycletimeResponse)
async def create_cycletime(
    cycletime: cycletime_schema.CycletimeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """サイクルタイム設定を登録"""
    cycletime_data = cycletime.model_dump()
    cycletime_data['user'] = current_user['username']
    db_cycletime = Cycletime(**cycletime_data)
    db.add(db_cycletime)
    db.commit()
    db.refresh(db_cycletime)
    return db_cycletime


@router.put("/cycletimes/{cycletime_id}", response_model=cycletime_schema.CycletimeResponse)
async def update_cycletime(
    cycletime_id: int,
    cycletime: cycletime_schema.CycletimeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """サイクルタイム設定を更新"""
    db_cycletime = db.query(Cycletime).filter(Cycletime.cycletime_id == cycletime_id).first()
    if not db_cycletime:
        raise HTTPException(status_code=404, detail="Cycletime setting not found")

    for key, value in cycletime.model_dump(exclude_unset=True).items():
        setattr(db_cycletime, key, value)

    db_cycletime.user = current_user['username']
    db.commit()
    db.refresh(db_cycletime)
    return db_cycletime


@router.delete("/cycletimes/{cycletime_id}")
async def delete_cycletime(
    cycletime_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """サイクルタイム設定を削除"""
    db_cycletime = db.query(Cycletime).filter(Cycletime.cycletime_id == cycletime_id).first()
    if not db_cycletime:
        raise HTTPException(status_code=404, detail="Cycletime setting not found")

    db.delete(db_cycletime)
    db.commit()
    return {"message": "Cycletime setting deleted successfully"}
