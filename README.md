# LookerMetadataExtractor

Intercepts and extracts metadata from saved Looker queries

## Quick Use

Install the package with the desired `<VERSION>` (e.g., `1.0.0` - check the GitHub releases for the latest stable version):

```
pip install looker_metadata_extractor @ git+https://github.com/CLDC-OU/LookerMetadataExtractor.git@<VERSION>
```

## Full Setup & Use

1. Set up a virtual environment

    ```
    python -m venv .venv
    .venv/bin/activate
    ```

2. Install the package, either with pip (as in [Quick Use](#quick-use)) or the following `requirements.txt`

    ```
    looker_metadata_extractor @ git+https://github.com/CLDC-OU/LookerMetadataExtractor.git@<VERSION>
    pyyaml
    python-dotenv
    ```

    ```
    pip install -r requirements.txt
    ```

3. Install playwright

    ```
    playwright install
    ```

4. (optional) Set up environmental variables in .env - only required for certain auth handlers

    ```
    LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME="username"
    LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD="password"
    ```

5. Create a configuration file (e.g., `config.yaml`) based on your Looker instance and desired extractors. See the [Configuration](#configuration) section for details

6. Create an instance of the LookerMetadataExtractor class with your configuration

    > [!NOTE]
    > See the example python scripts in the `examples/` directory for reference


    ```python
    from looker_metadata_extractor import LookerMetadataExtractor
    import yaml
    # Optional: load environment variables from .env file for auth handlers that require them
    from dotenv import load_dotenv
    load_dotenv()

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    extractor = LookerMetadataExtractor(**config)
    # Use the extract_metadata() method to begin the extraction process. If using a GeneralAuthHandler, you will need to log in manually for the extraction to proceed
    extractor.extract_metadata()
    # Use the save_extracted_data() method to save the extracted metadata to the configured output directory
    extractor.save_extracted_data()
    ```

## Environment Variables

- `LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME`: The username for authentication/login (only required for certain auth handlers)
- `LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD`: The password for authentication/login (only required for certain auth handlers)

## Configuration

> [!NOTE]
> See the example configuration files in the `examples/` directory for reference

Configuration is provided as a dictionary when instantiating the `LookerMetadataExtractor` class. The configuration includes the following top-level fields:

- `type`: The type of "navigator" to use. See [Navigator Types](#navigator-types)
- `context`: The context configuration. See [Context](#context)
- `auth`: The authentication configuration. See [Authentication](#authentication)
- `extractors`: A list of extractors to use for metadata extraction. See [Extractors](#extractors)

### Navigator Types

The navigator determines how the extractor will navigate the Looker instance. The available navigator types include:

- `handshake`: Navigator for Handshake (joinhandshake.com) Looker instances

### Context

Context is configured under the `context` key in the main configuration and includes the following fields:

- `headless`: Whether to run the browser in headless mode (headless = no UI) - this may introduce issues with automation detection on some sites
- `cookie_url`: The URL cookies are stored under
- (optional) `required_cookies`: A list of cookies required for the application to consider the session as being authenticated (typically a session id or similar. Anything that doesn't exist when not authenticated and does exist when authenticated). This can be left empty to skip cookie checking
- (optional) `reuse_context`: Whether to reuse the browser context (saves context between sessions in the `user_data_directory` directory)
- (optional) `user_data_directory`: The directory to store user data (cookies, local storage, etc.) when `reuse_context` is enabled
- (optional) `extract_timeout`: The base timeout (in milliseconds) for extraction operations. Can be overridden per-extractor
- (optional) `injectors`: A list of injectors to use for modifying the browser context. See [Injectors](#injectors)

#### Injectors

All injectors must specifiy a `type` field with the type of injector to use. The available injector types include:

- `flaresolverr`

##### FlareSolverr Injector

Required fields:

- `flaresolverr_url`: The URL of the FlareSolverr instance to use for solving Cloudflare challenges
- `cloudflare_challenge_url`: The URL that triggers the Cloudflare challenge

### Authentication

> [!NOTE]
> Auth configuration is still required if authentication is not needed. In this case, use the `none` authentication handler with no other fields

Authentication is configured under the `auth` key in the main configuration. The authentication configuration includes the following fields:

- (optional) `handler`: The type of authentication handler to use. Defaults to `general` for manual authentication. See [Authentication Handlers](#authentication-handlers)
- `auth_url`: The URL to the authentication/login page
- `successful_login_url`: The URL that indicates a successful login (i.e., the page you get sent to after logging in). Can include wildcards (`*` and `**`) for matching (e.g., `**/edu` for Handshake)

#### Authentication Handlers

Authentication handlers (other than `none`) will only authenticate if the `successful_login_url` is not detected when navigating to the `auth_url`. This allows for reuse of authenticated sessions when using `reuse_context`

The authentication handler determines how the extractor will authenticate with the Looker instance. The available authentication handler types include:

- `general`: A general authentication handler that requires manual login by the user
- `handshake`: An authentication handler for Handshake that automates the login process using provided credentials from environment variables - use with caution and ensure that credentials are stored securely
- `none`: No authentication handler. Assumes that the user is already authenticated. This includes context reuse with `reuse_context` enabled (after an initial manual login)

### Extractors

Each extractor in the `extractors` list is responsible for extracting metadata from a specific Looker report or dashboard. The extractor configuration includes the following fields:

- `url`: The URL of the Looker report or dashboard to extract metadata from
- `metadata_download_directory`: The base directory where the extracted metadata will be saved. The actual data will be saved in subdirectories based on the report or dashboard ID and the timestamp of the extraction
- `custom_timeout`: (optional) A custom timeout (in milliseconds) for this extractor, overriding the default timeout specified in the main configuration
- `extracts`: A list of extract types to extract from the Looker report or dashboard. See [Extract Types](#extract-types)

#### Extract Types

Each extract type defines a specific kind of metadata to extract from the Looker report or dashboard and any required parameters. The available extract types and their parameters include:

- `query`: Extracts the SQL query used in the Looker report (using the `/queries` endpoint)
- `explore`: Extracts the explore definition for the Looker report
    - `prefix`: A prefix to add to the explore name for the url endpoint (optional)
    - `explore_name`: The name of the explore to extract
- `model`: Extracts the model definition for the Looker report (using the `/models` endpoint)
