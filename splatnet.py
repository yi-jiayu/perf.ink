import base64
import hashlib
import secrets
import urllib.parse
from enum import Enum
from typing import Literal, Optional, TypedDict

import httpx
import structlog
import typer

logger = structlog.get_logger()

nsoapp_version = "2.3.1"
splatnet3_version = "1.0.0-5644e7a2"
app_user_agent = "woomy_bot/2.0.0"
browser_user_agent = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
)


class SplatnetQuery(Enum):
    COOP_RESULT = "a5692cf290ffb26f14f0f7b6e5023b07"
    COOP_HISTORY_DETAIL = "f3799a033f0a7ad4b1b396f9a3bafb1e"
    SCHEDULE = "10e1d424391e78d21670227550b3509f"


def _sha256(s: str):
    """Returns a URL-safe base64-encoded SHA256 hash of the given string without padding."""
    return (
        base64.urlsafe_b64encode(hashlib.sha256(s.encode()).digest())
        .decode()
        .rstrip("=")
    )


def request_session_token(client):
    state = secrets.token_urlsafe(32)
    session_token_code_verifier = secrets.token_urlsafe(32)
    session_token_code_challenge = _sha256(session_token_code_verifier)

    headers = {
        "User-Agent": browser_user_agent,
    }

    params = {
        "state": state,
        "redirect_uri": "npf71b963c1b7b6d119://auth",
        "client_id": "71b963c1b7b6d119",
        "scope": "openid user user.birthday user.mii user.screenName",
        "response_type": "session_token_code",
        "session_token_code_challenge": session_token_code_challenge,
        "session_token_code_challenge_method": "S256",
        "theme": "login_form",
    }

    response = client.get(
        url="https://accounts.nintendo.com/connect/1.0.0/authorize",
        headers=headers,
        params=params,
        follow_redirects=False,
    )
    return session_token_code_verifier, response.headers["location"]


def get_session_token(client, url: str, session_token_code_verifier: str):
    parsed_url = urllib.parse.urlsplit(url)
    parsed_url_query = urllib.parse.parse_qs(parsed_url.fragment)
    session_token_code = parsed_url_query["session_token_code"][0]

    headers = {
        "User-Agent": "OnlineLounge/" + nsoapp_version + " NASDKAPI Android",
    }
    body = {
        "client_id": "71b963c1b7b6d119",
        "session_token_code": session_token_code,
        "session_token_code_verifier": session_token_code_verifier,
    }

    response = client.post(
        url="https://accounts.nintendo.com/connect/1.0.0/api/session_token",
        headers=headers,
        data=body,
    )
    return response.json()["session_token"]


class NintendoToken(TypedDict):
    access_token: str
    id_token: str


def _get_nintendo_token(client: httpx.Client, session_token: str) -> NintendoToken:
    headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2)"}
    body = {
        "client_id": "71b963c1b7b6d119",
        "session_token": session_token,
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
    }
    response = client.post(
        url="https://accounts.nintendo.com/connect/1.0.0/api/token",
        headers=headers,
        json=body,
    )
    response.raise_for_status()
    return response.json()


class UserInfo(TypedDict):
    nickname: str
    language: str
    country: str
    birthday: str


def _get_user_info(client, access_token: str) -> UserInfo:
    headers = {
        "User-Agent": "NASDKAPI; Android",
        "authorization": "Bearer " + access_token,
    }
    user_response = client.get(
        url="https://api.accounts.nintendo.com/2.0.0/users/me",
        headers=headers,
    )
    return user_response.json()


def _get_f_token(client: httpx.Client, id_token: str, step: Literal[1, 2]):
    headers = {
        "User-Agent": app_user_agent,
    }
    body = {"token": id_token, "hashMethod": step}
    response = client.post(
        url="https://api.imink.app/f",
        headers=headers,
        json=body,
    )
    response.raise_for_status()
    data = response.json()
    f = data["f"]
    uuid = data["request_id"]
    timestamp = data["timestamp"]
    return f, uuid, timestamp


def _get_nso_access_token(client: httpx.Client, id_token: str, user: UserInfo) -> str:
    f, uuid, timestamp = _get_f_token(client, id_token, 1)
    body = {
        "parameter": {
            "f": f,
            "language": user["language"],
            "naBirthday": user["birthday"],
            "naCountry": user["country"],
            "naIdToken": id_token,
            "requestId": uuid,
            "timestamp": timestamp,
        }
    }

    headers = {
        "X-Platform": "Android",
        "X-ProductVersion": nsoapp_version,
        "User-Agent": "com.nintendo.znca/" + nsoapp_version + "(Android/7.1.2)",
    }

    response = client.post(
        url="https://api-lp1.znc.srv.nintendo.net/v3/Account/Login",
        headers=headers,
        json=body,
    )
    response.raise_for_status()
    data = response.json()
    return data["result"]["webApiServerCredential"]["accessToken"]


def _get_web_service_token(client: httpx.Client, nso_access_token: str) -> str:
    f, uuid, timestamp = _get_f_token(client, nso_access_token, 2)
    headers = {
        "X-Platform": "Android",
        "X-ProductVersion": nsoapp_version,
        "Authorization": f"Bearer {nso_access_token}",
        "User-Agent": "com.nintendo.znca/" + nsoapp_version + "(Android/7.1.2)",
    }
    body = {
        "parameter": {
            "f": f,
            "id": 4834290508791808,
            "registrationToken": nso_access_token,
            "requestId": uuid,
            "timestamp": timestamp,
        }
    }
    response = client.post(
        url="https://api-lp1.znc.srv.nintendo.net/v2/Game/GetWebServiceToken",
        headers=headers,
        json=body,
    )
    response.raise_for_status()
    data = response.json()
    return data["result"]["accessToken"]


def _get_bullet_token(client: httpx.Client, web_service_token: str, user: UserInfo):
    headers = {
        "Content-Type": "application/json",
        "Accept-Language": user["language"],
        "User-Agent": browser_user_agent,
        "X-Web-View-Ver": splatnet3_version,
        "X-NACOUNTRY": user["country"],
        "Origin": "https://api.lp1.av5ja.srv.nintendo.net",
        "X-Requested-With": "com.nintendo.znca",
    }
    cookies = {"_gtoken": web_service_token}
    response = client.post(
        url="https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens",
        headers=headers,
        cookies=cookies,
    )
    response.raise_for_status()
    data = response.json()
    return data["bulletToken"]


def _graphql(
    client: httpx.Client,
    bullet_token: str,
    query: SplatnetQuery,
    variables: dict | None = None,
):
    headers = {
        "authorization": f"Bearer {bullet_token}",
        "user_agent": browser_user_agent,
        "X-Web-View-Ver": splatnet3_version,
    }
    body = {
        "variables": variables or {},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": query.value,
            }
        },
    }
    response = client.post(
        url="https://api.lp1.av5ja.srv.nintendo.net/api/graphql",
        headers=headers,
        json=body,
    )
    response.raise_for_status()
    return response.json()


def get_schedule(client: httpx.Client, bullet_token: str):
    return _graphql(client, bullet_token, SplatnetQuery.SCHEDULE)


def get_salmon_run_jobs(client: httpx.Client, bullet_token: str):
    return _graphql(client, bullet_token, SplatnetQuery.COOP_RESULT)


def get_salmon_run_job_detail(client: httpx.Client, bullet_token: str, shift_id: str):
    return _graphql(
        client,
        bullet_token,
        SplatnetQuery.COOP_HISTORY_DETAIL,
        {"coopHistoryDetailId": shift_id},
    )


def get_splatnet_session(
    client: httpx.Client, nintendo_session_token: str
) -> tuple[str, str]:
    nintendo_token = _get_nintendo_token(client, nintendo_session_token)
    user = _get_user_info(client, nintendo_token["access_token"])
    nso_access_token = _get_nso_access_token(
        client, nintendo_token["access_token"], user
    )
    web_service_token = _get_web_service_token(client, nso_access_token)
    bullet_token = _get_bullet_token(client, web_service_token, user)
    return web_service_token, bullet_token


def main(
    session_token_file: Optional[typer.FileText] = typer.Option(None),
    proxy: Optional[str] = typer.Option(None),
    proxy_cert: Optional[str] = typer.Option(None),
):
    client_args = {}
    if proxy:
        client_args["proxies"] = {"all://": proxy}
    if proxy_cert:
        client_args["verify"] = proxy_cert
    with httpx.Client(**client_args) as client:
        if not session_token_file:
            verifier, sign_in_url = request_session_token(client)
            session_token_url = input("Session token URL: ")
            session_token = get_session_token(client, session_token_url, verifier)
        else:
            session_token = session_token_file.read()
        nintendo_token = _get_nintendo_token(client, session_token)
        logger.info("got nintendo token", value=nintendo_token)
        user = _get_user_info(client, nintendo_token["access_token"])
        logger.debug("got user info", value=user)
        nso_access_token = _get_nso_access_token(
            client, nintendo_token["access_token"], user
        )
        logger.info("got nso access token", value=nso_access_token)
        web_service_token = _get_web_service_token(client, nso_access_token)
        logger.info("got web service token", value=web_service_token)
        bullet_token = _get_bullet_token(client, web_service_token, user)
        logger.info("got bullet token", value=bullet_token)


if __name__ == "__main__":
    typer.run(main)
