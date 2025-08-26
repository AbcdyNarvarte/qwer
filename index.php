<?php
require_once __DIR__ . '/config/session.php';

// If a role session already exists for this tab, redirect to its dashboard
if(isset($_SESSION['user_level'])) {
    header("Location: dashboard.php?role=" . urlencode($_SESSION['user_level']));
    exit();
}

$error = '';

if($_SERVER['REQUEST_METHOD'] == 'POST') {
    require_once 'config/database.php';
    
    $username = $_POST['username'];
    $password = $_POST['password'];
    
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch();
    
    if($user && password_verify($password, $user['password'])) {
        // Switch this tab into a role-specific session bucket
        mrp_switch_to_role_session($user['user_level']);
        
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['user_level'] = $user['user_level'];
        
        header("Location: dashboard.php?role=" . urlencode($user['user_level']));
        exit();
    } else {
        $error = 'Invalid username or password';
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="assets/css/styles.css" rel="stylesheet">
</head>
<body class="full-height-center">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="login-card">
                    <div class="login-header">
                        <img src="assets/img/logo.png" alt="Novus Industry Solutions" class="brand-logo">
                        <h2>Novus Industry Solutions</h2>
                    </div>
                    
                    <?php if($error): ?>
                        <div class="alert alert-danger" role="alert">
                            <?php echo htmlspecialchars($error); ?>
                        </div>
                    <?php endif; ?>
                    
                    <form method="POST" action="">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-login">Sign In</button>
                    </form>
                    
                    <div class="mt-4 text-center">
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
