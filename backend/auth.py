"""
Authentication Module
Handles JWT token generation, validation, and route protection.
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict, Any

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def generate_jwt(user_id: int, username: str, role: str) -> str:
    """
    Generate a JWT token for a user.

    Args:
        user_id: User's database ID
        username: User's username
        role: User's role ('admin' or 'user')

    Returns:
        str: Encoded JWT token
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request() -> Optional[str]:
    """
    Extract JWT token from request Authorization header.

    Returns:
        str: Token if found, None otherwise
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None

    # Expected format: "Bearer <token>"
    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    return parts[1]


def jwt_required(f):
    """
    Decorator to protect routes - requires valid JWT token.

    Usage:
        @app.route('/protected')
        @jwt_required
        def protected_route():
            current_user = get_jwt_identity()
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({
                'success': False,
                'error': 'Token de autenticación requerido'
            }), 401

        payload = verify_jwt(token)

        if not payload:
            return jsonify({
                'success': False,
                'error': 'Token inválido o expirado'
            }), 401

        # Store user info in request context
        request.current_user = payload

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator to protect admin-only routes.

    Usage:
        @app.route('/admin/users')
        @admin_required
        def admin_only_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()

        if not token:
            return jsonify({
                'success': False,
                'error': 'Token de autenticación requerido'
            }), 401

        payload = verify_jwt(token)

        if not payload:
            return jsonify({
                'success': False,
                'error': 'Token inválido o expirado'
            }), 401

        if payload.get('role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Acceso denegado: se requieren permisos de administrador'
            }), 403

        # Store user info in request context
        request.current_user = payload

        return f(*args, **kwargs)

    return decorated_function


def get_jwt_identity() -> Optional[Dict[str, Any]]:
    """
    Get current user info from JWT in request context.

    Returns:
        dict: User payload from JWT, or None if not authenticated
    """
    return getattr(request, 'current_user', None)
