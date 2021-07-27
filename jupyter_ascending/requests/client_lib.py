from typing import TypeVar

import attr
from jsonrpcclient import request
from jsonrpcclient.exceptions import ReceivedNon2xxResponseError
from loguru import logger
from requests.exceptions import ConnectionError  # type: ignore

from jupyter_ascending._environment import EXECUTE_HOST_URL
from jupyter_ascending.handlers.server_extension import perform_notebook_request
from jupyter_ascending.json_requests import JsonBaseRequest

GenericJsonRequest = TypeVar("GenericJsonRequest", bound=JsonBaseRequest)


def request_notebook_command(json_request: GenericJsonRequest):
    """This is a command to be used by the client libraries to send a command to this server.

    It calls unpacks the JsonRequest and calls `perform_notebook_request` defined above."""
    try:
        result = request(
            EXECUTE_HOST_URL,
            perform_notebook_request.__name__,
            command_name=type(json_request).__name__,
            notebook_path=json_request.file_name,
            data=attr.asdict(json_request),
        )

        if not result.data.result:
            return

        if not result.data.result.get("success", True):
            raise Exception(f"Failed to complete request. {result.data}")

    except ConnectionError as e:
        logger.error(f"Unable to connect to server. Perhaps notebook is not running? {e}")
    except ReceivedNon2xxResponseError as e:
        logger.error(f"Unable to process request. Perhaps something else is running on this port? {e}")
