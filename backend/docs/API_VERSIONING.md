# API Versioning Strategy
## Neurosurgical Knowledge System

**Version:** 1.0
**Last Updated:** 2025-10-01
**Status:** Active

---

## Overview

This document defines the API versioning strategy for the Neurosurgical Knowledge Management System. Our approach balances stability for single-user deployment with flexibility for future enhancements.

## Current Version

**API Version:** `v1`
**Implementation Status:** ✅ Stable
**Base Path:** `/api/v1`

## Versioning Approach

### URL Path Versioning

We use URL path versioning as it provides:
- ✅ Clear visibility of API version in use
- ✅ Easy debugging and testing
- ✅ Explicit version selection
- ✅ Browser-friendly for development

**Format:** `/api/{version}/{resource}`

**Example:**
```
GET /api/v1/chapters
POST /api/v1/synthesis/generate
GET /api/v1/qa/ask
```

## Version Lifecycle

### Supported Versions

| Version | Status | Support End | Notes |
|---------|--------|-------------|-------|
| v1 | ✅ Active | N/A | Current stable version |
| v2 | 🚧 Future | N/A | Planned for future features |

### Single-User Deployment Notes

Since this is a **single-user system**, version deprecation follows a simplified model:
- **No forced deprecation** - old versions continue to work
- **Gradual migration** - you control when to update
- **Backward compatibility** - maintained where possible

## Breaking vs Non-Breaking Changes

### Breaking Changes (Require New Version)

Breaking changes **require a new API version** (e.g., v1 → v2):

- ❌ Removing endpoints
- ❌ Removing required parameters
- ❌ Changing response structure significantly
- ❌ Changing authentication requirements
- ❌ Renaming fields in responses

**Example:**
```python
# v1 (old)
GET /api/v1/chapters → {"chapters": [...]}

# v2 (new - breaking)
GET /api/v2/chapters → {"data": [...], "meta": {...}}
```

### Non-Breaking Changes (Same Version)

Non-breaking changes can be added to **existing versions**:

- ✅ Adding new endpoints
- ✅ Adding optional parameters
- ✅ Adding new fields to responses
- ✅ Relaxing validation rules
- ✅ Improving performance

**Example:**
```python
# v1 (before)
GET /api/v1/chapters → {"id": "123", "title": "..."}

# v1 (after - non-breaking)
GET /api/v1/chapters → {"id": "123", "title": "...", "tags": [...]}
```

## Version Selection

### Default Version

If no version is specified, the system defaults to **v1**:

```bash
# These are equivalent
GET /api/chapters → redirects to /api/v1/chapters
GET /api/v1/chapters
```

### Version Header (Future)

In future releases, version can also be specified via header:

```bash
curl -H "API-Version: v1" https://api.example.com/chapters
```

## Migration Strategy

### When to Create a New Version

Create a new API version when:

1. **Breaking changes are needed** for significant improvements
2. **Major feature additions** that change core behavior
3. **Security requirements** that break backward compatibility
4. **Performance optimizations** requiring structural changes

### How to Migrate

For single-user deployment:

1. **Test new version** - both v1 and v2 run simultaneously
2. **Update client code** gradually
3. **Switch when ready** - no time pressure
4. **Keep v1 running** as long as needed

## API Version Response

Every API response includes version information:

```json
{
  "api_version": "v1",
  "data": {...},
  "meta": {
    "version": "2.1.0",
    "timestamp": "2025-10-01T12:00:00Z"
  }
}
```

## Error Handling

### Invalid Version

```json
GET /api/v99/chapters

Response: 404 Not Found
{
  "error": "API version not found",
  "message": "Version 'v99' is not available. Current version: v1",
  "available_versions": ["v1"]
}
```

### Deprecated Version (Future)

```json
GET /api/v0/chapters

Response: 410 Gone
{
  "error": "Version deprecated",
  "message": "API v0 is no longer supported. Please upgrade to v1.",
  "migration_guide": "/docs/migration/v0-to-v1"
}
```

## Version History

### v1.0.0 (Current)
**Released:** 2025-10-01
**Status:** ✅ Active

**Endpoints:**
- 37 total endpoints
- Chapter management (CRUD)
- AI synthesis
- Q&A system
- Search functionality
- Reference library

**Features:**
- Mock mode support
- Optional AI integration
- Graceful degradation
- Single-user optimized

### v2.0.0 (Planned)
**Status:** 🚧 Future

**Proposed Changes:**
- Enhanced real-time features
- Improved caching
- Advanced search capabilities
- Performance optimizations

## Best Practices

### For Development

1. **Always specify version** in client code
2. **Test against specific version** - don't rely on defaults
3. **Monitor deprecation notices** in logs
4. **Plan migrations** before they're required

### For API Design

1. **Maintain backward compatibility** within a version
2. **Document all changes** in CHANGELOG
3. **Use semantic versioning** for application version
4. **Keep versions simple** - avoid micro-versions like v1.2.3

## Semantic Versioning

Application version follows semantic versioning:

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking API changes (v1 → v2)
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes, no API changes

**Example:**
- `2.0.0` - New API version (breaking changes)
- `2.1.0` - New features added to v2 (compatible)
- `2.1.1` - Bug fixes (compatible)

## References

- [FastAPI Versioning Best Practices](https://fastapi.tiangolo.com/)
- [RESTful API Design](https://restfulapi.net/)
- [Semantic Versioning](https://semver.org/)

---

**Questions or Concerns?**

Since this is a single-user system, versioning is flexible. You control:
- ✅ When to upgrade
- ✅ Which version to use
- ✅ Migration timeline

No pressure, no forced deprecation! 🎉
