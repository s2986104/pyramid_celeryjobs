from . import resources


def includeme(config):
    config.add_route('job', '/jobs/{uuid}',
                     factory=resources.job_factory)
    config.add_route('jobs', '/jobs',
                     factory=resources.joblist_factory)
