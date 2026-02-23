import requests
import concurrent.futures
import time
import statistics
import uuid
import random

# Configuration
API_URL = "https://07wrw4bg9j.execute-api.us-east-1.amazonaws.com/items"
# Using the token from verify_api.sh
TOKEN = "eyJraWQiOiJTN3ZqdHlSYVwvQnNuUU5QVGVtRmpnNm56SUhtVGhYRUhCZWd5WTNXTkRVTT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJjNGY4OTRkOC04MDUxLTcwYzEtZTFhMS00MzIyZGRkM2JkNjQiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX3A3SzZmVDdyQiIsImNvZ25pdG86dXNlcm5hbWUiOiJjNGY4OTRkOC04MDUxLTcwYzEtZTFhMS00MzIyZGRkM2JkNjQiLCJvcmlnaW5fanRpIjoiNjA4NjRlZWQtM2ZlNy00YWJkLTg3ZTctYzEzMzM0YmM5MjhiIiwiYXVkIjoiNzFobGUzNzJocjlvZ3F2dG91aGc3MmdhMWgiLCJldmVudF9pZCI6ImNhYjJlYjAyLWNjOTItNGIzMi1iOWE1LTEyNzg4OWJkNzRiNCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNzcxMzQzNDcyLCJleHAiOjE3NzEzNDcwNzIsImlhdCI6MTc3MTM0MzQ3MiwianRpIjoiN2Y5NTFkMzItMTQ4Mi00ZDk0LTk3N2EtMDQ1ZTY4MDljODVkIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.l8YVQkiv2w7rA3olzDrhzZkIVcr1ddDfstmteq5IcBvhHfjnrMkyRMsqatGf4A_F_DoSwJR04UZAGLlaFQevxEJr7tlFbuwIuSMFV0B-3ZGMAFwEex-26l2nL493aat0_UrZmVw45wZ6Sad_ocyet0Y6c1UUePXk59J4-vyM2mT3j-UxwozzrEkLtwqvexNCOuR7oC_MwxmjjIrPKIoJ7HJrudqAbpQr2fMaKdHjXL330juU1R_DeOdgBOQmXZf8SNSMUBNTDl2h8oIjWvUoJk941zf9V_4Vc45eA2vwZGN7p0BCtq24rMDUQFsBdpqOn1N7U8cgBTdJ7sUq-pfmpQ"
NUM_FLOWS = 100
CONCURRENT_FLOWS = 50 

def run_user_flow(flow_id):
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
    item_id = f"test-perf-{uuid.uuid4()}"
    results = []
    
    # helper
    def record(operation, start, resp, expected_status):
        duration = time.time() - start
        success = resp.status_code == expected_status
        return {
            "flow_id": flow_id,
            "operation": operation,
            "status_code": resp.status_code,
            "duration": duration,
            "success": success,
            "error": None if success else resp.text
        }

    # 1. POST (Create)
    start = time.time()
    payload = {
        "itemId": item_id,
        "name": f"Performance Test Item {flow_id}",
        "price": random.uniform(10.0, 100.0),
        "description": "Created during performance test"
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload)
        results.append(record("POST", start, resp, 201))
    except Exception as e:
        results.append({"flow_id": flow_id, "operation": "POST", "success": False, "error": str(e), "duration": time.time()-start})
        return results # Abort flow if creation fails

    # 2. GET (Read)
    start = time.time()
    try:
        resp = requests.get(f"{API_URL}/{item_id}", headers=headers)
        results.append(record("GET", start, resp, 200))
    except Exception as e:
        results.append({"flow_id": flow_id, "operation": "GET", "success": False, "error": str(e), "duration": time.time()-start})

    # 3. PUT (Update)
    start = time.time()
    payload["price"] = random.uniform(100.0, 200.0)
    try:
        resp = requests.put(f"{API_URL}/{item_id}", headers=headers, json=payload)
        results.append(record("PUT", start, resp, 200))
    except Exception as e:
        results.append({"flow_id": flow_id, "operation": "PUT", "success": False, "error": str(e), "duration": time.time()-start})

    # 4. DELETE (Delete)
    start = time.time()
    try:
        resp = requests.delete(f"{API_URL}/{item_id}", headers=headers)
        results.append(record("DELETE", start, resp, 200))
    except Exception as e:
        results.append({"flow_id": flow_id, "operation": "DELETE", "success": False, "error": str(e), "duration": time.time()-start})
        
    return results

def run_performance_test():
    print(f"Starting comprehensive performance test with {NUM_FLOWS} flows ({CONCURRENT_FLOWS} concurrent)...")
    print(f"Target URL: {API_URL}")
    print("Flow: POST -> GET -> PUT -> DELETE")
    
    all_results = []
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_FLOWS) as executor:
        future_to_id = {executor.submit(run_user_flow, i): i for i in range(NUM_FLOWS)}
        for future in concurrent.futures.as_completed(future_to_id):
            all_results.extend(future.result())
            
    total_duration = time.time() - start_time
    
    # Analyze results
    print("\n--- Test Results ---")
    print(f"Total Test Duration: {total_duration:.2f} seconds")
    
    ops = ["POST", "GET", "PUT", "DELETE"]
    for op in ops:
        op_results = [r for r in all_results if r["operation"] == op]
        successes = [r for r in op_results if r["success"]]
        failures = [r for r in op_results if not r["success"]]
        durations = [r["duration"] for r in op_results]
        
        print(f"\nOperation: {op}")
        print(f"  Count: {len(op_results)}")
        print(f"  Success: {len(successes)}")
        print(f"  Failed: {len(failures)}")
        if durations:
            print(f"  Avg Time: {statistics.mean(durations):.4f}s")
            print(f"  Max Time: {max(durations):.4f}s")
            
        if failures:
            print(f"  Sample Error: {failures[0].get('error') or failures[0].get('status_code')}")

if __name__ == "__main__":
    run_performance_test()
