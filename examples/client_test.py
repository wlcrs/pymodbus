#!/usr/bin/env python3
"""Pymodbus Client modbus call examples.

Very small example to do experiments on.

The corresponding server must be started before e.g. as:

    ./server_async.py
"""
import asyncio
import logging

import pymodbus.diag_message as req_diag
import pymodbus.mei_message as req_mei
from examples.client_async import run_async_client, setup_async_client
from examples.helper import get_commandline
from pymodbus.pdu import ExceptionResponse


_logger = logging.getLogger()


SLAVE = 0x01


def _check_call(rr):
    """Check modbus call worked generically."""
    assert not rr.isError()  # test that call was OK
    assert not isinstance(rr, ExceptionResponse)  # Device rejected request
    return rr


# ------------------------------------------------------
# Call modbus device (all possible calls are presented).
# ------------------------------------------------------
async def _handle_coils(client):
    """Read/Write coils."""
    _logger.info("### Reading Coil different number of bits (return 8 bits multiples)")
    rr = _check_call(await client.read_coils(32, 1, slave=SLAVE))  # addr 2
    assert len(rr.bits) == 8


async def _handle_discrete_input(client):
    """Read discrete inputs."""
    _logger.info("### Reading discrete input, Read address:0-7")
    rr = _check_call(await client.read_discrete_inputs(32, 8, slave=SLAVE))  # addr 2
    assert len(rr.bits) == 8


async def _handle_holding_registers(client):
    """Read/write holding registers."""
    _logger.info("### write holding register and read holding registers")
    _check_call(await client.write_register(3, 17, slave=SLAVE))
    rr = None
    rr = _check_call(await client.read_holding_registers(3, 1, slave=SLAVE))
    assert rr.registers[0] == 17
    rr = _check_call(await client.read_holding_registers(4, 2, slave=SLAVE))
    assert rr.registers[0] == 9
    assert rr.registers[1] == 27177


async def _execute_information_requests(client):
    """Execute extended information requests."""
    _logger.info("### Running information requests.")
    rr = _check_call(
        await client.execute(req_mei.ReadDeviceInformationRequest(unit=SLAVE))
    )
    assert rr.information[0] == b"pymodbus"


async def _execute_diagnostic_requests(client):
    """Execute extended diagnostic requests."""
    _logger.info("### Running diagnostic requests.")
    rr = _check_call(await client.execute(req_diag.ReturnQueryDataRequest(unit=SLAVE)))
    assert not rr.message[0]

    _check_call(
        await client.execute(req_diag.RestartCommunicationsOptionRequest(unit=SLAVE))
    )


# ------------------------
# Run the calls in groups.
# ------------------------


async def run_async_calls(client):
    """Demonstrate basic read/write calls."""
    await _handle_coils(client)
    await _handle_discrete_input(client)
    await _handle_holding_registers(client)
    await _execute_information_requests(client)
    await _execute_diagnostic_requests(client)


if __name__ == "__main__":
    cmd_args = get_commandline(
        server=False,
        description="Run modbus calls in asynchronous client.",
    )
    testclient = setup_async_client(cmd_args)
    asyncio.run(run_async_client(testclient, modbus_calls=run_async_calls))
