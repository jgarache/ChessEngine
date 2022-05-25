"""
Castle rights class allows to keep track of all flags relating to both king and queen side castling.
"""


class CastleRights:

    def __init__(self, wks, bks, wqs, bqs) -> None:
        # All of these variables are booleans allowing to determine if castling either queen or king side is possible
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
