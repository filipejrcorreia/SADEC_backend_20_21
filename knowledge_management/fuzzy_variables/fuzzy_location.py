import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class Fuzzy_Location:

    def __init__(self,infection_rate, population_number, population_density):
        self.infection_rate_input = infection_rate
        self.population_number_input = population_number
        self.population_density_input = population_density
    
    def set_infection_rate(self, infection_rate):
        self.infection_rate_input = infection_rate
    
    def set_population_number(self, population_number):
        self.population_number_input = population_number
    
    def set_population_density(self, population_density):
        self.population_density_input = population_density
    
    def get_fuzzy_value(self):
    
        infection_rate = ctrl.Antecedent(np.arange(0,2500,10), 'infection_rate') 
        population_number = ctrl.Antecedent(np.arange(0, 600000, 100), 'population_number') 
        population_density = ctrl.Antecedent(np.arange(0, 10000, 10), 'population_density')
        location_impact = ctrl.Consequent(np.arange(0,1.1,0.01), 'location_impact')
    
        infection_rate['baixo'] = fuzz.trapmf(infection_rate.universe, [-1,0,120,151])
        infection_rate['moderado'] = fuzz.trapmf(infection_rate.universe, [107,120,240,301 ])
        infection_rate['elevado'] = fuzz.trapmf(infection_rate.universe, [222,240,480,512])
        infection_rate['muito elevado'] = fuzz.trapmf(infection_rate.universe, [456,480,960,1003])
        infection_rate['extremamente elevado'] = fuzz.trapmf(infection_rate.universe, [871,960,1999,2500])
    
        population_number['muito baixa'] = fuzz.trapmf(population_number.universe, [-1,0,2000,3000])
        population_number['baixa'] = fuzz.trapmf(population_number.universe, [2000,3000,6000,7500])
        population_number['moderada'] = fuzz.trapmf(population_number.universe, [6000,7500,13000,15000])
        population_number['elevada'] = fuzz.trapmf(population_number.universe, [13000,15000,30000,40000])
        population_number['muito elevada'] = fuzz.trapmf(population_number.universe, [30000,40000,200000,230000])
        population_number['extremamente elevada'] = fuzz.trapmf(population_number.universe, [200000,230000,600000,600001])
    
        population_density['muito baixa'] = fuzz.trapmf(population_density.universe, [-1,0,6,15])
        population_density['baixa'] = fuzz.trapmf(population_density.universe, [6,15,25,40])
        population_density['moderada'] = fuzz.trapmf(population_density.universe, [25,40,60,100])
        population_density['elevada'] = fuzz.trapmf(population_density.universe, [60,100,170,2000])
        population_density['muito elevada'] = fuzz.trapmf(population_density.universe, [170,2000,5000,6000])
        population_density['extremamente elevada'] = fuzz.trapmf(population_density.universe, [5000,6000,10000,10001])
    
        location_impact['extremely low'] = fuzz.trimf(location_impact.universe, [-1,0,0.27])
        location_impact['very low'] = fuzz.trapmf(location_impact.universe, [0.13,0.27,0.4,0.54])
        location_impact['low'] = fuzz.trapmf(location_impact.universe, [0.4,0.54,0.675,0.75])
        location_impact['moderate'] = fuzz.trapmf(location_impact.universe, [0.675,0.75,0.8,0.85])
        location_impact['high'] = fuzz.trapmf(location_impact.universe, [0.8,0.85,0.9,1])

        rule1 = ctrl.Rule(infection_rate['extremamente elevado'] | population_density['elevada'] | population_number['extremamente elevada'] , location_impact['moderate'])    
        rule2 = ctrl.Rule(infection_rate['muito elevado'] | population_density['muito elevada'] | population_number['muito elevada'] | population_number['extremamente elevada'] , location_impact['moderate'])
        rule3 = ctrl.Rule(infection_rate['elevado'] | population_density['extremamente elevada'] | population_number['elevada'] , location_impact['low'])
        rule4 = ctrl.Rule(infection_rate['moderado'] | population_density['baixa'] | population_density['moderada'] | population_number['moderada'] | population_number['baixa'] , location_impact['very low'])
        rule5 = ctrl.Rule(infection_rate['baixo'] | population_density['baixa'] | population_density['muito baixa'] | population_number['baixa'] | population_number['muito baixa'] , location_impact['extremely low'])
    
        location_ctrl = ctrl.ControlSystem([rule1, rule2, rule3,rule4])
    
        location = ctrl.ControlSystemSimulation(location_ctrl)
    
    
        location.input['population_density'] = self.population_density_input
        location.input['infection_rate'] = self.infection_rate_input
        location.input['population_number'] = self.population_number_input
    
        # Crunch the numbers
        location.compute()
    
        return location.output['location_impact']
    
    
    
    
    
    