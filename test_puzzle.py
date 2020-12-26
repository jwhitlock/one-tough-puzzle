"""Tests for puzzle.py"""

import pytest

from puzzle import Orientation, Shape, End, Side, Turn, Piece


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


class TestPieces:
    def test_default_init(self):
        """Default is standard order"""
        piece = Piece(Shape.HEART, Shape.SPADE, Shape.SPADE, Shape.CLUB)
        assert str(piece) == "Red-♥♠♤♧"
        assert repr(piece) == (
            "Piece(Shape.HEART, Shape.SPADE, Shape.SPADE, Shape.CLUB)"
        )

    def test_full_init(self):
        """A non-standard order is converted to standard."""
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
