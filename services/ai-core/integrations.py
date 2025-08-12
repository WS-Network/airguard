"""Integration helpers for collecting telemetry data from various network protocols.

This module provides stub implementations for integrating with LoRaWAN, SNMP and MQTT.
In a production system these functions would use libraries like `paho-mqtt` and `pysnmp`
to communicate with real devices. Here we return simple example data structures to
demonstrate how the API can be extended.
"""

from typing import Dict, Any



def collect_lorawan_data(device_id: str) -> Dict[str, Any]:
    """
    Collect telemetry from a LoRaWAN device.

    Args:
        device_id: Identifier of the device.

    Returns:
        A dictionary containing sample metrics from the device.
    """
    # TODO: integrate with a LoRaWAN network server (e.g. ChirpStack) via MQTT.
    return {
        "device_id": device_id,
        "protocol": "lorawan",
        "signal_strength": -120,
        "payload": "example_payload",
    }



def collect_snmp_data(device_id: str) -> Dict[str, Any]:
    """
    Collect telemetry from an SNMP-enabled network device.

    Args:
        device_id: Identifier of the device or host.

    Returns:
        A dictionary with sample SNMP metrics.
    """
    # TODO: use pysnmp to query real SNMP OIDs from the device.
    return {
        "device_id": device_id,
        "protocol": "snmp",
        "sysUpTime": 123456,
        "ifSpeed": 1000000,
    }



def collect_mqtt_data(device_id: str) -> Dict[str, Any]:
    """
    Collect telemetry by subscribing to an MQTT topic for the given device.

    Args:
        device_id: Identifier of the device (used as a topic or part of it).

    Returns:
        A dictionary with the latest message published on the topic.
    """
    # TODO: use paho.mqtt.client to connect to an MQTT broker and consume messages.
    return {
        "device_id": device_id,
        "protocol": "mqtt",
        "topic": f"sensors/{device_id}/temperature",
        "value": 22.5,
    }



def collect_telemetry(device_id: str, protocol: str) -> Dict[str, Any]:
    """
    Dispatch telemetry collection based on the protocol.

    Args:
        device_id: Identifier of the device.
        protocol: Name of the protocol ('lorawan', 'snmp', or 'mqtt').

    Returns:
        A dictionary with telemetry data.

    Raises:
        ValueError: if an unsupported protocol is requested.
    """
    protocol = protocol.lower()
    if protocol == "lorawan":
        return collect_lorawan_data(device_id)
    if protocol == "snmp":
        return collect_snmp_data(device_id)
    if protocol == "mqtt":
        return collect_mqtt_data(device_id)
    raise ValueError(f"Unsupported protocol: {protocol}")
