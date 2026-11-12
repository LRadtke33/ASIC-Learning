"""cocotb 2.x self-checking test for gray4.  Mirrors tb_gray4.v."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, Timer


def ham(a, b):
    return (int(a) ^ int(b)).bit_count()


@cocotb.test()
async def test_reset_and_sequence(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    dut.rst_n.value = 0
    dut.en.value = 0
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await FallingEdge(dut.clk)
    assert int(dut.gray.value) == 0, f"reset gray={dut.gray.value}"
    assert int(dut.bin.value) == 0

    dut.en.value = 1
    prev = int(dut.gray.value)
    expected = 0
    for _ in range(32):
        await FallingEdge(dut.clk)
        expected = (expected + 1) & 0xF
        g = int(dut.gray.value)
        b = int(dut.bin.value)
        assert b == expected, f"bin {b} != {expected}"
        assert ham(prev, g) == 1, f"Hamming {prev:04b}->{g:04b}"
        assert g == (b ^ (b >> 1))
        prev = g

    dut.en.value = 0
    frozen = int(dut.gray.value)
    for _ in range(8):
        await FallingEdge(dut.clk)
        assert int(dut.gray.value) == frozen
