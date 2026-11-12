"""cocotb 2.x self-checking test for sync_fifo, with a Python list scoreboard."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge


@cocotb.test()
async def test_fill_drain_scoreboard(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    dut.rst_n.value = 0
    dut.wr.value = 0
    dut.rd.value = 0
    dut.din.value = 0
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await FallingEdge(dut.clk)
    assert int(dut.empty.value) == 1 and int(dut.full.value) == 0

    sb = []

    async def push(byte):
        await FallingEdge(dut.clk)
        dut.din.value = byte
        dut.wr.value = 1
        dut.rd.value = 0
        sb.append(byte)
        await FallingEdge(dut.clk)
        dut.wr.value = 0

    async def pop():
        await FallingEdge(dut.clk)
        dut.wr.value = 0
        dut.rd.value = 1
        await FallingEdge(dut.clk)
        dut.rd.value = 0
        got = int(dut.dout.value)
        exp = sb.pop(0)
        assert got == exp, f"dout {got:#x} != scoreboard {exp:#x}"

    for i in range(4):
        await push(0xA0 + i)
    await FallingEdge(dut.clk)
    assert int(dut.full.value) == 1 and int(dut.count.value) == 4

    # write-to-full ignored
    await FallingEdge(dut.clk)
    dut.din.value = 0xFF
    dut.wr.value = 1
    await FallingEdge(dut.clk)
    dut.wr.value = 0
    assert int(dut.full.value) == 1 and int(dut.count.value) == 4

    for _ in range(4):
        await pop()
    await FallingEdge(dut.clk)
    assert int(dut.empty.value) == 1
