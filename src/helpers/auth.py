import json
from dataclasses import dataclass
from typing import Any, Optional

from litestar import post, Response, Request
from litestar.connection import ASGIConnection
from litestar.exceptions import HTTPException
from litestar.security.jwt import JWTAuth, Token


@dataclass
class User:
    email: str
    password: str
    activated: bool = False

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


async def retrieve_user_handler(token: Token, connection: "ASGIConnection[Any, Any, Any, Any]") -> Optional[User]:
    db = connection.app.stores.get("users")
    if db is None:
        return None

    user = await db.get(token.sub)
    json_str = user.decode('utf-8')
    user = User(**json.loads(json_str))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.activated:
        raise HTTPException(status_code=403, detail="User is not activated")

    return user


# Initialize JWT Authentication
jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="abcd123",
    exclude=["/login", "/schema"]
)


@post("/login")
async def login_handler(data: User, request: Request) -> Response[str] | Any:
    db = request.app.stores.get("users")
    byte_data = await db.get(data.email)
    json_str = byte_data.decode('utf-8')
    user = User(**json.loads(json_str))
    if user.email and user.password == data.password:
        auth_res = jwt_auth.login(identifier=str(data.email), send_token_as_response_body=True)
        return auth_res
    return Response({"error": "Invalid credentials"}, status_code=401)
