<?php
require_once __DIR__ . '/config/session.php';

// Check if user is logged in in this role-specific session
if(!isset($_SESSION['user_level'])) {
    header("Location: index.php");
    exit();
}

// Redirect to appropriate dashboard based on user level
switch($_SESSION['user_level']) {
    case 'owner':
        header("Location: owner/owner_dashboard.php");
        break;
    case 'manager':
        header("Location: manager/manager_dashboard.php");
        break;
    case 'supplier':
        header("Location: supplier/supplier_dashboard.php");
        break;
    case 'employee':
        header("Location: dashboards/employee_dashboard.php");
        break;
    default:
        header("Location: index.php");
        break;
}
exit();
?>
