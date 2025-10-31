# CMS Server API Documentation

Complete API documentation for testing endpoints with Postman or any HTTP client.

## Base URL

**Production:** `https://teamwhiteprojectav-production.up.railway.app`

**Local Development:** `http://localhost:8000`

---

## Authentication

All endpoints except public read operations (list/retrieve) require authentication via token.

### Register User

Create a new user account.

**Endpoint:** `POST /cms/api/auth/register/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "test_user",
    "password": "test123",
    "password_confirm": "test123"
}
```

**Response (201 Created):**
```json
{
    "token": "abc123...",
    "user": {
        "id": 1,
        "username": "test_user"
    },
    "message": "User registered successfully"
}
```

**Postman Example:**
- Method: `POST`
- URL: `{{base_url}}/cms/api/auth/register/`
- Body: raw JSON (as shown above)

---

### Login

Authenticate an existing user and get an access token.

**Endpoint:** `POST /cms/api/auth/login/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "test_user",
    "password": "test123"
}
```

**Response (200 OK):**
```json
{
    "token": "abc123...",
    "user": {
        "id": 1,
        "username": "test_user"
    },
    "message": "Logged in successfully"
}
```

**Postman Example:**
- Method: `POST`
- URL: `{{base_url}}/cms/api/auth/login/`
- Body: raw JSON (as shown above)

**⚠️ Important:** Save the `token` from the response for authenticated requests!

---

### Get Current User Info

Get information about the currently authenticated user.

**Endpoint:** `GET /cms/api/auth/me/`

**Headers:**
```
Authorization: Token abc123...
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "test_user"
}
```

**Postman Example:**
- Method: `GET`
- URL: `{{base_url}}/cms/api/auth/me/`
- Headers: Add `Authorization` with value `Token <your_token>`

---

### Logout

Logout the current user and invalidate their token.

**Endpoint:** `POST /cms/api/auth/logout/`

**Headers:**
```
Authorization: Token abc123...
```

**Response (200 OK):**
```json
{
    "message": "Logged out successfully"
}
```

**Postman Example:**
- Method: `POST`
- URL: `{{base_url}}/cms/api/auth/logout/`
- Headers: Add `Authorization` with value `Token <your_token>`

---

## Blogs

### List All Blogs

Get a list of all blogs (public, no authentication required).

**Endpoint:** `GET /cms/api/blogs/`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "My Blog",
        "description": "Blog description",
        "user": 1,
        "created_at": "2025-10-31T10:00:00Z",
        "updated_at": "2025-10-31T10:00:00Z"
    }
]
```

**Postman Example:**
- Method: `GET`
- URL: `{{base_url}}/cms/api/blogs/`
- No authentication required

---

### Get Single Blog

Get details of a specific blog by ID (public, no authentication required).

**Endpoint:** `GET /cms/api/blogs/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "My Blog",
    "description": "Blog description",
    "user": 1,
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:00:00Z"
}
```

**Postman Example:**
- Method: `GET`
- URL: `{{base_url}}/cms/api/blogs/1/`
- No authentication required

---

### Create Blog

Create a new blog (authentication required).

**Endpoint:** `POST /cms/api/blogs/`

**Headers:**
```
Content-Type: application/json
Authorization: Token abc123...
```

**Request Body:**
```json
{
    "title": "My New Blog",
    "description": "This is my new blog description"
}
```

**Response (201 Created):**
```json
{
    "id": 2,
    "title": "My New Blog",
    "description": "This is my new blog description",
    "user": 1,
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:00:00Z"
}
```

**Postman Example:**
- Method: `POST`
- URL: `{{base_url}}/cms/api/blogs/`
- Headers: Add `Authorization: Token <your_token>`
- Body: raw JSON (as shown above)

---

### Update Blog

Update an existing blog (only owner can update).

**Endpoint:** `PUT /cms/api/blogs/{id}/` or `PATCH /cms/api/blogs/{id}/`

**Headers:**
```
Content-Type: application/json
Authorization: Token abc123...
```

**Request Body (PUT - full update):**
```json
{
    "title": "Updated Blog Title",
    "description": "Updated description"
}
```

**Request Body (PATCH - partial update):**
```json
{
    "title": "Only title updated"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Updated Blog Title",
    "description": "Updated description",
    "user": 1,
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:05:00Z"
}
```

**Postman Example:**
- Method: `PUT` or `PATCH`
- URL: `{{base_url}}/cms/api/blogs/1/`
- Headers: Add `Authorization: Token <your_token>`
- Body: raw JSON (as shown above)

---

### Delete Blog

Delete a blog (only owner can delete).

**Endpoint:** `DELETE /cms/api/blogs/{id}/`

**Headers:**
```
Authorization: Token abc123...
```

**Response (204 No Content):**

**Postman Example:**
- Method: `DELETE`
- URL: `{{base_url}}/cms/api/blogs/1/`
- Headers: Add `Authorization: Token <your_token>`

---

## Posts

### List All Posts

Get a list of all posts (public, no authentication required).

**Endpoint:** `GET /cms/api/posts/`

**Query Parameters:**
- `blog_id` (optional): Filter posts by blog ID
  - Example: `GET /cms/api/posts/?blog_id=1`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "My First Post",
        "description": "Post description",
        "content": "Post content here...",
        "blog": 1,
        "tags": [1, 2],
        "created_at": "2025-10-31T10:00:00Z",
        "updated_at": "2025-10-31T10:00:00Z"
    }
]
```

**Postman Example:**
- Method: `GET`
- URL: `{{base_url}}/cms/api/posts/`
- Or with filter: `{{base_url}}/cms/api/posts/?blog_id=1`
- No authentication required

---

### Get Single Post

Get details of a specific post by ID (public, no authentication required).

**Endpoint:** `GET /cms/api/posts/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "My First Post",
    "description": "Post description",
    "content": "Post content here...",
    "blog": 1,
    "tags": [1, 2],
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:00:00Z"
}
```

**Postman Example:**
- Method: `GET`
- URL: `{{base_url}}/cms/api/posts/1/`
- No authentication required

---

### Create Post

Create a new post (authentication required).

**Endpoint:** `POST /cms/api/posts/`

**Headers:**
```
Content-Type: application/json
Authorization: Token abc123...
```

**Request Body:**
```json
{
    "title": "New Post Title",
    "description": "Post description",
    "content": "Post content here...",
    "blog": 1,
    "tags": [1, 2]
}
```

**Response (201 Created):**
```json
{
    "id": 2,
    "title": "New Post Title",
    "description": "Post description",
    "content": "Post content here...",
    "blog": 1,
    "tags": [1, 2],
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:00:00Z"
}
```

**Postman Example:**
- Method: `POST`
- URL: `{{base_url}}/cms/api/posts/`
- Headers: Add `Authorization: Token <your_token>`
- Body: raw JSON (as shown above)

---

### Update Post

Update an existing post (only owner can update).

**Endpoint:** `PUT /cms/api/posts/{id}/` or `PATCH /cms/api/posts/{id}/`

**Headers:**
```
Content-Type: application/json
Authorization: Token abc123...
```

**Request Body:**
```json
{
    "title": "Updated Post Title",
    "description": "Updated description",
    "content": "Updated content...",
    "blog": 1,
    "tags": [1, 3]
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Updated Post Title",
    "description": "Updated description",
    "content": "Updated content...",
    "blog": 1,
    "tags": [1, 3],
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:05:00Z"
}
```

**Postman Example:**
- Method: `PUT` or `PATCH`
- URL: `{{base_url}}/cms/api/posts/1/`
- Headers: Add `Authorization: Token <your_token>`
- Body: raw JSON (as shown above)

---

### Delete Post

Delete a post (only owner can delete).

**Endpoint:** `DELETE /cms/api/posts/{id}/`

**Headers:**
```
Authorization: Token abc123...
```

**Response (204 No Content):**

**Postman Example:**
- Method: `DELETE`
- URL: `{{base_url}}/cms/api/posts/1/`
- Headers: Add `Authorization: Token <your_token>`

---

## Tags

### List All Tags

Get a list of all tags (public, no authentication required).

**Endpoint:** `GET /cms/api/tags/`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Python",
        "created_at": "2025-10-31T10:00:00Z",
        "updated_at": "2025-10-31T10:00:00Z"
    }
]
```

**Postman Example:**
- Method: `GET`
- URL: `{{base_url}}/cms/api/tags/`
- No authentication required

---

### Get Single Tag

Get details of a specific tag by ID (public, no authentication required).

**Endpoint:** `GET /cms/api/tags/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Python",
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:00:00Z"
}
```

**Postman Example:**
- Method: `GET`
- URL: `{{base_url}}/cms/api/tags/1/`
- No authentication required

---

### Create Tag

Create a new tag (authentication required).

**Endpoint:** `POST /cms/api/tags/`

**Headers:**
```
Content-Type: application/json
Authorization: Token abc123...
```

**Request Body:**
```json
{
    "name": "Django"
}
```

**Response (201 Created):**
```json
{
    "id": 2,
    "name": "Django",
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:00:00Z"
}
```

**Postman Example:**
- Method: `POST`
- URL: `{{base_url}}/cms/api/tags/`
- Headers: Add `Authorization: Token <your_token>`
- Body: raw JSON (as shown above)

---

### Update Tag

Update an existing tag (authentication required).

**Endpoint:** `PUT /cms/api/tags/{id}/` or `PATCH /cms/api/tags/{id}/`

**Headers:**
```
Content-Type: application/json
Authorization: Token abc123...
```

**Request Body:**
```json
{
    "name": "Updated Tag Name"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Updated Tag Name",
    "created_at": "2025-10-31T10:00:00Z",
    "updated_at": "2025-10-31T10:05:00Z"
}
```

**Postman Example:**
- Method: `PUT` or `PATCH`
- URL: `{{base_url}}/cms/api/tags/1/`
- Headers: Add `Authorization: Token <your_token>`
- Body: raw JSON (as shown above)

---

### Delete Tag

Delete a tag (authentication required).

**Endpoint:** `DELETE /cms/api/tags/{id}/`

**Headers:**
```
Authorization: Token abc123...
```

**Response (204 No Content):**

**Postman Example:**
- Method: `DELETE`
- URL: `{{base_url}}/cms/api/tags/1/`
- Headers: Add `Authorization: Token <your_token>`

---

## Admin & Documentation

### Django Admin Panel

Access the Django admin interface.

**Endpoint:** `GET /admin/`

**URL:** `https://teamwhiteprojectav-production.up.railway.app/admin/`

**Note:** Requires admin user credentials (superuser).

---

### API Documentation (Swagger UI)

Interactive API documentation.

**Endpoint:** `GET /api/docs/`

**URL:** `https://teamwhiteprojectav-production.up.railway.app/api/docs/`

**Note:** No authentication required for viewing documentation.

---

### API Documentation (ReDoc)

Alternative API documentation view.

**Endpoint:** `GET /api/redoc/`

**URL:** `https://teamwhiteprojectav-production.up.railway.app/api/redoc/`

**Note:** No authentication required for viewing documentation.

---

### OpenAPI Schema

Get the OpenAPI schema JSON.

**Endpoint:** `GET /api/schema/`

**URL:** `https://teamwhiteprojectav-production.up.railway.app/api/schema/`

**Response:** OpenAPI JSON schema

**Note:** No authentication required.

---

## Postman Setup Tips

### 1. Environment Variables

Create a Postman environment with:
- `base_url`: `https://teamwhiteprojectav-production.up.railway.app`
- `token`: (will be set after login/register)

### 2. Authentication Setup

1. Register or Login to get a token
2. Copy the token from the response
3. Set it as an environment variable: `token`
4. Use it in the Authorization header: `Token {{token}}`

### 3. Collection Organization

Organize your Postman collection:
```
CMS API
├── Authentication
│   ├── Register
│   ├── Login
│   ├── Get Current User
│   └── Logout
├── Blogs
│   ├── List Blogs
│   ├── Get Blog
│   ├── Create Blog
│   ├── Update Blog
│   └── Delete Blog
├── Posts
│   ├── List Posts
│   ├── Get Post
│   ├── Create Post
│   ├── Update Post
│   └── Delete Post
└── Tags
    ├── List Tags
    ├── Get Tag
    ├── Create Tag
    ├── Update Tag
    └── Delete Tag
```

### 4. Pre-request Script (Auto-set Token)

Add this to your collection's pre-request script:
```javascript
// Automatically add token to requests that need authentication
if (pm.environment.get("token")) {
    pm.request.headers.add({
        key: "Authorization",
        value: "Token " + pm.environment.get("token")
    });
}
```

---

## Error Responses

### 400 Bad Request
```json
{
    "error": "Bad Request",
    "message": "Validation error message",
    "code": "validation_error"
}
```

### 401 Unauthorized
```json
{
    "error": "Unauthorized",
    "message": "Authentication required",
    "code": "authentication_required"
}
```

### 403 Forbidden
```json
{
    "error": "Forbidden",
    "message": "You do not have permission to perform this action",
    "code": "permission_denied"
}
```

### 404 Not Found
```json
{
    "error": "Not Found",
    "message": "Resource not found",
    "code": "not_found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal Server Error",
    "message": "An unexpected error occurred",
    "code": "internal_server_error"
}
```

---

## Quick Start Workflow

1. **Register a new user:**
   ```
   POST /cms/api/auth/register/
   Body: {"username": "test", "password": "test123", "password_confirm": "test123"}
   ```

2. **Save the token** from the response

3. **Create a blog:**
   ```
   POST /cms/api/blogs/
   Headers: Authorization: Token <your_token>
   Body: {"title": "My Blog", "description": "Description"}
   ```

4. **Create a tag:**
   ```
   POST /cms/api/tags/
   Headers: Authorization: Token <your_token>
   Body: {"name": "Python"}
   ```

5. **Create a post:**
   ```
   POST /cms/api/posts/
   Headers: Authorization: Token <your_token>
   Body: {"title": "My Post", "description": "Desc", "content": "Content", "blog": 1, "tags": [1]}
   ```

6. **List all posts:**
   ```
   GET /cms/api/posts/
   (No authentication required)
   ```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Date format: `YYYY-MM-DDTHH:MM:SSZ`
- Authentication tokens do not expire automatically (logout to invalidate)
- Only blog/post owners can update or delete their resources
- All list and retrieve endpoints are public (no authentication required)
- Create, update, and delete operations require authentication

---

## Support

For interactive API documentation, visit:
- **Swagger UI:** `/api/docs/`
- **ReDoc:** `/api/redoc/`

