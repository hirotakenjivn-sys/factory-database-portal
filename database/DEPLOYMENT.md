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

## Docker Execution (Recommended)
If you are running the application with Docker and do not have `mysql` installed on your host machine, use the following commands:

### 1. Import Customers and Employees
```bash
docker exec -i factory-db mysql -u root -p factory_db < database/import_seed_data.sql
```

### 2. Import Products
```bash
docker exec -i factory-db mysql -u root -p factory_db < database/import_products.sql
```

### 3. Import Process Names
```bash
docker exec -i factory-db mysql -u root -p factory_db < database/import_process_names.sql
```

Note: You will be prompted for the database password after running each command.
