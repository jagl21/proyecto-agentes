"""
Flask API Server for Posts Application
Provides REST API endpoints for managing news posts.
Now includes authentication and serves the SPA frontend.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database
from models import Post
import auth
import os

# Configure Flask to serve static files from frontend directory
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')

# Enable CORS for all routes (allow frontend to access API)
CORS(app)

# Initialize database on startup
database.init_database()


@app.route('/')
@app.route('/<path:path>')
def serve_spa(path=''):
    """
    Serve the Single Page Application.
    All routes serve index.html, letting the JS router handle navigation.
    """
    # Serve index.html for all routes (SPA router handles the rest)
    if path and os.path.exists(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)
    else:
        return send_from_directory(frontend_dir, 'index.html')


# ============================================
# Authentication Routes
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Authenticate a user and return JWT token.

    Expected JSON:
    {
        "username": "string",
        "password": "string"
    }

    Returns:
        JSON with token and user info if successful
    """
    try:
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Username and password required'
            }), 400

        username = data['username']
        password = data['password']

        # Get user from database
        user = database.get_user_by_username(username)

        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401

        # Check if user is active
        if not user.get('is_active'):
            return jsonify({
                'success': False,
                'error': 'User account is disabled'
            }), 401

        # Verify password
        if not database.verify_password(password, user['password_hash']):
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401

        # Generate JWT token
        token = auth.generate_jwt(user['id'], user['username'], user['role'])

        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Login failed: {str(e)}'
        }), 500


@app.route('/api/auth/verify', methods=['GET'])
@auth.jwt_required
def verify_token():
    """
    GET /api/auth/verify
    Verify if the current JWT token is valid.

    Requires: Authorization header with Bearer token

    Returns:
        JSON with user info if token is valid
    """
    current_user = auth.get_jwt_identity()

    return jsonify({
        'success': True,
        'user': current_user
    }), 200


@app.route('/api/auth/me', methods=['GET'])
@auth.jwt_required
def get_current_user():
    """
    GET /api/auth/me
    Get current user information from JWT.

    Requires: Authorization header with Bearer token

    Returns:
        JSON with full user info
    """
    current_user = auth.get_jwt_identity()
    user = database.get_user_by_id(current_user['user_id'])

    if not user:
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404

    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'is_active': user['is_active'],
            'created_at': user['created_at']
        }
    }), 200


# ============================================
# User Management Routes (Admin Only)
# ============================================

@app.route('/api/users', methods=['GET'])
@auth.admin_required
def get_users():
    """
    GET /api/users
    Get all users (admin only).

    Requires: Admin JWT token

    Returns:
        JSON with list of all users
    """
    try:
        users = database.get_all_users()

        return jsonify({
            'success': True,
            'users': users
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve users: {str(e)}'
        }), 500


@app.route('/api/users', methods=['POST'])
@auth.admin_required
def create_user():
    """
    POST /api/users
    Create a new user (admin only).

    Requires: Admin JWT token

    Expected JSON:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "role": "user" or "admin" (optional, default: "user")
    }

    Returns:
        JSON with created user info
    """
    try:
        data = request.get_json()

        user_id = database.create_user(data)
        user = database.get_user_by_id(user_id)

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create user: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@auth.admin_required
def update_user(user_id):
    """
    PUT /api/users/<id>
    Update user information (admin only).

    Requires: Admin JWT token

    Args:
        user_id: ID of the user to update

    Expected JSON:
    {
        "email": "string" (optional),
        "role": "string" (optional),
        "is_active": boolean (optional),
        "password": "string" (optional)
    }

    Returns:
        JSON with success status
    """
    try:
        data = request.get_json()

        success = database.update_user(user_id, data)

        if not success:
            return jsonify({
                'success': False,
                'error': f'User with ID {user_id} not found'
            }), 404

        user = database.get_user_by_id(user_id)

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'is_active': user['is_active']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update user: {str(e)}'
        }), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@auth.admin_required
def delete_user(user_id):
    """
    DELETE /api/users/<id>
    Delete a user (admin only).

    Requires: Admin JWT token

    Args:
        user_id: ID of the user to delete

    Returns:
        JSON with success status
    """
    try:
        # Prevent deleting yourself
        current_user = auth.get_jwt_identity()
        if current_user['user_id'] == user_id:
            return jsonify({
                'success': False,
                'error': 'Cannot delete your own account'
            }), 400

        success = database.delete_user(user_id)

        if not success:
            return jsonify({
                'success': False,
                'error': f'User with ID {user_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete user: {str(e)}'
        }), 500


# ============================================
# Posts Routes (Public)
# ============================================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    GET /api/posts
    Retrieve all posts from the database.

    Returns:
        JSON response with array of posts
    """
    try:
        posts = database.get_all_posts()
        return jsonify({
            'success': True,
            'count': len(posts),
            'data': posts
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve posts: {str(e)}'
        }), 500


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    GET /api/posts/<id>
    Retrieve a specific post by ID.

    Args:
        post_id: The ID of the post to retrieve

    Returns:
        JSON response with post data or 404 error
    """
    try:
        post = database.get_post_by_id(post_id)

        if post is None:
            return jsonify({
                'success': False,
                'error': f'Post with ID {post_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'data': post
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve post: {str(e)}'
        }), 500


@app.route('/api/posts', methods=['POST'])
def create_post():
    """
    POST /api/posts
    Create a new post.

    Expected JSON body:
    {
        "title": "string (required)",
        "summary": "string (required)",
        "source_url": "string (required)",
        "release_date": "string (required)",
        "image_url": "string (optional)",
        "provider": "string (optional)",
        "type": "string (optional)"
    }

    Returns:
        JSON response with created post ID
    """
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400

        data = request.get_json()

        # Validate post data
        is_valid, error_message = Post.validate_post_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400

        # Create post in database
        post_id = database.create_post(data)

        # Retrieve the created post
        created_post = database.get_post_by_id(post_id)

        return jsonify({
            'success': True,
            'message': 'Post created successfully',
            'data': created_post
        }), 201

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create post: {str(e)}'
        }), 500


# ============================================
# Pending Posts Endpoints
# ============================================

@app.route('/api/pending-posts', methods=['GET'])
@auth.admin_required
def get_pending_posts():
    """
    GET /api/pending-posts
    Retrieve all pending posts from the database.

    Query Parameters:
        status (optional): Filter by status ('pending', 'approved', 'rejected')

    Returns:
        JSON response with array of pending posts
    """
    try:
        status = request.args.get('status')
        pending_posts = database.get_all_pending_posts(status=status)

        return jsonify({
            'success': True,
            'count': len(pending_posts),
            'data': pending_posts
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve pending posts: {str(e)}'
        }), 500


@app.route('/api/pending-posts/<int:post_id>', methods=['GET'])
@auth.admin_required
def get_pending_post(post_id):
    """
    GET /api/pending-posts/<id>
    Retrieve a specific pending post by ID.

    Args:
        post_id: The ID of the pending post to retrieve

    Returns:
        JSON response with pending post data or 404 error
    """
    try:
        pending_post = database.get_pending_post_by_id(post_id)

        if pending_post is None:
            return jsonify({
                'success': False,
                'error': f'Pending post with ID {post_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'data': pending_post
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve pending post: {str(e)}'
        }), 500


@app.route('/api/pending-posts', methods=['POST'])
def create_pending_post():
    """
    POST /api/pending-posts
    Create a new pending post (used by AI agent).

    Expected JSON body:
    {
        "title": "string (required)",
        "summary": "string (required)",
        "source_url": "string (required)",
        "release_date": "string (required)",
        "image_url": "string (optional)",
        "provider": "string (optional)",
        "type": "string (optional)",
        "status": "string (optional, default: 'pending')"
    }

    Returns:
        JSON response with created pending post ID
    """
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400

        data = request.get_json()

        # Validate post data
        is_valid, error_message = Post.validate_post_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400

        # Create pending post in database
        post_id = database.create_pending_post(data)

        # Retrieve the created pending post
        created_post = database.get_pending_post_by_id(post_id)

        return jsonify({
            'success': True,
            'message': 'Pending post created successfully',
            'data': created_post
        }), 201

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': str(ve)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create pending post: {str(e)}'
        }), 500


@app.route('/api/pending-posts/<int:post_id>', methods=['PUT'])
@auth.admin_required
def update_pending_post(post_id):
    """
    PUT /api/pending-posts/<id>
    Update a pending post's information (e.g., title, summary).

    Args:
        post_id: The ID of the pending post to update

    Expected JSON body (all fields optional):
    {
        "title": "string",
        "summary": "string",
        "image_url": "string",
        "provider": "string",
        "type": "string"
    }

    Returns:
        JSON response with success status
    """
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400

        data = request.get_json()

        # Update the pending post
        success = database.update_pending_post(post_id, data)

        if not success:
            return jsonify({
                'success': False,
                'error': f'Pending post with ID {post_id} not found or no fields to update'
            }), 404

        # Retrieve the updated pending post
        updated_post = database.get_pending_post_by_id(post_id)

        return jsonify({
            'success': True,
            'message': 'Pending post updated successfully',
            'data': updated_post
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update pending post: {str(e)}'
        }), 500


@app.route('/api/pending-posts/<int:post_id>/approve', methods=['PUT'])
@auth.admin_required
def approve_pending_post(post_id):
    """
    PUT /api/pending-posts/<id>/approve
    Approve a pending post and move it to published posts.

    Args:
        post_id: The ID of the pending post to approve

    Returns:
        JSON response with the new published post ID
    """
    try:
        # Approve the pending post (creates new post in posts table)
        new_post_id = database.approve_pending_post(post_id)

        if new_post_id is None:
            return jsonify({
                'success': False,
                'error': f'Pending post with ID {post_id} not found or failed to approve'
            }), 404

        # Retrieve the newly published post
        published_post = database.get_post_by_id(new_post_id)

        return jsonify({
            'success': True,
            'message': 'Post approved and published successfully',
            'data': {
                'pending_post_id': post_id,
                'published_post_id': new_post_id,
                'published_post': published_post
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to approve pending post: {str(e)}'
        }), 500


@app.route('/api/pending-posts/<int:post_id>/reject', methods=['PUT'])
@auth.admin_required
def reject_pending_post(post_id):
    """
    PUT /api/pending-posts/<id>/reject
    Reject a pending post (sets status to 'rejected').

    Args:
        post_id: The ID of the pending post to reject

    Returns:
        JSON response with success status
    """
    try:
        success = database.reject_pending_post(post_id)

        if not success:
            return jsonify({
                'success': False,
                'error': f'Pending post with ID {post_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Pending post rejected successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to reject pending post: {str(e)}'
        }), 500


@app.route('/api/pending-posts/<int:post_id>', methods=['DELETE'])
@auth.admin_required
def delete_pending_post(post_id):
    """
    DELETE /api/pending-posts/<id>
    Delete a pending post from the database.

    Args:
        post_id: The ID of the pending post to delete

    Returns:
        JSON response with success status
    """
    try:
        success = database.delete_pending_post(post_id)

        if not success:
            return jsonify({
                'success': False,
                'error': f'Pending post with ID {post_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Pending post deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete pending post: {str(e)}'
        }), 500


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors
    For API routes: return JSON error
    For SPA routes: serve index.html (let the router handle it)
    """
    # If request is for API endpoint, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404

    # Otherwise, serve the SPA (index.html)
    # This allows client-side routing to work on refresh
    return send_from_directory(frontend_dir, 'index.html')


@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 errors
    """
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    print("Starting Posts API Server...")
    print("Server running on http://localhost:5000")
    print("API endpoints available at http://localhost:5000/api/posts")
    app.run(debug=True, host='0.0.0.0', port=5000)
