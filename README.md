[![Static Badge](https://img.shields.io/badge/NOTICE-Work_in_progress-orange)](#)
# TOPdesk Statistics Home Assistant Integration

This Home Assistant integration retrieves ticket statistics from the TOPdesk API and displays them as sensors.

## Features
- Fetches statistics from the Call Management and Change Management modules
- Provides overall ticket counts per module
- Fetches the number of completed tickets
- Fetches the number of closed completed tickets
- Fetches the number of new tickets created today
- Supports multiple TOPdesk servers/instances

## Installation

### Prerequisites
- A running instance of Home Assistant.
- API access to a TOPdesk server.
    > _The API account used for this integration must have the correct permissions to read data from TOPdesk. It does not require write access._
- Username and application password for authentication.

### Manual Installation
1. Copy the `custom_components/topdesk_stats` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via the Home Assistant UI under **Settings** > **Devices & Services** > **TOPdesk Statistics**.
4. Configure the integration with your TOPdesk API credentials.

### Configuration
- **Host**: Your TOPdesk instance URL (e.g., `https://yourcompany.topdesk.net`)
- **Username**: The API username
- **Application Password**: The API application password
- **Instance Name**: A unique name for this integration instance

## Sensors
Once configured, the integration will provide the following sensors for each module:
- `Completed Tickets`
- `Closed Completed Tickets`
- `New Tickets Today`
- `Total Tickets` (overall count per module)
_Currently, only Call Management and Change Management are supported_

## Troubleshooting
- Ensure your TOPdesk API credentials are correct.
- Check that the API account has the necessary read permissions.
- Verify that your Home Assistant logs (`home-assistant.log`) do not show authentication errors.

### Logging
To enable debugging, add the following to your `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.topdesk_stats: debug
```

## Disclaimer
This integration is provided as-is, without any guarantees. Use it at your own risk. The developers are not responsible for any issues arising from its use.

## Contributions
Feel free to contribute via pull requests or open an issue for feature requests and bug reports.

## Contact
For any questions, please create an issue on GitHub.
