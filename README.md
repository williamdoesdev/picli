# picli

A cli tool for sending ad-hoc requests to the PI Web API for Aveva/OSISoft's PI System. I made this for myself to use at work, maybe it'll be useful to someone else too.

```bash
pip install .
picli
```

# Commands

Just type commands followed by arguments to change request parameters. For example, the following changes the endpoint to use for requests:

```
url https://fqdn.com/piwebapi
```

Multiple commands can be strung together. For example:

```
type summary interval 1d start 1/1/1970 end 1/1/2020
```

Each of these commands will execute in sequence.

| Command | Use |
| ------- | --- |
| <Nothing, just press enter> | Executes query. |
| help | Lists all available commands. |
| login | Sets credentials to use for authentication. |
| logout | Clears stored credentials. |
| url | Sets the API base URL for the active query. |
| server | Sets the PI server for the active query. |
| type | Sets the query type for the active query. |
| start | Sets the start time for the active query. |
| end | Sets the end time for the active query. |
| tags set | Sets the tags for the active query. Can be comma, semicolon, or pipe separated. |
| tags add | Adds tags to the active query. Can be comma, semicolon, or pipe separated. |
| tags remove | Removes tags from the active query. Can be comma, semicolon, or pipe separated. |
| tags clear | Clears the tags for the active query. |
| timezone | Sets the timezone for the active query. |
| interval | Sets the interval for the active query. |
| bound | Sets the boundary type for the active query. |
| timecalc | Sets the timestamp calculation for the active query. |
| basis | Sets the calculation basis for the active query. |
| summary | Sets the summary type for the active query. |
| config show | Logs the current configuration. |
| config set debug_mode | Sets whether to output debug information. |
| config set tls_cert_path | Sets the path to the TLS certificate to use. |
| config set output_file_path | Sets the path to save output to. |
| config set request_fields_to_save | Sets the fields to save between sessions. |
| config set store_credentials | Sets whether to store credentials for future use. true/false |
| config set auth_method | Sets the authentication method for the PI Web API. basic/windows |

# Config

Config files are in ~/.config/picli or ~/AppData/Local/picli

A save file is also generated to store request parameters between sessions. This is in ~/.local/share/picli or ~/AppData/Local/picli