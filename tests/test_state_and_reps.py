from backend.rep_counter import RepCounter
from backend.state_machine import (
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


def test_state_requires_consecutive_matching_candidates():
    machine = StateMachine(required_stable_frames=3)

    assert machine.update(Phase.DOWN) == Phase.UNKNOWN
    assert machine.update(Phase.UP) == Phase.UNKNOWN
    assert machine.update(Phase.DOWN) == Phase.UNKNOWN
    assert machine.update(Phase.DOWN) == Phase.UNKNOWN
    assert machine.update(Phase.DOWN) == Phase.DOWN


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


def test_rep_counts_when_transition_phase_occurs_between_down_and_up():
    counter = RepCounter()

    assert not counter.update(Phase.DOWN, True)
    assert not counter.update(Phase.TRANSITION, True)
    assert counter.update(Phase.UP, True)
    assert counter.count == 1


def test_invalid_return_to_up_does_not_count_or_leave_rep_armed():
    counter = RepCounter()

    counter.update(Phase.DOWN, True)
    assert not counter.update(Phase.UP, False)
    assert not counter.update(Phase.UP, True)
    assert counter.count == 0


def test_rep_counter_collects_metrics_for_the_completed_cycle():
    counter = RepCounter()

    counter.update(Phase.DOWN, True, {"knee_angle": 100.0})
    counter.update(Phase.TRANSITION, True, {"knee_angle": 90.0})
    assert counter.update(Phase.UP, True, {"knee_angle": 170.0})

    assert counter.completed_metrics == {
        "knee_angle": (90.0, 170.0),
    }