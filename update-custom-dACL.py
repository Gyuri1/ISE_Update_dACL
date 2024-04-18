import requests
from requests.auth import HTTPBasicAuth

# Disable warnings for unverified HTTPS requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# ISE Details - Replace with your ISE hostname/IP, ERS username, and password

ise_hostname = 'ise.company.com'
ers_username = 'ers_admin'
ers_password = 'ers_password'

# The word to append to each custom dACL name
append_word = '_custom'

# ISE ERS API URL for dACLs
dacls_url = f'https://{ise_hostname}:9060/ers/config/downloadableacl'

# Headers for the API request
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


ise_default_dacls = ['DENY_ALL_IPV4_TRAFFIC', 'DENY_ALL_IPV6_TRAFFIC', 'PERMIT_ALL_IPV4_TRAFFIC', 'PERMIT_ALL_IPV6_TRAFFIC']

debug = False

def update_dacl_name(dacl_id, current_name, new_name):
    print(f"dACl name: {current_name}, New name: {new_name}")
    get_url = f'{dacls_url}/{dacl_id}'
    get_response = requests.get(
        get_url,
        auth=HTTPBasicAuth(ers_username, ers_password),
        headers=headers,
        verify=False
    )
    get_response.raise_for_status()
   
    response_data = get_response.json()

    if debug:
        try:
            # Try to parse the response as JSON        
            print("Response JSON:")
            print(response_data)
        except ValueError:
            # If response is not JSON formatted, print the raw text
            print("Response Text:")
            print(get_response.text)

    update_url = f'{dacls_url}/{dacl_id}'


    response_data['DownloadableAcl']['name']= new_name 
    try:
        response = requests.put(
            update_url,
            auth=HTTPBasicAuth(ers_username, ers_password),
            headers=headers,
            json = response_data,
            verify=False
        )
        response.raise_for_status()
        print(f'Successfully updated dACL {current_name} to new name: {new_name}')
    except requests.exceptions.HTTPError as err:
        print(f'HTTP Error: {err}')
    except requests.exceptions.RequestException as e:
        print(f'Request Exception: {e}')
        


# Function to retrieve dACLs and update their names
def update_dacls():
    try:
        response = requests.get(
            dacls_url,
            auth=HTTPBasicAuth(ers_username, ers_password),
            headers=headers,
            verify=False  # Set to True if your ISE uses a valid SSL certificate
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        dacls = response.json()
        
        # Update the names of custom dACLs
        for dacl in dacls['SearchResult']['resources']:
            dacl_id = dacl['id']
            current_name = dacl['name']
            # Check if the dACL is custom based on a naming convention or criteria
            if current_name not in ise_default_dacls:  # built-in dACL ?
                new_name = f'{current_name}{append_word}'
                update_dacl_name(dacl_id, current_name, new_name)
    
    except requests.exceptions.HTTPError as err:
        print(f'HTTP Error: {err}')
    except requests.exceptions.RequestException as e:
        print(f'Request Exception: {e}')


# Main execution
if __name__ == '__main__':
    update_dacls()