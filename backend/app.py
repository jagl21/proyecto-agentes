"""
Flask API Server for Posts Application
Provides REST API endpoints for managing news posts.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import database
from models import Post

app = Flask(__name__)

# Enable CORS for all routes (allow frontend to access API)
CORS(app)

# Initialize database on startup
database.init_database()


@app.route('/')
def home():
    """
    Home route - API information
    """
    return jsonify({
        'message': 'Posts API Server',
        'version': '2.0',
        'endpoints': {
            'GET /api/posts': 'Get all published posts',
            'GET /api/posts/<id>': 'Get a specific post by ID',
            'POST /api/posts': 'Create a new published post',
            'GET /api/pending-posts': 'Get all pending posts',
            'GET /api/pending-posts/<id>': 'Get a specific pending post by ID',
            'POST /api/pending-posts': 'Create a new pending post',
            'PUT /api/pending-posts/<id>': 'Update a pending post',
            'PUT /api/pending-posts/<id>/approve': 'Approve and publish a pending post',
            'PUT /api/pending-posts/<id>/reject': 'Reject a pending post',
            'DELETE /api/pending-posts/<id>': 'Delete a pending post'
        }
    })


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
    """
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


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
