import logging
import uuid

from .models import Job


# TODO: try catch task submit errors
# TODO: dbsessions in post commit hook?
# TODO: errors in db comm in post coomit?
def submit_task(request, task):
    def submit_task_hook(success):
        if not success:
            return
        result = task.apply_async()

    request.tm.get().addAfterCommitHook(submit_task_hook)


# TODO: test some concurrency stuff here
#       which status do I see here and which in inspect task?
#       any conflicts on update?
#       what if task is realy realy fast and updates dbfile first?
def submit_job(request, task):
    # TODO: check task result ignored?
    log = logging.getLogger(__name__)
    # return a new job object to track task
    # this will also schedule task to be submittedon transaction commit
    job_id = str(uuid.uuid1())
    userid = request.authenticated_userid
    job = Job(job_id=job_id, owner=userid)

    def submit_job_hook(success):
        # transaction commit hook to submit job to queue
        if not success:
            return
        # TODO: check success
        # TODO: try catch task submission in case message queue is down
        # TODO: potential problem when executing eagerly with transactions
        #       taks begins and commits a transaction
        #       and here we are in the middle of a transaction
        result = task.delay()
        log.info("Job {} submitted.".format(job_id))
        # we need to start a new transaction
        request.tm.begin()
        # add job to session
        request.dbsession.add(job)
        request.dbsession.refresh(job)  # make sure we have the latest state
        # update job.task_ids
        job.state = "SUBMITTED"
        job.task_ids = chain_task_ids(result)
        # TODO: try catch commit
        request.tm.commit()
        # we can't use job.job_id here, because transaction commit
        # closes the session (maybe expunge job from session?)
        log.info("Job {} state submitted.".format(job_id))

    request.dbsession.add(job)
    request.tm.get().addAfterCommitHook(submit_job_hook)
    return job

    # TODO: job.args etc....
    #       job category etc...


# TODO: move to utils module?
def chain_task_ids(result):
    ids = []
    while result:
        ids.append(result.id)
        result = result.parent
    ids.reverse()
    return ids
