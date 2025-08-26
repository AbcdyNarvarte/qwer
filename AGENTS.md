# AGENTS.md

## Commands
- Start server: Start XAMPP control panel and run Apache + MySQL
- Test database: Run SQL queries in phpMyAdmin or MySQL client
- No build/lint commands - this is a plain PHP application

## Architecture
- PHP/MySQL MRP (Material Resource Planning) system with 4 user levels
- Database: `db` with tables: users, suppliers, clients, raw_mats, products, orders
- Main entry: index.php (login page), dashboard.php (router)
- Folders: config/ (database.php), dashboards/, manager/, owner/, assets/
- Authentication: Session-based with password hashing
- Bootstrap 5.1.3 via CDN for styling

## Code Style
- PHP: snake_case variables, camelCase in HTML/JS
- Database: Prepared statements with PDO, foreign key constraints
- Security: password_hash/verify, input validation, session checks
- HTML: Bootstrap classes, responsive design
- Error handling: Try-catch for DB, user-friendly messages
- File structure: Logical separation by user level and functionality
