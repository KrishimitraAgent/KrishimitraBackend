from pydantic import BaseModel
import requests


class CropPriceFilters(BaseModel):
    state: str = None
    district: str = None
    market: str = None
    variety: str = None
    grade: str = None
    offset: int = None
    limit: int = None


def call_price_api(filters: CropPriceFilters):
    """
    Simulate a call to a crop price API with the provided filters.
    Constructs a URL for a crop price API call based on the provided filters.
    If all filter values are None, it sends a GET URL with 'format' as a parameter.
    Otherwise, it adds present filters as query parameters.

    Args:
        filters: An instance of CropPriceFilters containing the desired filter values.

    Returns:
        A string representing the constructed API URL.
    """
    if isinstance(filters, dict):
        filters = CropPriceFilters(**filters)

    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {}

    # Check if all filter values are None
    # model_dump() is used to get a dictionary of the model's fields and their values
    all_none = True
    params["api-key"] = "579b464db66ec23bdd000001aba79f07780a439a665a7e0bb5f60996"
    params["format"] = "json" 
    for field_name, field_value in filters.model_dump(exclude_none=False).items():
        if field_value is not None:
            all_none = False
            break

    if all_none:
        pass
    else:
        # If any filter is present, add it as a parameter
        # model_dump(exclude_none=True) will only include fields that are not None
        for field_name, field_value in filters.model_dump(exclude_none=True).items():
            params["filters[" + field_name + "]"] = field_value

    # Construct the query string from the parameters
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    print(query_string)

    # Combine the base URL with the query string
    if query_string:
        try:
            print(f"Attempting to send GET request to: {base_url} with params: {params}")
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            print("Request successful!")
            # print(response.json())
            json_response = response.json()
            response_list = json_response['records']
            print(response_list)
            return response_list # Return the JSON response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Response text: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An unexpected error occurred: {req_err}")
        except ValueError: # Catches JSONDecodeError if response.json() fails
            print(f"Failed to decode JSON from response. Response text: {response.text}")
    else:
        return base_url
