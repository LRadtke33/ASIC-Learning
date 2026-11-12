Caravel wrapper sources, copied from LibreLane 3.0.17
  librelane/examples/spm-user_project_wrapper/
Apache-2.0, Efabless. 11 November 2026.

  user_project_wrapper.v   the pin contract (Wishbone, LA, 38 GPIOs,
                           analog_io, user_clock2, user_irq, eight supplies)
  defines.v                MPRJ_IO_PADS_1 = 19, MPRJ_IO_PADS_2 = 19,
                           MPRJ_IO_PADS = 38; GPIO power-on defaults

These files are the text the Caravel-integration lesson quotes.
This course has not hardened a full wrapper; Lab 6 is a standalone SPM.
