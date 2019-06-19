from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import Allow, ALL_PERMISSIONS

from . import models

ROLE_USER = "role:pyramid_celeryjob.user"
ROLE_ADMIN = "role:pyramid_celeryjob.admin"

VIEW = "view"


class JobListResource(object):

    __acl__ = ((Allow, ROLE_USER, VIEW), (Allow, ROLE_ADMIN, ALL_PERMISSIONS))


def joblist_factory(request):
    return JobListResource()


class JobResource(object):
    def __init__(self, dbjob):
        self.dbjob = dbjob

    @reify
    def __acl__(self):
        # TODO: self.acl should not be None :(
        return ((Allow, self.dbjob.owner, VIEW), (Allow, ROLE_ADMIN, ALL_PERMISSIONS))


def job_factory(request):
    # TODO: shall we include userid in query? -> return NotFound instead of denied
    uuid = request.matchdict["uuid"]
    dbjob = (
        request.dbsession.query(models.Job)
        .filter(models.Job.job_id == uuid)
        .one_or_none()
    )
    if dbjob is None:
        raise HTTPNotFound("No Job with uuid {}".format(uuid))
    return JobResource(dbjob)
