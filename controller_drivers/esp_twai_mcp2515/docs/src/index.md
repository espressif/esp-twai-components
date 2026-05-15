# MCP2515 Programming Guide

`esp_twai_mcp2515` wraps an external MCP2515 CAN controller and exposes the standard `esp_driver_twai` node API.

The component is useful when the selected ESP chip does not have an internal TWAI controller or when you need to add an additional TWAI node over SPI.

The API reference generated from headers is available at [API Reference](api.md).

## Hardware Connection

Connect ESP and MCP2515 as follows:

- SPI clock: ESP `SCLK` -> MCP2515 `SCK`
- SPI MOSI: ESP `MOSI` -> MCP2515 `SI`
- SPI MISO: ESP `MISO` -> MCP2515 `SO`
- Chip select: one GPIO -> MCP2515 `CS`
- Interrupt: one GPIO -> MCP2515 `INT`
- CAN transceiver side: MCP2515 `TXCAN`/`RXCAN` to transceiver, then `CANH`/`CANL` to bus

Typical MCP2515 modules use either `8 MHz` or `16 MHz` oscillator. Set `oscillator_hz` accordingly.

## Create a Node

Before creating the MCP2515 node:

1. Initialize the SPI bus with `spi_bus_initialize()`.
2. Install GPIO ISR service using `gpio_install_isr_service()`.

Then call [`twai_new_node_mcp2515()`](api.md#function-twai_new_node_mcp2515).

```c
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_twai.h"
#include "esp_twai_mcp2515.h"

#define MCP2515_SPI_HOST        SPI2_HOST
#define MCP2515_SPI_SCLK_GPIO   GPIO_NUM_6
#define MCP2515_SPI_MOSI_GPIO   GPIO_NUM_7
#define MCP2515_SPI_MISO_GPIO   GPIO_NUM_2
#define MCP2515_INT_GPIO        GPIO_NUM_4
#define MCP2515_CS_GPIO         GPIO_NUM_5

static void mcp2515_init_bus_and_isr(void)
{
    spi_bus_config_t bus_cfg = {
        .sclk_io_num = MCP2515_SPI_SCLK_GPIO,
        .mosi_io_num = MCP2515_SPI_MOSI_GPIO,
        .miso_io_num = MCP2515_SPI_MISO_GPIO,
        .quadwp_io_num = GPIO_NUM_NC,
        .quadhd_io_num = GPIO_NUM_NC,
    };

    ESP_ERROR_CHECK(spi_bus_initialize(MCP2515_SPI_HOST, &bus_cfg, SPI_DMA_CH_AUTO));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
}

twai_node_handle_t mcp2515_create_node(void)
{
    twai_node_handle_t node = NULL;
    twai_mcp2515_node_config_t cfg = {
        .io_cfg = {
            .int_gpio = MCP2515_INT_GPIO,
            .cs_gpio = MCP2515_CS_GPIO,
        },
        .spi_clock_hz = 5 * 1000 * 1000,
        .oscillator_hz = 8 * 1000 * 1000,
        .bit_timing = {
            .bitrate = 125000,
            .sp_permill = 875,
        },
        .fail_retry_cnt = -1,
        .tx_queue_depth = 4,
    };

    ESP_ERROR_CHECK(twai_new_node_mcp2515(MCP2515_SPI_HOST, &cfg, &node));
    return node;
}
```

After node creation, usage follows the regular TWAI node flow:

1. Optional: register callbacks with `twai_node_register_event_callbacks()`
2. Enable node: `twai_node_enable()`
3. Transmit/receive frames
4. Disable node: `twai_node_disable()`
5. Delete node: `twai_node_delete()`

## Configuration Notes

- [`spi_clock_hz`](api.md#struct-twai_mcp2515_node_config_t): SPI clock for MCP2515 transactions, typically up to 10 MHz depending on hardware layout.
- [`oscillator_hz`](api.md#struct-twai_mcp2515_node_config_t): MCP2515 crystal frequency in Hz. Set to `0` to use default `8 MHz`.
- [`bit_timing`](api.md#struct-twai_mcp2515_node_config_t): classic TWAI timing (`bitrate`, `sp_permill`) used to configure CNF registers.
- [`fail_retry_cnt`](api.md#struct-twai_mcp2515_node_config_t): MCP2515 supports `-1` (automatic retransmission) or `0` (one-shot).
- [`timestamp_resolution_hz`](api.md#struct-twai_mcp2515_node_config_t): `0` disables timestamp conversion.
- [`tx_queue_depth`](api.md#struct-twai_mcp2515_node_config_t): depth of software TX queue.
- [`flags.enable_loopback`](api.md#struct-twai_mcp2515_node_config_t): internal loopback for self-test.
- [`flags.enable_listen_only`](api.md#struct-twai_mcp2515_node_config_t): receive-only monitoring mode.

## Feature Compatibility

The MCP2515 backend follows `esp_driver_twai` APIs, but hardware limitations apply:

- Classical CAN only (no CAN FD)
- No range filter support
- Mask filter behavior depends on MCP2515 RX filter groups

Use return values such as `ESP_ERR_NOT_SUPPORTED` to detect unsupported features at runtime.

## Run MCP2515 Test App

The component includes tests at:

- `controller_drivers/esp_twai_mcp2515/test_apps/test_twai_mcp2515`

The test app demonstrates:

- Basic API compile/runtime checks
- Loopback TX/RX
- Queue resume across disable/enable
- Mask filter behavior
- Manual test against an external CAN node (`can-utils`)

Update test pin definitions to match your board wiring before running.
