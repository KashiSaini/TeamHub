# TeamHub — Django Backend Learning Project

A phase-by-phase Django backend project built to learn and implement real backend features by **building a complete team collaboration system**.

This project was designed as a learning journey, not just a final codebase. Instead of adding everything at once, the backend was built in layers so each Django concept could be understood in context.

---

## Project Summary

TeamHub is a backend for a team collaboration app, similar to a lightweight mix of Trello and Slack.

It currently includes:

- Django project structure
- PostgreSQL database
- Custom user model
- Core collaboration models
- Django admin setup
- Django REST Framework APIs (DRF)
- JWT authentication
- Permissions and team-based authorization
- Custom middleware
- Redis caching
- Signals
- Channels + WebSockets
- Realtime notifications
- Production-readiness concepts and structure

---

# Learning Roadmap Used in This Project

The project was built in phases.

## Phase 1A — Project foundation

### Goal
Set up the Django project correctly from the beginning so advanced features could be added cleanly later.

### What was added

1. Created the Django project.
2. Created apps:
   - `accounts`
   - `teams`
   - `tasks`
   - `notifications`
3. Connected Django to PostgreSQL.
4. Added environment variable support using `.env`.
5. Created a **custom user model** before full migrations.
6. Registered the custom user model in Django admin.
7. Ran initial migrations.
8. Created a superuser.

### Why this phase mattered

This phase created the base architecture of the project.

The biggest important decision here was:

- using a **custom user model from the beginning**

That avoids major problems later when adding JWT, permissions, profiles, and custom user fields.

### Main files involved

- `config/settings.py`
- `accounts/models.py`
- `accounts/admin.py`
- `.env`

### Core setup decisions

- Database: PostgreSQL
- Secrets/config: `.env`
- User model: `accounts.User`

---

## Phase 1B — Core models and relationships

### Goal
Build the real data backbone of the collaboration system.

### What was added

#### In `teams` app
- `Team`
- `TeamMembership`
- `Project`

#### In `tasks` app
- `Task`
- `Comment`

### Relationship design

The system was designed like this:

- A **User** can join many teams.
- A **Team** can have many users.
- That relationship uses `TeamMembership` so it can store:
  - role
  - joined time
- A **Team** has many **Projects**.
- A **Project** has many **Tasks**.
- A **Task** has many **Comments**.
- A task may be assigned to a user.

### Roles added in memberships

- owner
- admin
- member

### Why this design was chosen

A simple many-to-many relationship was not enough because team membership needed extra information like role and join date.

So the better Django design was:

- `ManyToManyField(... through="TeamMembership")`

### Admin work done

All core models were registered in admin so they could be tested and managed before APIs were built.

### Main files involved

- `teams/models.py`
- `tasks/models.py`
- `teams/admin.py`
- `tasks/admin.py`

---

## Phase 2 — DRF API layer

### Goal
Turn Django models into a usable API backend.

### What was added

1. Installed Django REST Framework.
2. Added DRF to `INSTALLED_APPS`.
3. Added basic DRF settings.
4. Created serializers for:
   - Team
   - TeamMembership
   - Project
   - Task
   - Comment
5. Created viewsets for CRUD APIs.
6. Added routers.
7. Connected API URLs in the main project.

### What APIs were created

- `/api/teams/`
- `/api/memberships/`
- `/api/projects/`
- `/api/tasks/`
- `/api/comments/`

### DRF concepts learned here

- `ModelSerializer`
- `ModelViewSet`
- `DefaultRouter`
- `perform_create()`
- `read_only_fields`
- `select_related()`

### Important logic added

When a team is created:

- the request user becomes `created_by`
- an owner membership is created automatically for that user

### Main files involved

- `teams/serializers.py`
- `tasks/serializers.py`
- `teams/views.py`
- `tasks/views.py`
- `teams/urls.py`
- `tasks/urls.py`
- `config/urls.py`

---

## Phase 3 — Authentication and permissions

### Goal
Make the API secure and restrict access based on team membership and roles.

### What was added

1. Installed `djangorestframework-simplejwt`.
2. Configured DRF authentication classes.
3. Added JWT settings.
4. Added registration API.
5. Added auth endpoints for:
   - register
   - login
   - refresh
   - verify
6. Added custom permission logic for teams, projects, tasks, and comments.
7. Added queryset filtering so users only see data for teams they belong to.
8. Added serializer validation for safe task assignment and memberships.

### Auth endpoints added

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/verify/`

### Key permission rules implemented

#### Teams
- Team members can read.
- Team admins/owners can modify.

#### Memberships
- Only owners/admins can add, update, or remove members.

#### Projects
- Only owners/admins can create or manage projects.

#### Tasks
- Team members can view tasks.
- Team admins/owners can edit all tasks.
- Task creator or assignee can edit their own task-related objects depending on rules.

#### Comments
- Team members can read comments.
- Comment authors or team admins/owners can edit/delete comments.

### Business validation added

- A user cannot be added to the same team twice.
- A task can only be assigned to a user who belongs to that task’s team.

### Main files involved

- `accounts/serializers.py`
- `accounts/views.py`
- `accounts/urls.py`
- `teams/permissions.py`
- `tasks/permissions.py`
- updated `teams/views.py`
- updated `tasks/views.py`
- updated serializers

---

## Phase 4 — Middleware and request lifecycle

### Goal
Understand and add project-wide request/response behavior.

### What was added

Two custom middleware classes were created:

1. `RequestIDMiddleware`
2. `RequestLogMiddleware`

### What each middleware does

#### `RequestIDMiddleware`
- creates a unique request ID for every request
- attaches it to the request object
- adds it to the response header as `X-Request-ID`

#### `RequestLogMiddleware`
- measures request duration
- logs:
  - request ID
  - method
  - path
  - response status
  - user
  - time taken

### Why this phase mattered

This phase helped explain:

- how middleware wraps views
- what runs before and after the view
- where sessions and Django auth middleware fit
- why JWT auth in DRF is different from Django session middleware

### Logging configuration

A custom logger was added to print middleware logs in the console.

### Main files involved

- `config/middleware.py`
- `config/settings.py`

---

## Phase 5 — Redis and caching

### Goal
Use Redis as a performance and temporary-data tool.

### What was added

1. Installed:
   - `django-redis`
   - `redis`
2. Added Redis URL to `.env`.
3. Configured Django cache backend using Redis.
4. Added cache settings to Django.
5. Began caching selected API responses.
6. Added a Redis-based example for temporary team invite tokens.
7. Added a cached dashboard-summary style pattern.

### Why Redis was introduced

Redis was used for:

- caching repeated API responses
- short-lived temporary data
- preparing for Channels/WebSockets later

### Important caching concepts learned

- cache is **not** the source of truth
- PostgreSQL remains the main database
- Redis stores temporary or rebuildable data
- timeouts matter
- invalidation is one of the hardest parts of caching
- protected endpoints must be cached carefully

### Important patterns introduced

#### Endpoint caching
Using decorators like:
- `cache_page(...)`
- `vary_on_headers("Authorization")`

#### Low-level cache usage
Using:
- `cache.set()`
- `cache.get()`
- `cache.delete()`

### Why `vary_on_headers("Authorization")` mattered

Because TeamHub APIs are user-specific.

Without varying by auth header, one user’s cached response could leak to another user.

### Main files involved

- `config/settings.py`
- updated `teams/views.py`
- `teams/utils.py`
- `teams/services.py`

---

## Phase 6 — Signals

### Goal
Make the app react automatically to model events in a clean way.

### What was added

1. Created a `Notification` model.
2. Registered notifications in admin.
3. Added signals for:
   - team member added
   - task assigned
   - comment added
4. Registered signals in app `ready()` methods.

### Notification model fields

- recipient
- type
- title
- message
- is_read
- created_at

### Signal behavior added

#### When a team member is added
A notification is created for the added user.

#### When a task is assigned
A notification is created for the assigned user.

#### When a comment is added
Notifications are created for relevant users such as the task creator and assignee, excluding the comment author where appropriate.

### Why signals were used here

Signals were used for **secondary side effects**, not core business logic.

That is the correct use case for signals.

### Important lesson learned

Signals are useful, but should not hide critical business rules.

Good uses:
- notifications
- cache invalidation
- audit side effects

Bad uses:
- permissions
- core validation
- main business decisions

### Main files involved

- `notifications/models.py`
- `notifications/admin.py`
- `teams/signals.py`
- `tasks/signals.py`
- `teams/apps.py`
- `tasks/apps.py`
- `config/settings.py`

---

## Phase 7 — Channels and WebSockets

### Goal
Add realtime behavior to TeamHub.

### What was added

1. Installed:
   - `channels[daphne]`
   - `channels_redis`
2. Added `daphne` to `INSTALLED_APPS`.
3. Configured `ASGI_APPLICATION`.
4. Added Redis channel layer configuration.
5. Created a WebSocket consumer for notifications.
6. Added WebSocket routing.
7. Added custom JWT middleware for WebSockets.
8. Replaced plain ASGI config with Channels routing.
9. Added a notification service that both:
   - saves to DB
   - pushes live over WebSocket
10. Updated signals to use this new notification service.

### Realtime feature implemented

#### Live notifications
Each user connects to:
- `/ws/notifications/?token=ACCESS_TOKEN`

When a notification is created:
- it is saved in PostgreSQL
- it is sent to the user’s WebSocket group through Redis
- the browser receives it instantly

### Consumer behavior

The `NotificationConsumer`:
- accepts authenticated users
- joins them to a user-specific group
- sends JSON messages back to the client
- can respond to `ping`

### WebSocket auth approach used

A custom JWT auth middleware was created for Channels.

Reason:
- Channels built-in `AuthMiddlewareStack` is session-based
- TeamHub uses JWT for API auth
- WebSocket auth therefore needed custom JWT handling

### Redis role in this phase

Redis became the channel layer used to broadcast events from Django server code to active WebSocket connections.

### Important bug fixed during this phase

A realtime push failure caused task creation to crash when Redis was unavailable.

That was fixed by making realtime push non-fatal:

- database notification is still created
- WebSocket push is attempted
- if Redis fails, the app logs a warning instead of breaking the whole request

### Main files involved

- `notifications/consumers.py`
- `notifications/routing.py`
- `notifications/auth.py`
- `notifications/services.py`
- `config/asgi.py`
- updated signal files
- `config/settings.py`

---

## Phase 8 — Production readiness

### Goal
Understand how TeamHub would be structured for real deployment.

### What was covered

1. Production settings vs development settings
2. WSGI vs ASGI
3. Gunicorn vs Uvicorn vs Daphne
4. Why TeamHub should be ASGI-first
5. Static files vs media files
6. Nginx role in deployment
7. Reverse proxying and WebSocket support
8. Deployment checks and secure production settings

### Important concepts learned

#### WSGI
Traditional Python web deployment interface.

#### ASGI
Required for async/realtime support like Channels and WebSockets.

#### Why TeamHub should use ASGI
Because TeamHub includes realtime WebSockets.

#### Recommended production architecture

```text
Internet
→ Nginx
→ ASGI server (Daphne/Uvicorn)
→ Django + Channels
→ PostgreSQL + Redis
```

### Production settings strategy discussed

Recommended settings split:

- `config/settings/base.py`
- `config/settings/dev.py`
- `config/settings/prod.py`

### Static/media strategy discussed

Static files:
- app assets
- served after `collectstatic`

Media files:
- user uploads
- stored and served separately

### Security and deployment topics discussed

- `DEBUG=False`
- `ALLOWED_HOSTS`
- secure cookies
- SSL redirect
- `CSRF_TRUSTED_ORIGINS`
- `check --deploy`

---

# Current Feature Set

As of now, TeamHub includes the following working backend capabilities.

## Authentication
- Custom user model
- JWT login
- token refresh
- token verify
- registration endpoint

## Collaboration models
- Teams
- memberships with roles
- projects
- tasks
- comments

## Access control
- team-based authorization
- owner/admin/member roles
- task/comment rules

## Developer tooling
- Django admin
- middleware request logging
- request ID tracing

## Performance / infrastructure
- PostgreSQL
- Redis cache
- Redis channel layer

## Event-driven behavior
- signals
- notification creation

## Realtime
- WebSocket notifications
- user-specific notification groups

---

# Current Project Structure

A simplified structure looks like this:

```text
teamhub/
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── teams/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── signals.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
│
├── tasks/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
│
├── notifications/
│   ├── admin.py
│   ├── auth.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   └── services.py
│
├── config/
│   ├── asgi.py
│   ├── middleware.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
└── .env
```

---

# Example Technology Stack Used

- **Django** — main web framework
- **Django REST Framework** — APIs
- **PostgreSQL** — relational database
- **Simple JWT** — token auth
- **Redis** — caching and channel layer
- **Channels** — WebSockets / realtime
- **Daphne** — ASGI development/runtime server

---

# How to Run the Project Locally

## 1. Create and activate virtual environment

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

## 2. Install dependencies

```bash
pip install django psycopg[binary] python-decouple djangorestframework djangorestframework-simplejwt django-redis redis "channels[daphne]" channels_redis
```

## 3. Create PostgreSQL database

Example:

```sql
CREATE DATABASE teamhub_db;
```

## 4. Add `.env`

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=teamhub_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=127.0.0.1
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
```

## 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Create superuser

```bash
python manage.py createsuperuser
```

## 7. Start Redis

If using Docker:

```bash
docker run -d --name teamhub-redis -p 6379:6379 redis:7
```

If the container already exists:

```bash
docker start teamhub-redis
```

## 8. Run server

```bash
python manage.py runserver
```

---

# Important API Endpoints

## Auth
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/verify/`

## Collaboration
- `/api/teams/`
- `/api/memberships/`
- `/api/projects/`
- `/api/tasks/`
- `/api/comments/`

## Admin
- `/admin/`

## WebSocket
- `/ws/notifications/?token=ACCESS_TOKEN`

---

# How Realtime Notifications Work

1. A model event happens, such as:
   - user added to team
   - task assigned
   - comment added
2. A Django signal runs.
3. The signal calls `create_notification(...)`.
4. A `Notification` row is created in PostgreSQL.
5. A WebSocket event is sent through Redis channel layer.
6. The connected client receives the event instantly.

---

# Testing WebSockets in Browser Console

After logging in and getting an access token, connect like this:

```javascript
const token = "YOUR_ACCESS_TOKEN";
const protocol = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${protocol}://${window.location.host}/ws/notifications/?token=${token}`);

socket.onopen = () => console.log("connected");
socket.onmessage = (event) => console.log("message:", JSON.parse(event.data));
socket.onclose = (event) => console.log("closed:", event.code, event.reason);
socket.onerror = (event) => console.log("socket error", event);
```

---

# Main Lessons from This Project

This project was built to learn Django deeply by building a realistic backend.

Key lessons learned:

- build features in layers, not all at once
- create the custom user model early
- model relationships correctly first
- use DRF to expose data cleanly
- JWT handles identity, permissions handle access
- middleware is for project-wide behavior
- Redis is for speed and temporary data, not core truth
- signals are best for side effects, not core business rules
- Channels + Redis make realtime features possible
- ASGI matters when WebSockets enter the project
- production structure is different from development structure

---

# Suggested Next Improvements

If development continues, good next steps would be:

- add notification API endpoints
- add unread notification count API
- add mark-as-read notification endpoint
- add file uploads / attachments
- add Docker and deployment files
- add background tasks for heavy async work

---

# Final Note

TeamHub is not just a backend app.

It is a structured Django mastery project built to learn:

- Django fundamentals
- DRF
- authentication and permissions
- middleware
- Redis
- signals
- Channels
- realtime systems
- deployment thinking
- filter and pagination
- drf-spectacular (OpenAPI Docs)

The project was intentionally built **phase by phase** so every new concept was connected to a real use case.
