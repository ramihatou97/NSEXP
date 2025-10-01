# Database Optimization Guide
## Neurosurgical Knowledge System

**Last Updated:** 2025-10-01

---

## Overview

This guide provides database optimization recommendations for improving query performance in the Neurosurgical Knowledge Management System.

## Recommended Indexes

### High-Priority Indexes (Add These First)

These indexes provide the most significant performance improvements:

```sql
-- 1. Chapter specialty filtering (very common query)
CREATE INDEX idx_chapters_specialty ON chapters(specialty);

-- 2. Chapter status filtering (for drafts vs published)
CREATE INDEX idx_chapters_status ON chapters(status);

-- 3. Reference type filtering
CREATE INDEX idx_references_type ON references(type);

-- 4. QA sessions by specialty
CREATE INDEX idx_qa_sessions_specialty ON qa_sessions(specialty);

-- 5. Textbook specialty lookup
CREATE INDEX idx_textbooks_specialty ON textbooks(specialty);

-- 6. Citations by chapter (for citation networks)
CREATE INDEX idx_citations_chapter_id ON citations(chapter_id);

-- 7. Created timestamp for sorting (most recent first)
CREATE INDEX idx_chapters_created_at ON chapters(created_at DESC);
CREATE INDEX idx_references_created_at ON references(created_at DESC);
```

### Composite Indexes (For Complex Queries)

Use these for queries that filter on multiple columns:

```sql
-- 1. Chapter by specialty AND status (very common)
CREATE INDEX idx_chapters_specialty_status ON chapters(specialty, status);

-- 2. References by type AND creation date
CREATE INDEX idx_references_type_created ON references(type, created_at DESC);

-- 3. QA sessions by specialty AND date
CREATE INDEX idx_qa_specialty_created ON qa_sessions(specialty, created_at DESC);
```

### Full-Text Search Indexes (PostgreSQL)

For improved search performance:

```sql
-- 1. Chapter content search
CREATE INDEX idx_chapters_content_fts ON chapters
USING GIN(to_tsvector('english', content));

-- 2. Chapter title search
CREATE INDEX idx_chapters_title_fts ON chapters
USING GIN(to_tsvector('english', title));

-- 3. Reference content search
CREATE INDEX idx_references_content_fts ON references
USING GIN(to_tsvector('english', content));
```

## Query Optimization Tips

### 1. Use Pagination

Always paginate large result sets:

```python
# Bad (loads everything)
chapters = await session.execute(select(Chapter))

# Good (paginated)
chapters = await session.execute(
    select(Chapter)
    .offset(page * page_size)
    .limit(page_size)
)
```

### 2. Select Only Needed Columns

Don't load unnecessary data:

```python
# Bad (loads all columns)
chapters = await session.execute(select(Chapter))

# Good (only needed columns)
chapters = await session.execute(
    select(Chapter.id, Chapter.title, Chapter.specialty)
)
```

### 3. Use Eager Loading for Relationships

Avoid N+1 query problems:

```python
# Bad (N+1 queries)
chapters = await session.execute(select(Chapter))
for chapter in chapters:
    references = await chapter.references  # Separate query each time!

# Good (eager loading)
chapters = await session.execute(
    select(Chapter).options(selectinload(Chapter.references))
)
```

### 4. Use COUNT Efficiently

For large tables, estimate counts:

```python
# Bad (slow for large tables)
count = await session.execute(select(func.count(Chapter.id)))

# Better (use database statistics for estimates)
# Or limit the count: ... LIMIT 1000
```

## Database Maintenance

### Regular Tasks

For optimal performance:

```sql
-- 1. Analyze tables (update statistics)
ANALYZE chapters;
ANALYZE references;
ANALYZE qa_sessions;

-- 2. Vacuum (reclaim space)
VACUUM ANALYZE;

-- 3. Reindex (rebuild indexes)
REINDEX TABLE chapters;
```

### Monitoring

Check for slow queries:

```sql
-- Enable query logging (postgresql.conf)
log_min_duration_statement = 1000  # Log queries > 1 second

-- Find slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

## Connection Pooling

Optimize database connections:

```python
# In database configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,        # Max simultaneous connections
    max_overflow=20,     # Additional connections if needed
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

## Performance Benchmarks

### Expected Query Times (Single-User)

| Operation | Without Index | With Index | Improvement |
|-----------|--------------|------------|-------------|
| List chapters by specialty | ~50ms | ~5ms | 10x faster |
| Search chapter content | ~200ms | ~20ms | 10x faster |
| Get chapter with references | ~100ms | ~15ms | 6.7x faster |
| Filter by status | ~30ms | ~3ms | 10x faster |

### Cache Impact

| Operation | No Cache | With Cache | Improvement |
|-----------|----------|------------|-------------|
| Repeated chapter list | ~5ms | ~0.1ms | 50x faster |
| Same Q&A query | ~2000ms (AI) | ~0.1ms | 20,000x faster |
| Reference lookup | ~10ms | ~0.1ms | 100x faster |

## Single-User Optimizations

Since this is a **single-user system**, we can optimize differently:

### 1. Aggressive Caching

```python
# Cache for longer (no concurrent updates to worry about)
@cached(ttl=600)  # 10 minutes
async def get_chapters():
    return await db.query(Chapter).all()
```

### 2. Simplified Transactions

```python
# No need for complex isolation levels
# SERIALIZABLE → READ_COMMITTED is fine for single user
```

### 3. In-Memory Acceleration

```python
# Load frequently accessed data into memory
frequently_used_refs = await load_top_references()
# Keep in memory for fast access
```

## Troubleshooting Slow Queries

### Identify Problem Queries

```sql
-- PostgreSQL: Show currently running queries
SELECT pid, query, state, query_start
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Explain query plan
EXPLAIN ANALYZE
SELECT * FROM chapters WHERE specialty = 'tumor';
```

### Common Issues

| Problem | Solution |
|---------|----------|
| Missing index | Add index on filtered columns |
| N+1 queries | Use eager loading |
| Large result set | Add pagination |
| Full table scan | Ensure indexes exist and are used |
| Slow JOIN | Index foreign key columns |

## Implementation Checklist

For immediate performance improvements:

- [ ] Add high-priority indexes (see above)
- [ ] Enable query caching in application
- [ ] Configure connection pooling
- [ ] Add pagination to list endpoints
- [ ] Use eager loading for relationships
- [ ] Monitor slow queries
- [ ] Schedule regular VACUUM ANALYZE

## Migration Script

To apply recommended indexes:

```bash
# Create indexes (run once)
python manage.py create_indexes

# Or manually via psql:
psql -U your_user -d neurosurgical_knowledge -f scripts/indexes.sql
```

## Further Reading

- [PostgreSQL Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [SQLAlchemy Query Performance](https://docs.sqlalchemy.org/en/14/faq/performance.html)
- [Database Performance Best Practices](https://use-the-index-luke.com/)

---

**Remember:** For a single-user system, aggressive caching and simpler optimization strategies work better than complex distributed solutions!
