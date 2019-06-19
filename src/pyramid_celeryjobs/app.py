import warnings

from celery import Celery, signals
from pyramid.paster import bootstrap
from pyramid.scripts.common import get_config_loader


app = Celery()


def add_worker_arguments(parser):
    parser.add_argument(
        '--ini', action='store', default=False,
        help='Point to pyramid ini file, or use # to point to a specific section with celery options.',
    ),
app.user_options['preload'].add(add_worker_arguments)
#app.user_options['worker'].add(add_worker_arguments)
#app.user_options['beat'].add(add_worker_arguments)


@signals.user_preload_options.connect
def handle_preload_options(options, **kwargs):
    # kwargs: app, sender, signal
    if options['ini']:
        configure_celery(options['ini'], kwargs['app'])


def configure_celery(settings, app=app):
    # settings may be string to an ini file
    # or a dictionary. It acceppts paster config uris, where
    # a URI fragment may reference an ini section. Otherwise look
    # for a section named 'celery'
    if not isinstance(settings, dict):
        loader = get_config_loader(settings)
        settings = loader.get_settings()
        if not settings:
            # try 'celery' section
            settings.update(loader.get_settings('celery'))
    # type conversion
    from celery.app.defaults import NAMESPACES
    for key, val in settings.items():
        # TODO: look into supporting tuple / dict options here as well
        #       and non-namespaced options like include / import
        ns, name = key.split('_', 1)
        val = NAMESPACES[ns.lower()][name.lower()].to_python(val)
        settings[key] = val
    # apply config
    app.conf.update(settings)


@signals.celeryd_init.connect
def on_celeryd_init(sender, instance, conf, options, **kwargs):
    """Configure Pyramid application.
    This event is triggered after a worker instance completes basic setup,
    but before it processes any tasks.
    """
    # global _PYRAMID_REGISTRY, _PYRAMID_CLOSER
    try:
        if 'ini' in options:
            if conf.get('PYRAMID_REGISTRY') is not None:
                warnings.warn('Can not initialise celery multiple times')
            # bootstrap pyramid app
            env = bootstrap(options['ini'])
            conf['PYRAMID_REGISTRY'] = env['registry']
            conf['PYRAMID_CLOSER'] = env['closer']
            # _PYRAMID_REGISTRY = env['registry']
            # _PYRAMID_CLOSER = env['closer']
    except Exception as e:
        warnings.warn('Error initialising Pyramid: {}'.format(e))


# TODO: the following signals would be nice to have to setup a pyramid
#       context before task run and to automatically manage transactions
#       for running tasks in a pyramid context.
#       however, we want to have tasks that don't need a pyramid context
#       so we would need to filter these signals somehow for tasks
#       that need or don't need a pyramid context set up.
# import transaction
# from pyramid.scripting import prepare
# @signals.task_prerun.connect
# def on_task_prerun(task_id, task, args, **kwargs):
#     """Setup Pyramid environment for a task.
#     This event is triggered before a task is executed by the Celery worker. A
#     Pyramid context is setup to make it appear as if the task is run in a
#     request context.
#     """
#     #     # This also get's called on eager tasks
#     # import ipdb; ipdb.set_trace()
#     #from celery.contrib import rdb; rdb.set_trace()
#     # prepare(registry=_PYRAMID_REGISTRY)
#     #prepare(registry=task.app.conf['PYRAMID_REGISTRY'])
#     #transaction.begin()


# @signals.task_success.connect
# def on_task_success(**kw):
#     """Commit transaction on task success.
#     This event is triggered when a task completes successfully.
#     """
#     from celery.contrib import rdb; rdb.set_trace()
#     transaction.commit()


# args, einfo, exception, kwargs, sender, signal, task_id, traceback
# @signals.task_retry.connect
# @signals.task_failure.connect
# @signals.task_revoked.connect
# def on_task_failure(**kw):
#     """Abort transaction on task errors.
#     """
#     from celery.contrib import rdb; rdb.set_trace()
#     transaction.abort()


# args, kwargs, retval, sender, signal, state, task, task_id
# @signals.task_postrun.connect
# def on_task_postrun(**kw):
#     """End the Pyramid request context.
#     This event is triggered after a task finishes running.
#     """
#     # This also get's called on eager tasks
#     import ipdb; idpb.set_trace()
#     #from celery.contrib import rdb; rdb.set_trace()
#     #_PYRAMID_CLOSER()

