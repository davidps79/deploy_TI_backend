from experta import *

from dtos import Quiz, Question
from anxiety import AnxietyExpertSystem
from depression import DepressionExpertSystem
from entity import Expert
from insomnia import InsomniaExpertSystem
from stress import StressExpertSystem


def ask_menu(question, options):
    print(question)
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
    choice = int(input("Seleccione una opción: "))
    return options[choice - 1]


screening_quiz = Quiz([
    Question(
        "age",
        "¿Cuál es su edad?",
        ["Menos de 18", "18-25", "26-35", "36-45", "46-55", "56-65", "Más de 65"],
        1,
    ),
    Question(
        "gender",
        "¿Cuál es su género?",
        ["Masculino", "Femenino", "Otro", "Prefiero no decir"],
        1,
    ),
    Question(
        "medical_history",
        "¿Tiene antecedentes médicos relevantes?",
        ["Sí", "No"],
        1,
    ),
    Question(
        "medication",
        "¿Actualmente toma algún medicamento?",
        ["Sí", "No"],
        1,
    ),
    Question(
        "sleep_issues",
        "¿Tiene problemas para conciliar el sueño o permanecer dormido?",
        ["Sí", "No"],
        1,
    ),
    Question(
        "irritability",
        "¿Se siente irritable o se enfada fácilmente?",
        ["Sí", "No"],
        1,
    ),
    Question(
        "mood",
        "¿Se siente frecuentemente triste o desanimado?",
        ["Sí", "No"],
        1,
    ),
    Question(
        "family_history",
        "¿Tiene algún historial familiar de trastornos psicológicos?",
        ["Sí", "No", "No estoy seguro"],
        1,
    ),
    Question(
        "appetite_weight_changes",
        "¿Ha notado algún cambio significativo en su apetito o peso recientemente?",
        ["Sí", "No"],
        1,
    ),
    Question(
        "concentration_memory_problems",
        "¿Ha experimentado problemas de concentración o memoria?",
        ["Sí", "No"],
        1,
    ),
    Question(
        "anxiety",
        "¿Ha experimentado problemas de ansiedad?",
        ["Sí", "No"],
        1,
    )
])


class UnifiedExpertSystem(Expert):
    @DefFacts()
    def _initial_action(self):
        yield Fact(action='collect_general_info')

    def input_data(self, input_json):
        self.declare(Fact(age=input_json['age']))
        self.declare(Fact(gender=input_json['gender']))
        self.declare(Fact(medical_history=input_json['medical_history']))
        self.declare(Fact(medication=input_json['medication']))
        self.declare(Fact(sleep_issues=input_json['sleep_issues']))
        self.declare(Fact(irritability=input_json['irritability']))
        self.declare(Fact(mood=input_json['mood']))
        self.declare(Fact(family_history=input_json['family_history']))
        self.declare(Fact(appetite_weight_changes=input_json['appetite_weight_changes']))
        self.declare(Fact(concentration_memory_problems=input_json['concentration_memory_problems']))
        self.declare(Fact(anxiety=input_json['anxiety']))
        if input_json['anxiety'] == "1":
            self.diagnosis.append("anxiety")
        if input_json['sleep_issues'] == "1":
            self.diagnosis.append("insomnia")
        if input_json['irritability'] == "1":
            self.diagnosis.append("stress")
        if input_json['mood'] == "1":
            self.diagnosis.append("depression")

    def __init__(self):
        super().__init__()
        self.recommendations = []
        self.diagnosis = []

    #def get_input_by_system(self, system):
    #    if system == 'insomnia':
    #        return get_input()
    #    elif system == 'stress':
    #        return get_input()
    #    elif system == 'depression':
    #        return DepressionExpertSystem().get_input()
    #    elif system == 'anxiety':
    #        return AnxietyExpertSystem().get_input()
    #    else:
    #        return {}

    def redirect_to_insomnia(self, insomnia_input):
        print("\nRedirigiendo al módulo de diagnóstico de insomnio...")
        insomnia_engine = InsomniaExpertSystem()
        insomnia_engine.reset()
        insomnia_engine.input_data(insomnia_input)
        insomnia_engine.run()
        self.recommendations.extend(insomnia_engine.get_recommendations())
        self.declare(Fact(action='check_irritability'))

    def redirect_to_stress(self, stress_input):
        print("\nRedirigiendo al módulo de diagnóstico de estrés...")
        stress_engine = StressExpertSystem()
        stress_engine.reset()
        stress_engine.input_data(stress_input)
        stress_engine.run()
        self.recommendations.extend(stress_engine.get_recommendations())

    def redirect_to_depression(self, depression_input):
        print("\nRedirigiendo al módulo de diagnóstico de depresión...")
        depression_engine = DepressionExpertSystem()
        depression_engine.reset()
        depression_engine.input_data(depression_input)
        depression_engine.run()
        self.recommendations.extend(depression_engine.get_recommendations())

    def redirect_to_anxiety(self, anxiety_input):
        print("\nRedirigiendo al módulo de diagnóstico de ansiedad...")
        anxiety_engine = AnxietyExpertSystem()
        anxiety_engine.reset()
        anxiety_engine.input_data(anxiety_input)
        anxiety_engine.run()
        self.recommendations.extend(anxiety_engine.get_recommendations())

    def get_recommendations(self):
        return self.recommendations

    def get_diagnosis(self):
        return self.diagnosis

