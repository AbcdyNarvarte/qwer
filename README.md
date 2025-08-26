# Login System with 4 User Levels

A simple PHP login system with MySQL database featuring 4 different user levels: Owner, Manager, Supplier, and Employee.

## Features

- **4 User Levels**: Owner, Manager, Supplier, Employee
- **Bootstrap Styling**: Modern and responsive design
- **MySQL Database**: Secure user authentication
- **Session Management**: Proper session handling
- **Individual Dashboards**: Each user level has its own dashboard

## Setup Instructions

### 1. Database Setup

1. Open your MySQL client (phpMyAdmin, MySQL Workbench, or command line)
2. Import the `database_setup.sql` file to create the database and tables
3. The database will be named `db` and will contain sample users

### 2. Database Configuration

Edit `config/database.php` if your MySQL settings are different:
```php
$host = 'localhost';     // Your MySQL host
$dbname = 'db';          // Database name
$username = 'root';      // Your MySQL username
$password = '';          // Your MySQL password
```

### 3. Web Server Setup

1. Place all files in your web server directory (e.g., `htdocs` for XAMPP)
2. Make sure PHP and MySQL are running
3. Access the application through your web browser

## Demo Accounts

The system comes with 4 pre-configured accounts:

| Username | Password | User Level |
|----------|----------|------------|
| owner    | password123 | Owner |
| manager  | password123 | Manager |
| supplier | password123 | Supplier |
| employee | password123 | Employee |

## File Structure

```
mrp/
├── config/
│   └── database.php          # Database connection
├── dashboards/
│   ├── owner_dashboard.php   # Owner dashboard
│   ├── manager_dashboard.php # Manager dashboard
│   ├── supplier_dashboard.php # Supplier dashboard
│   └── employee_dashboard.php # Employee dashboard
├── database_setup.sql        # Database setup script
├── index.php                 # Login page
├── dashboard.php             # Dashboard router
├── logout.php                # Logout functionality
└── README.md                 # This file
```

## Security Features

- Password hashing using PHP's `password_hash()` and `password_verify()`
- Prepared statements to prevent SQL injection
- Session-based authentication
- Input validation and sanitization
- Access control based on user levels

## Customization

Each dashboard can be customized by editing the respective files in the `dashboards/` directory. The current dashboards show simple welcome messages as requested.

## Requirements

- PHP 7.0 or higher
- MySQL 5.7 or higher
- Web server (Apache, Nginx, or XAMPP)
- Bootstrap 5.1.3 (loaded via CDN)
