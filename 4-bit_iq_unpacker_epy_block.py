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

    def __init__(self, chunk_size=4096, scale_factor=1.0,):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='IQ 8bit -> 4bit Unpacker',   # will show up in GRC
            in_sig=[(np.int8, 2)], # interleaved I/Q
            out_sig=[np.int8] # packed output
        )
        self.chunk_size = int(chunk_size)
        self.scale_factor = scale_factor
        self._Ibuf = np.empty(self.chunk_size, dtype=np.int8)
        self._Qbuf = np.empty(self.chunk_size, dtype=np.int8)
        self._Obuf = np.empty(self.chunk_size, dtype=np.int8)

    def work(self, input_items, output_items):
        inp = input_items[0]
        out = output_items[0]

        n = len(inp)         # number of IQ samples provided this call
        total_out = 0

		# Process in fixed-size chunks
        for start in range(0, n, self.chunk_size):
            end = min(start + self.chunk_size, n)
            L = end - start

            # Slice input directly into working buffers
            # No dtype conversion needed — masking int8 is fine.
            np.multiply(inp[start:end,0], self.scale_factor, out=self._Ibuf[:L], casting='unsafe')
            np.clip(self._Ibuf[:L],-8,7, out=self._Ibuf[:L])
            self._Ibuf[:L] = (self._Ibuf[:L].astype(np.int8) + 8).astype(np.uint8)
            
            np.multiply(inp[start:end,1], self.scale_factor, out=self._Qbuf[:L], casting='unsafe')
            np.clip(self._Qbuf[:L],-8,7, out=self._Qbuf[:L])
            self._Qbuf[:L] = (self._Qbuf[:L].astype(np.int8) + 8).astype(np.uint8)

            # Mask and pack
            # Note: (& 0x0F) works fine on int8 — result becomes int8 automatically
            self._Obuf[:L] = ((self._Ibuf[:L] & 0x0F) << 4) | (self._Qbuf[:L] & 0x0F)

            # Copy packed chunk to output
            out[total_out:total_out + L] = self._Obuf[:L]
            total_out += L
        return total_out
