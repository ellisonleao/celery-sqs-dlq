from celery.exceptions import Reject

from celery_sqs_dlq.celery import app


def dlq_task(**kwargs):
    retry_kwargs = kwargs.get("retry_kwargs", {})
    exceptions = kwargs.get("exceptions", ())

    def wraps(f):
        def wrapped_task(self, *args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exceptions as exc:
                if self.request.retries >= self.max_retries:
                    raise Reject(str(exc), requeue=False)
                raise exc
            except Exception as exc:
                raise Reject(str(exc), requeue=False)

        return app.task(retry_kwargs=retry_kwargs, autoretry_for=exceptions, bind=True)(
            wrapped_task
        )

    return wraps


@dlq_task(exceptions=(ZeroDivisionError,), retry_kwargs={"countdown": 1})
def should_retry():
    print("should raise zerodivision error, should retry until max retries")
    return 1 / 0


@dlq_task()
def should_not_retry():
    print("will raise unhandled exception, should not retry")
    raise Exception("unhandled exception")
