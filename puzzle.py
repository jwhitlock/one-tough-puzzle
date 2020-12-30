#!/usr/bin/env python3
"""Solve One Tough Puzzle™"""

from enum import Enum, IntEnum
from functools import total_ordering
from itertools import product
from typing import ClassVar, Dict, Tuple, Set, Union, Type, cast


class OrderedLabeledEnum(Enum):
    """An enumeration supporting ordering and a label"""

    def __init__(self, order: int, label: str):
        self.order = order
        self.label = label

    def __ge__(self, other: "OrderedLabeledEnum") -> bool:
        if self.__class__ is other.__class__:
            return self.order >= other.order
        return NotImplemented

    def __gt__(self, other: "OrderedLabeledEnum") -> bool:
        if self.__class__ is other.__class__:
            return self.order > other.order
        return NotImplemented

    def __le__(self, other: "OrderedLabeledEnum") -> bool:
        if self.__class__ is other.__class__:
            return self.order <= other.order
        return NotImplemented

    def __lt__(self, other: "OrderedLabeledEnum") -> bool:
        if self.__class__ is other.__class__:
            return self.order < other.order
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


PIPS = {
    (Shape.HEART, End.TAB): "♥",
    (Shape.HEART, End.BLANK): "♡",
    (Shape.DIAMOND, End.TAB): "♦",
    (Shape.DIAMOND, End.BLANK): "♢",
    (Shape.CLUB, End.TAB): "♣",
    (Shape.CLUB, End.BLANK): "♧",
    (Shape.SPADE, End.TAB): "♠",
    (Shape.SPADE, End.BLANK): "♤",
}


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
    def side(self) -> Side:
        return self._attributes[0]

    @property
    def ends(self) -> Tuple[End, End, End, End]:
        return self._attributes[1]

    @property
    def shapes(self) -> Tuple[Shape, Shape, Shape, Shape]:
        return self._attributes[2]

    @property
    def edges(
        self,
    ) -> Tuple[
        Tuple[Shape, End], Tuple[Shape, End], Tuple[Shape, End], Tuple[Shape, End]
    ]:
        shapes = self.shapes
        ends = self.ends
        return (
            (shapes[0], ends[0]),
            (shapes[1], ends[1]),
            (shapes[2], ends[2]),
            (shapes[3], ends[3]),
        )

    def end(self, edge: Edge) -> End:
        return self._attributes[1][edge.order]

    def shape(self, edge: Edge) -> Shape:
        return self._attributes[2][edge.order]

    def edge(self, edge: Edge) -> Tuple[Shape, End]:
        return (self._attributes[2][edge.order], self._attributes[1][edge.order])

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

    def __repr__(self) -> str:
        """Print a eval() representation."""
        parts = [str(self.side)]
        for shape, end in zip(self.shapes, self.ends):
            parts.extend([str(shape), str(end)])
        return f"{self.__class__.__name__}({', '.join(parts)})"

    def __str__(self) -> str:
        parts = [self.side.label, "-"]
        parts.extend([PIPS[edge] for edge in self.edges])
        return "".join(parts)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Orientation):
            return NotImplemented
        return self._attributes == other._attributes

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Orientation):
            return NotImplemented
        return self._attributes != other._attributes

    def __ge__(self, other: "Orientation") -> bool:
        return self._attributes >= other._attributes

    def __gt__(self, other: "Orientation") -> bool:
        return self._attributes > other._attributes

    def __le__(self, other: "Orientation") -> bool:
        return self._attributes <= other._attributes

    def __lt__(self, other: "Orientation") -> bool:
        return self._attributes < other._attributes

    def __hash__(self) -> int:
        return hash(self._attributes)

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
        return bool(
            self.side == Side.RED
            and self.ends == (End.TAB, End.TAB, End.BLANK, End.BLANK)
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


class Piece(Orientation):
    """A puzzle piece."""

    def __init__(
        self,
        north_shape: Shape,
        east_shape: Shape,
        south_shape: Shape,
        west_shape: Shape,
        north_end: End = End.TAB,
        east_end: End = End.TAB,
        south_end: End = End.BLANK,
        west_end: End = End.BLANK,
        side: Side = Side.RED,
    ):
        """
        Initialize a Piece and rotate to standard position.

        Standard position is Red side up, tabs at north and east, and blanks at south
        and west.
        """
        std = Orientation(
            side,
            north_shape,
            north_end,
            east_shape,
            east_end,
            south_shape,
            south_end,
            west_shape,
            west_end,
        ).to_standard()
        super().__init__(
            std.side,
            std.north_shape,
            std.north_end,
            std.east_shape,
            std.east_end,
            std.south_shape,
            std.south_end,
            std.west_shape,
            std.west_end,
        )

    def __eq__(self, other: object) -> bool:
        """Pieces with same attributes are not equal."""
        if not isinstance(other, Piece):
            return NotImplemented
        return self is other

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Orientation):
            return NotImplemented
        return self is not other

    def __hash__(self) -> int:
        return hash((self.side, *self.shapes))

    def __repr__(self) -> str:
        """Use defaults for repr"""
        return f"{self.__class__.__name__}({', '.join(str(s) for s in self.shapes)})"

    def row_pairs_with(self, other: "Piece") -> Set["RowPair"]:
        """Return pairs where this fits with the other piece."""
        combos = product((False, True), Turn, (False, True), Turn)
        fits = set()
        for flip, turn, other_flip, other_turn in combos:
            orient = OrientedPiece(self, flip, turn)
            other_orient = OrientedPiece(other, other_flip, other_turn)
            if orient.fits_right(other_orient):
                fits.add(RowPair(orient, other_orient))
        return fits


class OrientedPiece(Orientation):
    """A puzzle piece in a particular orientation."""

    def __init__(self, piece: Piece, flip: bool = False, turn: Turn = Turn.NO_TURN):
        self.piece = piece
        self.flip = flip
        self.turn = turn
        orientation = piece.reorient(flip=flip, turn=turn)
        super().__init__(
            orientation.side,
            orientation.north_shape,
            orientation.north_end,
            orientation.east_shape,
            orientation.east_end,
            orientation.south_shape,
            orientation.south_end,
            orientation.west_shape,
            orientation.west_end,
        )

    def __repr__(self) -> str:
        parts = [repr(self.piece)]
        if self.flip:
            parts.append("flip=True")
        if self.turn:
            parts.append(f"turn={self.turn!s}")

        return f"OrientedPiece({', '.join(p for p in parts)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrientedPiece):
            return NotImplemented
        return (
            (self.piece is other.piece)
            and (self.flip == other.flip)
            and (self.turn == other.turn)
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, OrientedPiece):
            return NotImplemented
        return (
            (self.piece is not other.piece)
            or (self.flip != other.flip)
            or (self.turn != other.turn)
        )

    def __hash__(self) -> int:
        return hash((self.piece, self.flip, self.turn))

    def fits_right(self, other: "OrientedPiece") -> bool:
        return (
            (self.piece is not other.piece)
            and (self.east_shape == other.west_shape)
            and (self.east_end != other.west_end)
        )


class RowPair:
    """A pair of matching pieces"""

    def __init__(self, left: OrientedPiece, right: OrientedPiece):
        assert left.fits_right(right)
        self._pair = (left, right)

    left = property(lambda self: self._pair[0])
    right = property(lambda self: self._pair[1])

    def __str__(self) -> str:
        return f"{self.left} → {self.right}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.left!r}, {self.right!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RowPair):
            return NotImplemented
        return self._pair == other._pair

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, RowPair):
            return NotImplemented
        return self._pair != other._pair

    def __ge__(self, other: "RowPair") -> bool:
        return self._pair >= other._pair

    def __gt__(self, other: "RowPair") -> bool:
        return self._pair > other._pair

    def __le__(self, other: "RowPair") -> bool:
        return self._pair <= other._pair

    def __lt__(self, other: "RowPair") -> bool:
        return self._pair < other._pair

    def __hash__(self) -> int:
        return hash(self._pair)

    def rows_with(self, piece: Piece) -> Set["Row"]:
        if piece in [op.piece for op in self._pair]:
            return set()

        rows = set()
        for flip, turn in product((False, True), Turn):
            orient = OrientedPiece(piece, flip, turn)
            if self.right.fits_right(orient):
                rows.add(Row(self.left, self.right, orient))
        return rows


class Row:
    def __init__(
        self, left: OrientedPiece, middle: OrientedPiece, right: OrientedPiece
    ):
        self._row = (left, middle, right)

    left = property(lambda self: self._row[0])
    middle = property(lambda self: self._row[1])
    right = property(lambda self: self._row[2])

    def __str__(self) -> str:
        return f"{self.left} → {self.middle} → {self.right}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.left!r}, {self.middle!r}, {self.right!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Row):
            return NotImplemented
        return self._row == other._row

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Row):
            return NotImplemented
        return self._row != other._row

    def __ge__(self, other: "Row") -> bool:
        return self._row >= other._row

    def __gt__(self, other: "Row") -> bool:
        return self._row > other._row

    def __le__(self, other: "Row") -> bool:
        return self._row <= other._row

    def __lt__(self, other: "Row") -> bool:
        return self._row < other._row

    def __hash__(self) -> int:
        return hash(self._row)


class EmptySpot:
    """A blank spot in a puzzle"""


class Puzzle:
    """A collection of OrientedPieces and EmptySpots that fit."""

    def __init__(
        self,
        width: int = 0,
        height: int = 0,
        pieces: Union[None, Tuple[Union[OrientedPiece, Type[EmptySpot]], ...]] = None,
    ):
        if width or height:
            width = max(1, width)
            height = max(1, height)
        if pieces is None:
            pieces = ()
        assert (width * height) >= len(pieces)
        if (width * height) > len(pieces):
            pieces += (EmptySpot,) * ((width * height) - len(pieces))
        self._puzzle = (width, height) + pieces

    width = property(lambda self: self._puzzle[0])
    height = property(lambda self: self._puzzle[1])
    pieces = property(lambda self: self._puzzle[2:])

    def get(self, row: int, col: int) -> Union[OrientedPiece, Type[EmptySpot]]:
        if row < 0 or col < 0 or row >= self.width or col >= self.height:
            raise IndexError
        return cast(
            Union[OrientedPiece, Type[EmptySpot]], self.pieces[self.width * row + col]
        )

    def __str__(self) -> str:
        """Draw the puzzle with unicode rank and box characters."""
        empty = all(p is EmptySpot for p in self.pieces)
        if empty:
            return f"(Empty {self.width}x{self.height} Puzzle)"

        col, row = 0, 0
        top, middle, bottom = [], [], []
        out = []
        for piece in self.pieces:

            # Check if surrounding spots are empty or pieces
            above: Union[OrientedPiece, Type[EmptySpot]] = EmptySpot
            if row != 0:
                above = self.get(row - 1, col)
            above_empty = above is EmptySpot

            left: Union[OrientedPiece, Type[EmptySpot]] = EmptySpot
            if col != 0:
                left = self.get(row, col - 1)
            left_empty = left is EmptySpot

            is_last_row = row == (self.width - 1)
            is_last_col = col == (self.height - 1)

            is_empty = piece is EmptySpot
            if is_empty:
                if above_empty:
                    n_char = " "
                else:
                    n_char = PIPS[cast(OrientedPiece, above).south]
                if left_empty:
                    w_char = " "
                else:
                    w_char = PIPS[cast(OrientedPiece, left).east]
                center_char = " "
            else:
                n_shape, n_end = piece.north
                if not above_empty:
                    n_end = End.TAB
                n_char = PIPS[(n_shape, n_end)]

                w_shape, w_end = piece.west
                if not left_empty:
                    w_end = End.TAB
                w_char = PIPS[(w_shape, w_end)]
                center_char = "R" if piece.side == Side.RED else "B"

            nw_char = {
                (False, False, False): "┼",
                (False, False, True): "├",
                (False, True, False): "┬",
                (False, True, True): "┌",
                (True, False, False): "┼",
                (True, False, True): "┘",
                (True, True, False): "┐",
                (True, True, True): " ",
            }
            top.append(nw_char[(is_empty, above_empty, left_empty)])
            top.append(n_char)
            middle.append(w_char)
            middle.append(center_char)

            if is_last_col:
                # Draw the right edge

                # piece is empty, above is empty
                ne_char = {
                    (False, False): "┤",
                    (False, True): "┐",
                    (True, False): "┘",
                    (True, True): " ",
                }
                top.append(ne_char[(is_empty, above_empty)])
                if is_empty:
                    middle.append(" ")
                else:
                    middle.append(PIPS[piece.east])

            if is_last_row:
                # Draw the bottom edge

                # piece is empty, left is empty
                sw_char = {
                    (False, False): "┴",
                    (False, True): "└",
                    (True, False): "┘",
                    (True, True): " ",
                }
                bottom.append(sw_char[(is_empty, left_empty)])
                if is_empty:
                    bottom.append(" ")
                else:
                    bottom.append(PIPS[piece.south])

                if is_last_col:
                    # Draw the bottom right corner
                    if is_empty:
                        bottom.append(" ")
                    else:
                        bottom.append("┘")

            # Move to next spot
            if is_last_col:
                col = 0
                row += 1

                out.append("".join(top))
                top = []
                out.append("".join(middle))
                middle = []
                if is_last_row:
                    out.append("".join(bottom))
            else:
                col += 1

        return "\n".join(out)

        col, row = 0, 0
        # Create width x height grid of
        width = self.width
        grid = tuple(
            self.pieces[x : x + width] for x in range(0, width * self.height, width)
        )

        out = ""
        for row_num, row in enumerate(grid):
            for col_num, col in enumerate(row):
                out += f"[{row_num},{col_num}]"
            out += "\n"
        return out[:-1]

    def __repr__(self) -> str:
        return "Puzzle()"


if __name__ == "__main__":
    pieces = sorted(
        [
            Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),
            Piece(Shape.CLUB, Shape.HEART, Shape.SPADE, Shape.HEART),
            Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART),
            Piece(Shape.DIAMOND, Shape.CLUB, Shape.CLUB, Shape.DIAMOND),
            Piece(Shape.SPADE, Shape.SPADE, Shape.HEART, Shape.CLUB),
            Piece(Shape.SPADE, Shape.DIAMOND, Shape.SPADE, Shape.HEART),
            Piece(Shape.HEART, Shape.DIAMOND, Shape.CLUB, Shape.CLUB),
            Piece(Shape.CLUB, Shape.HEART, Shape.DIAMOND, Shape.CLUB),
            Piece(Shape.HEART, Shape.SPADE, Shape.SPADE, Shape.CLUB),
        ]
    )
    print("Pieces:")
    for piece in pieces:
        print(f"  {piece}")
    possibilities = 8 ** len(pieces)
    print(f"{possibilities:,} possible combinations\n")

    print("Finding pairs...")
    row_pairs = set()
    for piece in pieces:
        for other in pieces:
            row_pairs |= piece.row_pairs_with(other)
    for row_pair in sorted(row_pairs):
        print(f"  {row_pair}")
    print(f"{len(row_pairs):,} row pairs\n")

    print("Finding rows...")
    rows = set()
    for row_pair in row_pairs:
        for piece in pieces:
            rows |= row_pair.rows_with(piece)
    for row in sorted(rows):
        print(f"  {row}")
    print(f"{len(rows):,} rows\n")
