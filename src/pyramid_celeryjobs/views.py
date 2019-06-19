from pyramid.view import view_config

from . import models
from .resources import VIEW


def result_to_dict(result):
    # TODO: add job details endpoint where we include this (for admins)
    # import ipdb; ipdb.set_trace()
    # TODO: cane we get task name?
    #       no we can't :( ...
    #       maybe rethink info we get from here
    if result.ready():
        if result.failed:
            return {
                "state": result.state,
                "result": str(result.get(propagate=False)),
                "info": str(result.result),
            }
        else:
            return {
                "state": result.state,
                "result": result.get(),
                "info": result.result,
            }
    return {"state": result.state, "result": None, "info": result.result}


def job_to_dict(dbjob):
    return {
        "job_id": dbjob.job_id,
        "state": dbjob.state,
        "msg": dbjob.msg,
        # 'results': results
    }


@view_config(
    route_name="jobs",
    request_method="GET",
    renderer="json",
    cors=True,
    openapi=True,
    permission=VIEW,
)
def jobs_list(request):
    # TODO: ... I want some cut off here... don't show ancient jobs
    # TODO: ... maybe move listing jobs to resource?
    userid = request.authenticated_userid
    query = request.dbsession.query(models.Job).filter(models.Job.owner == userid)
    jobs = []
    for job in query:
        # results = [
        #     app.AsyncResult(task_id)
        #     for task_id in (job.task_ids or [])
        # ]
        # results = [
        #     result_to_dict(result)
        #     for result in results
        # ]
        jobs.append(job_to_dict(job))
    return jobs


@view_config(
    route_name="job",
    request_method="GET",
    renderer="json",
    cors=True,
    openapi=True,
    permission=VIEW,
)
def job_get(request):
    dbjob = request.context.dbjob
    return job_to_dict(dbjob)
