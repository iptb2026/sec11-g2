import requests

BASE = "http://127.0.0.1:5001"

def get_token(username, password):
    r = requests.post(f"{BASE}/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200, f"Login failed for {username}: {r.text}"
    return r.json()["access_token"]

# 1. Acquire tokens for all 3 roles
admin_token = get_token("admin", "Password123!")
staff_token = get_token("staff", "Password123!")
customer_token = get_token("customer", "Password123!")

print("1. TOKENS ACQUIRED SUCCESSFULLY")

# 2. Test missing token on protected endpoint /auth/me
r_no_token = requests.get(f"{BASE}/auth/me")
print(f"2. Missing Token /auth/me: Status {r_no_token.status_code} (Expected 401)")
assert r_no_token.status_code == 401

# 3. Test invalid token
r_bad_token = requests.get(f"{BASE}/auth/me", headers={"Authorization": "Bearer invalid_token_123"})
print(f"3. Invalid Token /auth/me: Status {r_bad_token.status_code} (Expected 401)")
assert r_bad_token.status_code == 401

# 4. Test Customer Data Isolation via /accounts/my
r_cust_my = requests.get(f"{BASE}/accounts/my", headers={"Authorization": f"Bearer {customer_token}"})
print(f"4. Customer /accounts/my: Status {r_cust_my.status_code}, Accounts count: {len(r_cust_my.json())}")
assert r_cust_my.status_code == 200
for acc in r_cust_my.json():
    print(f"   Account {acc['account_number']} belongs to Customer ID {acc['customer_id']}")
    # Verify every account returned belongs to this customer (customer id = 6)
    assert acc['customer_id'] == 6

# 5. Test Staff on /accounts/my (Staff has no customer bank accounts)
r_staff_my = requests.get(f"{BASE}/accounts/my", headers={"Authorization": f"Bearer {staff_token}"})
print(f"5. Staff /accounts/my: Status {r_staff_my.status_code}, Accounts count: {len(r_staff_my.json())} (Expected 0)")
assert r_staff_my.status_code == 200
assert len(r_staff_my.json()) == 0

# 6. Test wrong password
r_wrong_pass = requests.post(f"{BASE}/auth/login", data={"username": "admin", "password": "WrongPassword!"})
print(f"6. Wrong Password: Status {r_wrong_pass.status_code} (Expected 401)")
assert r_wrong_pass.status_code == 401

# 7. Test Logout token revocation
r_logout = requests.post(f"{BASE}/auth/logout", headers={"Authorization": f"Bearer {admin_token}"})
print(f"7. Admin Logout: Status {r_logout.status_code} (Expected 204)")
assert r_logout.status_code == 204

print("\nALL AUTH & SECURITY TESTS PASSED!")
