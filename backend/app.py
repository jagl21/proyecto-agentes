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
        'version': '1.0',
        'endpoints': {
            'GET /api/posts': 'Get all posts',
            'GET /api/posts/<id>': 'Get a specific post by ID',
            'POST /api/posts': 'Create a new post'
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
