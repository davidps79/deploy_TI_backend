from experta import *
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

from dtos import Quiz, Question
from entity import Expert

depression_quiz = Quiz([
        Question(
            "factores_ambientales",
            "¿Tiene factores ambientales que puedan causar estrés?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "habitos",
            "¿Tiene hábitos que puedan afectar su salud mental?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "causas_psicologicas",
            "¿Tiene causas psicológicas que puedan causar depresión?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "cambios_hormonales",
            "¿Ha tenido cambios hormonales recientes?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "medicacion",
            "¿Está tomando medicación que pueda afectar su estado de ánimo?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "consecuencias",
            "¿Está experimentando consecuencias significativas en su vida?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "causas_fisiologicas",
            "¿Tiene causas fisiológicas que puedan causar depresión?",
            ["Sí", "No"],
            1,
        )
    ])

class DepressionExpertSystem(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        yield Fact(action="find_depression")

    def __init__(self):
        super().__init__()
        self.model = BayesianNetwork([
            ('FactoresAmbientales', 'Depresion'),
            ('Habitos', 'Depresion'),
            ('CausasPsicologicas', 'Depresion'),
            ('FactoresBiologicos', 'Depresion'),
            ('CambiosHormonales', 'FactoresBiologicos'),
            ('Medicación', 'FactoresBiologicos'),
            ('Consecuencias', 'FactoresBiologicos'),
            ('CausasFisiologicas', 'FactoresBiologicos')
        ])

        cpd_factores_ambientales = TabularCPD(variable='FactoresAmbientales', variable_card=2, values=[[0.9], [0.1]])
        cpd_habitos = TabularCPD(variable='Habitos', variable_card=2, values=[[0.8], [0.2]])
        cpd_causas_psicologicas = TabularCPD(variable='CausasPsicologicas', variable_card=2, values=[[0.7], [0.3]])
        cpd_cambios_hormonales = TabularCPD(variable='CambiosHormonales', variable_card=2, values=[[0.85], [0.15]])
        cpd_medicacion = TabularCPD(variable='Medicación', variable_card=2, values=[[0.6], [0.4]])
        cpd_consecuencias = TabularCPD(variable='Consecuencias', variable_card=2, values=[[0.75], [0.25]])
        cpd_causas_fisiologicas = TabularCPD(variable='CausasFisiologicas', variable_card=2, values=[[0.7], [0.3]])

        cpd_factores_biologicos = TabularCPD(
            variable='FactoresBiologicos', variable_card=2,
            values=[
                [0.9, 0.8, 0.7, 0.6, 0.8, 0.7, 0.6, 0.5, 0.7, 0.6, 0.5, 0.4, 0.6, 0.5, 0.4, 0.3],
                [0.1, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4, 0.5, 0.3, 0.4, 0.5, 0.6, 0.4, 0.5, 0.6, 0.7]
            ],
            evidence=['CambiosHormonales', 'Medicación', 'Consecuencias', 'CausasFisiologicas'],
            evidence_card=[2, 2, 2, 2]
        )

        cpd_depresion = TabularCPD(
            variable='Depresion', variable_card=2,
            values=[
                [0.9, 0.7, 0.5, 0.3, 0.7, 0.5, 0.3, 0.1, 0.5, 0.3, 0.1, 0.05, 0.3, 0.1, 0.05, 0.02],
                [0.1, 0.3, 0.5, 0.7, 0.3, 0.5, 0.7, 0.9, 0.5, 0.7, 0.9, 0.95, 0.7, 0.9, 0.95, 0.98]
            ],
            evidence=['FactoresAmbientales', 'Habitos', 'CausasPsicologicas', 'FactoresBiologicos'],
            evidence_card=[2, 2, 2, 2]
        )

        self.model.add_cpds(cpd_factores_ambientales, cpd_habitos, cpd_causas_psicologicas, cpd_cambios_hormonales,
                            cpd_medicacion, cpd_consecuencias, cpd_causas_fisiologicas, cpd_factores_biologicos,
                            cpd_depresion)
        self.model.check_model()
        self.inference = VariableElimination(self.model)
        self.recommendations = []
        self.diagnosis = []

    def input_data(self, input_json):
        self.declare(Fact(factores_ambientales=input_json['factores_ambientales']))
        self.declare(Fact(habitos=input_json['habitos']))
        self.declare(Fact(causas_psicologicas=input_json['causas_psicologicas']))
        self.declare(Fact(cambios_hormonales=input_json['cambios_hormonales']))
        self.declare(Fact(medicacion=input_json['medicacion']))
        self.declare(Fact(consecuencias=input_json['consecuencias']))
        self.declare(Fact(causas_fisiologicas=input_json['causas_fisiologicas']))
        self.declare(Fact(action='process_factores_ambientales'))

    @Rule(Fact(action='process_factores_ambientales'), AS.factores_ambientales << Fact(factores_ambientales=W()))
    def process_factores_ambientales(self, factores_ambientales):
        if factores_ambientales['factores_ambientales'] == '1':
            self.recommendations.append("Busque apoyo profesional.")
        self.declare(Fact(action='process_habitos'))

    @Rule(Fact(action='process_habitos'), AS.habitos << Fact(habitos=W()))
    def process_habitos(self, habitos):
        if habitos['habitos'] == '1':
            self.recommendations.append("Mejore sus hábitos de vida.")
        self.declare(Fact(action='process_causas_psicologicas'))

    @Rule(Fact(action='process_causas_psicologicas'), AS.causas_psicologicas << Fact(causas_psicologicas=W()))
    def process_causas_psicologicas(self, causas_psicologicas):
        if causas_psicologicas['causas_psicologicas'] == '1':
            self.recommendations.append("Considere la terapia cognitivo-conductual.")
        self.declare(Fact(action='process_cambios_hormonales'))

    @Rule(Fact(action='process_cambios_hormonales'), AS.cambios_hormonales << Fact(cambios_hormonales=W()))
    def process_cambios_hormonales(self, cambios_hormonales):
        if cambios_hormonales['cambios_hormonales'] == '1':
            self.recommendations.append("Evalúe sus cambios hormonales con un profesional.")
        self.declare(Fact(action='process_medicacion'))

    @Rule(Fact(action='process_medicacion'), AS.medicacion << Fact(medicacion=W()))
    def process_medicacion(self, medicacion):
        if medicacion['medicacion'] == '1':
            self.recommendations.append("Revise sus medicamentos con un médico.")
        self.declare(Fact(action='process_consecuencias'))

    @Rule(Fact(action='process_consecuencias'), AS.consecuencias << Fact(consecuencias=W()))
    def process_consecuencias(self, consecuencias):
        if consecuencias['consecuencias'] == '1':
            self.recommendations.append(
                "Considere hablar con un terapeuta sobre las consecuencias significativas en su vida.")
        self.declare(Fact(action='process_causas_fisiologicas'))

    @Rule(Fact(action='process_causas_fisiologicas'), AS.causas_fisiologicas << Fact(causas_fisiologicas=W()))
    def process_causas_fisiologicas(self, causas_fisiologicas):
        if causas_fisiologicas['causas_fisiologicas'] == '1':
            self.recommendations.append("Consulte con un profesional de la salud para tratar las causas fisiológicas.")
        self.declare(Fact(action='evaluate_depression_risk'))

    @Rule(Fact(action='evaluate_depression_risk'),
          AS.factores_ambientales << Fact(factores_ambientales=W()),
          AS.habitos << Fact(habitos=W()),
          AS.causas_psicologicas << Fact(causas_psicologicas=W()),
          AS.cambios_hormonales << Fact(cambios_hormonales=W()),
          AS.medicacion << Fact(medicacion=W()),
          AS.consecuencias << Fact(consecuencias=W()),
          AS.causas_fisiologicas << Fact(causas_fisiologicas=W()))
    def evaluate_depression_risk(self, factores_ambientales, habitos, causas_psicologicas, cambios_hormonales,
                                 medicacion, consecuencias, causas_fisiologicas):
        evidence = {
            'FactoresAmbientales': 1 if factores_ambientales['factores_ambientales'] == '1' else 0,
            'Habitos': 1 if habitos['habitos'] == '1' else 0,
            'CausasPsicologicas': 1 if causas_psicologicas['causas_psicologicas'] == '1' else 0,
            'CambiosHormonales': 1 if cambios_hormonales['cambios_hormonales'] == '1' else 0,
            'Medicación': 1 if medicacion['medicacion'] == '1' else 0,
            'Consecuencias': 1 if consecuencias['consecuencias'] == '1' else 0,
            'CausasFisiologicas': 1 if causas_fisiologicas['causas_fisiologicas'] == '1' else 0
        }
        prob_depresion = self.inference.query(variables=['Depresion'], evidence=evidence).values[1]
        print("Probabilidad calculada de depresión:", prob_depresion)
        self.recommendations.append(f"Probabilidad calculada de depresión: {prob_depresion}")

        if 0.30 <= prob_depresion < 0.40:
            self.diagnosis.append("Su probabilidad de depresión está en un rango bajo.")
            self.recommendations.append("Hable con un amigo o familiar de confianza sobre cómo se siente y busque actividades que le brinden placer y distracción.")

        elif 0.40 <= prob_depresion < 0.50:
            self.diagnosis.append("Su probabilidad de depresión es moderada.")
            self.recommendations.append("Considere hablar con un profesional de la salud mental para obtener apoyo adicional y considerar la terapia cognitivo-conductual.")

        elif 0.50 <= prob_depresion < 0.60:
            self.diagnosis.append("Su probabilidad de depresión es moderadamente alta.")
            self.recommendations.append("Es importante buscar ayuda profesional y considerar opciones de tratamiento, como la terapia y, posiblemente, la medicación.")

        elif prob_depresion >= 0.60:
            self.diagnosis.append("Su probabilidad de depresión es alta.")
            self.recommendations.append("Se recomienda encarecidamente buscar ayuda profesional de inmediato y considerar opciones de tratamiento intensivo, como la hospitalización o la terapia intensiva.")

    def get_recommendations(self):
        return self.recommendations

    def get_diagnosis(self):
        return self.diagnosis
