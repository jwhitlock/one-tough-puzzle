"""Tests for puzzle.py"""

from typing import Tuple

import pytest

from puzzle import (
    End,
    Orientation,
    OrientedPiece,
    Piece,
    Row,
    RowPair,
    Shape,
    Side,
    Turn,
    Puzzle,
    EmptySpot,
    solve_puzzle,
)


class TestShape:
    def test_order(self) -> None:
        assert Shape.CLUB < Shape.DIAMOND < Shape.HEART < Shape.SPADE

    def test_str(self) -> None:
        assert str(Shape.CLUB) == "Shape.CLUB"

    def test_label(self) -> None:
        assert Shape.DIAMOND.label == "Diamond"


class TestEnd:
    def test_order(self) -> None:
        assert End.TAB < End.BLANK


class TestSide:
    def test_order(self) -> None:
        assert Side.RED < Side.BLACK


class TestTurn:
    def test_order(self) -> None:
        assert Turn.NO_TURN < Turn.TURN_90 < Turn.TURN_180 < Turn.TURN_270


@pytest.fixture
def standard_orientation() -> Orientation:
    return Orientation(
        Side.RED,
        Shape.HEART,
        End.TAB,
        Shape.DIAMOND,
        End.TAB,
        Shape.DIAMOND,
        End.BLANK,
        Shape.HEART,
        End.BLANK,
    )


class TestOrientation:
    def test_standard_orientation(self, standard_orientation: Orientation) -> None:
        """Test an Orientation initialized to standard orientation"""
        assert standard_orientation.is_valid()
        assert standard_orientation.is_standard()
        as_standard = standard_orientation.to_standard()
        assert as_standard == standard_orientation
        assert str(standard_orientation) == "Red-♥♦♢♡"
        assert repr(standard_orientation) == (
            "Orientation(Side.RED,"
            " Shape.HEART, End.TAB, Shape.DIAMOND, End.TAB,"
            " Shape.DIAMOND, End.BLANK, Shape.HEART, End.BLANK)"
        )
        assert standard_orientation.side == Side.RED

        assert standard_orientation.north == (Shape.HEART, End.TAB)
        assert standard_orientation.east == (Shape.DIAMOND, End.TAB)
        assert standard_orientation.south == (Shape.DIAMOND, End.BLANK)
        assert standard_orientation.west == (Shape.HEART, End.BLANK)

        assert standard_orientation.north_shape == Shape.HEART
        assert standard_orientation.east_shape == Shape.DIAMOND
        assert standard_orientation.south_shape == Shape.DIAMOND
        assert standard_orientation.west_shape == Shape.HEART

        assert standard_orientation.north_end == End.TAB
        assert standard_orientation.east_end == End.TAB
        assert standard_orientation.south_end == End.BLANK
        assert standard_orientation.west_end == End.BLANK

    def test_rotated_90(self, standard_orientation: Orientation) -> None:
        """Test an Orientation rotated 90 from standard orientation"""
        orient = standard_orientation.reorient(turn=Turn.TURN_90)
        assert orient.is_valid()
        assert not orient.is_standard()
        standard = orient.to_standard()
        assert standard != orient
        rotated = orient.reorient(turn=Turn.TURN_270)
        assert standard == rotated
        assert str(orient) == "Red-♡♥♦♢"

    def test_flipped(self, standard_orientation: Orientation) -> None:
        """Test an Orientation flipped from standard orientation"""
        orient = standard_orientation.reorient(flip=True)
        assert orient.is_valid()
        assert not orient.is_standard()
        standard = orient.to_standard()
        assert standard != orient
        rotated = orient.reorient(flip=True)
        assert standard == rotated
        assert str(orient) == "Black-♥♡♢♦"

    def test_reorientation(self, standard_orientation: Orientation) -> None:
        """Test reorientation."""
        # Turn 90 (clockwise) four times
        rotated = standard_orientation.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♡♥♦♢"
        rotated = rotated.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♢♡♥♦"
        rotated = rotated.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♦♢♡♥"
        rotated = rotated.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♥♦♢♡"
        assert rotated == standard_orientation

        # Turn 180 twice
        rotated = standard_orientation.reorient(turn=Turn.TURN_180)
        assert str(rotated) == "Red-♢♡♥♦"
        rotated = rotated.reorient(turn=Turn.TURN_180)
        assert str(rotated) == "Red-♥♦♢♡"
        assert rotated == standard_orientation

        # Turn 270 four times
        rotated = standard_orientation.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♦♢♡♥"
        rotated = rotated.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♢♡♥♦"
        rotated = rotated.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♡♥♦♢"
        rotated = rotated.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♥♦♢♡"
        assert rotated == standard_orientation

        # Flip (Left to Right)
        flipped = standard_orientation.reorient(flip=True)
        assert str(flipped) == "Black-♥♡♢♦"
        flipped = flipped.reorient(flip=True)
        assert str(flipped) == "Red-♥♦♢♡"
        assert flipped == standard_orientation

        # Flip then rotate
        flipped = standard_orientation.reorient(flip=True, turn=Turn.TURN_90)
        assert str(flipped) == "Black-♦♥♡♢"
        flipped = flipped.reorient(flip=True, turn=Turn.TURN_90)
        assert str(flipped) == "Red-♥♦♢♡"
        assert flipped == standard_orientation

    def test_invalid(self) -> None:
        invalid = Orientation(
            Side.RED,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
        )
        assert not invalid.is_valid()

    def test_order(self, standard_orientation: Orientation) -> None:
        or_least = Orientation(
            Side.RED,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
        )
        assert or_least < standard_orientation
        assert standard_orientation > or_least


@pytest.fixture
def otp_pieces() -> Tuple[Piece, ...]:
    return (
        Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),
        Piece(Shape.CLUB, Shape.HEART, Shape.SPADE, Shape.HEART),
        Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART),
        Piece(Shape.DIAMOND, Shape.CLUB, Shape.CLUB, Shape.DIAMOND),
        Piece(Shape.SPADE, Shape.SPADE, Shape.HEART, Shape.CLUB),
        Piece(Shape.SPADE, Shape.DIAMOND, Shape.SPADE, Shape.HEART),
        Piece(Shape.HEART, Shape.DIAMOND, Shape.CLUB, Shape.CLUB),
        Piece(Shape.CLUB, Shape.HEART, Shape.DIAMOND, Shape.CLUB),
        Piece(Shape.HEART, Shape.SPADE, Shape.SPADE, Shape.CLUB),
    )


@pytest.fixture
def piece4(otp_pieces: Tuple[Piece, ...]) -> Piece:
    return otp_pieces[3]


@pytest.fixture
def piece9(otp_pieces: Tuple[Piece, ...]) -> Piece:
    return otp_pieces[8]


class TestPieces:
    def test_default_init(self, piece9: Piece) -> None:
        """Default is the standard orientation"""
        assert str(piece9) == "Red-♥♠♤♧"
        assert repr(piece9) == (
            "Piece(Shape.HEART, Shape.SPADE, Shape.SPADE, Shape.CLUB)"
        )
        assert piece9.side == Side.RED

        assert piece9.north == (Shape.HEART, End.TAB)
        assert piece9.east == (Shape.SPADE, End.TAB)
        assert piece9.south == (Shape.SPADE, End.BLANK)
        assert piece9.west == (Shape.CLUB, End.BLANK)

        assert piece9.north_shape == Shape.HEART
        assert piece9.east_shape == Shape.SPADE
        assert piece9.south_shape == Shape.SPADE
        assert piece9.west_shape == Shape.CLUB

        assert piece9.north_end == End.TAB
        assert piece9.east_end == End.TAB
        assert piece9.south_end == End.BLANK
        assert piece9.west_end == End.BLANK

    def test_full_init(self) -> None:
        """A non-standard orientation is converted to standard."""
        piece = Piece(
            Shape.SPADE,
            Shape.DIAMOND,
            Shape.HEART,
            Shape.DIAMOND,
            End.TAB,
            End.BLANK,
            End.BLANK,
            End.TAB,
            Side.BLACK,
        )
        assert str(piece) == "Red-♠♦♡♢"
        assert repr(piece) == (
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)"
        )


class TestOrientedPiece:
    def test_default_init(self) -> None:
        """Default is the standard orientation."""
        piece = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op = OrientedPiece(piece)
        assert str(op) == "Red-♠♦♡♢"
        assert repr(op) == (
            "OrientedPiece(Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND))"
        )
        assert piece.side == Side.RED

        assert piece.north == (Shape.SPADE, End.TAB)
        assert piece.east == (Shape.DIAMOND, End.TAB)
        assert piece.south == (Shape.HEART, End.BLANK)
        assert piece.west == (Shape.DIAMOND, End.BLANK)

        assert piece.north_shape == Shape.SPADE
        assert piece.east_shape == Shape.DIAMOND
        assert piece.south_shape == Shape.HEART
        assert piece.west_shape == Shape.DIAMOND

        assert piece.north_end == End.TAB
        assert piece.east_end == End.TAB
        assert piece.south_end == End.BLANK
        assert piece.west_end == End.BLANK

    def test_flipped_init(self) -> None:
        """A piece can be flipped at init."""
        piece = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op = OrientedPiece(piece, flip=True)
        assert str(op) == "Black-♠♢♡♦"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " flip=True)"
        )

    def test_turned_init(self) -> None:
        """A piece can be turned at init."""
        piece = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op = OrientedPiece(piece, turn=Turn.TURN_90)
        assert str(op) == "Red-♢♠♦♡"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " turn=Turn.TURN_90)"
        )

    def test_full_init(self) -> None:
        """A piece can be flipped and turned at init."""
        piece = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op = OrientedPiece(piece, flip=True, turn=Turn.TURN_90)
        assert str(op) == "Black-♦♠♢♡"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " flip=True, turn=Turn.TURN_90)"
        )

    def test_equality(self) -> None:
        """An OrientedPiece is equal when the same piece and orientation."""
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.DIAMOND)
        clone1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.DIAMOND)
        piece2 = Piece(Shape.CLUB, Shape.CLUB, Shape.HEART, Shape.SPADE)
        assert str(piece1) == "Red-♥♦♢♢"
        assert str(clone1) == "Red-♥♦♢♢"
        assert str(piece2) == "Red-♣♣♡♤"
        assert piece1 != clone1
        assert piece1 != piece2

        assert OrientedPiece(piece1) == OrientedPiece(piece1)
        assert OrientedPiece(piece1) != OrientedPiece(clone1)
        assert OrientedPiece(piece1) != OrientedPiece(piece2)

        assert OrientedPiece(piece1) != OrientedPiece(piece1, flip=True)
        assert OrientedPiece(piece1) != OrientedPiece(piece1, turn=Turn.TURN_90)
        assert OrientedPiece(piece1) != OrientedPiece(
            piece1, flip=True, turn=Turn.TURN_180
        )

        assert OrientedPiece(piece1, flip=True) == OrientedPiece(piece1, flip=True)
        assert OrientedPiece(piece1, turn=Turn.TURN_90) == OrientedPiece(
            piece1, turn=Turn.TURN_90
        )
        assert OrientedPiece(piece1, flip=True, turn=Turn.TURN_180) == OrientedPiece(
            piece1, flip=True, turn=Turn.TURN_180
        )

    @pytest.mark.parametrize(
        "flip1,turn1,flip2,turn2,fits",
        [
            (False, Turn.NO_TURN, False, Turn.NO_TURN, False),
            (False, Turn.TURN_90, False, Turn.TURN_90, True),
        ],
    )
    def test_fits_right(
        self, flip1: bool, turn1: Turn, flip2: bool, turn2: Turn, fits: bool
    ) -> None:
        """fits_right() returns True when oriented to fit."""
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.DIAMOND)
        piece2 = Piece(Shape.CLUB, Shape.CLUB, Shape.HEART, Shape.SPADE)
        op1 = OrientedPiece(piece1, flip1, turn1)
        op2 = OrientedPiece(piece2, flip2, turn2)
        assert op1.fits_right(op2) is fits


class TestRowPair:
    def test_init(self) -> None:
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)
        piece2 = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op1 = OrientedPiece(piece1)
        op2 = OrientedPiece(piece2)
        rp = RowPair(op1, op2)

        assert str(rp) == "Red-♥♦♢♡ → Red-♠♦♡♢"
        assert repr(rp) == (
            "RowPair(OrientedPiece(Piece("
            "Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)),"
            " OrientedPiece(Piece("
            "Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)))"
        )

    def test_rows_with(self) -> None:
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)
        piece2 = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op1 = OrientedPiece(piece1)
        op2 = OrientedPiece(piece2)
        rp = RowPair(op1, op2)

        # Can not make a row with a piece in the pair
        assert rp.rows_with(piece1) == set()
        assert rp.rows_with(piece2) == set()

        piece3 = Piece(Shape.SPADE, Shape.SPADE, Shape.HEART, Shape.CLUB)
        assert rp.rows_with(piece3) == set()

        piece4 = Piece(Shape.DIAMOND, Shape.CLUB, Shape.CLUB, Shape.DIAMOND)
        expected = [
            Row(
                OrientedPiece(piece1),
                OrientedPiece(piece2),
                OrientedPiece(piece4),
            ),
            Row(
                OrientedPiece(piece1),
                OrientedPiece(piece2),
                OrientedPiece(piece4, flip=True, turn=Turn.TURN_180),
            ),
        ]
        assert sorted(expected) == expected
        assert rp.rows_with(piece4) == set(expected)


class TestRow:
    def test_init(self) -> None:
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)
        piece2 = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        piece3 = Piece(Shape.SPADE, Shape.SPADE, Shape.HEART, Shape.CLUB)
        row = Row(OrientedPiece(piece1), OrientedPiece(piece2), OrientedPiece(piece3))
        assert str(row) == "Red-♥♦♢♡ → Red-♠♦♡♢ → Red-♠♠♡♧"
        assert repr(row) == (
            "Row(OrientedPiece(Piece("
            "Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)),"
            " OrientedPiece(Piece("
            "Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)),"
            " OrientedPiece(Piece("
            "Shape.SPADE, Shape.SPADE, Shape.HEART, Shape.CLUB)))"
        )


class TestPuzzle:
    def test_init_default(self) -> None:
        puzzle = Puzzle()
        assert puzzle.width == 0
        assert puzzle.height == 0
        assert puzzle.pieces == ()
        assert puzzle.get(0, 0) is EmptySpot
        assert str(puzzle) == "(Empty 0x0 Puzzle)"
        assert repr(puzzle) == "Puzzle()"

    def test_init_blank(self) -> None:
        puzzle = Puzzle(1, 1)
        assert puzzle.width == 1
        assert puzzle.height == 1
        assert puzzle.pieces == (EmptySpot,)
        assert puzzle.get(0, 0) is EmptySpot
        assert str(puzzle) == "(Empty 1x1 Puzzle)"
        assert repr(puzzle) == "Puzzle(1, 1)"

    def test_init_piece(self) -> None:
        piece = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)
        op = OrientedPiece(piece)
        puzzle = Puzzle(1, 1, (op,))
        assert puzzle.width == 1
        assert puzzle.height == 1
        assert puzzle.pieces == (op,)
        assert (
            str(puzzle)
            == """\
┌♥┐
♡R♦
└♢┘"""
        )
        assert (
            repr(puzzle)
            == "Puzzle(1, 1, (OrientedPiece(Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)),))"
        )

    def test_init_missing_piece(self) -> None:
        op1 = OrientedPiece(
            Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)
        )
        op2 = OrientedPiece(
            Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        )
        op3 = OrientedPiece(Piece(Shape.DIAMOND, Shape.CLUB, Shape.CLUB, Shape.DIAMOND))

        puzzle = Puzzle(2, 2, (op1, op2, op3))
        assert puzzle.width == 2
        assert puzzle.height == 2
        assert puzzle.pieces == (op1, op2, op3, EmptySpot)
        expected = """\
┌♥┬♠┐
♡R♦R♦
├♦┼♡┘
♢R♣  \n\
└♧┘  """
        assert str(puzzle) == expected


class TestSolvePuzzle:
    def test_fit_left_right(self, piece4: Piece, piece9: Piece) -> None:
        """A piece with one possible matching side fits 8 ways."""
        assert str(piece4) == "Red-♦♣♧♢"
        assert str(piece9) == "Red-♥♠♤♧"
        expected_orientations = [
            (piece9, False, Turn.NO_TURN, piece4, False, Turn.NO_TURN),
            (piece9, False, Turn.NO_TURN, piece4, True, Turn.TURN_180),
            (piece4, False, Turn.TURN_180, piece9, False, Turn.TURN_180),
            (piece4, False, Turn.TURN_180, piece9, True, Turn.NO_TURN),
            (piece4, True, Turn.NO_TURN, piece9, False, Turn.TURN_180),
            (piece4, True, Turn.NO_TURN, piece9, True, Turn.NO_TURN),
            (piece9, True, Turn.TURN_180, piece4, False, Turn.NO_TURN),
            (piece9, True, Turn.TURN_180, piece4, True, Turn.TURN_180),
        ]
        expected = [
            Puzzle(2, 1, (OrientedPiece(p1, f1, t1), OrientedPiece(p2, f2, t2)))
            for p1, f1, t1, p2, f2, t2 in expected_orientations
        ]
        assert sorted(expected) == expected
        puzzles = solve_puzzle(2, 1, (piece4, piece9))
        assert puzzles == set(expected)

    def test_fit_top_bottom(self, piece4: Piece, piece9: Piece) -> None:
        """A piece with one possible matching side fits 8 ways."""
        assert str(piece4) == "Red-♦♣♧♢"
        assert str(piece9) == "Red-♥♠♤♧"
        expected_orientations = [
            (piece9, False, Turn.TURN_270, piece4, False, Turn.TURN_270),
            (piece9, False, Turn.TURN_270, piece4, True, Turn.TURN_90),
            (piece4, False, Turn.TURN_90, piece9, False, Turn.TURN_90),
            (piece4, False, Turn.TURN_90, piece9, True, Turn.TURN_270),
            (piece9, True, Turn.TURN_90, piece4, False, Turn.TURN_270),
            (piece9, True, Turn.TURN_90, piece4, True, Turn.TURN_90),
            (piece4, True, Turn.TURN_270, piece9, False, Turn.TURN_90),
            (piece4, True, Turn.TURN_270, piece9, True, Turn.TURN_270),
        ]
        expected = [
            Puzzle(1, 2, (OrientedPiece(p1, f1, t1), OrientedPiece(p2, f2, t2)))
            for p1, f1, t1, p2, f2, t2 in expected_orientations
        ]
        assert sorted(expected) == expected
        puzzles = solve_puzzle(1, 2, (piece4, piece9))
        assert puzzles == set(expected)

    def test_no_fit_self(self, piece4: Piece) -> None:
        """A piece doesn't fit itself."""
        assert solve_puzzle(1, 2, (piece4, piece4)) == set()

    def test_fits_none(self) -> None:
        """A piece with no matches has no fits."""
        piece1 = Piece(Shape.SPADE, Shape.DIAMOND, Shape.SPADE, Shape.DIAMOND)
        piece2 = Piece(Shape.CLUB, Shape.HEART, Shape.CLUB, Shape.HEART)
        assert str(piece1) == "Red-♠♦♤♢"
        assert str(piece2) == "Red-♣♥♧♡"
        assert solve_puzzle(1, 2, (piece1, piece2)) == set()
