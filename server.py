from enum import Enum
from fastapi import FastAPI, status
from fastapi.routing import Scope
from pydantic import BaseModel
import secrets


app = FastAPI()

app.get("/health", status_code=status.HTTP_200_OK)


async def health():
    return {"service_name": "obliq", status: "up"}


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
    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)

    application_client: Application = Application(
        name=application.name,
        client_id=client_id,
        client_secret=client_secret,
        redirect_urls=application.redirect_urls,
        grant_types=application.grant_types,
        scope=application.scope,
        token_endpoint_auth_method=application.token_endpoint_auth_method,
    )

    database[application.name] = application

    return application_client


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="localhost", port=9999, reload=True)
