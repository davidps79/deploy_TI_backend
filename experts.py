from typing import Dict, Tuple

from dtos import Quiz, QuizAnswers
from anxiety import AnxietyExpertSystem, anxiety_quiz
from depression import DepressionExpertSystem, depression_quiz
from entity import Expert
from insomnia import InsomniaExpertSystem, insomnia_quiz
from stress import StressExpertSystem, stress_quiz
from unifiedSystem import UnifiedExpertSystem, screening_quiz

# lock = threading.Lock()
# : Dict[str, Tuple[Expert, Quiz]]
conditions = {
    "screening": (UnifiedExpertSystem, screening_quiz),
    "anxiety": (AnxietyExpertSystem, anxiety_quiz),
    "insomnia": (InsomniaExpertSystem, insomnia_quiz),
    "depression": (DepressionExpertSystem, depression_quiz),
    "stress": (StressExpertSystem, stress_quiz)
}


def get_quiz(condition: str) -> Quiz:
    return conditions[condition][1]


def get_expert(condition: str):
    return conditions[condition][0]


def get_analysis(answer: QuizAnswers):
    expert_class = get_expert(answer.condition)
    expert = expert_class()

    expert.reset()
    expert.input_data(answer.answers)
    expert.run()

    if answer.condition == "screening":
        return expert.get_diagnosis()
    return expert.get_recommendations()
