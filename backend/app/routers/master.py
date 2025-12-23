from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.customer import Customer
from ..models.product import Product
from ..models.employee import Employee
from ..models.supplier import Supplier
from ..models.lot import Lot
from ..models.process import ProcessNameType
from ..models.factory import Factory, MachineList
from ..models.material import MaterialRate
from ..models.spm import SPM
from ..schemas import customer as customer_schema
from ..schemas import product as product_schema
from ..schemas import employee as employee_schema
from ..schemas import supplier as supplier_schema
from ..schemas import process as process_schema
from ..schemas import factory as factory_schema
from ..schemas import material as material_schema
from ..schemas import spm as spm_schema
from ..schemas import spm as spm_schema
from .auth import get_current_user
from ..utils.auth import get_password_hash, generate_strong_password

router = APIRouter()

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
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check for associated data
    # Lots
    lots_count = db.query(Lot).filter(Lot.product_id == product_id).count()
    if lots_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete product with associated lots")

    # SPM settings
    spm_count = db.query(SPM).filter(SPM.product_id == product_id).count()
    if spm_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete product with associated SPM settings")

    # Material rates
    material_rates_count = db.query(MaterialRate).filter(MaterialRate.product_id == product_id).count()
    if material_rates_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete product with associated material rates")

    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}


# ==================== Employees ====================
@router.get("/employees", response_model=List[employee_schema.EmployeeResponse])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    employee_no: str = None,
    name: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Employee)

    # 従業員番号で検索
    if employee_no:
        query = query.filter(Employee.employee_no.contains(employee_no))

    # 名前で検索
    if name:
        query = query.filter(Employee.name.contains(name))

    # 従業員IDの降順でソート
    query = query.order_by(Employee.employee_id.desc())
    employees = query.offset(skip).limit(limit).all()
    return employees


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
    query = db.query(MachineList.machine_no)

    if machine_type:
        query = query.filter(MachineList.machine_type == machine_type)

    if search:
        query = query.filter(MachineList.machine_no.contains(search))

    machines = query.limit(20).all()
    return [{"machine_no": m.machine_no} for m in machines]


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
    query = db.query(MachineList).join(Factory, MachineList.factory_id == Factory.factory_id)
    if search:
        query = query.filter(MachineList.machine_no.contains(search))
    machines = query.offset(skip).limit(limit).all()

    # データを整形
    result = []
    for m in machines:
        factory = db.query(Factory).filter(Factory.factory_id == m.factory_id).first()
        result.append({
            "machine_list_id": m.machine_list_id,
            "factory_id": m.factory_id,
            "machine_no": m.machine_no,
            "machine_type": m.machine_type,
            "timestamp": m.timestamp,
            "user": m.user,
            "factory_name": factory.factory_name if factory else None,
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
    machine_type = machine_data.get("machine_type")
    factory_id = machine_data.get("factory_id")

    if not machine_no:
        raise HTTPException(status_code=400, detail="machine_no is required")

    if not factory_id:
        raise HTTPException(status_code=400, detail="factory_id is required")

    # 機械を登録
    db_machine = MachineList(
        factory_id=factory_id,
        machine_no=machine_no,
        machine_type=machine_type,
        user=current_user['username']
    )
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


# ==================== SPM ====================
@router.get("/spm", response_model=List[spm_schema.SPMWithDetails])
async def get_spm(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """SPM設定一覧を取得"""
    query = db.query(SPM).join(Product, SPM.product_id == Product.product_id)
    if search:
        query = query.filter(Product.product_code.contains(search))
    spm_list = query.offset(skip).limit(limit).all()

    # データを整形
    result = []
    for s in spm_list:
        result.append({
            "spm_id": s.spm_id,
            "product_id": s.product_id,
            "process_name": s.process_name,
            "press_no": s.press_no,
            "cycle_time": s.cycle_time,
            "timestamp": s.timestamp,
            "user": s.user,
            "product_code": db.query(Product).filter(Product.product_id == s.product_id).first().product_code,
        })
    return result


@router.post("/spm", response_model=spm_schema.SPMResponse)
async def create_spm(
    spm: spm_schema.SPMCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """SPM設定を登録"""
    spm_data = spm.model_dump()
    spm_data['user'] = current_user['username']
    db_spm = SPM(**spm_data)
    db.add(db_spm)
    db.commit()
    db.refresh(db_spm)
    return db_spm
