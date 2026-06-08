# Campus Connect — API Documentation
**Version:** 1.0  
**Base URL:** `https://api.atalha.com`  
**Protocol:** HTTPS only  
**Format:** JSON (except file uploads which use multipart/form-data)

---

## Authentication

Campus Connect uses **JWT (JSON Web Token)** authentication.

After login or register, you receive two tokens:

| Token | Lifetime | Purpose |
|---|---|---|
| `access` | 60 minutes | Send with every protected request |
| `refresh` | 30 days | Use to get a new access token when the old one expires |

### How to send the access token

Add this header to every protected request:

```
Authorization: Bearer <your_access_token>
```

### How to refresh an expired access token

```
POST /api/auth/token/refresh/
Body: { "refresh": "<your_refresh_token>" }
```

---

## Response Format

### Success responses
All successful responses return the relevant data directly.

### Error responses
All error responses follow this structure:

```json
{
    "field_name": ["Error message here."]
}
```

Or for non-field errors:

```json
{
    "error": "Error message here."
}
```

### HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created successfully |
| 204 | Deleted successfully (no response body) |
| 400 | Bad request / validation error |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (account disabled) |
| 404 | Resource not found |
| 500 | Server error |

---

## Endpoints

---

## 1. Auth

### 1.1 Register
Create a new user account. Returns tokens immediately — no separate login needed.

```
POST /api/auth/register/
Auth: Not required
```

**Request body:**
```json
{
    "email": "student@example.com",
    "username": "talha",
    "full_name": "Talha Ahmed",
    "password": "securepass123"
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| email | string | yes | valid email format, unique |
| username | string | yes | max 30 chars, unique |
| full_name | string | yes | max 100 chars |
| password | string | yes | min 8 characters |

**Success response — 201:**
```json
{
    "user": {
        "id": 1,
        "email": "student@example.com",
        "username": "talha",
        "full_name": "Talha Ahmed",
        "bio": "",
        "created_at": "2026-06-08T20:00:00Z"
    },
    "tokens": {
        "access": "eyJ...",
        "refresh": "eyJ..."
    }
}
```

**Error responses:**
```json
{ "email": ["This email is already registered."] }
{ "username": ["This username is already taken."] }
{ "password": ["Ensure this field has at least 8 characters."] }
```

---

### 1.2 Login
Authenticate an existing user.

```
POST /api/auth/login/
Auth: Not required
```

**Request body:**
```json
{
    "email": "student@example.com",
    "password": "securepass123"
}
```

**Success response — 200:**
```json
{
    "user": {
        "id": 1,
        "email": "student@example.com",
        "username": "talha",
        "full_name": "Talha Ahmed",
        "bio": "",
        "created_at": "2026-06-08T20:00:00Z"
    },
    "tokens": {
        "access": "eyJ...",
        "refresh": "eyJ..."
    }
}
```

**Error responses:**
```json
{ "error": "Email and password are required." }
{ "error": "Invalid email or password." }
{ "error": "This account has been disabled." }
```

---

### 1.3 Refresh Token
Get a new access token using the refresh token.

```
POST /api/auth/token/refresh/
Auth: Not required
```

**Request body:**
```json
{
    "refresh": "eyJ..."
}
```

**Success response — 200:**
```json
{
    "access": "eyJ..."
}
```

---

### 1.4 Get Auth Profile
Get the currently logged in user's basic info.

```
GET /api/auth/profile/
Auth: Required
```

**Success response — 200:**
```json
{
    "id": 1,
    "email": "student@example.com",
    "username": "talha",
    "full_name": "Talha Ahmed",
    "bio": "",
    "created_at": "2026-06-08T20:00:00Z"
}
```

---

### 1.5 List All Users
Returns a paginated list of all active users excluding the currently logged in user.

```
GET /api/auth/users/
Auth: Required
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| page | integer | page number (default: 1) |

**Success response — 200:**
```json
{
    "count": 25,
    "next": "https://api.atalha.com/api/auth/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 2,
            "email": "student2@example.com",
            "username": "student2",
            "full_name": "Second Student",
            "bio": "",
            "created_at": "2026-06-08T20:00:00Z"
        }
    ]
}
```

---

### 1.6 Get Single User
Get basic info for a specific user by their ID.

```
GET /api/auth/users/{id}/
Auth: Required
```

**URL parameters:**

| Parameter | Type | Description |
|---|---|---|
| id | integer | the user's ID |

**Success response — 200:**
```json
{
    "id": 2,
    "email": "student2@example.com",
    "username": "student2",
    "full_name": "Second Student",
    "bio": "",
    "created_at": "2026-06-08T20:00:00Z"
}
```

---

## 2. Profiles

### 2.1 Get My Profile
Returns the full private profile of the logged in user including private fields (dob, gender).

```
GET /api/profiles/me/
Auth: Required
```

**Success response — 200:**
```json
{
    "user": {
        "id": 1,
        "username": "talha",
        "full_name": "Talha Ahmed"
    },
    "bio": "Computer Science student",
    "about": "I love building apps.",
    "dob": "2000-01-15",
    "gender": "Male",
    "user_type": "STUDENT",
    "profile_photo": "https://res.cloudinary.com/...",
    "updated_at": "2026-06-08T20:00:00Z",
    "looking_for": [],
    "links": [],
    "education": [],
    "experience": [],
    "projects": [],
    "skills": []
}
```

---

### 2.2 Edit My Profile
Update one or more profile fields. Send only the fields you want to change.

```
PATCH /api/profiles/me/
Auth: Required
Content-Type: multipart/form-data (when uploading photo)
Content-Type: application/json (when updating text fields only)
```

**Fields (all optional):**

| Field | Type | Description |
|---|---|---|
| bio | string | short tagline, max 160 chars |
| about | string | longer description |
| dob | date | format: YYYY-MM-DD (private) |
| gender | string | (private) |
| user_type | string | STUDENT or CR |
| profile_photo | file | image file (jpg, jpeg, png, webp) |

**Example — text only (JSON):**
```json
{
    "bio": "Computer Science student",
    "about": "I love building apps."
}
```

**Example — with photo (form-data):**
```
profile_photo  →  [image file]
bio            →  Computer Science student
```

**Success response — 200:** returns the full updated profile (same as Get My Profile)

---

### 2.3 Get Public Profile
Returns another user's public profile. Private fields (dob, gender) are never included.

```
GET /api/profiles/{user_id}/
Auth: Required
```

**URL parameters:**

| Parameter | Type | Description |
|---|---|---|
| user_id | integer | the target user's ID |

**Success response — 200:**
```json
{
    "user": {
        "id": 2,
        "username": "student2",
        "full_name": "Second Student"
    },
    "bio": "Physics student",
    "about": "Interested in research.",
    "user_type": "STUDENT",
    "profile_photo": "https://res.cloudinary.com/...",
    "looking_for": [],
    "links": [],
    "education": [],
    "experience": [],
    "projects": [],
    "skills": []
}
```

---

## 3. Looking For

### 3.1 Add Looking For Item
Add a new "looking for" entry to your profile (e.g. "Study partner", "Team member").

```
POST /api/profiles/me/looking-for/
Auth: Required
Content-Type: application/json
```

**Request body:**
```json
{
    "value": "Study partner"
}
```

**Success response — 201:**
```json
{
    "id": 1,
    "value": "Study partner"
}
```

---

### 3.2 Delete Looking For Item

```
DELETE /api/profiles/me/looking-for/{id}/
Auth: Required
```

**Success response — 204:** no body

---

## 4. Links

### 4.1 Add Link

```
POST /api/profiles/me/links/
Auth: Required
Content-Type: application/json
```

**Request body:**
```json
{
    "link_name": "GitHub",
    "icon": "github",
    "url": "https://github.com/yourusername"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| link_name | string | yes | display name e.g. "GitHub" |
| icon | string | no | icon identifier e.g. "github", "linkedin" |
| url | string | yes | full URL |

**Success response — 201:**
```json
{
    "id": 1,
    "link_name": "GitHub",
    "icon": "github",
    "url": "https://github.com/yourusername"
}
```

---

### 4.2 Delete Link

```
DELETE /api/profiles/me/links/{id}/
Auth: Required
```

**Success response — 204:** no body

---

## 5. Education

### 5.1 Add Education

```
POST /api/profiles/me/education/
Auth: Required
Content-Type: multipart/form-data
```

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| institution_name | string | yes | name of institution |
| degree | string | yes | degree or certification |
| start_year | integer | yes | e.g. 2022 |
| end_year | integer | no | leave empty if currently studying |
| image | file | no | institution logo (jpg, jpeg, png, webp) |

**Success response — 201:**
```json
{
    "id": 1,
    "institution_name": "University of Dhaka",
    "degree": "BSc Computer Science",
    "start_year": 2022,
    "end_year": null,
    "image_url": "https://res.cloudinary.com/..."
}
```

---

### 5.2 Edit Education

```
PATCH /api/profiles/me/education/{id}/
Auth: Required
Content-Type: application/json
```

Send only the fields you want to update.

**Success response — 200:** returns the updated education object

---

### 5.3 Delete Education

```
DELETE /api/profiles/me/education/{id}/
Auth: Required
```

**Success response — 204:** no body

---

## 6. Experience

### 6.1 Add Experience

```
POST /api/profiles/me/experience/
Auth: Required
Content-Type: application/json
```

**Request body:**
```json
{
    "title": "Android Developer Intern",
    "organization": "Tech Company",
    "description": "Built mobile features using Java.",
    "start_date": "2024-01-01",
    "end_date": null
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| title | string | yes | role or position name |
| organization | string | yes | company, club, or institution |
| description | string | no | details about the role |
| start_date | date | yes | format: YYYY-MM-DD |
| end_date | date | no | leave null if current role |

**Success response — 201:** returns the created experience object

---

### 6.2 Edit Experience

```
PATCH /api/profiles/me/experience/{id}/
Auth: Required
Content-Type: application/json
```

**Success response — 200:** returns the updated experience object

---

### 6.3 Delete Experience

```
DELETE /api/profiles/me/experience/{id}/
Auth: Required
```

**Success response — 204:** no body

---

## 7. Projects

### 7.1 Add Project

```
POST /api/profiles/me/projects/
Auth: Required
Content-Type: application/json
```

**Request body:**
```json
{
    "name": "Campus Connect",
    "description": "A modular student platform.",
    "associated_with": "University of Dhaka"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| name | string | yes | project name |
| description | string | no | what the project does |
| associated_with | string | no | university, company, or event |

**Success response — 201:**
```json
{
    "id": 1,
    "name": "Campus Connect",
    "description": "A modular student platform.",
    "associated_with": "University of Dhaka",
    "created_at": "2026-06-08T20:00:00Z",
    "images": []
}
```

---

### 7.2 Edit Project

```
PATCH /api/profiles/me/projects/{id}/
Auth: Required
Content-Type: application/json
```

**Success response — 200:** returns the updated project object

---

### 7.3 Delete Project

```
DELETE /api/profiles/me/projects/{id}/
Auth: Required
```

**Success response — 204:** no body

---

## 8. Project Images

### 8.1 Add Project Image

```
POST /api/profiles/me/projects/{project_id}/images/
Auth: Required
Content-Type: multipart/form-data
```

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| image | file | yes | image file (jpg, jpeg, png, webp) |
| is_cover | boolean | no | true marks this as the cover image |
| position | integer | no | display order (default: 0) |

**Success response — 201:**
```json
{
    "id": 1,
    "image_url": "https://res.cloudinary.com/...",
    "is_cover": true,
    "position": 1,
    "uploaded_at": "2026-06-08T20:00:00Z"
}
```

---

### 8.2 Delete Project Image

```
DELETE /api/profiles/me/projects/{project_id}/images/{image_id}/
Auth: Required
```

**Success response — 204:** no body

---

## 9. Skills

### 9.1 List All Skills
Returns all skills in the master list. Supports search.

```
GET /api/profiles/skills/
Auth: Required
```

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| search | string | filter by skill name (case insensitive) |

**Example:** `GET /api/profiles/skills/?search=python`

**Success response — 200:**
```json
[
    {
        "id": 1,
        "name": "Python",
        "is_predefined": true
    },
    {
        "id": 2,
        "name": "Django REST Framework",
        "is_predefined": false
    }
]
```

---

### 9.2 Add Skill to Profile
Add a skill to your profile. Two ways to do this:

**Option A — Add a predefined skill by ID:**
```
POST /api/profiles/me/skills/
Auth: Required
Content-Type: application/json
```

```json
{
    "skill_id": 1,
    "proficiency": "INTERMEDIATE"
}
```

**Option B — Add a custom skill by name:**
```json
{
    "skill_name": "Django REST Framework",
    "proficiency": "BEGINNER"
}
```

If the skill name does not exist it is created automatically with `is_predefined: false`.

**Proficiency values:** `BEGINNER` / `INTERMEDIATE` / `ADVANCED`

**Success response — 201:**
```json
{
    "id": 1,
    "skill": {
        "id": 1,
        "name": "Python",
        "is_predefined": true
    },
    "proficiency": "INTERMEDIATE"
}
```

**Error response:**
```json
{ "error": "You already have this skill." }
```

---

### 9.3 Remove Skill from Profile

```
DELETE /api/profiles/me/skills/{id}/
Auth: Required
```

Note: `{id}` is the `UserSkill` ID from the profile response, not the `Skill` ID.

**Success response — 204:** no body

---

## Quick Reference

### Open endpoints (no token needed)
```
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
```

### Protected endpoints (token required)
All other endpoints require the Authorization header:
```
Authorization: Bearer <access_token>
```

### User type values
```
STUDENT    default
CR         Class Representative
```

### Proficiency level values
```
BEGINNER
INTERMEDIATE
ADVANCED
```

### Supported image formats
```
jpg, jpeg, png, webp
```
