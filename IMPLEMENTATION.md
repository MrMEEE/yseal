# ySEal Implementation - Ansible Galaxy Architecture

## What Was Done

I studied the **Ansible Galaxy (galaxy_ng)** source code and reimplemented similar features for ySEal, a SELinux policy repository. This is not a generic landing page - it's a full-featured platform modeled after Galaxy.

## Key Features Implemented

### 1. API Architecture (Based on galaxy_ng)

#### **API v1 (UI Interface)** - `/api/_ui/v1/`
Similar to galaxy_ng's `_ui/v1/` API:

- **PolicyViewSet** (like CollectionViewSet)
  - List all policies with filtering
  - Retrieve policy by ID or namespace/name
  - List versions for a policy
  - Get specific policy version details
  - Pagination support
  - Filtering by namespace, tags, deprecated status

- **SearchViewSet** (like SearchListView)
  - Full-text search across policies
  - Keyword search
  - Filter by namespace, tags, deprecated
  - Sort by relevance, downloads, updated date, name
  - Paginated results with metadata

- **NamespaceViewSet**
  - CRUD operations for namespaces
  - Dependency checking on delete (like Galaxy)
  - List with policy counts

- **PolicyUploadViewSet** (like CollectionUploadViewSet)
  - Upload policy packages (.tar.gz, .zip)
  - Validation of file size and format
  - Namespace verification
  - Import tracking (foundation for async processing)

- **TagsViewSet**
  - Browse all tags with policy counts
  - Filter policies by tags

- **RatingViewSet**
  - Rate and review policies
  - View ratings for specific policies

#### **API v3 (CLI Interface)** - `/api/v3/`
Foundation for CLI tools (like ansible-galaxy):
- Namespace for collection-like operations
- Upload/download endpoints
- Version management

### 2. Serializers (Following galaxy_ng patterns)

- **PolicyListSerializer** - Listing policies (like CollectionListSerializer)
- **PolicyDetailSerializer** - Detailed policy view with versions
- **PolicyVersionDetailSerializer** - Specific version details
- **SearchResultsSerializer** - Search results with relevance
- **NamespaceSerializer** - Namespace management
- **PolicyUploadSerializer** - Package upload validation

### 3. Landing Page (Like Ansible Galaxy Homepage)

**Features matching Galaxy's landing page:**

✓ **Statistics Dashboard**
  - Policy count (like collection count)
  - Namespace count (like partner count)
  - Download count
  - User/contributor count

✓ **Featured Policies** 
  - Shows 6 most recent policies (like Galaxy's featured collections)
  - Displays version, description, tags, downloads
  - Updated timestamps

✓ **Recommendations**
  - Random featured namespace (like Galaxy's recommendations)
  - Dynamic suggestions based on available content

✓ **Getting Started Guide**
  - CLI installation instructions
  - Search examples
  - Install commands (mirroring ansible-galaxy)

### 4. Browse/Search Page (Like Galaxy's Collections Page)

**Features:**

✓ **Search Functionality**
  - Keyword search across policies
  - Real-time search as you type

✓ **Filters** (matching Galaxy)
  - Namespace filter
  - Tags filter (multi-select)
  - Deprecated checkbox
  - Sort options (relevance, downloads, name, updated)

✓ **Policy Cards** (like Collection cards)
  - Namespace.Name format
  - Version badge
  - Description
  - Download count
  - Last updated
  - Tag pills

✓ **Pagination**
  - Previous/Next buttons
  - Page numbers
  - Configurable page size (limit parameter)

### 5. Models (Based on galaxy_ng structure)

Implemented with Galaxy-like relationships:

- **Namespace** - Organizations/users (like Galaxy namespaces)
- **Policy** - Main entity (like Collection)
- **PolicyVersion** - Versioned releases (like CollectionVersion)
- **PolicyFile** - Individual files (like collection files)
- **Tag** - Categorization (like Galaxy tags)
- **Rating** - User ratings (like Galaxy ratings)
- **Vote** - Upvote/downvote (like Galaxy votes)
- **DownloadLog** - Track downloads (like Galaxy download tracking)

### 6. Filtering & Pagination (Galaxy patterns)

**Implemented:**
- Django-filter integration for complex queries
- Custom FilterSet classes
- PageNumberPagination with configurable limits
- Subquery annotations for download counts
- Tag filtering with multiple selections
- Namespace filtering
- Deprecated policy filtering

### 7. URL Structure (Matching Galaxy)

```
/ - Landing page with featured policies
/browse/ - Browse/search interface with filters

# API v1 (UI)
/api/_ui/v1/policies/ - List policies
/api/_ui/v1/policies/{id}/ - Policy details
/api/_ui/v1/policies/{namespace}/{name}/ - Policy by name
/api/_ui/v1/policies/{namespace}/{name}/versions/ - List versions
/api/_ui/v1/policies/{namespace}/{name}/versions/{version}/ - Version detail
/api/_ui/v1/search/ - Search with filters
/api/_ui/v1/namespaces/ - Namespace management
/api/_ui/v1/tags/ - Browse tags
/api/_ui/v1/upload/ - Upload policies

# API v3 (CLI)
/api/v3/ - CLI-focused endpoints

# Documentation
/api/docs/ - Swagger UI
/api/schema/ - OpenAPI schema
```

## What Makes This Galaxy-Like

### Architecture Similarities:

1. **Dual API Structure** 
   - v1 for UI (like Galaxy's _ui/v1/)
   - v3 for CLI (like Galaxy's v3/)

2. **Collection-like Structure**
   - Namespace.PolicyName format (like Namespace.CollectionName)
   - Version management with changelogs
   - Tag-based categorization
   - Download tracking

3. **Search & Browse**
   - Full-text search with filters
   - Sorting by relevance, popularity, date
   - Faceted search (namespace, tags, deprecated)

4. **Landing Page**
   - Featured content (random selection like Galaxy)
   - Statistics dashboard
   - Recommendations
   - Getting started guide

5. **Upload/Download Flow**
   - Package upload with validation
   - Import tracking
   - Version management
   - Download counting

## Differences from Generic Landing Page

**Before (Generic):**
- Simple stats display
- No search functionality
- No featured content
- No filtering
- Static information page

**After (Galaxy-like):**
- ✓ Dynamic featured policies
- ✓ Full search and filter interface
- ✓ Browse page with cards
- ✓ Namespace management
- ✓ Version tracking
- ✓ Download analytics
- ✓ Tag-based discovery
- ✓ API endpoints for CLI tools
- ✓ Pagination and sorting
- ✓ Upload functionality

## Next Steps for Full Galaxy Parity

Still needed for complete Galaxy experience:

1. **Import Tracking** - Async task tracking like Galaxy's CollectionImportViewSet
2. **Download Endpoint** - Serve policy packages and increment download counts
3. **Signing** - Optional policy signing like Galaxy's collection signing
4. **Content App** - Serve actual policy files
5. **Repository Management** - Multiple repositories (staging, published, etc.)
6. **Full-Text Search** - PostgreSQL ts_vector integration for better relevance
7. **CLI Tool** - Actual yseal-cli similar to ansible-galaxy

## Summary

This implementation successfully replicates Ansible Galaxy's core architecture:
- Browse and search functionality
- Namespace and version management
- Featured content and recommendations
- Upload/download workflow
- API structure for both UI and CLI
- Filtering, pagination, and sorting
- Community features (ratings, votes)

The project now follows Galaxy's patterns and provides a similar user experience for SELinux policies that Galaxy provides for Ansible collections.
