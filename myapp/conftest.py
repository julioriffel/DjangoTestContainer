import os

import django
import pytest
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

# Ensure Django is initialized and settings are loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoTestContainer.settings')
django.setup()


# Fixture para iniciar o contêiner do PostgreSQL
@pytest.fixture(scope="session")
def postgres_container():
    with  PostgresContainer(
            image="postgres:16-alpine",
            dbname=settings.DATABASES['default']['NAME'],
            username=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD']
    ) as postgres:
        postgres.start()
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:6") as redis:
        redis.start()
        yield redis


# Fixture para configurar o banco de dados Django para os testes
@pytest.fixture(scope="session")
def django_db_settings(postgres_container, redis_container):
    """
    Configura o Django para usar o banco de dados do contêiner PostgreSQL e o Redis.
    """
    host = postgres_container.get_container_host_ip()
    port = postgres_container.get_exposed_port(5432)
    redis_host = redis_container.get_container_host_ip()
    redis_port = redis_container.get_exposed_port(6379)

    return {
        'DATABASES': {
            'HOST': host,
            'PORT': port,
        },
        'CACHES': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{redis_host}:{redis_port}/1",
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',

            }
        },
    }


# Fixture do Django para setup inicial do banco de dados
@pytest.fixture(scope="session")
def django_db_setup(django_db_settings):
    print(django_db_settings)
    settings.DATABASES['default'].update(django_db_settings['DATABASES'])
    settings.CACHES['default'] = django_db_settings['CACHES']
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True

    call_command('migrate')
    return django_db_settings


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test."""
    cache.clear()
    yield
    cache.clear()
