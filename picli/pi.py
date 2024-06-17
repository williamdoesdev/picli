from requests import get, post
from requests.auth import HTTPBasicAuth
from requests.exceptions import SSLError

from picli.config import tls_cert_path, auth_method, AuthMethod
from picli.credentials import username, password
from picli.commands import register_command
from picli.errors import PICLIValidationError, PICLIWebAPIError
from picli.log import info, debug
from picli.query import active_query, Query

results = []

def execute_query() -> list[dict]:
    '''Executes a query against the PI Web API.'''
    global results
    info('Executing query')
    server_web_id = _get_server_web_id()
    tag_web_ids = _get_tag_web_ids(server_web_id)
    results = _get_recorded_values(tag_web_ids)
    info('Query executed successfully.')
register_command(execute_query, [''])

def _get_server_web_id() -> str:
    info(f'Getting Web ID for server {active_query.pi_server} from PI Web API.')
    debug(f'TLS Cert Path: {tls_cert_path}')
    try:
        response = get(
            f'{active_query.api_base_url}/dataservers?name={active_query.pi_server}', 
            auth=_get_auth(),
            verify=tls_cert_path
        )
    except SSLError:
        raise PICLIWebAPIError(f'TLS issue while connecting to PI Web API.')
    debug(f'Request URL: {response.url}')
    debug(f'Response Status Code: {response.status_code}')
    debug(f'Response Content: {response.text}')
    
    if response.status_code != 200:
        raise PICLIWebAPIError(f'Error getting Web ID for {active_query.pi_server}. Likely incorrect server name.')
    
    web_id = response.json().get('WebId')
    if web_id is None:
        raise PICLIWebAPIError(f'Error getting Web ID for {active_query.pi_server}. Response was good, but did not contain Web ID.')
    
    return web_id

def _get_tag_web_ids(server_web_id: str) -> dict[str, str]:
    info(f'Getting Web IDs for tags {active_query.tags} from PI Web API')
    body = {}
    for tag in active_query.tags:
        body[tag] = {
            'Method': 'GET',
            'Resource': f'{active_query.api_base_url}/points/search?dataServerWebId={server_web_id}&query=tag:"{tag}"'
        }
    headers = {
        'X-Requested-With': ''
    }
    response = post(
        f'{active_query.api_base_url}/batch', 
        json=body, 
        auth=_get_auth(), 
        headers=headers,
        verify=tls_cert_path
    )
    debug(f'Request URL: {response.url}')
    debug(f'Request Body: {response.request.body}')
    debug(f'Response Status Code: {response.status_code}')
    debug(f'Response Content: {response.text}')
    
    if response.status_code != 207:
        raise PICLIWebAPIError(f'Error getting Web IDs for tags.')
    
    web_ids = {}
    for tag, tag_info in response.json().items():
        if tag_info.get('Status') != 200:
            raise PICLIWebAPIError(f'Error getting Web ID for tag {tag}. Likely incorrect tag name.')
        web_id = tag_info.get('Content').get('Items')[0].get('WebId')
        if web_id is None:
            raise PICLIWebAPIError(f'Error getting Web ID for tag {tag}. Response was good, but did not contain Web ID.')
        web_ids[tag] = web_id

    return web_ids

def _get_recorded_values(tag_web_ids: dict[str, str]) -> list[dict]:
    info(f'Getting recorded values for tags {active_query.tags} from PI Web API.')
    body = {}
    for tag, web_id in tag_web_ids.items():
        body[tag] = {
            'Method': 'GET',
            'Resource': f'{active_query.api_base_url}/streams/{web_id}/recorded?startTime={active_query.start_time}&endTime={active_query.end_time}&boundaryType={active_query.boundary_type.value}&timeZone={active_query.timezone}'
        }
    headers = {
        'X-Requested-With': ''
    }
    response = post(
        f'{active_query.api_base_url}/batch', 
        json=body, 
        auth=_get_auth(), 
        headers=headers,
        verify=tls_cert_path
    )
    debug(f'Request URL: {response.url}')
    debug(f'Response Status Code: {response.status_code}')
    debug(f'Response Content: {response.text}')

    if response.status_code != 207:
        raise PICLIWebAPIError(f'Error getting recorded values for tags {active_query.tags}.')
    
    recorded_values = []
    for tag, tag_info in response.json().items():
        if tag_info.get('Status') != 200:
            raise PICLIWebAPIError(f'Error getting recorded values for tag {tag}. Likely incorrect tag name.')
        for value in tag_info.get('Content').get('Items'):
            recorded_values.append({
                'Tag': tag,
                'Timestamp': value.get('Timestamp'),
                'Value': value.get('Value'),
                'Good': value.get('Good'),
                'Questionable': value.get('Questionable'),
                'Substituted': value.get('Substituted')
            })

    return recorded_values

def _get_auth():
    debug('Getting authentication method')
    debug(f'Auth method: {auth_method}')
    if auth_method == AuthMethod.BASIC:
        debug('Using basic authentication')
        debug(f'Username: {username}')
        debug(f'Password: {password}')
        return HTTPBasicAuth(username, password)
    elif auth_method == AuthMethod.NTLM:
        raise NotImplementedError('Windows authentication not yet implemented.')
    else:
        raise PICLIValidationError(f'Unsupported authentication method: {auth_method}.')