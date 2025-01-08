import os
import django
import pytest
from testcontainers.postgres import PostgresContainer
from django.conf import settings
from django.core.management import call_command

# Ensure Django is initialized and settings are loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoTestContainer.settings')
django.setup()


@pytest.fixture(scope='session')
def django_db_container():
    """Create a PostgreSQL container for testing."""
    postgres_container = PostgresContainer(
        image="postgres:16-alpine",
        dbname=settings.DATABASES['default']['NAME'],
        username=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD']
    )

    with postgres_container as container:
        original_db_settings = settings.DATABASES['default'].copy()

        # Update Django database settings with container configuration
        settings.DATABASES['default'].update({
            'HOST': container.get_container_host_ip(),
            'PORT': container.get_exposed_port(5432),
        })

        yield container

        # Restore original database settings
        settings.DATABASES['default'] = original_db_settings


@pytest.fixture(scope='session')
def django_db_setup(django_db_container):
    """Set up the database for testing."""
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
    call_command('migrate')

