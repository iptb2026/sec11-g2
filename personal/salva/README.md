# Salva Banking System — IPT2 Submission & System Guide

The **Salva Banking System** is a full-stack, enterprise-grade multi-tier banking web application developed for **Integrative Programming & Technologies 2 (IPT2)**. It provides real-time banking operations, strict multi-role access control, data ownership isolation, and double-entry transaction ledgers backed by a relational MySQL database.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             Quasar 2 (Vue 3 + Pinia) Frontend               │
│   • Admin Portal    • Staff Portal    • Customer Portal     │
│   Port: 9004 | Hash URL: http://localhost:9004/salva-wui/   │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON / JWT)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI (Python) Appserver                  │
│   • JWT Auth & Revocation  • RBAC & Customer Ownership      │
│   • Atomic Row Locking     • Financial Ledgers              │
│   Port: 8000 | Swagger Docs: http://127.0.0.1:8000/docs     │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy ORM / PyMySQL
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  MySQL Database (`salva`)                   │
│   • 17 Relational Tables   • Foreign Key Constraints        │
│   Port: 3306 | Host: 127.0.0.1                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Demo User Credentials

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `1234` | Full access: Roles, Account Types, Banks, Fee Types, User Management, Audit Logs, plus all Banking Operations. |
| **Bank Staff / Teller** | `mgarcia` | `1234` | Banking Operations: Accounts, Withdrawal Limits, Interest Policies, Deposits, Withdrawals, Internal/External Transfers, Fee Assessments, Interest Postings, General Ledger. |
| **Bank Customer** | `jdelacruz` | `1234` | Customer Self-Service: My Accounts (Savings & Checking), Portfolio Summary, Fast Internal Transfer, Interbank InstaPay Outward Transfer, Transaction History Timeline. |

---

## 🚀 Quick Start Guide

### 1. Database Setup (MySQL)
Make sure MySQL is running on port `3306` with database `salva` and credentials `salva`/`salva12`:
```sql
CREATE DATABASE IF NOT EXISTS salva;
CREATE USER IF NOT EXISTS 'salva'@'%' IDENTIFIED BY 'salva12';
GRANT ALL PRIVILEGES ON salva.* TO 'salva'@'%';
FLUSH PRIVILEGES;
```

### 2. Backend Setup & Run (FastAPI)
```powershell
cd c:\Users\Student\Downloads\salva\appserver

# Seed standard demo accounts and reference data
python app/database/seed.py

# Start FastAPI Uvicorn Server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

### 3. Frontend Setup & Run (Quasar)
```powershell
cd c:\Users\Student\Downloads\salva\appserver\frontend

# Install dependencies (Node 20 compatible)
npm install

# Launch Development Server
npm run dev

# Or build production bundle
npm run build
```
- **Web User Interface**: `http://localhost:9004/salva-wui/#/login`

---

## 🛡️ Security & Role-Based Access Control (RBAC)

1. **Authentication & Session Revocation**:
   - `POST /auth/login` issues JSON Web Tokens (JWT) signed with HMAC-SHA256 containing expiration (`exp`).
   - Session tracking records logins into MySQL `user_sessions`.
   - `POST /auth/logout` immediately marks the server session as revoked (`revoked_at`).
2. **Role Authorization**:
   - Endpoints in Layer 1 & 2 (`/roles/`, `/account-types/`, `/banks/`, `/fee-types/`, `/users/`, `/audit-logs/`, `/sessions/`) require `ADMIN` role.
   - Staff members trying to modify administration entities receive `403 Forbidden: Access forbidden: required role in ['ADMIN']`.
3. **Customer Data Ownership Enforcement**:
   - Customers accessing `/accounts/`, `/deposits/`, `/withdrawals/`, `/transfers/`, or `/interbank-transfers/` are automatically restricted to records where `customer_id == current_user.id` or account ownership matches.
   - Direct requests to access another customer's account (e.g. `GET /accounts/{other_id}`) return `403 Forbidden: You do not have permission to access another customer's account`.

---

## 📊 Database Architecture (17 Tables)

1. `roles` — System access roles (`ADMIN`, `STAFF`, `CUSTOMER`)
2. `users` — User profiles with bcrypt hashed passwords
3. `user_sessions` — Active & revoked JWT login sessions
4. `audit_logs` — Immutable system audit log
5. `account_types` — Savings, checking, time-deposit products
6. `accounts` — Bank accounts with available & ledger balances
7. `banks` — External partner clearing banks (BDO, BPI, MBTC, etc.)
8. `fee_types` — Service fee definitions and percentage rates
9. `withdrawal_limits` — Account daily withdrawal limits and tracking
10. `interest_policies` — Yield policy configurations and compounding rules
11. `deposits` — Cash, ATM, and online credit deposits with atomic locks
12. `withdrawals` — Cash and branch debit withdrawals with daily limit checks
13. `transfers` — Dual-account internal transfers with deadlock prevention
14. `interbank_transfers` — Outward interbank clearing transactions
15. `fee_records` — Fee assessments and account debits
16. `interest_records` — Interest calculations with before/after balance snapshots
17. `ledger_entries` — General ledger double-entry journal entries
