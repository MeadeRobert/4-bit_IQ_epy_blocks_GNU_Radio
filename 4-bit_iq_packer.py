"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='IQ 4bit -> 8bit Unpacker',   # will show up in GRC
            in_sig=[np.int8], # interleaved 4-bit I/Q
            out_sig=[(np.int8,2)] # upacked output of IChar IQ
        )
        

    def work(self, input_items, output_items):
        inp = input_items[0].astype(np.uint8)
        out = output_items[0]

        # Unpack high nibble = I, low nibble = Q
        i_vals = ((inp.astype(np.uint8) >> 4) & 0x0F)-8
        q_vals = (inp & 0x0F).astype(np.int8)-8

        # Interleave into 1x2 vector output
        out[:len(inp)] = np.column_stack((i_vals, q_vals))

        return len(inp)
