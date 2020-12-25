"""Solve One Tough Puzzle™"""

from enum import Enum, IntEnum
from typing import ClassVar, Dict, Tuple


class Shape(Enum):
    HEART = "Heart"
    DIAMOND = "Diamond"
    CLUB = "Club"
    SPADE = "Spade"


class End(Enum):
    TAB = "Tab"
    BLANK = "Blank"


class Side(Enum):
    RED = "Red"
    BLACK = "Black"


class Turn(IntEnum):
    NO_TURN = (0,)
    TURN_90 = (90,)
    TURN_180 = (180,)
    TURN_270 = 270


class Orientation:
    """An orientation of a peice."""

    pip: ClassVar[Dict[Tuple[Shape, End], str]] = {
        (Shape.HEART, End.TAB): "♥",
        (Shape.HEART, End.BLANK): "♡",
        (Shape.DIAMOND, End.TAB): "♦",
        (Shape.DIAMOND, End.BLANK): "♢",
        (Shape.CLUB, End.TAB): "♣",
        (Shape.CLUB, End.BLANK): "♧",
        (Shape.SPADE, End.TAB): "♠",
        (Shape.SPADE, End.BLANK): "♤",
    }

    def __init__(
        self,
        side: Side,
        north_shape: Shape,
        north_end: End,
        east_shape: Shape,
        east_end: End,
        south_shape: Shape,
        south_end: End,
        west_shape: Shape,
        west_end: End,
    ):
        """Initialize an orientation of a puzzle piece."""
        self.side = side
        self.order = [
            (north_shape, north_end),
            (east_shape, east_end),
            (south_shape, south_end),
            (west_shape, west_end),
        ]

    def __repr__(self):
        """Print a eval() representation."""
        parts = [self.side]
        for shape, end in self.order:
            parts.extend([shape, end])
        return f"{self.__class__.__name__}({', '.join(str(p) for p in parts)})"

    def is_valid(self) -> bool:
        """Determine if the orientation is from One Tough Puzzle."""
        return True

    def is_standard(self) -> bool:
        """Determine if the orientation is standard."""
        return self.side == Side.RED and [edge[1] for edge in self.order] == [
            End.TAB,
            End.TAB,
            End.BLANK,
            End.BLANK,
        ]

    def to_standard(self) -> "Orientation":
        if not self.is_valid():
            raise ValueError("Can not change invalid orientation to standard.")

        standard = self.reorient(flip=(self.side == Side.BLACK))
        while not standard.is_standard():
            standard = standard.reorient(turn=Turn.TURN_90)
        return standard

    def reorient(self, flip: bool = False, turn: Turn = Turn.NO_TURN) -> "Orientation":
        """Turn and flip to new orientation."""
        new_order = self.order[:]

        side = self.side
        if flip:
            # Flip left to right
            new_order = [new_order[0], new_order[3], new_order[2], new_order[1]]
            if side == Side.RED:
                side = Side.BLACK
            else:
                side = Side.RED

        index = {
            Turn.NO_TURN: 0,
            Turn.TURN_90: -1,
            Turn.TURN_180: -2,
            Turn.TURN_270: -3,
        }[turn]
        new_order = new_order[index:] + new_order[:index]
        return Orientation(
            side, *new_order[0], *new_order[1], *new_order[2], *new_order[3]
        )

    def __eq__(self, other):
        return (self.order == other.order) and (self.side == other.side)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        parts = [self.side.value, "-"]
        parts.extend([self.pip[edge] for edge in self.order])
        return "".join(parts)


class Piece:
    def __init__(
        self,
        north_shape: Shape,
        east_shape: Shape,
        south_shape: Shape,
        west_shape: Shape,
        north_orientation: End = End.TAB,
        east_orientation: End = End.TAB,
        south_orientation: End = End.BLANK,
        west_orientation: End = End.BLANK,
        side: Side = Side.RED,
    ):
        """
        Initialize a Piece and rotate to standard position.

        Standard position is Red side up, tabs at north and east, and blanks at south
        and west.
        """
        self.orientation = Orientation(
            side,
            north_shape,
            north_orientation,
            east_shape,
            east_orientation,
            south_shape,
            south_orientation,
            west_shape,
            west_orientation,
        ).to_standard()


if __name__ == "__main__":
    print("Hello, world!")
