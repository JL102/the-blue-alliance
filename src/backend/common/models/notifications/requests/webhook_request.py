import json

import logging
import requests

from backend.common.models.notifications.requests.request import Request
from typing import Optional
from urllib3.exceptions import MaxRetryError


WEBHOOK_VERSION = 1


class WebhookRequest(Request):
    """Represents a webhook notification payload.

    Attributes:
        notification (Notification): The Notification to send.
        url (string): The URL to send the notification payload to.
        secret (string): The secret to calculate the payload checksum with.
    """

    def __init__(self, notification, url, secret):
        """
        Args:
            notification (Notification): The Notification to send.
            url (string): The URL to send the notification payload to.
            secret (string): The secret to calculate the payload checksum with.
        """
        super(WebhookRequest, self).__init__(notification)

        self.url = url
        self.secret = secret

    def __str__(self) -> str:
        return "WebhookRequest(notification={} url={})".format(
            str(self.notification), self.url
        )

    def send(self) -> Optional[str]:
        """Attempt to send the notification."""
        # Build the request
        headers = {
            "Content-Type": 'application/json; charset=utf-8',
            "X-TBA-Version": "{}".format(WEBHOOK_VERSION),
        }
        payload = self._json_string()
        # This checksum is insecure and has been deprecated in favor of an HMAC
        headers["X-TBA-Checksum"] = self._generate_webhook_checksum(payload)
        # Generate hmac
        headers["X-TBA-HMAC"] = self._generate_webhook_hmac(payload)

        err = None

        try:
            response = requests.post(self.url, data=payload, headers=headers)
            logging.info(f'{response.status_code}, {requests.codes.ok}')
            if response.status_code == requests.codes.ok:
                self.defer_track_notification(1)
            else:
                logging.info(f'hello world, response code={response.status_code} and type={type(response.status_code)}, within400and500={400 <= response.status_code < 500} ')
                # Auto-raise a specific HTTPError, with message, depending on the status code
                response.raise_for_status()
                logging.info("This should not be reached with 404 status")
        except requests.exceptions.HTTPError as error:
            logging.info('Caught HTTPError')
            logging.error(error)
            err = str(error)
        except Exception as error:
            logging.info('Caught Exception')
            logging.error(error)
            err = f'Unknown error: {error}'
        except:
            logging.info('Caught non error')

        return err

    def _json_string(self) -> str:
        """JSON dict representation of an WebhookRequest object.

        JSON for WebhookRequest will look like...
        {
            "message_data": {...},
            "message_type": ...
        }

        Returns:
            dict: JSON representation of the WebhookRequest.
        """
        from backend.common.consts.notification_type import (
            TYPE_NAMES as NOTIFICATION_TYPE_NAMES,
        )

        json_dict = {
            "message_type": NOTIFICATION_TYPE_NAMES[self.notification.__class__._type()]
        }

        if self.notification.webhook_message_data:
            json_dict["message_data"] = self.notification.webhook_message_data

        return json.dumps(json_dict, ensure_ascii=True)

    # This checksum is insecure and has been deprecated in favor of an HMAC
    def _generate_webhook_checksum(self, payload):
        import hashlib

        ch = hashlib.sha1()
        ch.update(self.secret.encode("utf-8"))
        ch.update(payload.encode("utf-8"))
        return ch.hexdigest()

    def _generate_webhook_hmac(self, payload):
        import hashlib
        import hmac

        return hmac.new(
            self.secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
