import pymysql
import sys

def check():
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="evanoso",
            password="1234",
            database="evanoso",
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"[!] Could not connect to database: {e}")
        return

    with conn.cursor() as cursor:
        print("\n" + "=" * 65)
        print("  1. RECENT USERS (Newest first)")
        print("=" * 65)
        cursor.execute("SELECT id, username, email, first_name, last_name, role_id, account_status, created_at FROM users ORDER BY id DESC LIMIT 5;")
        rows = cursor.fetchall()
        for r in rows:
            print(f"ID: {r['id']} | Username: {r['username']} | Name: {r['first_name']} {r['last_name']} | Role ID: {r['role_id']} | Status: {r['account_status']} | Created: {r['created_at']}")

        print("\n" + "=" * 65)
        print("  2. RECENT ACCOUNTS & BALANCES")
        print("=" * 65)
        cursor.execute("SELECT id, account_number, customer_id, available_balance, ledger_balance, status, opened_at FROM accounts ORDER BY id DESC LIMIT 5;")
        rows = cursor.fetchall()
        for r in rows:
            print(f"Account #: {r['account_number']} | Customer ID: {r['customer_id']} | Available: PHP {r['available_balance']:,.2f} | Status: {r['status']}")

        print("\n" + "=" * 65)
        print("  3. RECENT TRANSFERS")
        print("=" * 65)
        cursor.execute("SELECT id, transfer_reference, source_account_id, destination_account_id, amount, status, created_at FROM transfers ORDER BY id DESC LIMIT 5;")
        rows = cursor.fetchall()
        if not rows:
            print("  (No transfers recorded yet)")
        for r in rows:
            print(f"Ref: {r['transfer_reference']} | From Acc #{r['source_account_id']} -> To Acc #{r['destination_account_id']} | Amount: PHP {r['amount']:,.2f} | Status: {r['status']} | Time: {r['created_at']}")

        print("\n" + "=" * 65)
        print("  4. RECENT DEPOSITS & WITHDRAWALS")
        print("=" * 65)
        cursor.execute("SELECT 'Deposit' as tx_type, reference_number, account_id, amount, deposit_channel as channel, created_at FROM deposits ORDER BY id DESC LIMIT 3;")
        deposits = cursor.fetchall()
        cursor.execute("SELECT 'Withdrawal' as tx_type, reference_number, account_id, amount, withdrawal_channel as channel, created_at FROM withdrawals ORDER BY id DESC LIMIT 3;")
        withdrawals = cursor.fetchall()
        recent_txs = deposits + withdrawals
        if not recent_txs:
            print("  (No deposits or withdrawals recorded yet)")
        for r in recent_txs:
            print(f"Type: {r['tx_type']} | Ref: {r['reference_number']} | Account ID: {r['account_id']} | Amount: PHP {r['amount']:,.2f} | Channel: {r['channel']} | Time: {r['created_at']}")

        print("\n" + "=" * 65)
        print("  5. RECENT AUDIT LOGS (Real-time actions from website)")
        print("=" * 65)
        cursor.execute("SELECT id, user_id, action_type, entity_name, entity_id, action_timestamp FROM audit_logs ORDER BY id DESC LIMIT 5;")
        rows = cursor.fetchall()
        if not rows:
            print("  (No audit logs recorded yet)")
        for r in rows:
            print(f"Log #{r['id']} | Action: {r['action_type']} | Entity: {r['entity_name']} (ID: {r['entity_id']}) | User ID: {r['user_id']} | Time: {r['action_timestamp']}")

        print("\n" + "=" * 65 + "\n")
    conn.close()

if __name__ == "__main__":
    check()
