import requests
from typing import Dict, Any, Optional, Union

class RestApiClient:
    """
    A simple REST API client that performs HTTP requests and returns JSON responses.
    """
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None) -> None:
        """
        Initializes the REST API client.

        Args:
            base_url (str): Base URL for the API endpoints.
            headers (Optional[Dict[str, str]]): Optional headers to include in each request.
        """
        self.base_url = base_url
        self.headers = headers or {}

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Union[Dict[str, Any], list]]:
        """
        Performs a GET request to the specified endpoint.

        Args:
            endpoint (str): API endpoint (relative or absolute) to call.
            params (Optional[Dict[str, Any]]): Query parameters for the request.

        Returns:
            Optional[Union[Dict[str, Any], list]]: Parsed JSON response if successful; otherwise, None.
        """
        url = self.base_url + endpoint
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"GET request failed for {url}: {e}")
            return None
        except ValueError:
            print("The response content is not valid JSON.")
            return None

    def post(self, endpoint: str, data: Optional[Any] = None, json_data: Optional[Dict[str, Any]] = None) -> Optional[Union[Dict[str, Any], list]]:
        """
        Performs a POST request to the specified endpoint.

        Args:
            endpoint (str): API endpoint (relative or absolute) to call.
            data (Optional[Any]): Data to send in the body of the request.
            json_data (Optional[Dict[str, Any]]): JSON data to send in the body of the request.

        Returns:
            Optional[Union[Dict[str, Any], list]]: Parsed JSON response if successful; otherwise, None.
        """
        url = self.base_url + endpoint
        try:
            response = requests.post(url, data=data, json=json_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"POST request failed for {url}: {e}")
            return None
        except ValueError:
            print("The response content is not valid JSON.")
            return None