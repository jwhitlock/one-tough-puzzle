"""Tests for puzzle.py"""

from typing import Tuple

import pytest

from puzzle import (
    Edge,
    EmptySpot,
    End,
    Orientation,
    OrientedPiece,
    Piece,
    Puzzle,
    Row,
    RowPair,
    Shape,
    Side,
    Turn,
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


@pytest.fixture
def all_clubs() -> Orientation:
    return Orientation(
        Side.RED,
        Shape.CLUB,
        End.TAB,
        Shape.CLUB,
        End.TAB,
        Shape.CLUB,
        End.BLANK,
        Shape.CLUB,
        End.BLANK,
    )


@pytest.fixture
def all_hearts() -> Orientation:
    return Orientation(
        Side.RED,
        Shape.HEART,
        End.TAB,
        Shape.HEART,
        End.TAB,
        Shape.HEART,
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
            Shape.HEART,
            End.TAB,
            Shape.HEART,
            End.TAB,
            Shape.HEART,
            End.TAB,  # Too many tabs
            Shape.HEART,
            End.BLANK,
        )

        assert not invalid.is_valid()

    def test_order(
        self,
        all_clubs: Orientation,
        all_hearts: Orientation,
        standard_orientation: Orientation,
    ) -> None:
        assert all_clubs < standard_orientation < all_hearts
        assert all_hearts > standard_orientation > all_clubs

    def test_fits(self, all_clubs: Orientation, all_hearts: Orientation) -> None:
        assert all_clubs.fits_right(all_clubs)
        assert not all_clubs.fits_right(all_hearts)

        assert all_clubs.fits_right(all_clubs)
        assert not all_clubs.fits_right(all_hearts)

        assert all_clubs.fits_above(all_clubs)
        assert not all_clubs.fits_above(all_hearts)

        assert all_clubs.fits_below(all_clubs)
        assert not all_clubs.fits_below(all_hearts)


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
def piece1(otp_pieces: Tuple[Piece, ...]) -> Piece:
    return otp_pieces[0]  # Red-♠♦♡♢


@pytest.fixture
def piece2(otp_pieces: Tuple[Piece, ...]) -> Piece:
    return otp_pieces[1]  # Red-♣♥♤♡


@pytest.fixture
def piece3(otp_pieces: Tuple[Piece, ...]) -> Piece:
    return otp_pieces[2]  # Red-♥♦♢♡


@pytest.fixture
def piece4(otp_pieces: Tuple[Piece, ...]) -> Piece:
    return otp_pieces[3]  # Red-♦♣♧♢


@pytest.fixture
def piece9(otp_pieces: Tuple[Piece, ...]) -> Piece:
    return otp_pieces[8]


class TestPiece:
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

    def test_fits_right_left(self, piece1: Piece, piece4: Piece) -> None:
        assert str(piece1) == "Red-♠♦♡♢"
        assert str(piece4) == "Red-♦♣♧♢"
        assert piece1.fits_right(piece4)
        assert not piece4.fits_right(piece1)
        assert not piece1.fits_right(piece1)

        assert piece4.fits_left(piece1)
        assert not piece1.fits_left(piece4)
        assert not piece1.fits_left(piece1)

    def test_fits_above_below(self, piece2: Piece, piece4: Piece) -> None:
        assert str(piece2) == "Red-♣♥♤♡"
        assert str(piece4) == "Red-♦♣♧♢"
        assert piece2.fits_above(piece4)
        assert not piece4.fits_above(piece2)
        assert not piece2.fits_above(piece2)

        assert piece4.fits_below(piece2)
        assert not piece2.fits_below(piece4)
        assert not piece2.fits_below(piece2)


class TestOrientedPiece:
    def test_default_init(self, piece1: Piece) -> None:
        """Default is the standard orientation."""
        op = OrientedPiece(piece1)
        assert str(op) == "Red-♠♦♡♢"
        assert repr(op) == (
            "OrientedPiece(Piece("
            "Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND))"
        )
        assert op.is_empty is False

        assert op.side == Side.RED

        assert op.north == (Shape.SPADE, End.TAB)
        assert op.east == (Shape.DIAMOND, End.TAB)
        assert op.south == (Shape.HEART, End.BLANK)
        assert op.west == (Shape.DIAMOND, End.BLANK)

        assert op.north_shape == Shape.SPADE
        assert op.east_shape == Shape.DIAMOND
        assert op.south_shape == Shape.HEART
        assert op.west_shape == Shape.DIAMOND

        assert op.north_end == End.TAB
        assert op.east_end == End.TAB
        assert op.south_end == End.BLANK
        assert op.west_end == End.BLANK

    def test_flipped_init(self, piece1: Piece) -> None:
        """A piece can be flipped at init."""
        op = OrientedPiece(piece1, flip=True)
        assert str(op) == "Black-♠♢♡♦"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " flip=True)"
        )

    def test_turned_init(self, piece1: Piece) -> None:
        """A piece can be turned at init."""
        op = OrientedPiece(piece1, turn=Turn.TURN_90)
        assert str(op) == "Red-♢♠♦♡"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " turn=Turn.TURN_90)"
        )

    def test_full_init(self, piece1: Piece) -> None:
        """A piece can be flipped and turned at init."""
        op = OrientedPiece(piece1, flip=True, turn=Turn.TURN_90)
        assert str(op) == "Black-♦♠♢♡"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " flip=True, turn=Turn.TURN_90)"
        )

    def test_equality(self, piece1: Piece, piece4: Piece) -> None:
        """An OrientedPiece is equal when the same piece and orientation."""
        clone1 = Piece(
            piece1.north_shape, piece1.east_shape, piece1.south_shape, piece1.west_shape
        )
        assert str(piece1) == "Red-♠♦♡♢"
        assert str(clone1) == "Red-♠♦♡♢"
        assert str(piece4) == "Red-♦♣♧♢"
        assert piece1 != clone1
        assert str(piece1) == str(clone1)
        assert piece1 != piece4

        assert OrientedPiece(piece1) == OrientedPiece(piece1)
        assert OrientedPiece(piece1) != OrientedPiece(clone1)
        assert OrientedPiece(piece1) != OrientedPiece(piece4)

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
        "flip,turn,str_out,fits",
        (
            (False, Turn.NO_TURN, "Red-♠♦♡♢", True),
            (False, Turn.TURN_90, "Red-♢♠♦♡", False),
            (False, Turn.TURN_180, "Red-♡♢♠♦", False),
            (False, Turn.TURN_270, "Red-♦♡♢♠", False),
            (True, Turn.NO_TURN, "Black-♠♢♡♦", False),
            (True, Turn.TURN_90, "Black-♦♠♢♡", False),
            (True, Turn.TURN_180, "Black-♡♦♠♢", True),
            (True, Turn.TURN_270, "Black-♢♡♦♠", False),
        ),
    )
    def test_fits_right(
        self,
        piece1: Piece,
        piece4: Piece,
        flip: bool,
        turn: Turn,
        str_out: str,
        fits: bool,
    ) -> None:
        """fits_right() returns True when oriented to fit."""
        op1 = OrientedPiece(piece1, flip, turn)
        assert str(op1) == str_out
        op4 = OrientedPiece(piece4)
        assert str(op4) == "Red-♦♣♧♢"
        assert op1.fits_right(op4) is fits

    @pytest.mark.parametrize(
        "flip,turn,str_out,fits",
        (
            (False, Turn.NO_TURN, "Red-♠♦♡♢", True),
            (False, Turn.TURN_90, "Red-♢♠♦♡", False),
            (False, Turn.TURN_180, "Red-♡♢♠♦", False),
            (False, Turn.TURN_270, "Red-♦♡♢♠", False),
            (True, Turn.NO_TURN, "Black-♠♢♡♦", False),
            (True, Turn.TURN_90, "Black-♦♠♢♡", False),
            (True, Turn.TURN_180, "Black-♡♦♠♢", True),
            (True, Turn.TURN_270, "Black-♢♡♦♠", False),
        ),
    )
    def test_fits_left(
        self,
        piece1: Piece,
        piece3: Piece,
        flip: bool,
        turn: Turn,
        str_out: str,
        fits: bool,
    ) -> None:
        """fits_left() returns True when oriented to fit."""
        op1 = OrientedPiece(piece1, flip, turn)
        assert str(op1) == str_out
        op3 = OrientedPiece(piece3)
        assert str(op3) == "Red-♥♦♢♡"
        assert op1.fits_left(op3) is fits

    @pytest.mark.parametrize(
        "flip,turn,str_out,fits",
        (
            (False, Turn.NO_TURN, "Red-♥♠♤♧", True),
            (False, Turn.TURN_90, "Red-♧♥♠♤", False),
            (False, Turn.TURN_180, "Red-♤♧♥♠", False),
            (False, Turn.TURN_270, "Red-♠♤♧♥", False),
            (True, Turn.NO_TURN, "Black-♥♧♤♠", True),
            (True, Turn.TURN_90, "Black-♠♥♧♤", False),
            (True, Turn.TURN_180, "Black-♤♠♥♧", False),
            (True, Turn.TURN_270, "Black-♧♤♠♥", False),
        ),
    )
    def test_fits_above(
        self,
        piece9: Piece,
        piece1: Piece,
        flip: bool,
        turn: Turn,
        str_out: str,
        fits: bool,
    ) -> None:
        """fits_below() returns True when oriented to fit."""
        op9 = OrientedPiece(piece9, flip, turn)
        assert str(op9) == str_out
        op1 = OrientedPiece(piece1)
        assert str(op1) == "Red-♠♦♡♢"
        assert op9.fits_above(op1) is fits

    @pytest.mark.parametrize(
        "flip,turn,str_out,fits",
        (
            (False, Turn.NO_TURN, "Red-♥♠♤♧", True),
            (False, Turn.TURN_90, "Red-♧♥♠♤", False),
            (False, Turn.TURN_180, "Red-♤♧♥♠", False),
            (False, Turn.TURN_270, "Red-♠♤♧♥", False),
            (True, Turn.NO_TURN, "Black-♥♧♤♠", True),
            (True, Turn.TURN_90, "Black-♠♥♧♤", False),
            (True, Turn.TURN_180, "Black-♤♠♥♧", False),
            (True, Turn.TURN_270, "Black-♧♤♠♥", False),
        ),
    )
    def test_fits_below(
        self,
        piece9: Piece,
        piece1: Piece,
        flip: bool,
        turn: Turn,
        str_out: str,
        fits: bool,
    ) -> None:
        """fits_below() returns True when oriented to fit."""
        op9 = OrientedPiece(piece9, flip, turn)
        assert str(op9) == str_out
        op1 = OrientedPiece(piece1)
        assert str(op1) == "Red-♠♦♡♢"
        assert op9.fits_below(op1) is fits

    def test_fits_neighbors(
        self, piece1: Piece, piece2: Piece, piece3: Piece, piece4: Piece
    ) -> None:
        op1 = OrientedPiece(piece1)
        neighbors = {
            Edge.NORTH: OrientedPiece(piece2),
            Edge.SOUTH: OrientedPiece(piece3),
            Edge.EAST: OrientedPiece(piece4),
            Edge.WEST: EmptySpot(),
        }
        fits = op1.fits_neighbors(neighbors)
        assert fits == {
            Edge.NORTH: True,
            Edge.SOUTH: True,
            Edge.EAST: True,
            Edge.WEST: True,
        }
        assert op1.fits_all_neighbors(neighbors)

        neighbors = {
            Edge.NORTH: EmptySpot(),
            Edge.SOUTH: OrientedPiece(piece2),
            Edge.EAST: OrientedPiece(piece3),
            Edge.WEST: OrientedPiece(piece4),
        }
        fits = op1.fits_neighbors(neighbors)
        assert fits == {
            Edge.NORTH: True,
            Edge.SOUTH: False,
            Edge.EAST: False,
            Edge.WEST: False,
        }
        assert not op1.fits_all_neighbors(neighbors)


class TestEmptySpot:
    def test_init(self) -> None:
        es = EmptySpot()
        assert repr(es) == "EmptySpot()"
        assert es.is_empty is True

    def test_equality(self, piece1: Piece) -> None:
        eq1 = EmptySpot()
        eq2 = EmptySpot()
        assert eq1 != eq2
        assert piece1 != eq1
        assert eq1 != piece1

    def test_fits(self, piece1: Piece) -> None:
        eq1 = EmptySpot()
        eq2 = EmptySpot()
        assert eq1.fits_right(eq2)
        assert eq1.fits_left(eq2)
        assert eq1.fits_above(eq2)
        assert eq1.fits_below(eq2)

        assert eq1.fits_right(piece1)
        assert eq1.fits_left(piece1)
        assert eq1.fits_above(piece1)
        assert eq1.fits_below(piece1)

        assert piece1.fits_right(eq1)
        assert piece1.fits_left(eq1)
        assert piece1.fits_above(eq1)
        assert piece1.fits_below(eq1)

    def test_fits_neighbors(self, piece2: Piece, piece3: Piece, piece4: Piece) -> None:
        op1 = EmptySpot()
        neighbors = {
            Edge.NORTH: OrientedPiece(piece2),
            Edge.SOUTH: OrientedPiece(piece3),
            Edge.EAST: OrientedPiece(piece4),
            Edge.WEST: EmptySpot(),
        }
        fits = op1.fits_neighbors(neighbors)
        assert fits == {
            Edge.NORTH: True,
            Edge.SOUTH: True,
            Edge.EAST: True,
            Edge.WEST: True,
        }
        assert op1.fits_all_neighbors(neighbors)


class TestRowPair:
    def test_init(self) -> None:
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)  # 3
        piece2 = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)  # 1
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
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.HEART)  # 3
        piece2 = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)  # 1
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
        assert len(puzzle.pieces) == 0
        assert isinstance(puzzle.get(0, 0), EmptySpot)
        assert str(puzzle) == "(Empty 0x0 Puzzle)"
        assert repr(puzzle) == "Puzzle()"

    def test_init_blank(self) -> None:
        puzzle = Puzzle(1, 1)
        assert puzzle.width == 1
        assert puzzle.height == 1
        assert len(puzzle.pieces) == 1
        assert isinstance(puzzle.pieces[0], EmptySpot)
        assert isinstance(puzzle.get(0, 0), EmptySpot)
        assert str(puzzle) == "(Empty 1x1 Puzzle)"
        assert repr(puzzle) == "Puzzle(1, 1)"

    def test_init_piece(self, piece3: Piece) -> None:
        op3 = OrientedPiece(piece3)
        puzzle = Puzzle(1, 1, (op3,))
        assert puzzle.width == 1
        assert puzzle.height == 1
        assert puzzle.pieces == (op3,)
        assert (
            str(puzzle)
            == """\
┌♥┐
♡R♦
└♢┘"""
        )
        assert repr(puzzle) == f"Puzzle(1, 1, (OrientedPiece({piece3!r}),))"

    def test_init_missing_piece(
        self, piece3: Piece, piece1: Piece, piece4: Piece
    ) -> None:
        op3 = OrientedPiece(piece3)
        op1 = OrientedPiece(piece1)
        op4 = OrientedPiece(piece4)
        puzzle = Puzzle(2, 2, (op3, op1, op4))

        assert puzzle.width == 2
        assert puzzle.height == 2
        assert len(puzzle.pieces) == 4
        assert puzzle.pieces[:3] == (op3, op1, op4)
        assert puzzle.pieces[3].is_empty
        expected = """\
┌♥┬♠┐
♡R♦R♦
├♦┼♡┘
♢R♣  \n\
└♧┘  """
        assert str(puzzle) == expected

    def test_init_row_pair(self, piece1: Piece, piece3: Piece) -> None:
        op1 = OrientedPiece(piece1)
        op3 = OrientedPiece(piece3)
        assert str(op1) == "Red-♠♦♡♢"
        assert str(op3) == "Red-♥♦♢♡"
        puzzle = Puzzle(2, 1, (op3, op1))
        assert (
            str(puzzle)
            == """\
┌♥┬♠┐
♡R♦R♦
└♢┴♡┘\
"""
        )

    def test_init_fails_negative_width(self) -> None:
        with pytest.raises(ValueError) as err:
            Puzzle(-1, 0)
        assert str(err.value) == "Negative width is not allowed"

    def test_init_fails_negative_height(self) -> None:
        with pytest.raises(ValueError) as err:
            Puzzle(0, -1)
        assert str(err.value) == "Negative height is not allowed"

    def test_init_fails_only_width_zero(self) -> None:
        with pytest.raises(ValueError) as err:
            Puzzle(0, 1)
        assert str(err.value) == "width must be positive since height is positive"

    def test_init_fails_only_height_zero(self) -> None:
        with pytest.raises(ValueError) as err:
            Puzzle(1, 0)
        assert str(err.value) == "height must be positive since width is positive"

    def test_init_fails_too_many_pieces(self, piece1: Piece, piece2: Piece) -> None:
        with pytest.raises(ValueError) as err:
            Puzzle(1, 1, (OrientedPiece(piece1), OrientedPiece(piece2)))
        assert (
            str(err.value)
            == "2 pieces will not fit in a puzzle of size 1 (width 1, height 1)"
        )

    def test_init_fails_pieces_do_not_fit(self, piece1: Piece, piece2: Piece) -> None:
        with pytest.raises(ValueError) as err:
            Puzzle(2, 1, (OrientedPiece(piece1), OrientedPiece(piece2)))
        assert str(err.value) == (
            "Piece Red-♠♦♡♢ does not fit at col 0, row 0: Edge.EAST is Red-♣♥♤♡"
        )

    def test_get_neighbors(self, piece3: Piece, piece1: Piece, piece4: Piece) -> None:
        op3 = OrientedPiece(piece3)
        op1 = OrientedPiece(piece1)
        op4 = OrientedPiece(piece4)
        puzzle = Puzzle(2, 2, (op3, op1, op4))

        piece = puzzle.get(0, 0)
        assert piece == op3
        neighbors = puzzle.get_neighbors(0, 0)
        assert neighbors[Edge.NORTH].is_empty
        assert neighbors[Edge.SOUTH] == op4
        assert neighbors[Edge.WEST].is_empty
        assert neighbors[Edge.EAST] == op1

        piece = puzzle.get(1, 1)
        assert piece.is_empty
        neighbors = puzzle.get_neighbors(1, 1)
        assert neighbors[Edge.NORTH] == op1
        assert neighbors[Edge.SOUTH].is_empty
        assert neighbors[Edge.WEST] == op4
        assert neighbors[Edge.EAST].is_empty


class TestSolvePuzzle:
    def test_fit_left_right(self, piece4: Piece, piece9: Piece) -> None:
        """A piece with one possible matching side fits 8 ways."""
        assert str(piece4) == "Red-♦♣♧♢"
        assert str(piece9) == "Red-♥♠♤♧"
        expected_orientations = [
            (piece4, False, Turn.NO_TURN, piece9, False, Turn.NO_TURN),
            (piece4, False, Turn.NO_TURN, piece9, True, Turn.TURN_180),
            (piece9, False, Turn.TURN_180, piece4, False, Turn.TURN_180),
            (piece9, False, Turn.TURN_180, piece4, True, Turn.NO_TURN),
            (piece9, True, Turn.NO_TURN, piece4, False, Turn.TURN_180),
            (piece9, True, Turn.NO_TURN, piece4, True, Turn.NO_TURN),
            (piece4, True, Turn.TURN_180, piece9, False, Turn.NO_TURN),
            (piece4, True, Turn.TURN_180, piece9, True, Turn.TURN_180),
        ]
        expected = [
            Puzzle(2, 1, (OrientedPiece(p1, f1, t1), OrientedPiece(p2, f2, t2)))
            for p1, f1, t1, p2, f2, t2 in expected_orientations
        ]
        assert sorted(expected) == expected
        puzzles = solve_puzzle(2, 1, (piece4, piece9))
        assert puzzles == set(expected)
        assert (
            str(expected[0])
            == """\
┌♦┬♥┐
♢R♣R♠
└♧┴♤┘\
"""
        )

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
        assert (
            str(expected[0])
            == """\
┌♠┐
♥R♤
├♣┤
♦R♧
└♢┘\
"""
        )

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
