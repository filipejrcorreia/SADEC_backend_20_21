import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class Fuzzy_Headache:

    def __init__(self,headache_type = 0,headache_intensity = 0):
        self.headache_type_input = headache_type
        self.headache_intensity_input = headache_intensity

    def set_headache_type(self, headache_type):
        self.headache_type = headache_type

    def set_headache_intensity(self, headache_intensity):
        self.headache_intensity = headache_intensity

    def get_fuzzy_value(self):

        headache_type = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'headache_type') 
        headache_intensity = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'headache_intensity') 
        headache_intensity['moderada'] = fuzz.trapmf(headache_intensity.universe, [-1,0,0.3,0.7])
        headache_intensity['severa'] = fuzz.trapmf(headache_intensity.universe, [0.3,0.7,1, 1.1])

        headache_type['enxaqueca'] = fuzz.sigmf(headache_type.universe, 0.2,-25.0)
        headache_type['cefaleia'] = fuzz.gbellmf(headache_type.universe, 0.17,1.5,0.5)
        headache_type['tensao'] = fuzz.sigmf(headache_type.universe, 0.8, 25.0)
        
        covid_related_headache = ctrl.Consequent(np.arange(0,1.1,0.1), 'covid_related_headache')
        covid_related_headache['low'] = fuzz.trimf(covid_related_headache.universe, [-1,0,0.5])
        covid_related_headache['medium']  = fuzz.trimf(covid_related_headache.universe, [0,0.5,1.0])
        covid_related_headache['high']  = fuzz.trimf(covid_related_headache.universe, [0.5,1.0,1.1])
        
        rule1 = ctrl.Rule(headache_type['tensao'], covid_related_headache['high'] )
        rule2 = ctrl.Rule(headache_intensity['severa'] | headache_type['enxaqueca'], covid_related_headache['medium'] )
        rule3 = ctrl.Rule(headache_intensity['moderada'] | headache_type['cefaleia'] , covid_related_headache['low'] )

        headache_ctrl = ctrl.ControlSystem([rule1,rule2,rule3])
        headache = ctrl.ControlSystemSimulation(headache_ctrl)
        headache.input['headache_intensity'] = self.headache_intensity_input
        headache.input['headache_type'] = self.headache_type_input

        # Crunch the numbers
        headache.compute()

        return headache.output['covid_related_headache']





