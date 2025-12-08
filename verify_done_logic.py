import urllib.request
import urllib.parse
import json
import datetime

BASE_URL = "http://localhost:8000/api"

def login():
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({
        "username": "admin",
        "password": "admin123"
    }).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    with urllib.request.urlopen(req) as response:
        token_data = json.loads(response.read().decode('utf-8'))
        return token_data['access_token']

def ensure_packing_process_name_type(token):
    # Check if PACKING exists in ProcessNameType
    url = f"{BASE_URL}/master/process-names?search=PACKING"
    with urllib.request.urlopen(url) as response:
        names = json.loads(response.read().decode('utf-8'))
        if any(n['process_name'] == "PACKING" for n in names):
            print("PACKING process name type already exists.")
            return

    # Create PACKING process name type
    print("Creating PACKING process name type...")
    data = {
        "process_name": "PACKING",
        "day_or_spm": False # Assuming DAY type for packing
    }
    req = urllib.request.Request(
        f"{BASE_URL}/master/process-names",
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            print("Created PACKING process name type.")
    except urllib.error.HTTPError as e:
        print(f"Failed to create process name type: {e}")
        # It might have been created by another test run or race condition, so we continue

def get_or_create_packing_process(product_id, token):
    ensure_packing_process_name_type(token)
    # Check if PACKING process exists for this product
    url = f"{BASE_URL}/press/processes?product_id={product_id}"
    with urllib.request.urlopen(url) as response:
        processes = json.loads(response.read().decode('utf-8'))
        for p in processes:
            if "PACKING" in p['process_name'].upper() or "梱包" in p['process_name']:
                return p['process_id']
    
    # Create PACKING process if not exists
    print("Creating PACKING process...")
    data = {
        "product_id": product_id,
        "process_no": 99,
        "process_name": "PACKING",
        "rough_cycletime": 10.0,
        "setup_time": 0,
        "production_limit": 99999
    }
    req = urllib.request.Request(
        f"{BASE_URL}/press/processes",
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    with urllib.request.urlopen(req) as response:
        new_process = json.loads(response.read().decode('utf-8'))
        return new_process['process_id']

def register_trace(product_id, process_id, result="pass"):
    data = {
        "product_id": product_id,
        "lot_number": "TEST-LOT-DONE",
        "process_id": process_id,
        "employee_id": 1, # Assuming admin is 1
        "ok_quantity": 100,
        "ng_quantity": 0,
        "result": result,
        "date": datetime.date.today().isoformat(),
        "note": "Verification Test"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/trace/stamp-trace-simple",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def verify_done_logic():
    # 0. Login
    try:
        token = login()
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 1. Get a product (using the first one found)
    with urllib.request.urlopen(f"{BASE_URL}/master/products") as response:
        products = json.loads(response.read().decode('utf-8'))
        if not products:
            print("No products found.")
            return
        product_id = products[0]['product_id']
        print(f"Using Product ID: {product_id}")

    # 2. Get a normal process (e.g., PRESS)
    normal_process_id = None
    with urllib.request.urlopen(f"{BASE_URL}/press/processes?product_id={product_id}") as response:
        processes = json.loads(response.read().decode('utf-8'))
        if processes:
            normal_process_id = processes[0]['process_id']
            print(f"Using Normal Process ID: {normal_process_id} ({processes[0]['process_name']})")
    
    if not normal_process_id:
        print("No normal process found.")
        return

    # 3. Get or create PACKING process
    packing_process_id = get_or_create_packing_process(product_id, token)
    print(f"Using PACKING Process ID: {packing_process_id}")

    # 4. Register trace for Normal Process
    print("Registering trace for Normal Process...")
    resp_normal = register_trace(product_id, normal_process_id)
    print(f"Registered Trace ID: {resp_normal['stamp_trace_id']}")

    # 5. Register trace for PACKING Process
    print("Registering trace for PACKING Process...")
    resp_packing = register_trace(product_id, packing_process_id)
    print(f"Registered Trace ID: {resp_packing['stamp_trace_id']}")

    # 6. Verify 'done' flag
    print("Verifying 'done' flag...")
    with urllib.request.urlopen(f"{BASE_URL}/trace/stamp-traces?limit=5") as response:
        traces = json.loads(response.read().decode('utf-8'))
        
        trace_normal = next((t for t in traces if t['stamp_trace_id'] == resp_normal['stamp_trace_id']), None)
        trace_packing = next((t for t in traces if t['stamp_trace_id'] == resp_packing['stamp_trace_id']), None)

        if trace_normal:
            print(f"Normal Trace Done: {trace_normal['done']} (Expected: False)")
        else:
            print("Normal Trace not found.")

        if trace_packing:
            print(f"Packing Trace Done: {trace_packing['done']} (Expected: True)")
        else:
            print("Packing Trace not found.")

if __name__ == "__main__":
    verify_done_logic()
