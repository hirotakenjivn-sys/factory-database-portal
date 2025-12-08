
import sys
import os
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.production_scheduler import ProductionScheduler
from app.models import Process, Product, PO, MachineList, ProcessNameType, Calendar, Customer, Factory

def test_scheduler():
    # Mock DB Session
    db = MagicMock()

    # Mock Data
    factory = Factory(factory_id=1, factory_name="Main Factory")
    machine = MachineList(machine_list_id=1, factory_id=1, machine_no="P01", machine_type="PRESS")
    customer = Customer(customer_id=1, customer_name="Test Customer")
    product = Product(product_id=1, product_code="PROD-001", customer_id=1, is_active=True)
    process = Process(
        process_id=1, product_id=1, process_no=1, process_name="PRESS-PROCESS",
        rough_cycletime=Decimal("60"), setup_time=Decimal("30")
    )
    today = date.today()
    po = PO(
        po_id=1, po_number="PO-001", product_id=1, po_quantity=100000,
        delivery_date=today + timedelta(days=10), is_delivered=False
    )
    pnt = ProcessNameType(process_name="PRESS-PROCESS", day_or_spm=True)

    # Mock Query Logic
    def query_side_effect(model):
        query_mock = MagicMock()
        
        if model == MachineList:
            query_mock.filter.return_value.all.return_value = [machine]
            query_mock.all.return_value = [machine]
        elif model == Product:
            query_mock.filter.return_value.all.return_value = [product]
        elif model == PO:
            # Chain for PO
            filter_mock = query_mock.filter.return_value
            filter_mock.order_by.return_value.first.return_value = po
            filter_mock.all.return_value = [po]
            # Also handle simple filter().all()
            filter_mock.all.return_value = [po]
        elif model == Process:
            query_mock.filter.return_value.order_by.return_value.all.return_value = [process]
            # Also handle filter().first()
            query_mock.filter.return_value.first.return_value = process
        elif model == ProcessNameType:
            query_mock.filter.return_value.first.return_value = pnt
        elif model == Calendar:
            query_mock.filter.return_value.first.return_value = None
        
        return query_mock

    db.query.side_effect = query_side_effect

    # Initialize Scheduler with 12 hours
    scheduler = ProductionScheduler(db, working_hours=12)
    
    # Run Schedule Generation
    print("Generating Schedule...")
    try:
        result = scheduler.generate_schedule()
        
        print(f"Constrained Schedules: {len(result['constrained_schedules'])}")
        
        total_qty = 0
        for sch in result['constrained_schedules']:
            print(f"Date: {sch['planned_start'].date()}, Start: {sch['planned_start'].time()}, End: {sch['planned_end'].time()}, Qty: {sch['po_quantity']}")
            total_qty += sch['po_quantity']
            
        print(f"Total Scheduled Qty: {total_qty}")
        print(f"Expected Qty: 100000")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scheduler()
