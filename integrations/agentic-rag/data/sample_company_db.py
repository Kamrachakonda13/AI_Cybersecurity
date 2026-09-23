"""
Generate the sample company SQLite database for the SQL query tool.

Creates data/sample_company.db with realistic tables:
    users         - employees with roles and teams
    products      - the platform's product catalog
    transactions  - customer transactions
    support_tickets - customer support tickets

Run once to create, or again to regenerate:
    python data/sample_company_db.py
"""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "sample_company.db"

random.seed(42)

USERS = [
    ("u001", "alice@acme.com", "Alice", "csuite", "executive", "2020-01-15"),
    ("u002", "bob@acme.com", "Bob", "manager", "platform", "2021-03-22"),
    ("u003", "carol@acme.com", "Carol", "junior", "product", "2023-06-01"),
    ("u004", "dave@acme.com", "Dave", "manager", "sre", "2019-11-10"),
    ("u005", "eve@acme.com", "Eve", "senior", "security", "2018-05-20"),
    ("u006", "frank@acme.com", "Frank", "junior", "engineering", "2024-02-14"),
    ("u007", "grace@acme.com", "Grace", "manager", "analytics", "2020-09-08"),
    ("u008", "henry@acme.com", "Henry", "senior", "platform", "2017-07-03"),
    ("u009", "ivy@acme.com", "Ivy", "junior", "marketing", "2024-08-19"),
    ("u010", "jack@acme.com", "Jack", "csuite", "executive", "2016-02-11"),
]

PRODUCTS = [
    ("p001", "Workflow Engine", "automation", 299.00, "active"),
    ("p002", "Integration Hub", "connectivity", 199.00, "active"),
    ("p003", "Analytics Suite", "analytics", 499.00, "active"),
    ("p004", "Notification Service", "messaging", 99.00, "active"),
    ("p005", "Auth Gateway", "security", 149.00, "active"),
    ("p006", "Legacy Billing", "billing", 199.00, "deprecated"),
    ("p007", "Enterprise Support", "support", 999.00, "active"),
    ("p008", "Data Pipeline", "data", 349.00, "beta"),
    ("p009", "Mobile SDK", "mobile", 79.00, "active"),
    ("p010", "Compliance Kit", "compliance", 599.00, "active"),
]

SUPPORT_CATEGORIES = ["billing", "technical", "account", "bug", "feature_request"]
SEVERITIES = ["low", "medium", "high", "critical"]

CUSTOMERS = [f"cust_{i:04d}" for i in range(1, 51)]


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript("""
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            team TEXT NOT NULL,
            hire_date TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            status TEXT NOT NULL
        );

        CREATE TABLE support_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            created_date TEXT NOT NULL,
            resolved_date TEXT,
            description TEXT NOT NULL
        );
    """)

    conn.executemany(
        "INSERT INTO users (user_id, email, full_name, role, team, hire_date) VALUES (?, ?, ?, ?, ?, ?)",
        USERS,
    )
    conn.executemany(
        "INSERT INTO products (product_id, name, category, price, status) VALUES (?, ?, ?, ?, ?)",
        PRODUCTS,
    )

    # Transactions: 500 rows over the last 12 months
    tx_statuses = ["completed", "completed", "completed", "refunded", "pending"]
    start = datetime(2025, 9, 20)
    txs = []
    for _ in range(500):
        customer = random.choice(CUSTOMERS)
        product = random.choice(PRODUCTS)
        amount = round(product[3] * random.uniform(0.8, 1.2), 2)
        date = (start - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        status = random.choice(tx_statuses)
        txs.append((customer, product[0], amount, date, status))
    conn.executemany(
        "INSERT INTO transactions (customer_id, product_id, amount, transaction_date, status) VALUES (?, ?, ?, ?, ?)",
        txs,
    )

    # Support tickets: 200 rows
    descriptions = [
        "Unable to authenticate after password reset",
        "Billing amount does not match quote",
        "Workflow is stuck in pending state",
        "Integration with Salesforce fails silently",
        "Dashboard is slow to load under load",
        "Need bulk export of transaction history",
        "API returns 500 on large payloads",
        "Notification emails arriving delayed",
        "Account permissions not syncing",
        "Feature request for custom webhook retries",
    ]
    tickets = []
    for _ in range(200):
        customer = random.choice(CUSTOMERS)
        category = random.choice(SUPPORT_CATEGORIES)
        severity = random.choice(SEVERITIES)
        status = random.choice(["open", "in_progress", "resolved", "resolved", "closed"])
        created = start - timedelta(days=random.randint(0, 180))
        resolved = None
        if status in ("resolved", "closed"):
            resolved = created + timedelta(days=random.randint(1, 14))
        tickets.append((
            customer,
            category,
            severity,
            status,
            created.strftime("%Y-%m-%d"),
            resolved.strftime("%Y-%m-%d") if resolved else None,
            random.choice(descriptions),
        ))
    conn.executemany(
        "INSERT INTO support_tickets (customer_id, category, severity, status, created_date, resolved_date, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
        tickets,
    )

    conn.commit()

    # Summary
    for table in ("users", "products", "transactions", "support_tickets"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n} rows")

    conn.close()
    print(f"\nCreated {DB_PATH} ({DB_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    print("Generating sample company database...")
    main()
