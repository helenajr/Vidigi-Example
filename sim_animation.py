import simpy
import random
import pandas as pd
from vidigi.utils import populate_store


class g:
    patient_inter = 5
    mean_n_consult_time = 6
    number_of_nurses = 2
    sim_duration = 120
    number_of_runs = 5

class Patient:
    def __init__(self, p_id):
        self.id = p_id

class Model:
    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.event_log = []
        self.patient_counter = 0
        self.init_resources()
        self.run_number = run_number
    
    def init_resources(self):
        self.nurse = simpy.Store(self.env)
        populate_store(num_resources=g.number_of_nurses,
                       simpy_store=self.nurse,
                       sim_env=self.env)

    def generator_patient_arrivals(self):
        while True:
            self.patient_counter += 1
            p = Patient(self.patient_counter)
            self.env.process(self.attend_clinic(p))
            sampled_inter = random.expovariate(1.0 / g.patient_inter)
            yield self.env.timeout(sampled_inter)

    def attend_clinic(self, patient):
        self.arrival = self.env.now
        self.event_log.append(
            {'patient' : patient.id,
             'pathway' : 'Simplest',
             'event_type' : 'arrival_departure',
             'event' : 'arrival',
             'time' : self.env.now}
        )

        start_q_nurse = self.env.now
        self.event_log.append(
            {'patient' : patient.id,
             'pathway' : 'Simplest',
             'event_type' : 'queue',
             'event' : 'treatment_wait_begins',
             'time' : self.env.now}
        )

        treatment_resource = yield self.nurse.get()

        end_q_nurse = self.env.now
        patient.q_time_nurse = end_q_nurse - start_q_nurse
        self.event_log.append(
        {'patient' : patient.id,
        'pathway' : 'Simplest',
        'event_type' : 'resource_use',
        'event' : 'treatment_begins',
        'time' : self.env.now,
        'resource_id': treatment_resource.id_attribute
         }
        )

        sampled_nurse_act_time = random.expovariate(1.0 / 
                                                        g.mean_n_consult_time)
        
        yield self.env.timeout(sampled_nurse_act_time)

        self.event_log.append(
        {'patient' : patient.id,
        'pathway' : 'Simplest',
        'event_type' : 'resource_use_end',
        'event' : 'treatment_complete',
        'time' : self.env.now,
        'resource_id': treatment_resource.id_attribute}
        )
        self.nurse.put(treatment_resource)

        self.event_log.append(
        {'patient' : patient.id,
        'pathway' : 'Simplest',
        'event_type' : 'arrival_departure',
        'event' : 'depart',
        'time' : self.env.now}
        )
            

    def run(self):
        self.env.process(self.generator_patient_arrivals())
        self.env.run(until=g.sim_duration)
        self.event_log = pd.DataFrame(self.event_log)
        self.event_log["run"] = self.run_number
        return {'event_log':self.event_log}

class Trial:
    def  __init__(self):
        self.all_event_logs = []

    def run_trial(self):
        for run in range(g.number_of_runs):
            my_model = Model(run)
            model_outputs = my_model.run()
            event_log = model_outputs["event_log"]
            
            self.all_event_logs.append(event_log)
        self.all_event_logs = pd.concat(self.all_event_logs)

# Create an instance of the Trial class
my_trial = Trial()

# Call the run_trial method of our Trial object
my_trial.run_trial()

my_trial.all_event_logs.tail(100)