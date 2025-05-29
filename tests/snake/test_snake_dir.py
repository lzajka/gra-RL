from general.direction import Direction
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def assert_deletion(a : Direction, b : Direction, expected : Direction):
    c = a.remove_rotation(b)
    assert c == expected, f"{a} - {b} != {c}, oczekiwano {c}"

def assert_addition(a : Direction, b : Direction, expected : Direction):
    c = a.add_rotation(b)
    assert c == expected, f"{a} + {b} != {c}, oczekiwano {c}"

def perform_tests(a : Direction, b : Direction, expected : Direction):
    assert_addition(a, b, expected)
    assert_addition(b, a, expected)

    # a + b = expected -> a = expected - b ^ b = expected - a
    assert_deletion(expected, b, a)
    assert_deletion(expected, a, b)

@pytest.mark.parametrize('dir_a,expected', 
[
    (Direction.UP, Direction.UP),
    (Direction.RIGHT, Direction.RIGHT),
    (Direction.DOWN, Direction.DOWN),
    (Direction.LEFT, Direction.LEFT)
    
    ])
def test_up(dir_a: Direction, expected: Direction):
    perform_tests(dir_a, Direction.UP, expected)

@pytest.mark.parametrize('dir_a,expected',
[
    (Direction.UP, Direction.RIGHT),
    (Direction.RIGHT, Direction.DOWN),
    (Direction.DOWN, Direction.LEFT),
    (Direction.LEFT, Direction.UP)
    
    ])
def test_right(dir_a: Direction, expected: Direction):
    perform_tests(dir_a, Direction.RIGHT, expected)
@pytest.mark.parametrize('dir_a,expected',
[
    (Direction.UP, Direction.DOWN),
    (Direction.RIGHT, Direction.LEFT),
    (Direction.DOWN, Direction.UP),
    (Direction.LEFT, Direction.RIGHT)
    
    ])
def test_down(dir_a: Direction, expected: Direction):
    perform_tests(dir_a, Direction.DOWN, expected)

@pytest.mark.parametrize('dir_a,expected',
[
    (Direction.UP, Direction.LEFT),
    (Direction.RIGHT, Direction.UP),
    (Direction.DOWN, Direction.RIGHT),
    (Direction.LEFT, Direction.DOWN)
    
    ])
def test_left(dir_a: Direction, expected: Direction):
    perform_tests(dir_a, Direction.LEFT, expected)

# l r u d
@pytest.mark.parametrize('dir,expected',[
                         (Direction.LEFT,   [1,0,0,0]),
                         (Direction.RIGHT,  [0,1,0,0]),
                         (Direction.UP,     [0,0,1,0]),
                         (Direction.DOWN,   [0,0,0,1])])
def test_get_dummies(dir : Direction, expected):
    assert dir.get_dummies() == expected, 'expected '