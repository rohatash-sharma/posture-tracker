from .bicep_curl import BicepCurlAnalyzer
from .deadlift import DeadliftAnalyzer
from .lunge import LungeAnalyzer
from .plank import PlankAnalyzer
from .pushup import PushUpAnalyzer
from .squat import SquatAnalyzer


EXERCISES = {
    "Bicep Curl": BicepCurlAnalyzer,
    "Squat": SquatAnalyzer,
    "Push-Up": PushUpAnalyzer,
    "Deadlift": DeadliftAnalyzer,
    "Lunge": LungeAnalyzer,
    "Plank": PlankAnalyzer,
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