import urllib.request
import json

def fetch_stamp_traces():
    url = "http://localhost:8000/api/trace/stamp-traces?limit=20"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            traces = json.loads(data)
            
            print(f"Found {len(traces)} records:")
            print("-" * 80)
            for trace in traces:
                print(f"ID: {trace.get('stamp_trace_id')}")
                print(f"Date: {trace.get('date')}")
                print(f"Product: {trace.get('product_code')}")
                print(f"Process: {trace.get('process_name')}")
                print(f"Lot: {trace.get('lot_number')}")
                print(f"Employee: {trace.get('employee_name')}")
                print(f"Result: {trace.get('result')} (OK: {trace.get('ok_quantity')}, NG: {trace.get('ng_quantity')})")
                print("-" * 80)
            
    except Exception as e:
        print(f"Error fetching traces: {e}")

if __name__ == "__main__":
    fetch_stamp_traces()
