# ESPADA Banking System — Evanoso Frontend & API

A full-stack banking interface and API implementation for the IPT2 final project submission. Built with **Vue 3**, **Quasar Framework**, **FastAPI**, and **MySQL**.

---

## ⚡ TL;DR — Quick Setup & Database Seeding

> [!IMPORTANT]
> A fresh clone or new environment has **no database data**. You must run `python seed.py` once to create all 17 tables and default demo accounts before running the application.

### 1. Database & Seeding
Ensure MySQL/MariaDB is running on port 3306 with database `evanoso`:
```powershell
cd personal\evanoso\appserver
python seed.py
```
*(Creates all tables, roles, reference banks, account types, test users, and a customer account with ₱25,000 balance).*

### 2. Start Backend (Terminal 1)
```powershell
cd personal\evanoso\appserver
python -m uvicorn app.main:app --host 127.0.0.1 --port 5001 --reload
```
- API Docs: `http://127.0.0.1:5001/docs`

### 3. Start Frontend (Terminal 2)
```powershell
cd personal\evanoso\appclient
npm install
npm run dev -- --host 127.0.0.1 --port 9000
```
- Web App: `http://127.0.0.1:9000`

### 🔑 Test Credentials (All accounts use `Password123!`)
| Role | Username | Password | View / Capabilities |
|---|---|---|---|
| **Admin** | `admin` | `Password123!` | Blue theme — User CRUD, Roles, Banks, Sessions, Audit Logs |
| **Staff** | `staff` | `Password123!` | Teal theme — Account opening, Deposit/Withdrawal processing |
| **Customer** | `customer` | `Password123!` | Purple theme — Own balance (₱25k), Transfers, Transaction history |

---

## 1. Architecture Overview

```
[ Browser / Quasar Client ]  (Port 9000)
             │
             │ HTTP / REST API (JWT Bearer Auth)
             ▼
[ FastAPI / Uvicorn Server ]  (Port 5001)
             │
             │ SQLAlchemy ORM / PyMySQL
             ▼
[ MySQL Relational Database ] (Port 3306)
```

- **Frontend**: Vue 3 + Vite + Quasar Framework + Pinia Store + Vue Router + Axios
- **Backend**: FastAPI + Uvicorn + SQLAlchemy + PyMySQL + Jose JWT + Passlib (bcrypt)
- **Database**: MySQL with schema across Layer 1 (Reference Data), Layer 2 (Identity & Access), Layer 3 (Accounts), Layer 4 (Transactions), and Layer 5 (Ledger).

---

## 2. Prerequisites & Requirements

- **Node.js** v18+ (tested with v20+)
- **Python** 3.11+
- **MySQL** 8.0+ running on `localhost:3306`

---

## 3. Installation & Setup

### Terminal 1: Database Setup & Seeding

1. Ensure MySQL is running on port 3306 and database `evanoso` (or configured database) exists:
   ```sql
   CREATE DATABASE IF NOT EXISTS evanoso;
   ```
2. Navigate to the backend directory:
   ```bash
   cd personal/evanoso/appserver
   ```
3. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy pymysql python-jose passlib bcrypt python-multipart email-validator
   ```
4. Run the seed script to create all database tables and default test users:
   ```bash
   python seed.py
   ```

### Terminal 2: Start Backend Server

From `personal/evanoso/appserver`:
```bash
# Windows PowerShell:
uvicorn app.main:app --host 127.0.0.1 --port 5001 --reload

# Linux / macOS:
./run.sh
```
- API Documentation (Swagger UI): `http://127.0.0.1:5001/docs`
- Health Check: `http://127.0.0.1:5001/`

### Terminal 3: Start Frontend Application

From `personal/evanoso/appclient`:
```bash
cd personal/evanoso/appclient
npm install
npm run dev
```
- Application will open on: `http://localhost:9000`

---

## 4. Environment Variables

### Frontend (`personal/evanoso/appclient/.env`)
```ini
# Backend API Base URL
VITE_API_BASE_URL=http://localhost:5001
```

### Backend (`personal/evanoso/appserver/app/core/config.py`)
Configurable via system environment variables:
| Variable | Default Value | Description |
|---|---|---|
| `DB_USER` | `evanoso` | MySQL user |
| `DB_PASSWORD` | `1234` | MySQL password |
| `DB_HOST` | `127.0.0.1` | MySQL host address |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `evanoso` | Database schema name |

---

## 5. Test User Credentials

| Role | Username | Password | Access Level |
|---|---|---|---|
| **ADMIN** | `admin` | `Password123!` | System Administration, User CRUD, Role CRUD, Bank CRUD, Account Types, Fee Types, Session Revocation, Audit Logs |
| **STAFF** | `staff` | `Password123!` | Banking Operations, Account Opening, Deposit Processing, Withdrawal Processing |
| **CUSTOMER** | `customer` | `Password123!` | Personal Dashboard, Own Account Balances, Internal Fund Transfers, Personal Transaction History |

---

## 6. Role-Based Capabilities & Differentiation

The frontend implements distinct layouts, navigation flows, and capabilities tailored to each role:

### Admin (`/admin/*`)
- **Blue theme** with full administration drawer.
- **Dashboard**: System-wide counts of Users, Roles, Accounts, and Banks.
- **Users Management**: Full CRUD interface (Create, Read, Update, Delete) with validation dialogs.
- **Roles Management**: Full CRUD for system roles and permissions.
- **Banks Management**: Full CRUD for partner and clearing banks.
- **Account Types & Fee Types**: Full CRUD for interest rates, minimum balances, and fee schedules.
- **Accounts**: Complete oversight of all customer accounts with status toggling.
- **Sessions & Audit Logs**: Real-time session monitoring with remote revocation capability and read-only audit log review.

### Staff (`/staff/*`)
- **Teal theme** with operations-focused drawer.
- **Hidden Admin Areas**: Staff cannot view or edit Roles, Banks, System Settings, Sessions, or Audit Logs.
- **Account Opening**: Form to open new bank accounts for customers.
- **Deposit Processing**: Process cash/ATM/online deposits with automatic available and ledger balance incrementing.
- **Withdrawal Processing**: Process teller withdrawals with balance validation and daily limit checks.

### Customer (`/customer/*`)
- **Deep purple theme** tailored for banking customers.
- **Customer Data Ownership**: Customers **only** see their own accounts via the secure `GET /accounts/my` endpoint. Changing account IDs in the UI cannot expose another user's balance.
- **Personal Dashboard**: Aggregate available balance across all accounts and status indicator.
- **My Accounts**: Visual account cards displaying account numbers, branch info, and balances.
- **Fund Transfers**: Transfer money to another account with immediate balance debit/credit updates.
- **Transaction History**: Filterable history of personal deposits, withdrawals, and transfers.

---

## 7. CRUD Demonstration (IPT2 Requirement)

### Resource: Users (`/users/`)

1. **CREATE**:
   - In Admin Panel > Users, click **Add User**.
   - Fill in username, password, names, email, and assign a role.
   - Frontend sends `POST /users/`. Status: `201 Created`.
2. **READ**:
   - Table immediately renders the list from `GET /users/`.
3. **UPDATE**:
   - Click the **Edit** (pencil) icon on any user row.
   - Update first name, email, or status.
   - Frontend sends `PUT /users/{id}`. Status: `200 OK`.
4. **DELETE**:
   - Click the **Delete** (trash) icon.
   - Confirm in the Quasar confirmation dialog.
   - Frontend sends `DELETE /users/{id}`. Status: `204 No Content`.
   - If related records exist (foreign key constraint), server returns `409 Conflict` and frontend displays a friendly warning banner.

---

## 8. Hoppscotch / cURL API Verification Examples

### 1. Authenticate (Login)
```bash
curl -X POST "http://127.0.0.1:5001/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Password123!"
```
**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Fetch User Profile (`/auth/me`)
```bash
curl -X GET "http://127.0.0.1:5001/auth/me" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```
**Response (`200 OK`):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@bank.local",
  "first_name": "System",
  "middle_name": null,
  "last_name": "Admin",
  "role_id": 1,
  "role_code": "ADMIN",
  "role_name": "System Administrator",
  "account_status": "ACTIVE"
}
```

### 3. Customer Data Ownership (`/accounts/my`)
```bash
curl -X GET "http://127.0.0.1:5001/accounts/my" \
  -H "Authorization: Bearer <CUSTOMER_ACCESS_TOKEN>"
```
**Response (`200 OK`):**
```json
[
  {
    "id": 1,
    "account_number": "1000-2026-0001",
    "customer_id": 3,
    "account_type_id": 1,
    "available_balance": 25000.00,
    "ledger_balance": 25000.00,
    "currency_code": "PHP",
    "status": "ACTIVE",
    "opened_at": "2026-08-27T05:00:00",
    "closed_at": null,
    "branch_code": "MAIN-01"
  }
]
```
