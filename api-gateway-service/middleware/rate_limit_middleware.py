# from fastapi import FastAPI, Request, Response
# from starlette.middleware.base import BaseHTTPMiddleware

# app = FastAPI()
# limiter = AsyncTokenBucketManager(rate=2.0, capacity=10)

# class AsyncRateLimitMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         client_ip = request.client.host
        
#         # Here is the explicit usage of the async paradigm
#         is_allowed = await limiter.consume(client_ip)
        
#         if not is_allowed:
#             return Response(
#                 content="Rate limit exceeded. Your 'Dream-Chasing' is too fast.",
#                 status_code=429
#             )
        
#         # We MUST await the next layer of the onion
#         response = await call_next(request)
#         return response

# app.add_middleware(AsyncRateLimitMiddleware)