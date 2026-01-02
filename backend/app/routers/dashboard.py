from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from ..database import get_db
from ..models.po import PO
from ..models.mold import BrokenMold
from ..models.customer import Customer
from ..models.product import Product
from ..models.process import Process
from ..models.iot_button_event import IotButtonEvent
from ..models.employee import Employee
from ..models.factory import MachineList
from ..models.material import MaterialRate

router = APIRouter()


@router.get("/cards")
async def get_dashboard_cards(db: Session = Depends(get_db)):
    """
    ダッシュボードカード用の統計データ（8カード）
    """
    # Products
    products = db.query(func.count(Product.product_id)).scalar() or 0

    # Customers
    customers = db.query(func.count(Customer.customer_id)).scalar() or 0

    # Processes
    processes = db.query(func.count(Process.process_id)).scalar() or 0

    # Count (IoT Events from Raspi)
    count = db.query(func.count(IotButtonEvent.event_id)).scalar() or 0

    # Employees
    employees = db.query(func.count(Employee.employee_id)).scalar() or 0

    # Machine List
    machine_list = db.query(func.count(MachineList.machine_list_id)).scalar() or 0

    # Material Rates
    material_rates = db.query(func.count(MaterialRate.material_rate_id)).scalar() or 0

    return {
        "products": products,
        "customers": customers,
        "processes": processes,
        "count": count,
        "employees": employees,
        "machine_list": machine_list,
        "material_rates": material_rates
    }


@router.get("/sales-weekly")
async def get_sales_weekly(db: Session = Depends(get_db)):
    """
    週別PO売上推移（仮データ）
    """
    return [
        {"week": 1, "quantity": 12000},
        {"week": 2, "quantity": 15000},
        {"week": 3, "quantity": 11000},
        {"week": 4, "quantity": 14000}
    ]


@router.get("/production-daily")
async def get_production_daily(db: Session = Depends(get_db)):
    """
    直近7日の生産数推移（仮データ）
    """
    today = date.today()
    return [
        {"date": str(today - timedelta(days=6)), "quantity": 5200},
        {"date": str(today - timedelta(days=5)), "quantity": 5400},
        {"date": str(today - timedelta(days=4)), "quantity": 5100},
        {"date": str(today - timedelta(days=3)), "quantity": 5500},
        {"date": str(today - timedelta(days=2)), "quantity": 5300},
        {"date": str(today - timedelta(days=1)), "quantity": 4800},
        {"date": str(today), "quantity": 5000}
    ]
