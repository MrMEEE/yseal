# ySEal - Your Security Enhanced Architecture Library

<div align="center">

![ySEal Logo](https://via.placeholder.com/150?text=ySEal)

**A modern platform for hosting and distributing SELinux Policy collections**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)

[Features](#features) • [Installation](#installation) • [API Documentation](#api-documentation) • [CLI Tool](#cli-tool) • [Contributing](#contributing)

</div>

---

## 🎯 Overview

**ySEal** (Your Security Enhanced Architecture Library) is a modern, scalable platform inspired by [Ansible Galaxy](https://galaxy.ansible.com) but designed specifically for hosting, discovering, and distributing SELinux Policy collections. It provides a comprehensive ecosystem for security professionals to share, rate, and manage SELinux policies across different systems and use cases.

### Why ySEal?

- 🔒 **Centralized SELinux Policy Repository** - One place to find policies for applications, services, and agents
- 🌟 **Community-Driven** - Vote and rate policies based on quality and effectiveness
- 🔄 **Git Integration** - Policies are stored in Git repositories for version control and transparency
- 🛠️ **CLI Tool** - Install policies with a simple command: `yseal policy install namespace.policyname`
- 🚀 **Scalable** - Built with Django REST Framework, PostgreSQL, Redis, and Celery
- 📊 **Analytics** - Track downloads, ratings, and policy popularity

---

## ✨ Features

### Core Features
- **Namespace Organization** - Group policies under namespaces (e.g., `selinux`, `fedora`, `custom`)
- **Version Management** - Semantic versioning for policies with full changelog support
- **Search & Discovery** - Advanced search with filters by tags, platforms, and deprecation status
- **Rating & Voting System** - Community feedback with upvotes/downvotes and 5-star ratings
- **Git Repository Integration** - Automatic syncing from Git repositories
- **RESTful API** - Complete API for CLI tool and third-party integrations
- **User Authentication** - Token-based auth for both web UI and CLI
- **Download Analytics** - Track policy usage and popularity

### Technical Features
- 🐍 **Django 4.2+** - Modern Python web framework
- 🔥 **Django REST Framework** - Powerful API toolkit
- 🐘 **PostgreSQL** - Advanced database with full-text search
- 🔴 **Redis** - Caching and message broker
- 🌾 **Celery** - Asynchronous task processing
- 📝 **API Documentation** - Auto-generated with drf-spectacular (Swagger/OpenAPI)
- 🐳 **Docker Ready** - Containerized deployment support

---

## 🚀 Quick Start

### Prerequisites

**For Development/Testing (SQLite):**
- Python 3.10+

**For Production (PostgreSQL):**
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Git

### Installation

#### Option 1: SQLite Setup (Recommended for Testing)

```bash
# Clone the repository
git clone https://github.com/MrMEEE/yseal.git
cd yseal

# Run the automated setup script
./setup_sqlite.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up SQLite database
- Create a superuser
- Collect static files

Then start the development server:
```bash
source venv/bin/activate
python manage.py runserver
```

#### Option 2: PostgreSQL Setup (For Production)

1. **Clone the repository**
```bash
git clone https://github.com/MrMEEE/yseal.git
cd yseal
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and set:
# USE_POSTGRES=True
# DB_NAME=yseal
# DB_USER=yseal
# DB_PASSWORD=your_password
```

5. **Create PostgreSQL database**
```bash
createdb yseal
createuser yseal -P  # Set password
psql -c "GRANT ALL PRIVILEGES ON DATABASE yseal TO yseal;"
```

6. **Run migrations**
```bash
python manage.py migrate
```

7. **Create a superuser**
```bash
python manage.py createsuperuser
```

8. **Load initial data (optional)**
```bash
python manage.py loaddata fixtures/initial_data.json
```

9. **Start the development server**
```bash
python manage.py runserver
```

10. **Start Celery worker (in a separate terminal)**
```bash
celery -A yseal worker -l info
```

11. **Start Celery beat for scheduled tasks (in a separate terminal)**
```bash
celery -A yseal beat -l info
```

The application will be available at `http://localhost:8000`

### Access Points

- **Web UI**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/
- **API Schema**: http://localhost:8000/api/schema/

---

## 📚 Project Structure

```
yseal/
├── apps/                          # Django applications
│   ├── accounts/                  # User authentication & profiles
│   │   ├── models.py             # User, UserProfile
│   │   ├── serializers.py        # User serializers
│   │   ├── views.py              # Auth views
│   │   └── urls.py               # Auth endpoints
│   ├── api/                       # API endpoints
│   │   ├── v1/                   # UI-specific API (like _ui/v1)
│   │   └── v3/                   # Main CLI API
│   ├── core/                      # Core utilities & base models
│   │   └── models.py             # TimeStampedModel, SoftDeleteModel
│   ├── namespaces/                # Namespace management
│   │   ├── models.py             # Namespace, NamespaceLink
│   │   └── admin.py              # Admin configuration
│   ├── policies/                  # SELinux policy management
│   │   ├── models.py             # Policy, PolicyVersion, PolicyFile
│   │   └── admin.py              # Policy admin
│   ├── search/                    # Search functionality
│   └── voting/                    # Voting & rating system
│       ├── models.py             # Vote, Rating
│       └── admin.py              # Voting admin
├── yseal/                         # Project configuration
│   ├── settings.py               # Django settings
│   ├── urls.py                   # URL configuration
│   ├── celery.py                 # Celery configuration
│   └── wsgi.py                   # WSGI configuration
├── static/                        # Static files (CSS, JS)
├── media/                         # User-uploaded files
├── templates/                     # HTML templates
├── logs/                          # Application logs
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## 🔌 API Documentation

### API Versions

ySEal provides two API versions:

1. **API v3** (`/api/v3/`) - Main API for CLI tool
2. **API UI v1** (`/api/_ui/v1/`) - UI-specific endpoints

### Authentication

All authenticated endpoints require a token in the header:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v3/policies/
```

#### Getting a Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Response:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### Key Endpoints for CLI Tool

#### Search Policies
```bash
GET /api/v3/policies/?search=apache&tags=web,security
GET /api/_ui/v1/search/?keywords=nginx&type=policy
```

#### List Namespaces
```bash
GET /api/v3/namespaces/
GET /api/v3/namespaces/{name}/
```

#### Get Policy Details
```bash
GET /api/v3/policies/{namespace}/{name}/
GET /api/v3/policies/{namespace}/{name}/versions/
GET /api/v3/policies/{namespace}/{name}/versions/{version}/
```

#### Download Policy
```bash
GET /api/v3/policies/{namespace}/{name}/versions/{version}/download/
```

#### Vote on Policy
```bash
POST /api/v3/policies/{namespace}/{name}/vote/
Content-Type: application/json

{
  "value": 1,  # 1 for upvote, -1 for downvote
  "comment": "Great policy for Apache!"
}
```

#### Rate Policy
```bash
POST /api/v3/policies/{namespace}/{name}/rate/
Content-Type: application/json

{
  "score": 5,  # 1-5 stars
  "review": "Excellent SELinux policy, works perfectly on RHEL 9"
}
```

### Interactive API Documentation

Visit http://localhost:8000/api/docs/ for interactive Swagger UI documentation where you can test all endpoints.

---

## 🛠️ CLI Tool

The **yseal-cli** tool (to be developed) will work similar to `ansible-galaxy`:

### Planned Commands

```bash
# Search for policies
yseal policy search apache

# Show policy information
yseal policy info selinux.apache

# List available versions
yseal policy versions selinux.apache

# Install a policy
yseal policy install selinux.apache

# Install specific version
yseal policy install selinux.apache:1.2.3

# List installed policies
yseal policy list

# Remove a policy
yseal policy remove selinux.apache

# Login (get token)
yseal login

# Rate a policy
yseal policy rate selinux.apache --score 5 --review "Excellent!"

# Vote on a policy
yseal policy vote selinux.apache --upvote
```

### Configuration File

`~/.yseal/config`
```ini
[general]
server_url = https://yseal.example.com
token = your-auth-token-here

[install]
policy_path = /etc/selinux/custom/
```

---

## 🗄️ Database Schema

### Core Models

#### User & Authentication
- **User** - Custom user model with extended fields
- **UserProfile** - Additional user profile information

#### Namespaces
- **Namespace** - Policy namespace/organization
- **NamespaceLink** - External links for namespaces

#### Policies
- **Policy** - Main policy entity
- **PolicyVersion** - Specific version of a policy
- **PolicyFile** - Individual files within a policy version
- **Tag** - Tags for categorization
- **DownloadLog** - Track policy downloads

#### Voting
- **Vote** - Upvote/downvote on policies
- **Rating** - 5-star ratings with reviews
- **RatingHelpfulness** - Track helpful ratings

---

## 🔧 Configuration

### Database Configuration

ySEal supports both SQLite and PostgreSQL:

**SQLite (Default for Development/Testing)**
- Set `USE_POSTGRES=False` in `.env`
- No database server required
- Perfect for local development and testing
- Limited full-text search capabilities

**PostgreSQL (Recommended for Production)**
- Set `USE_POSTGRES=True` in `.env`
- Advanced full-text search with GIN indexes
- Better performance for large datasets
- ArrayField support for lists
- Requires PostgreSQL server

The models automatically adapt based on your database choice.

### Environment Variables

Key configuration options in `.env`:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
USE_POSTGRES=False  # Set to True for PostgreSQL
DB_NAME=yseal
DB_USER=yseal
DB_PASSWORD=yseal
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0

# Policy Settings
MAX_POLICY_SIZE_MB=10
GIT_SYNC_INTERVAL_HOURS=24
```

### Django Settings

See `yseal/settings.py` for all configuration options.

---

## 🧪 Testing

Run tests with:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/policies/tests/test_models.py

# Run with verbose output
pytest -v
```

---

## 🐳 Docker Deployment

(Docker configuration to be added)

```bash
# Build and run with docker-compose
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

---

## � Testing

ySEal uses pytest for testing with SQLite for fast test execution.

### Run Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run specific test file
pytest apps/policies/tests/test_models.py

# Run in parallel (faster)
pytest -n auto
```

### Test Configuration

Tests use SQLite in-memory database for speed. Configuration is in `yseal/test_settings.py`.

---

## �🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Option 1: SQLite (Quick start)
./setup_sqlite.sh

# Option 2: Manual setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run linting
flake8 apps/
black apps/
isort apps/

# Run tests
pytest
```

---

## 📖 Documentation

- [API Documentation](http://localhost:8000/api/docs/) - Interactive API docs
- [Admin Guide](docs/admin-guide.md) - Server administration
- [User Guide](docs/user-guide.md) - Using the web interface
- [CLI Guide](docs/cli-guide.md) - Command-line tool
- [Developer Guide](docs/developer-guide.md) - Contributing code

---

## 🔒 Security

### Reporting Security Issues

Please report security vulnerabilities to: security@yseal.example.com

### Security Features

- Token-based authentication
- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection
- Rate limiting (planned)
- SSL/TLS in production

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by [Ansible Galaxy](https://galaxy.ansible.com) and [galaxy_ng](https://github.com/ansible/galaxy_ng)
- Built with [Django](https://www.djangoproject.com/) and [Django REST Framework](https://www.django-rest-framework.org/)
- SELinux community for their amazing work

---

## 📞 Contact & Support

- **Website**: https://yseal.example.com
- **GitHub**: https://github.com/MrMEEE/yseal
- **Issues**: https://github.com/MrMEEE/yseal/issues
- **Discussions**: https://github.com/MrMEEE/yseal/discussions

---

## 🗺️ Roadmap

- [x] Core Django project structure
- [x] User authentication system
- [x] Namespace management
- [x] Policy models with versioning
- [x] Voting and rating system
- [ ] Complete REST API implementation
- [ ] Git repository integration
- [ ] Search functionality
- [ ] Web UI templates
- [ ] CLI tool (yseal-cli)
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Production deployment guide
- [ ] Monitoring and logging
- [ ] Rate limiting
- [ ] API key management

---

<div align="center">

**Made with ❤️ for the SELinux community**

⭐ Star us on GitHub if you find this project useful!

</div>
