from math_rag.application.containers import ApplicationContainer


def test_load_basic_settings(application_container: ApplicationContainer):
    # arrange
    em_settings_loader_service = application_container.em_settings_loader_service()

    # act
    basic_settings = em_settings_loader_service.load_basic_settings('default', 'default')
    basic_settings_openai = em_settings_loader_service.load_basic_settings(
        'openai', 'text-embedding-3-large'
    )

    # assert
    assert basic_settings.max_time == 60.0
    assert basic_settings.max_num_retries == 6

    assert basic_settings_openai.max_time == 60.0
    assert basic_settings_openai.max_num_retries == 6


def test_load_batch_settings(application_container: ApplicationContainer):
    # arrange
    em_settings_loader_service = application_container.em_settings_loader_service()

    # act
    batch_settings = em_settings_loader_service.load_batch_settings('default', 'default')

    batch_settings_openai = em_settings_loader_service.load_batch_settings(
        'openai', 'text-embedding-3-large'
    )

    # assert
    assert batch_settings.poll_interval == 300.0
    assert batch_settings.max_tokens_per_day is None
    assert batch_settings.max_num_retries == 0

    assert batch_settings_openai.poll_interval == 300.0
    assert batch_settings_openai.max_tokens_per_day == 20_000_000.0
    assert batch_settings_openai.max_num_retries == 0


def test_load_concurrent_settings(application_container: ApplicationContainer):
    # arrange
    em_settings_loader_service = application_container.em_settings_loader_service()

    # act
    concurrent_settings = em_settings_loader_service.load_concurrent_settings('default', 'default')

    concurrent_settings_openai = em_settings_loader_service.load_concurrent_settings(
        'openai', 'text-embedding-3-large'
    )

    # assert
    assert concurrent_settings.max_requests_per_minute is None
    assert concurrent_settings.max_tokens_per_minute is None
    assert concurrent_settings.max_num_retries == 3

    assert concurrent_settings_openai.max_requests_per_minute == 5_000.0
    assert concurrent_settings_openai.max_tokens_per_minute == 1_000_000.0
    assert concurrent_settings_openai.max_num_retries == 3
