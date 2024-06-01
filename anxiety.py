from experta import *
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

from dtos import Quiz, Question
from entity import Expert

anxiety_quiz = Quiz([
        Question(
            "anxiety_symptoms",
            "¿Cuáles de los siguientes síntomas de ansiedad experimenta con frecuencia?",
            ["Preocupación excesiva", "Inquietud", "Fatiga", "Dificultad para concentrarse", "Irritabilidad",
             "Tensión muscular", "Problemas para dormir"],
            1,
        ),
        Question(
            "daytime_impact",
            "¿Cuánto afecta su ansiedad a su vida diaria?",
            ["Nada", "Un poco", "Moderadamente", "Mucho", "Extremadamente"],
            1,
        ),
        Question(
            "physiological_cause",
            "¿Ha sido diagnosticado con alguna de las siguientes condiciones médicas?",
            ["Enfermedades neurológicas", "Enfermedades cardiorespiratorias", "Enfermedades gastrointestinales",
             "Enfermedades endocrinas", "Ninguna de las anteriores"],
            1,
        ),
        Question(
            "medication_use",
            "¿Está tomando alguno de los siguientes medicamentos?",
            ["Antidepresivos", "Estimulantes", "Corticosteroides", "Antihipertensivos", "Ninguno de los anteriores"],
            1
        ),
        Question(
            "psychological_cause",
            "¿Está experimentando alguna de las siguientes condiciones psicológicas?",
            ["Estrés", "Depresión", "Ninguna de las anteriores"],
            1
        ),
        Question(
            "lifestyle_factor",
            "¿Tiene alguno de los siguientes hábitos?",
            ["Consumo de cafeína o alcohol en exceso", "Alimentación inadecuada", "Falta de ejercicio",
             "Uso excesivo de dispositivos electrónicos", "Ninguno de los anteriores"],
            1
        ),
        Question(
            "sleep_problems",
            "¿Tiene problemas para dormir debido a su ansiedad?",
            ["Sí", "No"],
            1
        )
    ])

class AnxietyExpertSystem(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        yield Fact(action="find_anxiety")

    def __init__(self):
        super().__init__()
        self.model = BayesianNetwork([
            ('SleepProblems', 'Anxiety'),
            ('CaffeineUse', 'Anxiety'),
            ('MedicationUse', 'Anxiety'),
            ('PsychologicalIssues', 'Anxiety')
        ])

        cpd_sleep_problems = TabularCPD(variable='SleepProblems', variable_card=2, values=[[0.7], [0.3]])
        cpd_caffeine_use = TabularCPD(variable='CaffeineUse', variable_card=2, values=[[0.6], [0.4]])
        cpd_medication_use = TabularCPD(variable='MedicationUse', variable_card=2, values=[[0.8], [0.2]])
        cpd_psychological_issues = TabularCPD(variable='PsychologicalIssues', variable_card=2, values=[[0.5], [0.5]])

        cpd_anxiety = TabularCPD(
            variable='Anxiety', variable_card=2,
            values=[
                [0.9, 0.8, 0.7, 0.6, 0.8, 0.7, 0.6, 0.5, 0.75, 0.65, 0.55, 0.45, 0.7, 0.6, 0.5, 0.4],  # No Anxiety
                [0.1, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4, 0.5, 0.25, 0.35, 0.45, 0.55, 0.3, 0.4, 0.5, 0.6]  # Anxiety
            ],
            evidence=['SleepProblems', 'CaffeineUse', 'MedicationUse', 'PsychologicalIssues'],
            evidence_card=[2, 2, 2, 2]
        )

        self.model.add_cpds(cpd_sleep_problems, cpd_caffeine_use, cpd_medication_use, cpd_psychological_issues,
                            cpd_anxiety)
        self.model.check_model()
        self.inference = VariableElimination(self.model)
        self.recommendations = []
        self.diagnosis = []

    def input_data(self, input_json):
        self.declare(Fact(anxiety_symptoms=input_json['anxiety_symptoms']))
        self.declare(Fact(daytime_impact=input_json['daytime_impact']))
        self.declare(Fact(physiological_cause=input_json['physiological_cause']))
        self.declare(Fact(medication_use=input_json['medication_use']))
        self.declare(Fact(psychological_cause=input_json['psychological_cause']))
        self.declare(Fact(lifestyle_factor=input_json['lifestyle_factor']))
        self.declare(Fact(sleep_problems=input_json['sleep_problems']))
        self.declare(Fact(action='process_anxiety_symptoms'))

    @Rule(Fact(action='process_anxiety_symptoms'), AS.anxiety_symptoms << Fact(anxiety_symptoms=W()))
    def process_anxiety_symptoms(self, anxiety_symptoms):
        self.diagnosis.append(f"Síntomas de ansiedad: {anxiety_symptoms['anxiety_symptoms']}")
        self.declare(Fact(action='process_daytime_impact'))

    @Rule(Fact(action='process_daytime_impact'), AS.daytime_impact << Fact(daytime_impact=W()))
    def process_daytime_impact(self, daytime_impact):
        self.diagnosis.append(f"Impacto en la vida diaria: {daytime_impact['daytime_impact']}")
        if daytime_impact['daytime_impact'] in ['4', '5']:
            self.recommendations.append(
                "Recomendamos que consulte a un profesional de la salud para un diagnóstico y tratamiento más detallado.")
        else:
            self.recommendations.append("Puede considerar implementar las siguientes prácticas generales:")
            self.recommendations.append("- Mantener una rutina diaria regular.")
            self.recommendations.append("- Practicar técnicas de relajación.")
            self.recommendations.append("- Evitar el consumo excesivo de cafeína y alcohol.")
            self.recommendations.append("- Crear un ambiente de sueño adecuado.")
        self.declare(Fact(action='process_physiological_cause'))

    @Rule(Fact(action='process_physiological_cause'), AS.physiological_cause << Fact(physiological_cause=W()))
    def process_physiological_cause(self, physiological_cause):
        if physiological_cause['physiological_cause'] != '5':
            self.diagnosis.append(f"Causa fisiológica potencial: {physiological_cause['physiological_cause']}")
            self.recommendations.append("Consulte con un profesional de la salud para tratar la condición médica subyacente.")
        if physiological_cause['physiological_cause'] != '3':
            if physiological_cause['physiological_cause'] == '1':
                self.recommendations.append(
                    "Considere técnicas de manejo del estrés como mindfulness y respiración profunda.")
            elif physiological_cause['physiological_cause'] == '2':
                self.recommendations.append(
                    "Considere hablar con un terapeuta sobre opciones de tratamiento para la depresión.")
        self.declare(Fact(action='process_medication_use'))

    @Rule(Fact(action='process_medication_use'), AS.medication_use << Fact(medication_use=W()))
    def process_medication_use(self, medication_use):
        if medication_use['medication_use'] != '5':
            self.diagnosis.append(f"Uso de medicación potencialmente influyente: {medication_use['medication_use']}")
            self.recommendations.append("Revise los medicamentos con su médico para ver si pueden estar afectando su ansiedad.")
        self.declare(Fact(action='process_lifestyle_factor'))

    @Rule(Fact(action='process_lifestyle_factor'), AS.lifestyle_factor << Fact(lifestyle_factor=W()))
    def process_lifestyle_factor(self, lifestyle_factor):
        if lifestyle_factor['lifestyle_factor'] != '5':
            self.diagnosis.append(
                f"Factor de estilo de vida potencialmente influyente: {lifestyle_factor['lifestyle_factor']}")
        if lifestyle_factor['lifestyle_factor'] != '6':
            if lifestyle_factor['lifestyle_factor'] == '1':
                self.recommendations.append("Reduzca el consumo de cafeína.")
            elif lifestyle_factor['lifestyle_factor'] == '2':
                self.recommendations.append("Reduzca el consumo de alcohol.")
            elif lifestyle_factor['lifestyle_factor'] == '3':
                self.recommendations.append("Mejore su alimentación.")
            elif lifestyle_factor['lifestyle_factor'] == '4':
                self.recommendations.append("Incorpore ejercicio regular en su rutina diaria.")
            elif lifestyle_factor['lifestyle_factor'] == '5':
                self.recommendations.append("Reduzca el uso de dispositivos electrónicos.")
        self.declare(Fact(action='process_sleep_problems'))

    @Rule(Fact(action='process_sleep_problems'), AS.sleep_problems << Fact(sleep_problems=W()))
    def process_sleep_problems(self, sleep_problems):
        if sleep_problems['sleep_problems'] != '2':
            self.diagnosis.append(f"Problemas de sueño: {sleep_problems['sleep_problems']}")
            self.recommendations.append("Intente mejorar su higiene del sueño.")
        self.declare(Fact(action='evaluate_anxiety_risk'))

    @Rule(Fact(action='evaluate_anxiety_risk'),
          AS.anxiety_symptoms << Fact(anxiety_symptoms=W()),
          AS.daytime_impact << Fact(daytime_impact=W()),
          AS.physiological_cause << Fact(physiological_cause=W()),
          AS.medication_use << Fact(medication_use=W()),
          AS.psychological_cause << Fact(psychological_cause=W()),
          AS.lifestyle_factor << Fact(lifestyle_factor=W()),
          AS.sleep_problems << Fact(sleep_problems=W()))
    def evaluate_anxiety_risk(self, anxiety_symptoms, daytime_impact, physiological_cause, medication_use,
                              psychological_cause, lifestyle_factor, sleep_problems):
        evidence = {
            'SleepProblems': 0 if sleep_problems['sleep_problems'] == '2' else 1,
            'CaffeineUse': 1 if lifestyle_factor['lifestyle_factor'] in ['1', '2'] else 0,
            'MedicationUse': 0 if medication_use['medication_use'] == '5' else 1,
            'PsychologicalIssues': 0 if psychological_cause['psychological_cause'] == '3' else 1
        }
        prob_anxiety = self.inference.query(variables=['Anxiety'], evidence=evidence).values[1]
        print("Probabilidad calculada de ansiedad:", prob_anxiety)
        self.recommendations.append(f"Probabilidad calculada de ansiedad: {prob_anxiety}")

        if 0.30 <= prob_anxiety < 0.40:
            self.diagnosis.append("Su probabilidad de ansiedad está en un rango bajo.")
            self.recommendations.append("Pruebe técnicas de relajación como la respiración profunda o el mindfulness.")

        elif 0.40 <= prob_anxiety < 0.50:
            self.diagnosis.append("Su probabilidad de ansiedad es moderada.")
            self.recommendations.append(
                "Considere hablar con un terapeuta sobre sus preocupaciones y busque apoyo en amigos y familiares.")

        elif 0.50 <= prob_anxiety < 0.60:
            self.diagnosis.append("Su probabilidad de ansiedad es moderadamente alta.")
            self.recommendations.append(
                "Es recomendable buscar ayuda profesional para obtener un diagnóstico preciso y considerar opciones de tratamiento.")

        elif prob_anxiety >= 0.60:
            self.diagnosis.append("Su probabilidad de ansiedad es alta.")
            self.recommendations.append(
                "Es crucial buscar ayuda profesional de inmediato para un tratamiento adecuado y el apoyo necesario.")
            self.recommendations.append(
                "Evite el consumo de alcohol y drogas recreativas, ya que pueden empeorar los síntomas de la ansiedad.")
            self.recommendations.append(
                "Pruebe técnicas de manejo del estrés como el ejercicio regular, la meditación o el yoga.")
            self.recommendations.append(
                "Hable con su médico sobre la posibilidad de terapia cognitivo-conductual (TCC) o medicación para la ansiedad.")
            self.recommendations.append(
                "Considere la posibilidad de unirse a un grupo de apoyo o buscar terapia individual para obtener apoyo adicional.")
            self.recommendations.append(
                "Priorice el autocuidado y establezca límites saludables en su vida diaria para reducir el estrés.")

    def get_recommendations(self):
        return self.recommendations

    def get_diagnosis(self):
        return self.diagnosis
