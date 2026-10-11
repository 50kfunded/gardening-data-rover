# SPDX-License-Identifier: MIT
"""Planned framing checks. Keep partial lines through timeouts, with bounded memory."""

from shared.data_format import MAX_LINE_BYTES


class LineBuffer:
    def __init__(self):
        self.pending = bytearray()
        self.discarding = False

    def feed(self, chunk):
        """Yield a whole line, or None for one oversized line at its newline."""
        for byte in chunk:
            if not self.discarding:
                if len(self.pending) < MAX_LINE_BYTES:
                    self.pending.append(byte)
                else:
                    self.pending.clear()
                    self.discarding = True
            if byte == 10:
                yield None if self.discarding else bytes(self.pending)
                self.pending.clear()
                self.discarding = False

    def finish(self):
        """An unfinished line at shutdown counts as malformed, not as a reading."""
        incomplete = bool(self.pending) or self.discarding
        self.pending.clear()
        self.discarding = False
        return incomplete
