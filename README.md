# BlogV2 - AI-Powered Blog Generation API

## Overview

This API provides AI-powered blog post generation with SEO optimization. It allows you to generate markdown-formatted blog posts based on a given topic, with optional features like image generation and keyword research.

## API Endpoints

### 1. Generate Blog Post

**Endpoint:** `POST /api/v1/generate`

Generate a new blog post based on the provided topic.

#### Request Body

```json
{
  "topic": "string (required) - The main topic of the blog post",
  "author": "string (optional, default: 'Admin') - Author name",
  "generate_images": "boolean (optional, default: false) - Whether to generate images",
  "find_keywords": "boolean (optional, default: false) - Whether to find low competition keywords",
  "return_markdown": "boolean (optional, default: true) - Whether to return markdown content directly"
}
```

#### Success Response (JSON - when return_markdown=false)

```json
{
  "status": "success",
  "message": "Blog post generated successfully",
  "data": {
    "title": "string - Generated blog post title",
    "slug": "string - URL-friendly slug",
    "markdown_path": "string - Path to saved markdown file",
    "markdown_content": "string - Full markdown content",
    "metadata": {
      "author": "string - Author name",
      "generated_at": "string - ISO timestamp",
      "word_count": "number - Word count of the generated content"
    }
  }
}
```

#### Success Response (Markdown - when return_markdown=true)
- **Content-Type:** `text/markdown`
- **Headers:**
  - `Content-Disposition`: Attachment filename
  - `X-File-Name`: Generated filename
  - `X-Title`: Blog post title
  - `X-Generated-At`: ISO timestamp

#### Error Response

```json
{
  "detail": "string - Error message"
}
```

### 2. List Generated Blog Posts

**Endpoint:** `GET /api/v1/list`

List all generated blog posts with their metadata.

#### Success Response

```json
{
  "status": "success",
  "data": [
    {
      "filename": "string - Name of the markdown file",
      "title": "string - Blog post title",
      "path": "string - Full path to the markdown file",
      "created_at": "string - ISO timestamp of file creation",
      "size_kb": "number - File size in KB"
    }
  ]
}
```

### 3. API Root

**Endpoint:** `GET /`

Basic API information and available endpoints.

#### Success Response

```json
{
  "message": "Welcome to the Blog Generation API",
  "endpoints": {
    "generate_blog": {
      "method": "POST",
      "url": "/api/v1/generate",
      "description": "Generate a new blog post"
    },
    "list_blogs": {
      "method": "GET",
      "url": "/api/v1/list",
      "description": "List all generated blog posts"
    }
  },
  "docs": "/docs"
}
```

## API Documentation

For interactive API documentation and testing, visit:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (copy `.env.example` to `.env` and update values)
4. Run the API server:
   ```bash
   python blog_api.py
   ```

The API will be available at `http://localhost:8000`

## Frontend

A React-based frontend is available in the `blog-frontend` directory. See the frontend README for setup instructions.

## License

[Your License Here]
