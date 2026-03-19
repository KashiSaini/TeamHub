import logging
import time
import uuid


logger = logging.getLogger("teamhub.middleware")


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())

        response = self.get_response(request)

        response["X-Request-ID"] = request.request_id
        return response


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()

        response = self.get_response(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            user_info = f"{user.username} (id={user.id})"
        else:
            user_info = "anonymous"

        request_id = getattr(request, "request_id", "no-request-id")

        logger.info(
            "[%s] %s %s -> %s | user=%s | %.2f ms",
            request_id,
            request.method,
            request.path,
            response.status_code,
            user_info,
            duration_ms,
        )

        return response