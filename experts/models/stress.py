from experta import *
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

from app.dtos import Quiz, Question
from experts.models.entity import Expert

stress_quiz = Quiz([
        Question(
            "cuestiones_cronicas",
            "¿Tiene cuestiones crónicas que le generen estrés?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "situaciones_cotidianas",
            "¿Experimenta situaciones cotidianas estresantes frecuentemente?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "sucesos_vitales",
            "¿Ha experimentado algún suceso vital estresante recientemente?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "susceptibilidad_interna",
            "¿Tiene predisposición fisiológica al estrés?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "valoracion_cognitiva",
            "¿Suele tener pensamientos negativos sobre las situaciones?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "relaciones_interpersonales",
            "¿Tiene conflictos en sus relaciones interpersonales?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "presion_laboral",
            "¿Siente presión laboral o académica?",
            ["Sí", "No"],
            1,
        ),
        Question(
            "falta_apoyo_social",
            "¿Le falta apoyo social?",
            ["Sí", "No"],
            1,
        )
    ])

class StressExpertSystem(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        yield Fact(action="start")

    def __init__(self):
        super().__init__()
        self.model = BayesianNetwork([
            ('CuestionesCronicas', 'FactoresAmbientales'),
            ('SituacionesCotidianas', 'FactoresAmbientales'),
            ('SucesosVitales', 'FactoresAmbientales'),
            ('FactoresAmbientales', 'Estrés'),
            ('SusceptibilidadInterna', 'FactoresInternos'),
            ('ValoracionCognitiva', 'FactoresInternos'),
            ('FactoresInternos', 'Estrés'),
            ('RelacionesInterpersonales', 'FactoresPersonalesSociales'),
            ('PresionLaboralAcademica', 'FactoresPersonalesSociales'),
            ('FactoresPersonalesSociales', 'Estrés'),
            ('FaltaApoyoSocial', 'Estrés')
        ])

        cpd_cuestiones_cronicas = TabularCPD(variable='CuestionesCronicas', variable_card=2, values=[[0.8], [0.2]])
        cpd_situaciones_cotidianas = TabularCPD(variable='SituacionesCotidianas', variable_card=2,
                                                values=[[0.85], [0.15]])
        cpd_sucesos_vitales = TabularCPD(variable='SucesosVitales', variable_card=2, values=[[0.9], [0.1]])
        cpd_factores_ambientales = TabularCPD(variable='FactoresAmbientales', variable_card=2,
                                              values=[[0.9, 0.7, 0.5, 0.3, 0.7, 0.5, 0.3, 0.1],
                                                      [0.1, 0.3, 0.5, 0.7, 0.3, 0.5, 0.7, 0.9]],
                                              evidence=['CuestionesCronicas', 'SituacionesCotidianas',
                                                        'SucesosVitales'],
                                              evidence_card=[2, 2, 2])

        cpd_susceptibilidad_interna = TabularCPD(variable='SusceptibilidadInterna', variable_card=2,
                                                 values=[[0.75], [0.25]])
        cpd_valoracion_cognitiva = TabularCPD(variable='ValoracionCognitiva', variable_card=2, values=[[0.7], [0.3]])
        cpd_factores_internos = TabularCPD(variable='FactoresInternos', variable_card=2,
                                           values=[[0.9, 0.6, 0.3, 0.1],
                                                   [0.1, 0.4, 0.7, 0.9]],
                                           evidence=['SusceptibilidadInterna', 'ValoracionCognitiva'],
                                           evidence_card=[2, 2])

        cpd_relaciones_interpersonales = TabularCPD(variable='RelacionesInterpersonales', variable_card=2,
                                                    values=[[0.65], [0.35]])
        cpd_presion_laboral_academica = TabularCPD(variable='PresionLaboralAcademica', variable_card=2,
                                                   values=[[0.6], [0.4]])
        cpd_factores_personales_sociales = TabularCPD(variable='FactoresPersonalesSociales', variable_card=2,
                                                      values=[[0.9, 0.7, 0.5, 0.3],
                                                              [0.1, 0.3, 0.5, 0.7]],
                                                      evidence=['RelacionesInterpersonales', 'PresionLaboralAcademica'],
                                                      evidence_card=[2, 2])

        cpd_falta_apoyo_social = TabularCPD(variable='FaltaApoyoSocial', variable_card=2, values=[[0.55], [0.45]])

        cpd_estres = TabularCPD(variable='Estrés', variable_card=2,
                                values=[
                                    [0.9, 0.8, 0.7, 0.6, 0.8, 0.7, 0.6, 0.5, 0.7, 0.6, 0.5, 0.4, 0.6, 0.5, 0.4, 0.3],
                                    [0.1, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4, 0.5, 0.3, 0.4, 0.5, 0.6, 0.4, 0.5, 0.6, 0.7]],
                                evidence=['FactoresAmbientales', 'FactoresInternos', 'FactoresPersonalesSociales',
                                          'FaltaApoyoSocial'],
                                evidence_card=[2, 2, 2, 2])

        self.model.add_cpds(cpd_cuestiones_cronicas, cpd_situaciones_cotidianas, cpd_sucesos_vitales,
                            cpd_factores_ambientales,
                            cpd_susceptibilidad_interna, cpd_valoracion_cognitiva, cpd_factores_internos,
                            cpd_relaciones_interpersonales, cpd_presion_laboral_academica,
                            cpd_factores_personales_sociales,
                            cpd_falta_apoyo_social, cpd_estres)
        self.model.check_model()
        self.inference = VariableElimination(self.model)
        self.recommendations = []
        self.diagnosis = []

    def input_data(self, input_json):
        self.declare(Fact(cuestiones_cronicas=input_json['cuestiones_cronicas']))
        self.declare(Fact(situaciones_cotidianas=input_json['situaciones_cotidianas']))
        self.declare(Fact(sucesos_vitales=input_json['sucesos_vitales']))
        self.declare(Fact(susceptibilidad_interna=input_json['susceptibilidad_interna']))
        self.declare(Fact(valoracion_cognitiva=input_json['valoracion_cognitiva']))
        self.declare(Fact(relaciones_interpersonales=input_json['relaciones_interpersonales']))
        self.declare(Fact(presion_laboral=input_json['presion_laboral']))
        self.declare(Fact(falta_apoyo_social=input_json['falta_apoyo_social']))
        self.declare(Fact(action='process_cuestiones_cronicas'))

    @Rule(Fact(action='process_cuestiones_cronicas'), AS.cuestiones_cronicas << Fact(cuestiones_cronicas=W()))
    def process_cuestiones_cronicas(self, cuestiones_cronicas):
        if cuestiones_cronicas['cuestiones_cronicas'] == '1':
            self.recommendations.append("Busque apoyo profesional para tratar condiciones crónicas de estrés.")
        self.declare(Fact(action='process_situaciones_cotidianas'))

    @Rule(Fact(action='process_situaciones_cotidianas'), AS.situaciones_cotidianas << Fact(situaciones_cotidianas=W()))
    def process_situaciones_cotidianas(self, situaciones_cotidianas):
        if situaciones_cotidianas['situaciones_cotidianas'] == '1':
            self.recommendations.append("Pruebe técnicas de relajación y mindfulness para reducir el estrés diario.")
        self.declare(Fact(action='process_sucesos_vitales'))

    @Rule(Fact(action='process_sucesos_vitales'), AS.sucesos_vitales << Fact(sucesos_vitales=W()))
    def process_sucesos_vitales(self, sucesos_vitales):
        if sucesos_vitales['sucesos_vitales'] == '1':
            self.recommendations.append("Considere técnicas de manejo del estrés para eventos recientes.")
        self.declare(Fact(action='process_susceptibilidad_interna'))

    @Rule(Fact(action='process_susceptibilidad_interna'),
          AS.susceptibilidad_interna << Fact(susceptibilidad_interna=W()))
    def process_susceptibilidad_interna(self, susceptibilidad_interna):
        if susceptibilidad_interna['susceptibilidad_interna'] == '1':
            self.recommendations.append("Evalúe su predisposición fisiológica con un profesional de la salud.")
        self.declare(Fact(action='process_valoracion_cognitiva'))

    @Rule(Fact(action='process_valoracion_cognitiva'), AS.valoracion_cognitiva << Fact(valoracion_cognitiva=W()))
    def process_valoracion_cognitiva(self, valoracion_cognitiva):
        if valoracion_cognitiva['valoracion_cognitiva'] == '1':
            self.recommendations.append(
                "Trabaje en la reestructuración cognitiva para mejorar sus pensamientos negativos.")
        self.declare(Fact(action='process_relaciones_interpersonales'))

    @Rule(Fact(action='process_relaciones_interpersonales'),
          AS.relaciones_interpersonales << Fact(relaciones_interpersonales=W()))
    def process_relaciones_interpersonales(self, relaciones_interpersonales):
        if relaciones_interpersonales['relaciones_interpersonales'] == '1':
            self.recommendations.append(
                "Fortalezca sus relaciones interpersonales y resuelva conflictos de manera asertiva.")
        self.declare(Fact(action='process_presion_laboral'))

    @Rule(Fact(action='process_presion_laboral'), AS.presion_laboral << Fact(presion_laboral=W()))
    def process_presion_laboral(self, presion_laboral):
        if presion_laboral['presion_laboral'] == '1':
            self.recommendations.append("Gestione su carga laboral y busque equilibrio entre trabajo y vida personal.")
        self.declare(Fact(action='process_falta_apoyo_social'))

    @Rule(Fact(action='process_falta_apoyo_social'), AS.falta_apoyo_social << Fact(falta_apoyo_social=W()))
    def process_falta_apoyo_social(self, falta_apoyo_social):
        if falta_apoyo_social['falta_apoyo_social'] == '1':
            self.recommendations.append("Busque construir una red de apoyo social para mejorar su bienestar.")
        self.declare(Fact(action='evaluate_stress_risk'))

    @Rule(Fact(action='evaluate_stress_risk'),
          AS.cuestiones_cronicas << Fact(cuestiones_cronicas=W()),
          AS.situaciones_cotidianas << Fact(situaciones_cotidianas=W()),
          AS.sucesos_vitales << Fact(sucesos_vitales=W()),
          AS.susceptibilidad_interna << Fact(susceptibilidad_interna=W()),
          AS.valoracion_cognitiva << Fact(valoracion_cognitiva=W()),
          AS.relaciones_interpersonales << Fact(relaciones_interpersonales=W()),
          AS.presion_laboral << Fact(presion_laboral=W()),
          AS.falta_apoyo_social << Fact(falta_apoyo_social=W()))
    def evaluate_stress_risk(self, cuestiones_cronicas, situaciones_cotidianas, sucesos_vitales,
                             susceptibilidad_interna, valoracion_cognitiva, relaciones_interpersonales, presion_laboral,
                             falta_apoyo_social):
        evidence = {
            'CuestionesCronicas': 0 if cuestiones_cronicas['cuestiones_cronicas'] == '2' else 1,
            'SituacionesCotidianas': 0 if situaciones_cotidianas['situaciones_cotidianas'] == '2' else 1,
            'SucesosVitales': 0 if sucesos_vitales['sucesos_vitales'] == 'No' else 1,
            'SusceptibilidadInterna': 0 if susceptibilidad_interna['susceptibilidad_interna'] == '2' else 1,
            'ValoracionCognitiva': 0 if valoracion_cognitiva['valoracion_cognitiva'] == '2' else 1,
            'RelacionesInterpersonales': 0 if relaciones_interpersonales['relaciones_interpersonales'] == '2' else 1,
            'PresionLaboralAcademica': 0 if presion_laboral['presion_laboral'] == '2' else 1,
            'FaltaApoyoSocial': 0 if falta_apoyo_social['falta_apoyo_social'] == '2' else 1,
        }
        prob_stress = self.inference.query(variables=['Estrés'], evidence=evidence).values[1]
        print("Probabilidad calculada de estrés:", prob_stress)
        self.recommendations.append(f"Probabilidad calculada de estrés: {prob_stress}")

        if 0.30 <= prob_stress < 0.40:
            self.diagnosis.append("Su probabilidad de estrés está en un rango bajo.")
            self.recommendations.append(
                "Siga practicando técnicas de manejo del estrés y busque mantener un equilibrio saludable en su vida diaria.")

        elif 0.40 <= prob_stress < 0.50:
            self.diagnosis.append("Su probabilidad de estrés es moderada.")
            self.recommendations.append(
                "Además de las técnicas de manejo del estrés, considere hablar con un profesional de la salud mental para obtener apoyo adicional.")

        elif 0.50 <= prob_stress < 0.60:
            self.diagnosis.append("Su probabilidad de estrés es moderadamente alta.")
            self.recommendations.append(
                "Es importante buscar formas adicionales de reducir el estrés, como practicar actividades físicas regularmente y establecer límites saludables.")

        elif prob_stress >= 0.60:
            self.diagnosis.append("Su probabilidad de estrés es alta.")
            self.recommendations.append(
                "Se recomienda encarecidamente buscar ayuda profesional para abordar y gestionar su estrés de manera efectiva.")

    def get_recommendations(self):
        return self.recommendations

    def get_diagnosis(self):
        return self.diagnosis
