import django
import pytest
from django.conf import settings
from django.core.management import call_command
from testcontainers.postgres import PostgresContainer


def pytest_configure():
    """Configure Django settings for tests."""
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                # These will be overridden by the container config
                'NAME': 'test_db',
                'USER': 'test_user',
                'PASSWORD': 'test_password',
                'HOST': 'localhost',
                'PORT': '5432',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'myapp',  # Add your app here
            # Add other Django apps as needed
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        SECRET_KEY='test_key_not_for_production',
        DEBUG=True,
        USE_TZ=True,
        TIME_ZONE='UTC',
        ROOT_URLCONF='myapp.urls',  # Add your URL configuration
    )

    # Initialize Django
    django.setup()


@pytest.fixture(scope='session')
def django_db_container():
    """Create a PostgreSQL container for testing."""
    postgres_container = PostgresContainer(
        image="postgres:16-alpine",
        dbname="test_db",
        username="test_user",
        password="test_password"
    )
    with postgres_container as container:
        # Update Django database settings with container configuration
        settings.DATABASES['default'].update({
            'HOST': container.get_container_host_ip(),
            'PORT': container.get_exposed_port(5432),
        })
        yield container


@pytest.fixture(scope='session')
def django_db_setup(django_db_container):
    """Set up the database for testing."""
    settings.DATABASES['default']['ATOMIC_REQUESTS'] = True
    call_command('migrate')


@pytest.fixture(scope='session')
def celery_config():
    """Configure Celery for testing if needed."""
    return {
        'broker_url': 'memory://',
        'result_backend': 'db+sqlite:///results.sqlite',
        'task_always_eager': True,
        'task_eager_propagates': True,
    }


@pytest.fixture
def authenticated_client(client, django_user_model):
    """Create an authenticated client for testing."""
    user = django_user_model.objects.create_user(
        username='testuser',
        password='testpass123'
    )
    client.login(username='testuser', password='testpass123')
    return client
