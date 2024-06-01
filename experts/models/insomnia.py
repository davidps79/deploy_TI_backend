from experta import *
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

from app.dtos import Quiz, Question
from experts.models.entity import Expert

insomnia_quiz = Quiz([
        Question(
            "difficulty_sleep",
            "¿Cuál de las siguientes opciones describe mejor su problema para dormir?",
            ["Dificultad para iniciar el sueño", "Dificultad para mantener el sueño",
             "Despertares nocturnos frecuentes", "Despertares tempranos", "Sueño no reparador"],
            1,
        ),
        Question(
            "daytime_consequence",
            "¿Cuál de las siguientes consecuencias diurnas experimenta con más frecuencia?",
            ["Fatiga", "Somnolencia diurna", "Irritabilidad", "Dificultad para concentrarse",
             "Disminución de la memoria", "Disminución del rendimiento laboral y académico", "Problemas de conducta",
             "Baja motivación y energía", "Tendencia a errores y accidentes", "Preocupación por el sueño"],
            1,
        ),
        Question(
            "isi_score",
            "Por favor responda a las siguientes preguntas con un número del 0 al 4 (0: No en absoluto, 1: Un poco, 2: Moderadamente, 3: Severamente, 4: Muy severamente)",
            ["Dificultad para conciliar el sueño", "Dificultad para mantener el sueño", "Despertar muy temprano",
             "Insatisfacción con su patrón de sueño actual",
             "A qué medida ha notado que su problema del sueño afecta su funcionamiento diario",
             "Qué tanto se nota su problema del sueño en los demás", "Qué tanto le preocupa su problema del sueño"],
            3,
        ),
        Question(
            "medical_cause",
            "¿Ha sido diagnosticado con alguna de las siguientes condiciones médicas?",
            ["Enfermedades neurológicas", "Enfermedades cardiorespiratorias", "Enfermedades gastrointestinales",
             "Enfermedades endocrinas", "Ninguna de las anteriores"],
            1,
        ),
        Question(
            "medication_use",
            "¿Está tomando alguno de los siguientes medicamentos?",
            ["Antidepresivos", "Estimulantes", "Corticosteroides", "Antihipertensivos", "Ninguno de los anteriores"],
            1,
        ),
        Question(
            "psychological_cause",
            "¿Está experimentando alguna de las siguientes condiciones psicológicas?",
            ["Estrés", "Ansiedad", "Depresión", "Ninguna de las anteriores"],
            1,
        ),
        Question(
            "lifestyle_factor",
            "¿Tiene alguno de los siguientes hábitos?",
            ["Consumo de cafeína, nicotina o alcohol antes de dormir",
             "Alimentación inadecuada (comidas pesadas antes de dormir)", "Falta de ejercicio",
             "Uso de dispositivos electrónicos antes de dormir", "Ninguno de los anteriores"],
            1,
        ),
        Question(
            "sleep_environment",
            "¿Su entorno de sueño es adecuado?",
            ["Sí", "No (p.ej., ruido, luz, temperatura inapropiada, colchón incómodo)"],
            1,
        )
    ])
class InsomniaExpertSystem(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        yield Fact(action='start')
        yield Fact(knowledge_base='Insomnia Diagnosis')

    def __init__(self):
        super().__init__()
        self.model = BayesianNetwork([
            ('SleepEnvironment', 'Insomnia'),
            ('CaffeineUse', 'Insomnia'),
            ('MedicationUse', 'Insomnia'),
            ('PsychologicalIssues', 'Insomnia')
        ])

        cpd_sleep_environment = TabularCPD(variable='SleepEnvironment', variable_card=2, values=[[0.8], [0.2]])
        cpd_caffeine_use = TabularCPD(variable='CaffeineUse', variable_card=2, values=[[0.7], [0.3]])
        cpd_medication_use = TabularCPD(variable='MedicationUse', variable_card=2, values=[[0.9], [0.1]])
        cpd_psychological_issues = TabularCPD(variable='PsychologicalIssues', variable_card=2, values=[[0.6], [0.4]])

        cpd_insomnia = TabularCPD(
            variable='Insomnia', variable_card=2,
            values=[
                [0.9, 0.7, 0.8, 0.6, 0.75, 0.55, 0.65, 0.45, 0.7, 0.5, 0.6, 0.4, 0.5, 0.3, 0.4, 0.2],  # No Insomnia
                [0.1, 0.3, 0.2, 0.4, 0.25, 0.45, 0.35, 0.55, 0.3, 0.5, 0.4, 0.6, 0.5, 0.7, 0.6, 0.8]  # Insomnia
            ],
            evidence=['SleepEnvironment', 'CaffeineUse', 'MedicationUse', 'PsychologicalIssues'],
            evidence_card=[2, 2, 2, 2]
        )

        self.model.add_cpds(cpd_sleep_environment, cpd_caffeine_use, cpd_medication_use, cpd_psychological_issues,
                            cpd_insomnia)
        self.model.check_model()
        self.inference = VariableElimination(self.model)
        self.recommendations = []
        self.diagnosis = []

    def input_data(self, input_json):
        self.declare(Fact(difficulty_sleep=input_json['difficulty_sleep']))
        self.declare(Fact(daytime_consequence=input_json['daytime_consequence']))
        self.declare(Fact(isi_score=input_json['isi_score']))
        self.declare(Fact(medical_cause=input_json['medical_cause']))
        self.declare(Fact(medication_use=input_json['medication_use']))
        self.declare(Fact(psychological_cause=input_json['psychological_cause']))
        self.declare(Fact(lifestyle_factor=input_json['lifestyle_factor']))
        self.declare(Fact(sleep_environment=input_json['sleep_environment']))
        self.declare(Fact(action='process_difficulty_sleep'))

    @Rule(Fact(action='process_difficulty_sleep'), AS.difficulty_sleep << Fact(difficulty_sleep=W()))
    def process_difficulty_sleep(self, difficulty_sleep):
        print("Problema para dormir:", difficulty_sleep['difficulty_sleep'])
        self.declare(Fact(action='process_daytime_consequence'))

    @Rule(Fact(action='process_daytime_consequence'), AS.daytime_consequence << Fact(daytime_consequence=W()))
    def process_daytime_consequence(self, daytime_consequence):
        print("Consecuencia diurna más frecuente:", daytime_consequence['daytime_consequence'])
        self.declare(Fact(action='process_isi_score'))

    @Rule(Fact(action='process_isi_score'), AS.isi_score << Fact(isi_score=W()))
    def process_isi_score(self, isi_score):
        score = isi_score['isi_score']
        print("Puntuación de ISI:", score)
        if score <= 7:
            self.recommendations.append("Interpretación: Insomnio sin significancia clínica.")
        elif score <= 14:
            self.recommendations.append("Interpretación: Insomnio subumbral.")
        elif score <= 21:
            self.recommendations.append("Interpretación: Insomnio moderado.")
        else:
            self.recommendations.append("Interpretación: Insomnio severo.")
        self.declare(Fact(action='process_medical_cause'))

    @Rule(Fact(action='process_medical_cause'), AS.medical_cause << Fact(medical_cause=W()))
    def process_medical_cause(self, medical_cause):
        if medical_cause['medical_cause'] != '5':
            self.recommendations.append("Consulte con un profesional de la salud para tratar la condición médica subyacente.")
        self.declare(Fact(action='process_medication_use'))

    @Rule(Fact(action='process_medication_use'), AS.medication_use << Fact(medication_use=W()))
    def process_medication_use(self, medication_use):
        if medication_use['medication_use'] != '5':
            self.recommendations.append("Revise los medicamentos con su médico para ver si pueden estar afectando su sueño.")
        self.declare(Fact(action='process_psychological_cause'))

    @Rule(Fact(action='process_psychological_cause'), AS.psychological_cause << Fact(psychological_cause=W()))
    def process_psychological_cause(self, psychological_cause):
        if psychological_cause['psychological_cause'] != '4':
            if psychological_cause['psychological_cause'] == '1':
                self.recommendations.append(
                    "Considere técnicas de manejo del estrés como mindfulness y respiración profunda.")
            elif psychological_cause['psychological_cause'] == '2':
                self.recommendations.append("La terapia cognitivo-conductual puede ser útil para manejar la ansiedad.")
            elif psychological_cause['psychological_cause'] == '3':
                self.recommendations.append(
                    "Considere hablar con un terapeuta sobre opciones de tratamiento para la depresión.")
        self.declare(Fact(action='process_lifestyle_factor'))

    @Rule(Fact(action='process_lifestyle_factor'), AS.lifestyle_factor << Fact(lifestyle_factor=W()))
    def process_lifestyle_factor(self, lifestyle_factor):
        if lifestyle_factor['lifestyle_factor'] != '5':
            if lifestyle_factor['lifestyle_factor'] == '1':
                self.recommendations.append("Evite consumir cafeína, nicotina o alcohol antes de dormir.")
            elif lifestyle_factor['lifestyle_factor'] == '2':
                self.recommendations.append("Intente evitar comidas pesadas antes de acostarse.")
            elif lifestyle_factor['lifestyle_factor'] == '3':
                self.recommendations.append("Incorpore ejercicio regular en su rutina diaria.")
            elif lifestyle_factor['lifestyle_factor'] == '4':
                self.recommendations.append(
                    "Evite el uso de dispositivos electrónicos al menos una hora antes de dormir.")
        self.declare(Fact(action='process_sleep_environment'))

    @Rule(Fact(action='process_sleep_environment'), AS.sleep_environment << Fact(sleep_environment=W()))
    def process_sleep_environment(self, sleep_environment):
        if sleep_environment['sleep_environment'] != '1':
            self.recommendations.append("Asegúrese de que su entorno de sueño sea cómodo y propicio para dormir (sin ruido, luz y temperatura adecuadas).")
        self.declare(Fact(action='evaluate_insomnia_risk'))

    @Rule(Fact(action='evaluate_insomnia_risk'),
          AS.sleep_environment << Fact(sleep_environment=W()),
          AS.lifestyle_factor << Fact(lifestyle_factor=W()),
          AS.medication_use << Fact(medication_use=W()),
          AS.psychological_cause << Fact(psychological_cause=W()))
    def evaluate_insomnia_risk(self, sleep_environment, lifestyle_factor, medication_use, psychological_cause):
        evidence = {
            'SleepEnvironment': 0 if sleep_environment['sleep_environment'] == '1' else 1,
            'CaffeineUse': 0 if lifestyle_factor['lifestyle_factor'] != '1' else 1,
            'MedicationUse': 0 if medication_use['medication_use'] == '5' else 1,
            'PsychologicalIssues': 0 if psychological_cause['psychological_cause'] == '4' else 1
        }
        prob_insomnia = self.inference.query(variables=['Insomnia'], evidence=evidence)
        insomnia_prob = prob_insomnia.values[1]
        print("Probabilidad calculada de insomnio:", insomnia_prob)
        self.recommendations.append(f"Probabilidad calculada de insomnio: {insomnia_prob}")
        if 0.40 <= insomnia_prob < 0.50:
            self.diagnosis.append("Su probabilidad de insomnio está en un rango moderado.")
            self.recommendations.append(
                "Considere mejorar su higiene del sueño, como mantener un horario regular de sueño y evitar la cafeína y la nicotina antes de acostarse.")

        elif 0.50 <= insomnia_prob < 0.60:
            self.diagnosis.append("Su probabilidad de insomnio es moderadamente alta.")
            self.recommendations.append(
                "Además de mejorar su higiene del sueño, considere practicar técnicas de relajación antes de acostarse, como meditación o respiración profunda.")

        elif 0.60 <= insomnia_prob < 0.70:
            self.diagnosis.append("Su probabilidad de insomnio es alta.")
            self.recommendations.append(
                "Junto con mejorar su higiene del sueño y practicar técnicas de relajación, considere buscar ayuda profesional para evaluar y abordar cualquier condición subyacente que pueda estar contribuyendo a su insomnio.")

        elif insomnia_prob >= 0.70:
            self.diagnosis.append("Su probabilidad de insomnio es muy alta.")
            self.recommendations.append(
                "Es altamente recomendable que busque ayuda profesional de un médico o especialista en trastornos del sueño para una evaluación y tratamiento adecuados.")

        self.declare(Fact(action='final_recommendations'))

    @Rule(Fact(action='final_recommendations'), AS.isi_score << Fact(isi_score=W()))
    def final_recommendations(self, isi_score):
        score = isi_score['isi_score']
        if score > 14:
            self.recommendations.append(
                "Recomendamos que consulte a un profesional de la salud para un diagnóstico y tratamiento más detallado.")
        else:
            self.recommendations.append("Puede considerar implementar las siguientes prácticas generales:")
            self.recommendations.append("- Mantener una rutina regular para dormir.")
            self.recommendations.append("- Evitar el uso de dispositivos electrónicos antes de dormir.")
            self.recommendations.append("- Crear un ambiente de sueño adecuado.")
            self.recommendations.append("- Practicar técnicas de relajación antes de acostarse.")


    def get_recommendations(self):
        return self.recommendations

    def get_diagnosis(self):
        return self.diagnosis