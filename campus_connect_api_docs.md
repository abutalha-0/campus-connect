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
        "role": "STUDENT",
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
        "role": "STUDENT",
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
    "role": "STUDENT",
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
            "role": "STUDENT",
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
    "role": "STUDENT",
    "bio": "",
    "created_at": "2026-06-08T20:00:00Z"
}
```

---

### 1.7 Faculty Register
Create a new **faculty** account. Returns tokens immediately — no separate login needed. Faculty use the same login endpoint (1.2) as students.

```
POST /api/faculty/register/
Auth: Not required
Content-Type: application/json
```

**Request body:**
```json
{
    "full_name": "Dr. Farhana Islam",
    "email": "farhana@university.edu",
    "employee_id": "FAC-2291",
    "department": "CSE",
    "designation": "ASSISTANT_PROFESSOR",
    "password": "securepass123"
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| full_name | string | yes | max 100 chars |
| email | string | yes | valid email format, unique |
| employee_id | string | yes | max 50 chars, unique |
| department | string | yes | max 100 chars |
| designation | string | yes | one of the designation values below |
| password | string | yes | min 8 characters |

There is **no username field** — a username is auto-generated from the email
and is not shown to faculty.

**Designation values:**
```
LECTURER
ASSISTANT_PROFESSOR
ASSOCIATE_PROFESSOR
PROFESSOR
```

**Success response — 201:**
```json
{
    "user": {
        "id": 5,
        "email": "farhana@university.edu",
        "username": "farhana",
        "full_name": "Dr. Farhana Islam",
        "role": "FACULTY",
        "bio": "",
        "created_at": "2026-06-08T20:00:00Z"
    },
    "faculty_profile": {
        "employee_id": "FAC-2291",
        "department": "CSE",
        "designation": "ASSISTANT_PROFESSOR",
        "is_verified": false
    },
    "tokens": {
        "access": "eyJ...",
        "refresh": "eyJ..."
    }
}
```

New faculty accounts start with `is_verified: false`. An unverified faculty
member **can still log in**, but is expected to have limited access (e.g. cannot
create classes or subjects) until the admin office verifies the account.

**Error responses:**
```json
{ "email": ["This email is already registered."] }
{ "employee_id": ["This employee ID is already registered."] }
{ "password": ["Ensure this field has at least 8 characters."] }
{ "designation": ["\"X\" is not a valid choice."] }
```

---

## 1F. Faculty Profile

Endpoints for a faculty member to view and edit their **own** profile. All
require a faculty account's token. A student token returns `404`.

### 1F.1 Get My Faculty Profile

```
GET /api/faculty/me/
Auth: Required (faculty)
```

**Success response — 200:**
```json
{
    "user": {
        "id": 5,
        "username": "farhana",
        "full_name": "Dr. Farhana Islam",
        "email": "farhana@university.edu"
    },
    "full_name": "Dr. Farhana Islam",
    "employee_id": "FAC-2291",
    "department": "CSE",
    "designation": "ASSOCIATE_PROFESSOR",
    "is_verified": false,
    "profile_photo": "https://res.cloudinary.com/...",
    "updated_at": "2026-06-08T20:00:00Z",
    "links": [
        {
            "id": 1,
            "link_name": "LinkedIn",
            "icon": "linkedin",
            "url": "https://linkedin.com/in/farhana-islam"
        }
    ]
}
```

---

### 1F.2 Edit My Faculty Profile
Update one or more identity fields. Send only the fields you want to change.

```
PATCH /api/faculty/me/
Auth: Required (faculty)
Content-Type: application/json  (text fields only)
Content-Type: multipart/form-data  (when uploading a photo)
```

**Fields (all optional):**

| Field | Type | Description |
|---|---|---|
| full_name | string | display name, max 100 chars (stored on the user account) |
| department | string | max 100 chars |
| designation | string | one of the designation values |
| profile_photo | file | image file (jpg, jpeg, png, webp) |

`email`, `employee_id`, `is_verified`, and `username` are **read-only** and
cannot be changed through this endpoint (any values sent are ignored).

**Success response — 200:** returns the full updated profile (same shape as 1F.1)

---

### 1F.3 Add Faculty Link

```
POST /api/faculty/me/links/
Auth: Required (faculty)
Content-Type: application/json
```

**Request body:**
```json
{
    "link_name": "LinkedIn",
    "icon": "linkedin",
    "url": "https://linkedin.com/in/farhana-islam"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| link_name | string | yes | display name e.g. "LinkedIn" |
| icon | string | no | icon identifier e.g. "linkedin", "github" |
| url | string | yes | full URL |

**Success response — 201:**
```json
{
    "id": 1,
    "link_name": "LinkedIn",
    "icon": "linkedin",
    "url": "https://linkedin.com/in/farhana-islam"
}
```

---

### 1F.4 Delete Faculty Link

```
DELETE /api/faculty/me/links/{id}/
Auth: Required (faculty)
```

**Success response — 204:** no body

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

## 10. Classroom — Subjects

### 10.0 List My Subjects
Returns all subjects owned by the requesting faculty. Group by `intake` on the
client to render the "Subjects Taught" section.

```
GET /api/classroom/subjects/
Auth: Required (verified faculty)
```

**Success response — 200:**
```json
[
    {
        "id": 1,
        "name": "Data Structures",
        "intake": "42",
        "section": "B",
        "room": "302",
        "code": "739326",
        "faculty_name": "Dr. Farhana Islam",
        "created_at": "2026-06-08T20:00:00Z"
    }
]
```

---

### 10.1 Add Subject
Create a subject. Only a **verified faculty** account may add subjects; the
subject is owned by that faculty and issued a unique 6-digit share **code**
that class creators use to attach it to their class.

```
POST /api/classroom/subjects/
Auth: Required (verified faculty)
Content-Type: application/json
```

**Request body:**
```json
{
    "name": "Data Structures",
    "intake": "42",
    "section": "B",
    "room": "402"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| name | string | yes | subject name, max 200 chars |
| intake | string | yes | intake identifier e.g. "42" |
| section | string | yes | section e.g. "B" |
| room | string | no | room number e.g. "402" |

`code` is generated by the server and cannot be supplied by the client
(any value sent is ignored).

**Success response — 201:**
```json
{
    "id": 1,
    "name": "Data Structures",
    "intake": "42",
    "section": "B",
    "room": "402",
    "code": "828230",
    "faculty_name": "Dr. Farhana Islam",
    "created_at": "2026-06-08T20:00:00Z"
}
```

**Error responses:**
```json
{ "intake": ["This field is required."] }
```
```json
// 403 — account not verified
{ "detail": "Your faculty account is pending verification by the admin office. You cannot add subjects until it is verified." }
```
```json
// 403 — not a faculty account
{ "detail": "Only faculty members can perform this action." }
```

---

### 10.2 Get Subject Detail
Retrieve a subject's detail: its faculty owner, or any student whose class
contains it (via Classroom, §13). Anyone else gets `404`.

```
GET /api/classroom/subjects/{id}/
Auth: Required
```

**Success response — 200:**
```json
{
    "id": 1,
    "name": "Data Structures",
    "intake": "42",
    "section": "B",
    "room": "402",
    "code": "828230",
    "faculty_name": "Dr. Farhana Islam",
    "is_owner": false,
    "can_post": true,
    "created_at": "2026-06-08T20:00:00Z"
}
```

`is_owner` is `true` only for the subject's faculty (use it to show subject
settings/update/delete). `can_post` is `true` for the faculty owner or the
class **CR** (use it to show "Post Resource"/"Post Notice"). This same shape
(including `is_owner`/`can_post`) is returned everywhere a subject appears —
list, create, and inside a class response.

---

### 10.3 Update Subject
Update one or more subject fields. Send only the fields you want to change.
The share `code` is immutable and cannot be changed (any value sent is ignored).

```
PATCH /api/classroom/subjects/{id}/
Auth: Required (verified faculty, owner)
Content-Type: application/json
```

**Fields (all optional):**

| Field | Type | Description |
|---|---|---|
| name | string | subject name, max 200 chars |
| intake | string | intake identifier |
| section | string | section |
| room | string | room number |

**Success response — 200:** returns the full updated subject (same shape as 10.2)

---

### 10.4 Delete Subject

```
DELETE /api/classroom/subjects/{id}/
Auth: Required (verified faculty, owner)
```

**Success response — 204:** no body

---

## 11. Classroom — Resources

Resources belong to a subject. They are grouped in the UI by the
**Saturday–Friday week of their upload time** (`created_at`) — there is no
manual week/topic field.

**Access:**
- **View** (GET): the subject's faculty owner, or any student whose class
  contains the subject. Others get `404`.
- **Post** (POST): the faculty owner, or the **CR** (creator) of a class that
  contains the subject. Otherwise `403`.
- **Edit/Delete** (PATCH/DELETE): the item's author, or the subject's faculty
  owner (moderation). Otherwise `403`.

Each resource includes a **`can_edit`** flag telling the client whether the
current user may edit/delete it.

A resource is either an **uploaded document** (PDF/PPT/DOC) or a **video link**:
- To upload a document, send `multipart/form-data` with a `file` part — it is
  stored on Cloudinary and its URL returned as `file_url`.
- For a video, send `file_url` directly as the video link.

**Resource types:**
```
PDF    PDF document
PPT    Slides
DOC    Doc
VID    Video (link)
```

### 11.1 List Subject Resources
Returns a flat list ordered newest-first; group by the Saturday–Friday week of
`created_at` on the client.

```
GET /api/classroom/subjects/{subject_id}/resources/
Auth: Required (verified faculty, owner)
```

**Success response — 200:**
```json
[
    {
        "id": 1,
        "title": "Course Syllabus.pdf",
        "resource_type": "PDF",
        "description": "Full grading breakdown and weekly outline.",
        "file_url": "https://res.cloudinary.com/...",
        "created_at": "2026-06-08T20:00:00Z"
    }
]
```

---

### 11.2 Add Resource

```
POST /api/classroom/subjects/{subject_id}/resources/
Auth: Required (verified faculty, owner)
Content-Type: multipart/form-data  (document upload)
Content-Type: application/json     (video link, or already-hosted URL)
```

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| title | string | yes | resource title, max 200 chars |
| resource_type | string | yes | one of PDF / PPT / DOC / VID |
| description | string | no | what the resource is for |
| file | file | no | document to upload (PDF/PPT/DOC) |
| file_url | string | no | video link, or a pre-hosted URL |

The week a resource belongs to is derived from its `created_at` upload time —
there is no week/topic field to send.

**Success response — 201:** returns the created resource (same shape as 11.1)

**Error responses:**
```json
{ "title": ["This field is required."] }
{ "resource_type": ["\"ZIP\" is not a valid choice."] }
```

---

### 11.3 Edit Resource
Send only the fields you want to change. Uploading a new `file` replaces
`file_url`.

```
PATCH /api/classroom/subjects/{subject_id}/resources/{id}/
Auth: Required (verified faculty, owner)
Content-Type: application/json  or  multipart/form-data
```

**Success response — 200:** returns the updated resource

---

### 11.4 Delete Resource

```
DELETE /api/classroom/subjects/{subject_id}/resources/{id}/
Auth: Required (verified faculty, owner)
```

**Success response — 204:** no body

---

## 12. Classroom — Notices

Notices belong to a subject. Each notice has an author, an optional highlighted
callout, and an optional file attachment.

**Access** is the same as resources (§11): the faculty owner and enrolled
students may **view**; the faculty owner or the class **CR** may **post**; the
author or the faculty owner (moderation) may **edit/delete**.

The highlighted callout has two independent optional parts — either is enough
to trigger the highlight, and both may be used together:
- `highlight` — free-text label, e.g. "Exam date" or "New deadline" (max 200 chars).
- `event_date` / `event_time` — a **structured** date/time (e.g. an exam or
  deadline), kept separate from `highlight` so a future **Schedule** feature
  can read it directly. `event_time` is only meaningful when `event_date` is
  set — sending a time without a date is a validation error.

Every notice includes:
- `author` — `{ id, full_name, role }` where `role` (`FACULTY` / `CR` /
  `STUDENT`) is the badge to display.
- `mine` — `true` if the requesting user is the author.
- `can_edit` — `true` if the current user may edit/delete this notice.
- `has_highlight` — `true` if `highlight` and/or `event_date` is set (show the
  highlighted callout box).

### 12.1 List Subject Notices
Returns notices newest-first.

```
GET /api/classroom/subjects/{subject_id}/notices/
Auth: Required (faculty owner or enrolled student)
```

**Success response — 200:**
```json
[
    {
        "id": 1,
        "text": "Midterm exam syllabus has been finalized.",
        "highlight": "Exam date",
        "event_date": "2026-07-20",
        "event_time": "10:00:00",
        "attachment_url": "",
        "created_at": "2026-06-08T20:00:00Z",
        "author": {
            "id": 5,
            "full_name": "Dr. Farhana Islam",
            "role": "FACULTY"
        },
        "mine": true,
        "can_edit": true,
        "has_highlight": true
    }
]
```

---

### 12.2 Post Notice

```
POST /api/classroom/subjects/{subject_id}/notices/
Auth: Required (faculty owner or class CR)
Content-Type: application/json     (no attachment)
Content-Type: multipart/form-data  (with attachment)
```

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| text | string | yes | the notice body |
| highlight | string | no | free-text callout label, e.g. "Exam date" (max 200 chars) |
| event_date | string | no | `YYYY-MM-DD`; setting this alone also triggers the highlight |
| event_time | string | no | `HH:MM:SS`; requires `event_date` to also be set |
| file | file | no | optional attachment (uploaded to Cloudinary) |

`author` is taken from the authenticated user; `attachment_url` is set from the
uploaded `file` and cannot be supplied directly.

**Success response — 201:** returns the created notice (same shape as 12.1)

**Error responses:**
```json
{ "text": ["This field is required."] }
{ "event_time": ["event_time requires event_date to also be set."] }
```
```json
// 403 — not the faculty owner or class CR
{ "detail": "You do not have permission to post notices here." }
```

---

### 12.3 Edit Notice
Send only the fields you want to change. The item's **author**, or the
subject's **faculty owner** (moderation), may edit it — otherwise `403`.
Uploading a new `file` replaces the attachment. Send `event_date: null` to
clear the date (and `event_time` with it).

```
PATCH /api/classroom/subjects/{subject_id}/notices/{id}/
Auth: Required (author or faculty owner)
Content-Type: application/json  or  multipart/form-data
```

**Success response — 200:** returns the updated notice

**Error response — 403:**
```json
{ "detail": "You can only edit your own notices." }
```

---

### 12.4 Delete Notice
The item's **author**, or the subject's **faculty owner** (moderation), may
delete it.

```
DELETE /api/classroom/subjects/{subject_id}/notices/{id}/
Auth: Required (author or faculty owner)
```

**Success response — 204:** no body

---

## 13. Classroom — Classes (student side)

A **class** is created by a **CR** (a student whose `student_profile.user_type`
is `CR`) and groups together courses (subjects) added via their secret codes.
Each class has its own shareable **class code** that other students use to join
it. A student is in **one class at a time** — either the one they created or the
one they joined. The CR of a class can post/manage resources & notices in its
subjects (see §11–12).

> All endpoints require a **student** account (`role == STUDENT`). Faculty
> receive `403`.

Every class response includes an **`is_creator`** flag: `true` for the student
who created the class (who can manage courses and delete it), `false` for a
student who merely joined (read-only; they can leave). It also includes
**`creator_name`** (the class creator's full name) for the class settings view.

### 13.1 Look Up a Subject by Code
Resolves a subject's secret code to its details — used by the "add course" draft
to show the subject name before the class is created.

```
GET /api/classroom/classes/lookup/?code=482913
Auth: Required (student)
```

**Success response — 200:** the subject (same shape as §10.2)

**Error response — 404:**
```json
{ "error": "No subject found with that code." }
```

---

### 13.2 Create My Class
Creates the current student's class. Optionally seed it with subjects by their
secret codes. Returns `400` if the student already owns a class.

```
POST /api/classroom/classes/
Auth: Required (student)
Content-Type: application/json
```

**Request body (optional):**
```json
{ "subject_codes": ["482913", "117205"] }
```

**Success response — 201:**
```json
{
    "id": 1,
    "code": "68KYRP",
    "subjects": [ { "id": 1, "name": "Data Structures", "code": "482913", "...": "..." } ],
    "is_creator": true,
    "created_at": "2026-06-08T20:00:00Z"
}
```

**Error responses:**
```json
// 403 — not a CR
{ "error": "Only a CR can create a class. Configure it from your profile." }
```
```json
// 400
{ "error": "You already have a class. Delete it before creating a new one." }
{ "error": "You are already in a class. Leave it before creating your own." }
```

---

### 13.3 Get My Class
Returns the class the student created **or** joined, with `is_creator`.

```
GET /api/classroom/classes/me/
Auth: Required (student)
```

**Success response — 200:** the class (same shape as 13.2). `404` if the
student is not in any class.

---

### 13.4 Add a Course to My Class
Adds a subject by its secret code.

```
POST /api/classroom/classes/me/subjects/
Auth: Required (student)
Content-Type: application/json
```

**Request body:**
```json
{ "code": "117205" }
```

**Success response — 201:** the added subject (same shape as §10.2)

**Error responses:**
```json
{ "error": "No subject found with that code." }
{ "error": "This course is already in your class." }
```

---

### 13.5 Remove a Course from My Class

```
DELETE /api/classroom/classes/me/subjects/{subject_id}/
Auth: Required (student)
```

**Success response — 204:** no body

---

### 13.6 Delete My Class
Requires the account password as confirmation.

```
DELETE /api/classroom/classes/me/
Auth: Required (student)
Content-Type: application/json
```

**Request body:**
```json
{ "password": "your_account_password" }
```

**Success response — 204:** no body

**Error response — 400:**
```json
{ "error": "Incorrect password." }
```

---

### 13.7 Join a Class
Join an existing class by its class code. Blocked if the student already owns
or is already in a class.

```
POST /api/classroom/classes/join/
Auth: Required (student)
Content-Type: application/json
```

**Request body:**
```json
{ "code": "68KYRP" }
```

**Success response — 201:** the joined class (same shape as 13.2, `is_creator: false`)

**Error responses:**
```json
{ "error": "No class found with that code." }
{ "error": "You are already in a class. Leave it before joining another." }
{ "error": "You already have your own class. Delete it before joining another." }
```

---

### 13.8 Leave a Class
Leave the class the student joined. (Creators don't leave — they delete, §13.6.)

```
DELETE /api/classroom/classes/leave/
Auth: Required (student)
```

**Success response — 204:** no body

**Error response — 400:**
```json
{ "error": "You are not a member of any class." }
```

---

## Quick Reference

### Open endpoints (no token needed)
```
POST /api/auth/register/
POST /api/faculty/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
```

### Protected endpoints (token required)
All other endpoints require the Authorization header:
```
Authorization: Bearer <access_token>
```

### Account role values
Returned as `role` on the user object. Set at registration and read-only afterwards.
```
STUDENT    registered via /api/auth/register/
FACULTY    registered via /api/faculty/register/
```

### User type values
The profile-level `user_type` (distinct from the account `role` above).
```
STUDENT    default
CR         Class Representative
```

### Faculty designation values
```
LECTURER
ASSISTANT_PROFESSOR
ASSOCIATE_PROFESSOR
PROFESSOR
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
