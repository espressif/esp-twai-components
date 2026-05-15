# MCP2515 Controller Driver

[![Component Registry](https://components.espressif.com/components/espressif/esp_twai_mcp2515/badge.svg)](https://components.espressif.com/components/espressif/esp_twai_mcp2515)

MCP2515 external TWAI controller driver component for ESP-IDF.

## What It Provides

- `twai_new_node_mcp2515()` to create a TWAI node backed by MCP2515 over SPI
- Compatibility with `esp_driver_twai` node APIs
- Support for loopback and listen-only modes

## Notes

- Classical CAN only (no CAN FD)
- Some TWAI APIs are unsupported on MCP2515 and return `ESP_ERR_NOT_SUPPORTED`

## Documentation

For detailed information about the MCP2515 component, including API reference and user guides, please visit:

- **Programming Guide & API Reference**: [MCP2515 Documentation](https://espressif.github.io/esp-twai-components/latest/controller_drivers/esp_twai_mcp2515/index.html)
