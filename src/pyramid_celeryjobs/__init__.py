from .app import app, configure_celery


def configure(config, ini_location):
    configure_celery(ini_location)


def includeme(config):
    settings = config.get_settings()

    # Add CORS support
    config.include('pyramid_cors')
    config.add_cors_preflight_handler()

    # TODO: load models ... probably won't need it anyway
    # import pyramid_celeryjobs.models  # noqa
    config.add_directive("configure_celery", configure)
    config.include(".routes")
    config.scan()
