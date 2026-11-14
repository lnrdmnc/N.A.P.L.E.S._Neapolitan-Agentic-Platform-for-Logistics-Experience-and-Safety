"""Router index: a new route file is registered by adding one line here.

agents_proxy stays last: it forwards every /api/* path not matched above.
"""

from app.routes import agents_proxy, events, health

ROUTERS = [
    health.router,
    events.router,
    agents_proxy.router,
]
