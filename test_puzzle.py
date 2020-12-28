"""Tests for puzzle.py"""

import pytest

from puzzle import Orientation, Shape, End, Side, Turn, Piece, OrientedPiece


class TestShape:
    def test_order(self):
        assert Shape.CLUB < Shape.DIAMOND < Shape.HEART < Shape.SPADE

    def test_str(self):
        assert str(Shape.CLUB) == "Shape.CLUB"

    def test_label(self):
        assert Shape.DIAMOND.label == "Diamond"


class TestEnd:
    def test_order(self):
        assert End.TAB < End.BLANK


class TestSide:
    def test_order(self):
        assert Side.RED < Side.BLACK


class TestTurn:
    def test_order(self):
        assert Turn.NO_TURN < Turn.TURN_90 < Turn.TURN_180 < Turn.TURN_270


class TestOrientation:
    def test_standard_orientation(self):
        """Test an Orientation initialized to standard orientation"""
        orient = Orientation(
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
        assert orient.is_valid()
        assert orient.is_standard()
        standard = orient.to_standard()
        assert standard == orient
        assert str(orient) == "Red-♥♦♢♡"
        assert repr(orient) == (
            "Orientation(Side.RED,"
            " Shape.HEART, End.TAB, Shape.DIAMOND, End.TAB,"
            " Shape.DIAMOND, End.BLANK, Shape.HEART, End.BLANK)"
        )
        assert orient.side == Side.RED

        assert orient.north == (Shape.HEART, End.TAB)
        assert orient.east == (Shape.DIAMOND, End.TAB)
        assert orient.south == (Shape.DIAMOND, End.BLANK)
        assert orient.west == (Shape.HEART, End.BLANK)

        assert orient.north_shape == Shape.HEART
        assert orient.east_shape == Shape.DIAMOND
        assert orient.south_shape == Shape.DIAMOND
        assert orient.west_shape == Shape.HEART

        assert orient.north_end == End.TAB
        assert orient.east_end == End.TAB
        assert orient.south_end == End.BLANK
        assert orient.west_end == End.BLANK

    def test_rotated_90(self):
        """Test an Orientation rotated 90 from standard orientation"""
        orient = Orientation(
            Side.RED,
            Shape.HEART,
            End.BLANK,
            Shape.HEART,
            End.TAB,
            Shape.DIAMOND,
            End.TAB,
            Shape.DIAMOND,
            End.BLANK,
        )
        assert orient.is_valid()
        assert not orient.is_standard()
        standard = orient.to_standard()
        assert standard != orient
        rotated = orient.reorient(turn=Turn.TURN_270)
        assert standard == rotated
        assert str(orient) == "Red-♡♥♦♢"

    def test_flipped(self):
        """Test an Orientation flipped from standard orientation"""
        orient = Orientation(
            Side.BLACK,
            Shape.HEART,
            End.TAB,
            Shape.HEART,
            End.BLANK,
            Shape.DIAMOND,
            End.BLANK,
            Shape.DIAMOND,
            End.TAB,
        )
        assert orient.is_valid()
        assert not orient.is_standard()
        standard = orient.to_standard()
        assert standard != orient
        rotated = orient.reorient(flip=True)
        assert standard == rotated
        assert str(orient) == "Black-♥♡♢♦"

    def test_reorientation(self):
        """Test reorientation."""
        orient = Orientation(
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
        assert orient.is_valid()
        assert orient.is_standard()
        assert str(orient) == "Red-♥♦♢♡"

        # Turn 90 (clockwise) four times
        rotated = orient.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♡♥♦♢"
        rotated = rotated.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♢♡♥♦"
        rotated = rotated.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♦♢♡♥"
        rotated = rotated.reorient(turn=Turn.TURN_90)
        assert str(rotated) == "Red-♥♦♢♡"
        assert rotated == orient

        # Turn 180 twice
        rotated = orient.reorient(turn=Turn.TURN_180)
        assert str(rotated) == "Red-♢♡♥♦"
        rotated = rotated.reorient(turn=Turn.TURN_180)
        assert str(rotated) == "Red-♥♦♢♡"
        assert rotated == orient

        # Turn 270 four times
        rotated = orient.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♦♢♡♥"
        rotated = rotated.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♢♡♥♦"
        rotated = rotated.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♡♥♦♢"
        rotated = rotated.reorient(turn=Turn.TURN_270)
        assert str(rotated) == "Red-♥♦♢♡"
        assert rotated == orient

        # Flip (Left to Right)
        flipped = orient.reorient(flip=True)
        assert str(flipped) == "Black-♥♡♢♦"
        flipped = flipped.reorient(flip=True)
        assert str(flipped) == "Red-♥♦♢♡"
        assert flipped == orient

        # Flip then rotate
        flipped = orient.reorient(flip=True, turn=Turn.TURN_90)
        assert str(flipped) == "Black-♦♥♡♢"
        flipped = flipped.reorient(flip=True, turn=Turn.TURN_90)
        assert str(flipped) == "Red-♥♦♢♡"
        assert flipped == orient

    def test_invalid(self):
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

    def test_order(self):
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
        or_least2 = Orientation(
            Side.RED,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
            Shape.CLUB,
            End.TAB,
            Shape.DIAMOND,
            End.TAB,
        )
        assert or_least < or_least2
        assert or_least2 > or_least


class TestPieces:
    def test_default_init(self):
        """Default is the standard orientation"""
        piece = Piece(Shape.HEART, Shape.SPADE, Shape.SPADE, Shape.CLUB)
        assert str(piece) == "Red-♥♠♤♧"
        assert repr(piece) == (
            "Piece(Shape.HEART, Shape.SPADE, Shape.SPADE, Shape.CLUB)"
        )
        assert piece.side == Side.RED

        assert piece.north == (Shape.HEART, End.TAB)
        assert piece.east == (Shape.SPADE, End.TAB)
        assert piece.south == (Shape.SPADE, End.BLANK)
        assert piece.west == (Shape.CLUB, End.BLANK)

        assert piece.north_shape == Shape.HEART
        assert piece.east_shape == Shape.SPADE
        assert piece.south_shape == Shape.SPADE
        assert piece.west_shape == Shape.CLUB

        assert piece.north_end == End.TAB
        assert piece.east_end == End.TAB
        assert piece.south_end == End.BLANK
        assert piece.west_end == End.BLANK

    def test_full_init(self):
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

    def test_fits_none(self):
        """A piece with no matches has no fits."""
        piece1 = Piece(
            Shape.SPADE,
            Shape.DIAMOND,
            Shape.SPADE,
            Shape.DIAMOND,
        )
        piece2 = Piece(
            Shape.CLUB,
            Shape.HEART,
            Shape.CLUB,
            Shape.HEART,
        )
        assert str(piece1) == "Red-♠♦♤♢"
        assert str(piece2) == "Red-♣♥♧♡"
        assert piece1.fits_right(piece2) == set()

    def test_fit_one_side(self):
        """A piece with one possible matching side fits 4 ways."""
        piece1 = Piece(
            Shape.DIAMOND,
            Shape.HEART,
            Shape.HEART,
            Shape.HEART,
        )
        piece2 = Piece(
            Shape.CLUB,
            Shape.CLUB,
            Shape.DIAMOND,
            Shape.CLUB,
        )
        assert str(piece1) == "Red-♦♥♡♡"
        assert str(piece2) == "Red-♣♣♢♧"
        expected = [
            (
                OrientedPiece(piece1, turn=Turn.TURN_90),
                OrientedPiece(piece2, turn=Turn.TURN_90),
            ),
            (
                OrientedPiece(piece1, turn=Turn.TURN_90),
                OrientedPiece(piece2, flip=True, turn=Turn.TURN_90),
            ),
            (
                OrientedPiece(piece1, flip=True, turn=Turn.TURN_90),
                OrientedPiece(piece2, turn=Turn.TURN_90),
            ),
            (
                OrientedPiece(piece1, flip=True, turn=Turn.TURN_90),
                OrientedPiece(piece2, flip=True, turn=Turn.TURN_90),
            ),
        ]
        assert sorted(expected) == expected
        assert piece1.fits_right(piece2) == set(expected)


class TestOrientedPiece:
    def test_default_init(self):
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

    def test_flipped_init(self):
        """A piece can be flipped at init."""
        piece = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op = OrientedPiece(piece, flip=True)
        assert str(op) == "Black-♠♢♡♦"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " flip=True)"
        )

    def test_turned_init(self):
        """A piece can be turned at init."""
        piece = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op = OrientedPiece(piece, turn=Turn.TURN_90)
        assert str(op) == "Red-♢♠♦♡"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " turn=Turn.TURN_90)"
        )

    def test_full_init(self):
        """A piece can be flipped and turned at init."""
        piece = Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND)
        op = OrientedPiece(piece, flip=True, turn=Turn.TURN_90)
        assert str(op) == "Black-♦♠♢♡"
        assert repr(op) == (
            "OrientedPiece("
            "Piece(Shape.SPADE, Shape.DIAMOND, Shape.HEART, Shape.DIAMOND),"
            " flip=True, turn=Turn.TURN_90)"
        )

    def test_equality(self):
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
    def test_fits_right(self, flip1, turn1, flip2, turn2, fits):
        """fits_right() returns True when oriented to fit."""
        piece1 = Piece(Shape.HEART, Shape.DIAMOND, Shape.DIAMOND, Shape.DIAMOND)
        piece2 = Piece(Shape.CLUB, Shape.CLUB, Shape.HEART, Shape.SPADE)
        op1 = OrientedPiece(piece1, flip1, turn1)
        op2 = OrientedPiece(piece2, flip2, turn2)
        assert op1.fits_right(op2) is fits
