import logging
import os
import pytz
from datetime import datetime

# Configure the user activity logger
class UserActivityLogger:
    def __init__(self):
        # Ensure log directory exists
        os.makedirs('C:/capstone/log_f', exist_ok=True)
        
        # Configure the main logger
        self.logger = logging.getLogger('user_activity')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to prevent duplicate logs
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler('C:/capstone/log_f/user_activity.log')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)

    def log_activity(self, user_id, username, action, feature, operation, details=None):
        """
        Log user activity with standardized format
        
        Parameters:
        - user_id: User's ID
        - username: User's username
        - action: The specific action performed (e.g., 'Added client', 'Updated supplier')
        - feature: The feature being used (client, order, storage, supplier, mail)
        - operation: CRUD operation (create, read, update, delete, search)
        - details: Additional details about the action
        """
        timestamp = datetime.now(pytz.timezone('Asia/Manila')).strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"User ID: {user_id} | Username: {username} | Feature: {feature} | Operation: {operation} | Action: {action}"
        
        if details:
            message += f" | Details: {details}"
            
        message += f" | Time: {timestamp}"
        
        self.logger.info(message)

# Create a singleton instance
user_activity_logger = UserActivityLogger()