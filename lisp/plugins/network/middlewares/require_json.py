from falcon import (
    Request,
    HTTPUnsupportedMediaType,
)


class RequireJSONMiddleware:
    def process_resource(self, req: Request, *args) -> None:
        if req.method not in ("POST", "PUT", "PATCH"):
            return

        if "application/json" not in req.content_type:
            raise HTTPUnsupportedMediaType(
                description="Content-Type must be application/json"
            )
