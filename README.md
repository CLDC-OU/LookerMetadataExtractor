# LookerMetadataExtractor

Intercepts and extracts metadata from saved Looker queries

## Setup & Use

1. Set up a virtual environment

    ```
    python -m venv .venv
    .venv/bin/activate
    ```

2. Install the required dependencies

    ```
    pip install -r requirements.txt
    ```

3. Install playwright

    ```
    playwright install
    ```

4. Set up environmental variables in .env

    ```
    LOOKER_METADATA_EXTRACTOR_AUTH_USERNAME="username"
    LOOKER_METADATA_EXTRACTOR_AUTH_PASSWORD="password"
    ```

5. Create an instance of the LookerMetadataExtractor class with your configuration

    ```python
    from looker_metadata_extractor import LookerMetadataExtractor
    import yaml

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    extractor = LookerMetadataExtractor(**config)
    ```

6. Use the `extract_metadata()` method to begin the extraction process. If using a `GeneralAuthHandler`, you will need to log in manually for the extraction to proceed

    ```python
    extractor.extract_metadata()
    ```

7. Use the `save_extracted_data()` method to save the extracted metadata to the configured output directory

    ```python
    extractor.save_extracted_data()
    ```

## Configuration

- `type`: The type of "navigator" to use. Currently only supports `handshake`
- `auth_url`: The URL to the authentication/login page
- `successful_login_url`: The URL that indicates a successful login (i.e., the page you get sent to after logging in)
- `cookie_url`: The URL cookies are stored under
- `required_cookies`: A list of cookies required for the application to consider the session as being authenticated (typically a session id or similar. Anything that doesn't exist when not authenticated and does exist when authenticated)
- `headless`: Whether to run the browser in headless mode (headless = no UI)
- `reuse_context`: Whether to reuse the browser context (saves context between sessions in a `user_data` directory)
- `extractors`: A list of extractors to use for metadata extraction. See [Extractors](#extractors)

## Extractors

Each extractor in the `extractors` list is responsible for extracting metadata from a specific Looker report or dashboard. The extractor configuration includes the following fields:

- `url`: The URL of the Looker report or dashboard to extract metadata from
- `metadata_download_directory`: The base directory where the extracted metadata will be saved. The actual data will be saved in subdirectories based on the report or dashboard ID and the timestamp of the extraction
- `extracts`: A list of extract types to extract from the Looker report or dashboard. See [Extract Types](#extract-types)

## Extract Types

Each extract type defines a specific kind of metadata to extract from the Looker report or dashboard and any required parameters. The available extract types and their parameters include:

- `query`: Extracts the SQL query used in the Looker report (using the `/queries` endpoint)
- `explore`: Extracts the explore definition for the Looker report
    - `prefix`: A prefix to add to the explore name for the url endpoint (optional)
    - `explore_name`: The name of the explore to extract
- `model`: Extracts the model definition for the Looker report (using the `/models` endpoint)
