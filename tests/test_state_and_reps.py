from core.rep_counter import RepCounter
from core.state_machine import (
    Phase,
    StateMachine,
)


def test_state_stabilizes():

    machine = StateMachine(
        required_stable_frames=2
    )

    assert (
        machine.update(
            Phase.DOWN
        )
        == Phase.UNKNOWN
    )

    assert (
        machine.update(
            Phase.DOWN
        )
        == Phase.DOWN
    )


def test_rep_requires_down_then_up():

    counter = RepCounter()

    assert not counter.update(
        Phase.UP,
        True,
    )

    assert not counter.update(
        Phase.DOWN,
        True,
    )

    assert counter.update(
        Phase.UP,
        True,
    )

    assert counter.count == 1