from django.core.cache import cache

class TestCache:
    def test_cache(self):
        value = 123
        cache.set('key', value)
        assert cache.get('key') == value