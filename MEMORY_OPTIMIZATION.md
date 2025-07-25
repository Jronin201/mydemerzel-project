# Memory Optimization Guide for Render Deployment

## Problem Solved

Your Render deployment was running out of memory (512MB limit) because:

1. **Large embedding files (170MB total)** were loaded into memory at startup
2. **All TTRPG systems loaded simultaneously** regardless of usage
3. **No memory management** for embeddings
4. **Multiple workers** potentially loading embeddings multiple times

## Solution Implemented

### 1. Lazy Loading System

- **Before**: All 170MB of embeddings loaded at startup
- **After**: Embeddings loaded only when specific TTRPG system is accessed
- **Memory savings**: ~160MB+ at startup

### 2. Memory-Optimized Cache

- LRU cache with configurable size (default: 1 system at a time)
- Automatic eviction of unused embeddings
- Garbage collection after cache eviction

### 3. Single Worker Configuration

- **Before**: Multiple workers = multiple copies of embeddings in memory
- **After**: Single worker process with worker recycling
- **Configuration**: `workers = 1` in `gunicorn.conf.py`

### 4. Memory Monitoring

- Real-time memory usage tracking
- Memory status API endpoint: `/api/memory-status`
- Cache clearing API: `/api/clear-cache`

## Deployment Configuration

### Updated Files

1. **`memory_optimized_embeddings.py`** - New lazy loading system
2. **`memory_optimized_search.py`** - Memory-efficient search
3. **`gunicorn.conf.py`** - Optimized Gunicorn configuration
4. **`start-optimized.sh`** - Memory-aware startup script
5. **`requirements-prod.txt`** - Added psutil for monitoring
6. **`app.py`** - Updated to use new memory-optimized system

### Render Configuration

Update your Render service to use:

```bash
# Build Command
pip install -r requirements-prod.txt

# Start Command
./start-optimized.sh
```

Or alternatively:

```bash
gunicorn -c gunicorn.conf.py app:app
```

### Environment Variables

Required environment variables remain the same:

- `OPENAI_API_KEY`
- `FLASK_SECRET_KEY`
- Any other existing variables

## Memory Usage Estimates

| Component      | Before      | After              |
| -------------- | ----------- | ------------------ |
| Startup Memory | ~200MB+     | ~20MB              |
| Dune System    | +111MB      | +111MB (on demand) |
| Mouse Guard    | +53MB       | +53MB (on demand)  |
| The One Ring   | +6.5MB      | +6.5MB (on demand) |
| **Total Peak** | **~370MB+** | **~130MB**         |

## Monitoring and Debugging

### Memory Status Endpoint

```bash
curl https://your-app.onrender.com/api/memory-status
```

Returns:

```json
{
  "memory_usage": {
    "rss_mb": 125.3,
    "vms_mb": 450.2,
    "percent": 24.5
  },
  "embedding_cache": {
    "cached_systems": ["dune"],
    "cache_size": 1,
    "max_cache_size": 1
  },
  "optimization_recommendations": ["Memory usage is acceptable"]
}
```

### Clear Cache (if needed)

```bash
curl -X POST https://your-app.onrender.com/api/clear-cache
```

### Log Monitoring

Watch for these log messages:

- `🧠 Memory-optimized embedding manager initialized`
- `🎯 Using cached [system] embeddings`
- `💾 Cached [system] embeddings in memory`
- `🧹 Evicting [system] embeddings from memory`

## Usage Patterns

### Single User/System

- Memory usage: ~100-150MB
- Only one TTRPG system loaded at a time
- Optimal for most use cases

### Multiple Systems

- Systems loaded on-demand
- LRU eviction prevents memory buildup
- Slight delay when switching between systems

## Troubleshooting

### If Memory Issues Persist

1. **Check cache size**: Reduce to 0 for minimal memory usage

   ```python
   embedding_manager = MemoryOptimizedEmbeddingManager(max_cache_size=0)
   ```

2. **Monitor via logs**: Look for eviction messages
3. **Use clear cache endpoint**: Manually clear cache between sessions
4. **Verify single worker**: Ensure `workers = 1` in configuration

### Performance vs Memory Trade-offs

- **More memory**: Increase `max_cache_size` to 2-3
- **Less memory**: Set `max_cache_size` to 0 (reload every time)
- **Balanced**: Keep default `max_cache_size = 1`

## Success Metrics

Your deployment should now:

- ✅ Start successfully within 512MB limit
- ✅ Handle TTRPG conversations without memory errors
- ✅ Automatically manage memory usage
- ✅ Provide memory monitoring capabilities
- ✅ Support all three TTRPG systems on demand

## Next Steps

1. Deploy with the new configuration
2. Monitor memory usage via the `/api/memory-status` endpoint
3. Adjust `max_cache_size` based on usage patterns
4. Consider upgrading Render plan if you need multiple concurrent systems

The optimization should reduce your memory footprint by **60-70%** while maintaining full functionality.
