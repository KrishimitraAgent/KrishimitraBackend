from pydantic import BaseModel
import requests
import pandas as pd
import os


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


def call_price_api_data(filters: CropPriceFilters):
    """
    Read crop price data from a local CSV file and apply filters.
    
    Args:
        filters: An instance of CropPriceFilters containing the desired filter values.
    
    Returns:
        A list of dictionaries representing the filtered crop price data.
    """
    if isinstance(filters, dict):
        filters = CropPriceFilters(**filters)
    
    csv_file_path = r"C:\Users\ASUS\Downloads\crop_price.csv"
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return []
    
    try:
        # Read the CSV file
        print(f"Reading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        # Apply filters
        filtered_df = df.copy()
        
        # Get the filter values, excluding None values
        filter_dict = filters.model_dump(exclude_none=True)
        
        if filter_dict:
            print(f"Applying filters: {filter_dict}")
            
            # Apply each filter
            for field_name, field_value in filter_dict.items():
                if field_name in ['offset', 'limit']:
                    continue  # Handle these separately
                
                if field_name in filtered_df.columns:
                    # Case-insensitive filtering for string columns
                    if filtered_df[field_name].dtype == 'object':
                        filtered_df = filtered_df[
                            filtered_df[field_name].str.contains(
                                str(field_value), 
                                case=False, 
                                na=False
                            )
                        ]
                    else:
                        filtered_df = filtered_df[filtered_df[field_name] == field_value]
                else:
                    print(f"Warning: Column '{field_name}' not found in Excel data")
        
        # Handle offset and limit for pagination
        total_records = len(filtered_df)
        
        if filters.offset is not None:
            filtered_df = filtered_df.iloc[filters.offset:]
        
        if filters.limit is not None:
            filtered_df = filtered_df.head(filters.limit)
        
        # Convert to list of dictionaries
        result = filtered_df.to_dict('records')
        
        print(f"Found {len(result)} records out of {total_records} total filtered records")
        print(f"Sample of filtered data: {result[:2] if result else 'No data found'}")
        
        return result
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    