# Device42 to SolarWinds WHD sync tool

The _d42_sync_tool.py_ uploads data from Device42 to SolarWinds WebHelpDesk.
Device42 Data that is synced is as follows:
- Buildings (WHD: Locations)
- Vendors (WHD: Manufacturers)
- Type (WHD: Asset Type)
- Hardware (WHD: Models)
- Devices (WHD: Asset)

## Usage
The _d42_sync_tool.py_ has a separate _settings.cfg_ file which holds all of the settings including:
- Device42 credentials 
- Device42 URL
- WHD credentials
- WHD URL
- Other settings (logging, debug...)

You can run the tool by typing _python_ _d42_sync_tool.py_ in command prompt in Windows or in Linux terminal.