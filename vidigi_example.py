import random
import numpy as np
import pandas as pd
import simpy
from sim_tools.distributions import Exponential, Lognormal
from vidigi.utils import populate_store

class g:
    '''
    Create a scenario to parameterise the simulation model

    Parameters:
    -----------
    random_number_set: int, optional (default=DEFAULT_RNG_SET)
        Set to control the initial seeds of each stream of pseudo
        random numbers used in the model.

    n_cubicles: int
        The number of treatment cubicles

    trauma_treat_mean: float
        Mean of the trauma cubicle treatment distribution (Lognormal)

    trauma_treat_var: float
        Variance of the trauma cubicle treatment distribution (Lognormal)

        arrival_rate: float
        Set the mean of the exponential distribution that is used to sample the
        inter-arrival time of patients

    '''
    random_number_set = 42

    n_cubicles = 4
    trauma_treat_mean = 40
    trauma_treat_var = 5

    arrival_rate = 5
    sim_duration = 600
    number_of_runs = 100

class Patient:
    '''
    Class defining details for a patient entity
    '''
    def __init__(self, p_id):
        '''
        Constructor method

        Params:
        -----
        identifier: int
            a numeric identifier for the patient.
        '''
        self.identifier = p_id
        self.arrival = -np.inf
        self.wait_treat = -np.inf #q_time_nurse
        self.total_time = -np.inf
        self.treat_duration = -np.inf

class Model:
    '''
    Simulates the simplest minor treatment process for a patient

    1. Arrive
    2. Examined/treated by nurse when one available
    3. Discharged
    '''
    def __init__(self, run_number):
        self.env = simpy.Environment()
        self.event_log = []
        self.patient_counter = 0
        self.patients = []
        self.init_resources()
        self.run_number = run_number

        self.results_df = pd.DataFrame()
        self.results_df["Patient ID"] = [1]
        self.results_df["Queue Time Cubicle"] = [0.0]
        self.results_df["Time with Nurse"] = [0.0]
        self.results_df.set_index("Patient ID", inplace=True)

        self.mean_q_time_cubicle = 0

        self.patient_inter_arrival_dist = Exponential(mean = g.arrival_rate,
                                                      random_seed = self.run_number*g.random_number_set)
        self.treat_dist = Lognormal(mean = g.trauma_treat_mean,
                                    stdev = g.trauma_treat_var,
                                    random_seed = self.run_number*g.random_number_set)

    def init_resources(self):
        '''
        Init the number of resources
        and store in the arguments container object

        Resource list:
            1. Nurses/treatment bays (same thing in this model)

        '''
        self.treatment_cubicles = simpy.Store(self.env)

        populate_store(num_resources=g.n_cubicles,
                       simpy_store=self.treatment_cubicles,
                       sim_env=self.env)

    def generator_patient_arrivals(self):
        while True:
            self.patient_counter += 1

            p = Patient(self.patient_counter)

            self.patients.append(p)

            self.env.process(self.attend_clinic(p))

            sampled_inter = self.patient_inter_arrival_dist.sample()

            yield self.env.timeout(sampled_inter)

    def attend_clinic(self, patient):
        self.arrival = self.env.now
        self.event_log.append(
            {'patient': patient.identifier,
             'pathway': 'Simplest',
             'event_type': 'arrival_departure',
             'event': 'arrival',
             'time': self.env.now}
        )

        start_wait = self.env.now
        self.event_log.append(
            {'patient': patient.identifier,
             'pathway': 'Simplest',
             'event': 'treatment_wait_begins',
             'event_type': 'queue',
             'time': self.env.now}
        )

        treatment_resource = yield self.treatment_cubicles.get()

        self.wait_treat = self.env.now - start_wait
        self.event_log.append(
            {'patient': patient.identifier,
                'pathway': 'Simplest',
                'event': 'treatment_begins',
                'event_type': 'resource_use',
                'time': self.env.now,
                'resource_id': treatment_resource.id_attribute
                }
        )

        self.treat_duration = self.treat_dist.sample()
        yield self.env.timeout(self.treat_duration)

        self.event_log.append(
            {'patient': patient.identifier,
                'pathway': 'Simplest',
                'event': 'treatment_complete',
                'event_type': 'resource_use_end',
                'time': self.env.now,
                'resource_id': treatment_resource.id_attribute}
        )

        self.treatment_cubicles.put(treatment_resource)

        self.total_time = self.env.now - self.arrival
        self.event_log.append(
            {'patient': patient.identifier,
            'pathway': 'Simplest',
            'event': 'depart',
            'event_type': 'arrival_departure',
            'time': self.env.now}
        )

    def calculate_run_results(self):
        self.mean_q_time_cubicle = self.results_df["Queue Time Cubicle"].mean()

    def run(self):
        self.env.process(self.generator_patient_arrivals())
        self.env.run(until=g.sim_duration)
        self.calculate_run_results()
        self.event_log = pd.DataFrame(self.event_log)
        self.event_log["run"] = self.run_number
        return {'results': self.results_df, 'event_log': self.event_log}

class Trial:
    def  __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results["Run Number"] = [0]
        self.df_trial_results["Arrivals"] = [0]
        self.df_trial_results["Mean Queue Time Cubicle"] = [0.0]
        self.df_trial_results.set_index("Run Number", inplace=True)

        self.all_event_logs = []

    def run_trial(self):
        #print(f"{g.n_cubicles} nurses")
        #print("") ## Print a blank line
        for run in range(g.number_of_runs):
            random.seed(run)

            my_model = Model(run)
            model_outputs = my_model.run()
            patient_level_results = model_outputs["results"]
            event_log = model_outputs["event_log"]

            self.df_trial_results.loc[run] = [
                len(patient_level_results),
                my_model.mean_q_time_cubicle,
            ]

            #print(event_log)

            self.all_event_logs.append(event_log)
        self.all_event_logs = pd.concat(self.all_event_logs)

# Create an instance of the Trial class
my_trial = Trial()

# Call the run_trial method of our Trial object
my_trial.run_trial()

my_trial.all_event_logs.head()
