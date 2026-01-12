import logging
import sys
import json
from datetime import datetime, timezone
from flask import Flask, jsonify, request, g, redirect

# Configure logging to stdout (CloudWatch friendly)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.route('/', methods=['GET'])
    def index():
        """Root endpoint - redirect to profile (auth)"""
        return redirect('/profile')

    @app.route('/health', methods=['GET'])
    def health_check():
        """Public health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

    @app.route('/profile', methods=['GET'])
    def get_profile():
        """Protected profile endpoint - reads OIDC headers from ALB"""
        # In a real ALB+Cognito setup, x-amzn-oidc-data contains the JWT
        # For this demo, check if header exists or user claims are present
        
        # NOTE: In a real scenario you would verify the signature of JWT in x-amzn-oidc-data
        # For simplicity in this demo, we check for presence or a simulated header
        
        # ALB passes these headers after successful authentication
        oidc_data = request.headers.get('x-amzn-oidc-data')
        
        if not oidc_data and not app.config.get('TESTING'):
            # In testing we might bypass this or mock it, but if live and missing header -> 401
            logger.warning("Unauthorized access attempt to /profile")
            return jsonify({"error": "Unauthorized"}), 401
            
        # Simulating extraction of claims. In real app, decode JWT.
        # Here we mock return values if it's a test or assuming ALB passed legitimate format
        user_info = {
            "user_id": "mock-user-id",
            "email": request.headers.get('x-amzn-oidc-email', 'user@example.com'),
            "name": request.headers.get('x-amzn-oidc-name', 'John Doe')
        }
        
        if oidc_data:
             # Just showing we acknowledged the auth header
             logger.info("Authenticated request received")

        return jsonify(user_info), 200

    @app.route('/orders', methods=['POST'])
    def create_order():
        """Protected orders endpoint"""
        # Reuse same auth logic for demo
        oidc_data = request.headers.get('x-amzn-oidc-data')
        if not oidc_data and not app.config.get('TESTING'):
             return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid payload"}), 400
            
        item = data.get("item")
        quantity = data.get("quantity")
        
        if not item or not quantity or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Invalid item or quantity"}), 400
            
        order_id = "ORD-12345" # Mock ID
        logger.info(f"Order created: {order_id} for {item} x{quantity}")
        
        return jsonify({
            "order_id": order_id,
            "status": "created"
        }), 201

    @app.errorhandler(Exception)
    def handle_error(e):
        logger.error(f"Unhandled exception: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=app.config['PORT'])
