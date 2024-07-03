"""HTTP client for ice_cream_benelux."""

import logging
import time

import requests


class HTTPClient:
    """HTTP client for ice_cream_benelux."""

    def __init__(self, logger: logging.Logger) -> None:
        """Initialize the HTTP client."""
        self._logger = logger

    def request_with_retry(
        self,
        url: str,
        method: str = "GET",
        retries: int = 3,
        wait_time: int = 2,
        retry_statuses=None,
        retry_on_empty: bool = True,
        **kwargs,
    ) -> dict:
        """Retry a request.

        Parameters:
        ----------
        url : str
            The URL to send the request to.
        method : str, optional
            The HTTP method (default is 'GET').
        retries : int, optional
            Number of retries (default is 3).
        wait_time : int, optional
            Wait time between retries in seconds (default is 2).
        retry_statuses : list, optional
            List of status codes to retry on (default is None).
        retry_on_empty : bool, optional
            Whether to retry if response.text is empty (default is True).
        kwargs : dict
            Additional arguments passed to requests.request.

        Returns:
        -------
        dict
            The json response.

        """
        if retry_statuses is None:
            retry_statuses = []

        for attempt in range(retries):
            try:
                response = requests.request(method, url, timeout=5, **kwargs)
                if response.status_code in retry_statuses or (
                    retry_on_empty and not response.text
                ):
                    self._logger.debug(
                        "%s Attempt %d/%d failed with status %d or empty response. Retrying in %d seconds",
                        url,
                        attempt + 1,
                        retries,
                        response.status_code,
                        wait_time,
                    )
                    time.sleep(wait_time)
                else:
                    response.raise_for_status()  # Ensure the request was successful
                    return response.json()

            except requests.exceptions.HTTPError as http_err:
                self._logger.error(
                    "%s HTTP error occurred: %s. Attempt %d/%d. Retrying in %d seconds",
                    url,
                    str(http_err),
                    attempt + 1,
                    retries,
                    wait_time,
                )
                time.sleep(wait_time)

            except requests.exceptions.RequestException as req_err:
                self._logger.error(
                    "%s Error during request: %s. Attempt %d/%d. Retrying in %d seconds",
                    url,
                    str(req_err),
                    attempt + 1,
                    retries,
                    wait_time,
                )
                time.sleep(wait_time)

        return {}