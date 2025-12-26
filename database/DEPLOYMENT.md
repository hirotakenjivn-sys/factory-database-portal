# Production Deployment Guide

To import the data into the production database, execute the generated SQL files in the following order.

## Prerequisites
- Ensure you have access to the MySQL database.
- Ensure the database schema (`init.sql`) has been applied.

## Execution Order

### 1. Import Customers and Employees
This file contains the seed data for Customers and Employees.
It must be run **first** because Products depend on Customers.

```bash
mysql -u [USER] -p [DATABASE_NAME] < database/import_seed_data.sql
```

### 2. Import Products
This file contains the Product list.
It links products to customers by name.

```bash
mysql -u [USER] -p [DATABASE_NAME] < database/import_products.sql
```

## Notes
- **Safety**: The scripts use `INSERT IGNORE` and `INSERT ... SELECT ... WHERE NOT EXISTS`, so they are safe to run multiple times. Existing data will not be duplicated.
- **Encoding**: The files are encoded in `UTF-8`. Ensure your terminal or MySQL client supports UTF-8.
