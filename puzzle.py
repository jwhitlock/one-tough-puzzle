"""Solve One Tough Puzzle™"""

from enum import Enum, IntEnum
from functools import total_ordering
from itertools import product
from typing import ClassVar, Dict, Tuple


class OrderedLabeledEnum(bytes, Enum):
    """An enumeration supporting ordering and a label"""

    def __new__(cls, value, label):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        return obj

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Shape(OrderedLabeledEnum):
    """Puzzle end shape, in alphabetical order."""

    CLUB = (1, "Club")
    DIAMOND = (2, "Diamond")
    HEART = (3, "Heart")
    SPADE = (4, "Spade")


class End(OrderedLabeledEnum):
    """Does the end stick out (tab) or in (blank)?"""

    TAB = (1, "Tab")
    BLANK = (2, "Blank")


class Side(OrderedLabeledEnum):
    """Is the red or black side up?"""

    RED = (1, "Red")
    BLACK = (2, "Black")


class Turn(IntEnum):
    NO_TURN = 0
    TURN_90 = 90
    TURN_180 = 180
    TURN_270 = 270


class Edge(OrderedLabeledEnum):
    NORTH = (0, "North")
    EAST = (1, "East")
    SOUTH = (2, "South")
    WEST = (3, "West")


class Orientation:
    """An orientation of a peice."""

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
        self._attributes = (
            side,
            (north_end, east_end, south_end, west_end),
            (north_shape, east_shape, south_shape, west_shape),
        )

    @property
    def side(self):
        return self._attributes[0]

    @property
    def ends(self):
        return self._attributes[1]

    @property
    def shapes(self):
        return self._attributes[2]

    @property
    def edges(self):
        return tuple(zip(self.shapes, self.ends))

    def end(self, edge: Edge):
        return self._attributes[1][edge.value]

    def shape(self, edge: Edge):
        return self._attributes[2][edge.value]

    def edge(self, edge: Edge):
        return (self._attributes[2][edge.value], self._attributes[1][edge.value])

    north = property(lambda self: self.edge(Edge.NORTH))
    east = property(lambda self: self.edge(Edge.EAST))
    south = property(lambda self: self.edge(Edge.SOUTH))
    west = property(lambda self: self.edge(Edge.WEST))
    north_shape = property(lambda self: self.shape(Edge.NORTH))
    east_shape = property(lambda self: self.shape(Edge.EAST))
    south_shape = property(lambda self: self.shape(Edge.SOUTH))
    west_shape = property(lambda self: self.shape(Edge.WEST))
    north_end = property(lambda self: self.end(Edge.NORTH))
    east_end = property(lambda self: self.end(Edge.EAST))
    south_end = property(lambda self: self.end(Edge.SOUTH))
    west_end = property(lambda self: self.end(Edge.WEST))

    def __repr__(self):
        """Print a eval() representation."""
        parts = [str(self.side)]
        for shape, end in zip(self.shapes, self.ends):
            parts.extend([shape, end])
        return f"{self.__class__.__name__}({', '.join(str(p) for p in parts)})"

    _pip: ClassVar[Dict[Tuple[Shape, End], str]] = {
        (Shape.HEART, End.TAB): "♥",
        (Shape.HEART, End.BLANK): "♡",
        (Shape.DIAMOND, End.TAB): "♦",
        (Shape.DIAMOND, End.BLANK): "♢",
        (Shape.CLUB, End.TAB): "♣",
        (Shape.CLUB, End.BLANK): "♧",
        (Shape.SPADE, End.TAB): "♠",
        (Shape.SPADE, End.BLANK): "♤",
    }

    def __str__(self):
        parts = [self.side.label, "-"]
        parts.extend([self._pip[edge] for edge in self.edges])
        return "".join(parts)

    def __eq__(self, other):
        if not isinstance(other, Orientation):
            return NotImplemented
        return self._attributes == other._attributes

    def __ne__(self, other):
        if not isinstance(other, Orientation):
            return NotImplemented
        return self._attributes != other._attributes

    def __ge__(self, other: "Orientation"):
        return self._attributes >= other._attributes

    def __gt__(self, other: "Orientation"):
        return self._attributes > other._attributes

    def __le__(self, other: "Orientation"):
        return self._attributes <= other._attributes

    def __lt__(self, other):
        return self._attributes < other._attributes

    def is_valid(self) -> bool:
        """Determine if the orientation could be from One Tough Puzzle."""
        return self.ends in (
            (End.TAB, End.TAB, End.BLANK, End.BLANK),
            (End.BLANK, End.TAB, End.TAB, End.BLANK),
            (End.BLANK, End.BLANK, End.TAB, End.TAB),
            (End.TAB, End.BLANK, End.BLANK, End.TAB),
        )

    def is_standard(self) -> bool:
        """Determine if the orientation is standard."""
        return self.side == Side.RED and self.ends == (
            End.TAB,
            End.TAB,
            End.BLANK,
            End.BLANK,
        )

    def to_standard(self) -> "Orientation":
        if not self.is_valid():
            raise ValueError("Can not change invalid orientation to standard.")

        standard = self.reorient(flip=(self.side == Side.BLACK))
        while not standard.is_standard():
            standard = standard.reorient(turn=Turn.TURN_90)
        return standard

    def reorient(self, flip: bool = False, turn: Turn = Turn.NO_TURN) -> "Orientation":
        """Turn and flip to new orientation."""
        new_edges = list(self.edges)
        new_side = self.side

        if flip:
            # Flip left to right
            new_edges = [new_edges[0], new_edges[3], new_edges[2], new_edges[1]]
            if self.side == Side.RED:
                new_side = Side.BLACK
            else:
                new_side = Side.RED

        index = {
            Turn.NO_TURN: 0,
            Turn.TURN_90: -1,
            Turn.TURN_180: -2,
            Turn.TURN_270: -3,
        }[turn]
        new_edges = new_edges[index:] + new_edges[:index]
        return Orientation(
            new_side, *new_edges[0], *new_edges[1], *new_edges[2], *new_edges[3]
        )


class Piece:
    """A puzzle piece."""

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

    def __repr__(self):
        parts = [shape for shape, end in self.orientation.edges]
        return f"{self.__class__.__name__}({', '.join(str(p) for p in parts)})"

    def __str__(self):
        return str(self.orientation)

    side = property(lambda self: self.orientation.side)
    north = property(lambda self: self.orientation.north)
    east = property(lambda self: self.orientation.east)
    south = property(lambda self: self.orientation.south)
    west = property(lambda self: self.orientation.west)
    north_shape = property(lambda self: self.orientation.north_shape)
    east_shape = property(lambda self: self.orientation.east_shape)
    south_shape = property(lambda self: self.orientation.south_shape)
    west_shape = property(lambda self: self.orientation.west_shape)
    north_end = property(lambda self: self.orientation.north_end)
    east_end = property(lambda self: self.orientation.east_end)
    south_end = property(lambda self: self.orientation.south_end)
    west_end = property(lambda self: self.orientation.west_end)

    def fits_right(self, other: "Piece"):
        """Return pairs where this fits with the other piece."""
        combos = product((False, True), Turn, (False, True), Turn)
        fits = []
        for flip, turn, other_flip, other_turn in combos:
            orient = OrientedPiece(self, flip, turn)
            other_orient = OrientedPiece(other, other_flip, other_turn)
            if orient.fits_right(other_orient):
                fits.append((orient, other_orient))
        return fits


class OrientedPiece:
    """A puzzle piece in a particular orientation."""

    def __init__(self, piece: Piece, flip: bool = False, turn: Turn = Turn.NO_TURN):
        self.piece = piece
        self.flip = flip
        self.turn = turn
        self.orientation = piece.orientation.reorient(flip=flip, turn=turn)

    def __repr__(self):
        parts = [repr(self.piece)]
        if self.flip:
            parts.append("flip=True")
        if self.turn:
            parts.append(f"turn={self.turn!s}")

        return f"OrientedPiece({', '.join(p for p in parts)})"

    def __str__(self):
        return str(self.orientation)

    def __eq__(self, other):
        return (
            (self.piece == other.piece)
            and (self.flip == other.flip)
            and (self.turn == other.turn)
        )

    side = property(lambda self: self.orientation.side)
    north = property(lambda self: self.orientation.north)
    east = property(lambda self: self.orientation.east)
    south = property(lambda self: self.orientation.south)
    west = property(lambda self: self.orientation.west)
    north_shape = property(lambda self: self.orientation.north_shape)
    east_shape = property(lambda self: self.orientation.east_shape)
    south_shape = property(lambda self: self.orientation.south_shape)
    west_shape = property(lambda self: self.orientation.west_shape)
    north_end = property(lambda self: self.orientation.north_end)
    east_end = property(lambda self: self.orientation.east_end)
    south_end = property(lambda self: self.orientation.south_end)
    west_end = property(lambda self: self.orientation.west_end)

    def fits_right(self, other):
        return (self.east_shape == other.west_shape) and (
            self.east_end != other.west_end
        )


if __name__ == "__main__":
    print("Hello, world!")
