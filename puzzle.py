#!/usr/bin/env python3
"""Solve One Tough Puzzle™"""

from enum import Enum, IntEnum
from functools import total_ordering
from itertools import product
from typing import ClassVar, Dict, Tuple, Set, Union, Type, Sequence, Any, cast
from math import floor


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
        **params: Any,
    ):
        """Initialize an orientation of a puzzle piece."""
        self._attributes = (
            side,
            (north_end, east_end, south_end, west_end),
            (north_shape, east_shape, south_shape, west_shape),
        )
        super().__init__()

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

    def fits_right(self, other: object) -> bool:
        if not isinstance(other, Orientation):
            return NotImplemented
        return bool(
            (self.east_shape == other.west_shape) and (self.east_end != other.west_end)
        )

    def fits_left(self, other: "Orientation") -> bool:
        return bool(
            (self.west_shape == other.east_shape) and (self.west_end != other.east_end)
        )

    def fits_below(self, other: "Orientation") -> bool:
        return bool(
            (self.south_shape == other.north_shape)
            and (self.south_end != other.north_end)
        )

    def fits_above(self, other: "Orientation") -> bool:
        return bool(
            (self.north_shape == other.south_shape)
            and (self.north_end != other.south_end)
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
            side=std.side,
            north_shape=std.north_shape,
            north_end=std.north_end,
            east_shape=std.east_shape,
            east_end=std.east_end,
            south_shape=std.south_shape,
            south_end=std.south_end,
            west_shape=std.west_shape,
            west_end=std.west_end,
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

    def fits_right(self, other: object) -> bool:
        if not isinstance(other, Piece):
            return NotImplemented
        return (self is not other) and super().fits_right(other)

    def fits_left(self, other: object) -> bool:
        if not isinstance(other, Piece):
            return NotImplemented
        return (self is not other) and super().fits_left(other)

    def fits_below(self, other: object) -> bool:
        if not isinstance(other, Piece):
            return NotImplemented
        return (self is not other) and super().fits_below(other)

    def fits_above(self, other: object) -> bool:
        if not isinstance(other, Piece):
            return NotImplemented
        return (self is not other) and super().fits_above(other)


class BaseOrientedPiece:
    def __init__(self, piece: Union[Piece, None], **params: Any):
        self.piece = piece
        super().__init__(**params)  # type: ignore

    def __ne__(self, other: object) -> bool:
        return not self == other

    def fits_neighbors(
        self, neighbors: Dict[Edge, "BaseOrientedPiece"]
    ) -> Dict[Edge, bool]:
        return {
            Edge.NORTH: self.fits_above(neighbors[Edge.NORTH]),
            Edge.EAST: self.fits_right(neighbors[Edge.EAST]),
            Edge.SOUTH: self.fits_below(neighbors[Edge.SOUTH]),
            Edge.WEST: self.fits_left(neighbors[Edge.WEST]),
        }

    @property
    def is_empty(self) -> bool:
        return self.piece is None

    def fits_all_neighbors(self, neighbors: Dict[Edge, "BaseOrientedPiece"]) -> bool:
        return all(self.fits_neighbors(neighbors).values())

    def fits_right(self, other: object) -> bool:
        attr = getattr(super(), "fits_right")
        if attr:
            return bool(attr(other))
        else:
            raise NotImplementedError("fits_right")

    def fits_left(self, other: object) -> bool:
        attr = getattr(super(), "fits_left")
        if attr:
            return bool(attr(other))
        else:
            raise NotImplementedError("fits_left")

    def fits_below(self, other: object) -> bool:
        attr = getattr(super(), "fits_below")
        if attr:
            return bool(attr(other))
        else:
            raise NotImplementedError("fits_below")

    def fits_above(self, other: object) -> bool:
        attr = getattr(super(), "fits_above")
        if attr:
            return bool(attr(other))
        else:
            raise NotImplementedError("fits_above")


class EmptySpot(BaseOrientedPiece):
    """An empty spot in the puzzle."""

    def __init__(self) -> None:
        super().__init__(piece=None)

    def __repr__(self) -> str:
        return "EmptySpot()"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        return False

    def __hash__(self) -> int:
        return hash((None,))

    def fits_right(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        return True

    def fits_left(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        return True

    def fits_below(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        return True

    def fits_above(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        return True


class OrientedPiece(BaseOrientedPiece, Orientation):
    """A puzzle piece in a particular orientation."""

    def __init__(self, piece: Piece, flip: bool = False, turn: Turn = Turn.NO_TURN):
        assert piece is not None
        self.piece = piece
        self.flip = flip
        self.turn = turn
        orientation = piece.reorient(flip=flip, turn=turn)
        super().__init__(
            piece=piece,
            side=orientation.side,
            north_shape=orientation.north_shape,
            north_end=orientation.north_end,
            east_shape=orientation.east_shape,
            east_end=orientation.east_end,
            south_shape=orientation.south_shape,
            south_end=orientation.south_end,
            west_shape=orientation.west_shape,
            west_end=orientation.west_end,
        )

    def __repr__(self) -> str:
        parts = [repr(self.piece)]
        if self.flip:
            parts.append("flip=True")
        if self.turn:
            parts.append(f"turn={self.turn!s}")

        return f"OrientedPiece({', '.join(p for p in parts)})"

    def __hash__(self) -> int:
        return hash((self.piece, self.flip, self.turn))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        if self.piece is None or other.piece is None:
            return False
        other = cast(OrientedPiece, other)
        return (
            (self.piece is other.piece)
            and (self.flip == other.flip)
            and (self.turn == other.turn)
        )

    def fits_right(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        if other.piece is None:
            return True
        return super().fits_right(cast(OrientedPiece, other))

    def fits_left(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        if other.piece is None:
            return True
        return super().fits_left(cast(OrientedPiece, other))

    def fits_below(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        if other.piece is None:
            return True
        return super().fits_below(cast(OrientedPiece, other))

    def fits_above(self, other: object) -> bool:
        if not isinstance(other, BaseOrientedPiece):
            return NotImplemented
        if other.piece is None:
            return True
        return super().fits_above(cast(OrientedPiece, other))


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


class Puzzle:
    """A collection of OrientedPieces and EmptySpots that fit."""

    def __init__(
        self,
        width: int = 0,
        height: int = 0,
        pieces: Union[None, Tuple[BaseOrientedPiece, ...]] = None,
    ):
        if width < 0:
            raise ValueError("Negative width is not allowed")
        if height < 0:
            raise ValueError("Negative height is not allowed")
        if width == 0 and height > 0:
            raise ValueError("width must be positive since height is positive")
        if height == 0 and width > 0:
            raise ValueError("height must be positive since width is positive")

        if pieces is None:
            pieces = ()
        if len(pieces) > (width * height):
            raise ValueError(
                f"{len(pieces)} pieces will not fit in a puzzle of size"
                f" {width * height} (width {width}, height {height})"
            )
        # Fill out empty spaces
        if (width * height) > len(pieces):
            pieces += (EmptySpot(),) * ((width * height) - len(pieces))

        self._puzzle = (width, height) + pieces

        # Verify pieces fit
        for col, row in product(range(width), range(height)):
            piece = self.get(col, row)
            neighbors = self.get_neighbors(col, row)
            fits = piece.fits_neighbors(neighbors)
            if not all(fits.values()):
                edges = [edge for edge, fit in fits.items() if not fit]
                edge_msgs = [f"{edge} is {neighbors[edge]}" for edge in edges]
                raise ValueError(
                    f"Piece {piece} does not fit at col {col}, row {row}:"
                    f" {', '.join(edge_msgs)}"
                )

    width = property(lambda self: self._puzzle[0])
    height = property(lambda self: self._puzzle[1])

    @property
    def pieces(self) -> Tuple[BaseOrientedPiece, ...]:
        return self._puzzle[2:]

    def __repr__(self) -> str:
        bits = []
        all_empty = all(piece.is_empty for piece in self.pieces)
        if self.width != 0 or self.height != 0 or not all_empty:
            bits.extend([str(self.width), str(self.height)])
        if not all_empty:
            bits.append(str(self.pieces))
        return f"Puzzle({', '.join(bits)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Puzzle):
            return NotImplemented
        return self._puzzle == other._puzzle

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Puzzle):
            return NotImplemented
        return self._puzzle != other._puzzle

    def __ge__(self, other: "Puzzle") -> bool:
        return self._puzzle >= other._puzzle

    def __gt__(self, other: "Puzzle") -> bool:
        return self._puzzle > other._puzzle

    def __le__(self, other: "Puzzle") -> bool:
        return self._puzzle <= other._puzzle

    def __lt__(self, other: "Puzzle") -> bool:
        return self._puzzle < other._puzzle

    def __hash__(self) -> int:
        return hash(self._puzzle)

    def get(self, col: int, row: int) -> BaseOrientedPiece:
        """Get the piece / EmptySpot, or an EmptySpot if out of range."""
        if col < 0 or row < 0 or col >= self.width or row >= self.height:
            return EmptySpot()
        return cast(BaseOrientedPiece, self.pieces[(self.width * row) + col])

    def get_neighbors(self, col: int, row: int) -> Dict[Edge, BaseOrientedPiece]:
        """Get the surrounding neighbors, which may be EmptySpots."""
        return {
            Edge.NORTH: self.get(col, row - 1),
            Edge.EAST: self.get(col + 1, row),
            Edge.SOUTH: self.get(col, row + 1),
            Edge.WEST: self.get(col - 1, row),
        }

    def __str__(self) -> str:
        """Draw the puzzle with unicode rank and box characters."""
        empty = all(p.is_empty for p in self.pieces)
        if empty:
            return f"(Empty {self.width}x{self.height} Puzzle)"

        col, row = 0, 0
        top, middle, bottom = [], [], []
        out = []
        for piece in self.pieces:

            # Check if surrounding spots are empty or pieces
            neighbors = self.get_neighbors(col, row)
            above = neighbors[Edge.NORTH]
            left = neighbors[Edge.WEST]

            is_last_row = row == (self.width - 1)
            is_last_col = col == (self.height - 1)

            if piece.is_empty:
                if above.is_empty:
                    n_char = " "
                else:
                    n_char = PIPS[cast(OrientedPiece, above).south]
                if left.is_empty:
                    w_char = " "
                else:
                    w_char = PIPS[cast(OrientedPiece, left).east]
                center_char = " "
            else:
                n_shape, n_end = cast(OrientedPiece, piece).north
                if not above.is_empty:
                    n_end = End.TAB
                n_char = PIPS[(n_shape, n_end)]

                w_shape, w_end = cast(OrientedPiece, piece).west
                if not left.is_empty:
                    w_end = End.TAB
                w_char = PIPS[(w_shape, w_end)]

                center_char = (
                    "R" if cast(OrientedPiece, piece).side == Side.RED else "B"
                )

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
            top.append(nw_char[(piece.is_empty, above.is_empty, left.is_empty)])
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
                top.append(ne_char[(piece.is_empty, above.is_empty)])
                if piece.is_empty:
                    middle.append(" ")
                else:
                    middle.append(PIPS[cast(OrientedPiece, piece).east])

            if is_last_row:
                # Draw the bottom edge

                # piece is empty, left is empty
                sw_char = {
                    (False, False): "┴",
                    (False, True): "└",
                    (True, False): "┘",
                    (True, True): " ",
                }
                bottom.append(sw_char[(piece.is_empty, left.is_empty)])
                if piece.is_empty:
                    bottom.append(" ")
                else:
                    bottom.append(PIPS[cast(OrientedPiece, piece).south])

                if is_last_col:
                    # Draw the bottom right corner
                    if piece.is_empty:
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

    def fit_at(self, piece: Piece, at_column: int, at_row: int) -> Set["Puzzle"]:
        """Return puzzles where this piece fits at the given spot."""

        for oriented_piece in self.pieces:
            if oriented_piece.piece is piece:
                # Can't add piece twice
                return set()

        if not self.get(at_column, at_row).is_empty:
            # Can't add to the same spot twice
            return set()

        # Create a puzzle of the new size with EmptySpots if needed
        new_width = max(self.width, at_column + 1)
        new_height = max(self.height, at_row + 1)
        puzzle = self
        if new_width != puzzle.width or new_height != puzzle.height:
            # puzzle = puzzle.expand_to(new_width, new_height)
            puzzle = Puzzle(new_width, new_height)
            for col, row in product(range(new_width), range(new_height)):
                old_piece = self.get(col, row)
                if not old_piece.is_empty:
                    puzzle = puzzle.place_at(cast(OrientedPiece, old_piece), col, row)

        puzzles = set()
        for flip, turn in product((False, True), Turn):
            orient = OrientedPiece(piece, flip, turn)
            try:
                new_puzzle = puzzle.place_at(orient, at_column, at_row)
            except ValueError:
                pass
            else:
                puzzles.add(new_puzzle)
        return puzzles

    def place_at(self, piece: OrientedPiece, at_column: int, at_row: int) -> "Puzzle":
        """Place a piece, returning a new puzzle."""
        if (
            at_column < 0
            or at_column >= self.width
            or at_row < 0
            or at_row >= self.height
        ):
            raise NotImplementedError("Resizing not implemented")

        if not self.get(at_column, at_row).is_empty:
            raise ValueError("There is already a piece there.")

        pieces = list(self.pieces)
        pieces[at_column + at_row * self.width] = piece
        return Puzzle(self.width, self.height, tuple(pieces))


def solve_puzzle_with_details(
    columns: int, rows: int, pieces: Sequence[Piece], verbose: bool = False
) -> Dict[int, Set[Puzzle]]:
    assert rows * columns == len(pieces)

    puzzles_by_size = {0: {Puzzle()}}
    for size in range(1, (rows * columns) + 1):
        # Determine the rows and columns for this attempt
        at_col = (size - 1) % columns
        at_row = int(floor((size - 1) / columns))
        width = min(size, at_col + 1)
        height = at_row + 1
        if verbose:
            print(
                f"Looking for solutions for {size}-piece puzzle"
                f" at {at_col}x{at_row} in {width}x{height} Puzzle"
            )

        last_puzzles = puzzles_by_size[size - 1]
        next_puzzles = set()
        for puzzle in last_puzzles:
            for piece in pieces:
                next_puzzles |= puzzle.fit_at(piece, at_col, at_row)
        if verbose:
            print(f"Found {len(next_puzzles)} {size}-piece puzzles. First 3:")
            for puzzle in sorted(next_puzzles)[:3]:
                print(puzzle)
                print()

        puzzles_by_size[size] = next_puzzles

    return puzzles_by_size


def solve_puzzle(
    columns: int, rows: int, pieces: Sequence[Piece], verbose: bool = False
) -> Set[Puzzle]:
    puzzles_by_size = solve_puzzle_with_details(columns, rows, pieces, verbose)
    return puzzles_by_size[len(pieces)]


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

    puzzles_by_size = solve_puzzle(3, 3, pieces, verbose=True)
