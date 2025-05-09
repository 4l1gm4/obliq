from enum import Enum
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import secrets
from passlib.context import CryptContext
import uuid

app = FastAPI()
pass_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return {"service_name": "obliq", "status": "up"}


# register endpoint : allow an app to register in the database, get the clientid and clientsecr
database = {}


class TokenAuthMethod(str, Enum):
    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
    NONE = "none"


class ApplicationRegistrationRequest(BaseModel):
    name: str
    redirect_urls: list[str] | None = None
    grant_types: list[str]
    scope: str
    token_endpoint_auth_method: TokenAuthMethod


class ApplicationRegistrationResponse(BaseModel):
    client_id: str
    client_secret: str
    redirect_urls: list[str] | None


class Application(BaseModel):
    name: str
    client_id: str
    client_secret: str
    redirect_urls: list[str] | None
    grant_types: list[str]
    scope: str
    token_endpoint_auth_method: TokenAuthMethod


@app.post("/register")
async def register(application: ApplicationRegistrationRequest):

    # generate a clientid and client_secre
    client_id = str(uuid.uuid4())
    client_secret = pass_context.hash(secrets.token_urlsafe(32))

    application_client: Application = Application(
        name=application.name,
        client_id=client_id,
        client_secret=client_secret,
        redirect_urls=application.redirect_urls,
        grant_types=application.grant_types,
        scope=application.scope,
        token_endpoint_auth_method=application.token_endpoint_auth_method,
    )

    database[application.name] = application_client
    return application_client


@app.get("/applications")
async def get_all_applications():
    return database


@app.post("/token")
async def get_token(client_id: str, client_secret: str, grant_type: str):
    print(
        f"{client_id}, {client_secret}, grant_types:{grant_type}, {await is_app_exists(client_id, client_secret)}"
    )
    if grant_type == "client_credentials":
        if (
            not client_id
            or not client_secret
            or await is_app_exists(client_id, client_secret)
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
            )
    return "this is a dummy token"


async def is_app_exists(client_id: str, client_secret: str) -> bool:
    for app in database:
        if app["client_id"] == client_id and app["client_secret"] == client_secret:
            return True

    return False


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="localhost", port=9999, reload=True)
