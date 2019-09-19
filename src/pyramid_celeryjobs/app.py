import json
import warnings

from celery import Celery, signals
from celery.app.defaults import NAMESPACES
from pyramid.paster import bootstrap
from pyramid.scripts.common import get_config_loader
from pyramid.util import DottedNameResolver


app = Celery()


def add_worker_arguments(parser):
    parser.add_argument(
        "--ini",
        action="store",
        default=False,
        help="Point to pyramid ini file, or use # to point to a specific section with celery options.",
    )


app.user_options["preload"].add(add_worker_arguments)


@signals.user_preload_options.connect
def handle_preload_options(options, **kwargs):
    # kwargs: app, sender, signal
    if options["ini"]:
        configure_celery(options["ini"], kwargs["app"])


def _parse_use_ssl(opt, val):
    # TODO: return True / False / or parsed json
    try:
        return opt.to_python(val)
    except TypeError:
        # it is not a valid bool string
        pass
    # still here? ... try json decode and return a dict
    ret = json.loads(val)
    ret['cert_reqs'] = DottedNameResolver().resolve(ret['cert_reqs'])
    return ret


def _parse_schedule(opt, val):
    resolver = DottedNameResolver()
    val = json.loads(val)
    for key, entry in val.items():
        if isinstance(entry['schedule'], dict):
            schedule = resolver.resolve(entry['schedule']['factory'])(
                *entry['schedule'].get('args', ()),
                **entry['schedule'].get('kwargs', {})
            )
        else:
            schedule = float(entry['schedule'])
        entry['schedule'] = schedule
    return val


def _parse_ini_val(opt, val):
    # parses a string coming from ini file with a celery option into a python
    # data type
    # TODO: exception handlig / throwing / validation?
    if opt.type == 'tuple':
        return tuple(v.strip() for v in val.split('\n') if v.strip())
    if opt.type in ('dict', 'any'):
        # TODO: parse types?
        #       e.g. schedule vs crontab?
        val = json.loads(val)
        for item in val.values():
            item.pop('crontab', None)
        return val
    return opt.to_python(val)


def _parse_celery_settings(settings):
    # parse celery settings and update values in settings dict (also return it)
    # settings comes directly from an ini file. It is a dictionary with keys to string.
    # dictionaries are json encoded and lists/tuples are new line separated.

    PARSER = {
        ('broker', 'use_ssl'): _parse_use_ssl,
        ('beat', 'schedule'): _parse_schedule,
    }

    for key, val in settings.items():
        if key.lower() in NAMESPACES:
            # no split required
            val = _parse_ini_val(NAMESPACES[key.lower()], val)
        else:
            ns, name = key.split("_", 1)
            parse_func = PARSER.get((ns.lower(), name.lower()), _parse_ini_val)
            val = parse_func(
                NAMESPACES[ns.lower()][name.lower()],
                val
            )
        settings[key] = val
    return settings


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
            settings.update(loader.get_settings("celery"))
    # type conversion
    _parse_celery_settings(settings)
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
        if "ini" in options:
            if conf.get("PYRAMID_REGISTRY") is not None:
                warnings.warn("Can not initialise celery multiple times")
            # bootstrap pyramid app
            env = bootstrap(options["ini"])
            conf["PYRAMID_REGISTRY"] = env["registry"]
            conf["PYRAMID_CLOSER"] = env["closer"]
            # _PYRAMID_REGISTRY = env['registry']
            # _PYRAMID_CLOSER = env['closer']
    except Exception as e:
        warnings.warn("Error initialising Pyramid: {}".format(e))


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
