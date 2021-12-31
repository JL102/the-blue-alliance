from typing import Optional

import requests

from backend.common.models.keys import Year
from backend.common.sitevars.fms_api_secrets import FMSApiSecrets


class FRCAPI:
    class ValidationError(Exception):
        pass

    @classmethod
    def with_credentials(cls, username: str, authkey: str):
        auth_token = FMSApiSecrets.generate_auth_token(username, authkey)
        return cls(auth_token)

    def __init__(self, auth_token: Optional[str] = None):
        # Load auth_token from Sitevar if not specified
        if not auth_token:
            auth_token = FMSApiSecrets.auth_token()

        if not auth_token:
            raise Exception(
                f"Missing FRC API auth token. Setup {FMSApiSecrets.key()} sitevar."
            )

        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Basic {auth_token}"})

    def root(self) -> requests.Response:
        return self._get("/")

    def event_list(self, year: Year) -> requests.Response:
        endpoint = f"/{year}/events"
        return self._get(endpoint)

    def event_info(self, year: Year, event_short: str) -> requests.Response:
        endpoint = f"/{year}/events?eventCode={event_short}"
        return self._get(endpoint)

    def event_teams(self, year: Year, event_short: str, page: int) -> requests.Response:
        endpoint = f"/{year}/teams?eventCode={event_short}&page={page}"
        return self._get(endpoint)

    def event_team_avatars(
        self, year: Year, event_short: str, page: int
    ) -> requests.Response:
        endpoint = f"/{year}/avatars?eventCode={event_short}&page={page}"
        return self._get(endpoint)

    def awards(
        self,
        year: int,
        event_code: Optional[str] = None,
        team_number: Optional[int] = None,
    ) -> requests.Response:
        if not event_code and not team_number:
            raise FRCAPI.ValidationError(
                "awards expects either an event_code, team_number, or both"
            )

        # Work around a bug with the v3.0 awards endpoint where teamNumber is non-optional.
        # Passing a `0` will get us all awards for an Event
        # https://usfirst.collab.net/sf/go/artf6025
        if event_code is not None and team_number is None:
            team_number = 0

        if event_code is not None and team_number is not None:
            endpoint = f"/{year}/awards/{event_code}/{team_number}"
        else:
            endpoint = f"/{year}/awards/{event_code or team_number}"

        return self._get(endpoint)

    def district_list(self, year: Year) -> requests.Response:
        endpoint = f"/{year}/districts"
        return self._get(endpoint)

    """ Attempt to fetch the endpoint from the FRC API

        Returns:
            The Flask response object - should be used by the consumer.
    """

    def _get(self, endpoint: str) -> requests.Response:
        # Remove any leading / - we'll add it later (safer then adding a slash)
        endpoint = endpoint.lstrip("/")

        url = f"https://frc-api.firstinspires.org/v3.0/{endpoint}"
        headers = {
            "Accept": "application/json",
            "Cache-Control": "no-cache, max-age=10",
            "Pragma": "no-cache",
        }

        return self.session.get(url, headers=headers)
