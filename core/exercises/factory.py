from .deadlift import DeadliftAnalyzer
from .pushup import PushUpAnalyzer
from .squat import SquatAnalyzer


EXERCISES = {
    "Squat": SquatAnalyzer,
    "Push-Up": PushUpAnalyzer,
    "Deadlift": DeadliftAnalyzer,
}


def create_analyzer(
    name: str,
):

    try:
        analyzer_class = EXERCISES[name]

    except KeyError as exc:

        raise ValueError(
            f"Unsupported exercise: {name}"
        ) from exc

    return analyzer_class()