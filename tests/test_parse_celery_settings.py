import json

import pytest


def test_tuple():
    from pyramid_celeryjobs.app import _parse_celery_settings
    settings = {
        'broker_url': 'amqp://guest:guest@localhost:5672//',
        'imports': 'myapp.tasks'
    }
    _parse_celery_settings(settings)
    assert isinstance(settings['imports'], tuple)


def test_any():
    from pyramid_celeryjobs.app import _parse_celery_settings
    settings = {
        'task_annotations': json.dumps({'*': {'rate_limit': '10/s'}})
    }
    _parse_celery_settings(settings)
    assert isinstance(settings['task_annotations'], dict)


def test_dict():
    # test some dict parameter
    from pyramid_celeryjobs.app import _parse_celery_settings
    settings = {
        'task_queues': json.dumps({
            'cpubound': {
                'exchange': 'cpubound',
                'routing_key': 'cpubound',
            },
        })
    }
    _parse_celery_settings(settings)
    assert isinstance(settings['task_queues'], dict)


def test_ssl_bool():
    # test ssl settings true/false
    from pyramid_celeryjobs.app import _parse_celery_settings
    settings = {
        'broker_use_ssl': 'True'
    }
    _parse_celery_settings(settings)
    assert isinstance(settings['broker_use_ssl'], bool)


def test_ssl_dict():
    # test ssl settings as dict
    from pyramid_celeryjobs.app import _parse_celery_settings
    settings = {
        'broker_use_ssl': json.dumps({
            'keyfile': '/var/ssl/private/worker-key.pem',
            'certfile': '/var/ssl/amqp-server-cert.pem',
            'ca_certs': '/var/ssl/myca.pem',
            'cert_reqs': 'ssl.CERT_REQUIRED'
        })
    }
    _parse_celery_settings(settings)
    assert isinstance(settings['broker_use_ssl'], dict)
    from ssl import VerifyMode
    assert isinstance(settings['broker_use_ssl']['cert_reqs'], VerifyMode)


def test_unknown():
    # test unknown setting
    from pyramid_celeryjobs.app import _parse_celery_settings
    settings = {
        'task_whatever': 'fail'
    }
    with pytest.raises(KeyError):
        _parse_celery_settings(settings)


def test_beat_schedule():
    # test various variants to define a beat schedule
    from pyramid_celeryjobs.app import _parse_celery_settings
    settings = {
        'beat_schedule': json.dumps({
            'schedule': {
                'task': 'tasks.add',
                'schedule': 30.0,
                'args': (16, 16)
            },
            'crontab': {
                'task': 'tasks.add',
                'schedule': {
                    'factory': 'celery.schedules.crontab',
                    'kwargs': {
                        'hour': 7,
                        'minute': 30,
                        'day_of_week': 1
                    }
                }
            },
            'timedelta': {
                'task': 'tasks.add',
                'schedule': {
                    'factory': 'datetime.timedelta',
                    'args': [1, 10]
                }
            },
        })
    }
    _parse_celery_settings(settings)
    assert isinstance(settings['beat_schedule'], dict)
    assert isinstance(settings['beat_schedule']['schedule']['schedule'], float)
    from celery.schedules import crontab
    assert isinstance(settings['beat_schedule']['crontab']['schedule'], crontab)
    from datetime import timedelta
    assert isinstance(settings['beat_schedule']['timedelta']['schedule'], timedelta)
