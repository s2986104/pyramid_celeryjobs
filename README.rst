

design decision:
----------------
- assume some persistent result backend otherwise job tracking will get tricky
  TODO: we halso have a job object ... how to update that? on read? on beat?
        with completion event hooks?


Package to configure Celery and track tasks realiably
=====================================================

- configure celery from ini file
- configure celery worker with pyramid context from same ini file
  -> design decicsion: worker will always have a pyramid registry available
     if a worker does not need that, it does not need this package
     => maybe this pkg will provide some sort of disable pyramid integration
        to make celery worker configuration easier

TODO:
  - may need some way to configure celery beat as well, because we assume a
    db / cache result store which needs to be cleaned up by beat


Job model:
==========

- there will be a Job object in the database, which will keep track of submitted jobs
  and their state. Via this job object we can find out about who submitted a job when,
  and whether there should be an AsyncResult object for that.

TODO:
  - how does this job model get picked up by alembic?
    migrations will need to look at this as well (version pinning?)
  - this jobs table may grow very big ... we need some clean up here as well (beat?)
  - collect long term stats, which job, how often, how long, by whom
