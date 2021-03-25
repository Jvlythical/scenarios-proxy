# Scenarios Proxy

Mock API and/or proxy for a HTTP service. Uses scenarios-backend to retrieve mocked responses or proxies requests to actual service.

## Dependencies

* Install pipx

    ```
    sudo apt-get install pipx
    ```

* Install mitmproxy

    ```
    pipx install mitmproxy
    ```

* Inject pip packages into mitmproxy

    ```
    pipx inject mitmproxy requests pyyaml watchdog
    ```

## Getting Started

* Copy config/settings.yml.sample to config/settings.yml

* Edit as needed

## Usage

```
./init.sh mitmdump
```
