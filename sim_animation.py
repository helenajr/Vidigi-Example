import simpy
import random
import pandas as pd
from vidigi.utils import populate_store
from vidigi.animation import animate_activity_log


class g:
    patient_inter = 1
    mean_n_consult_time = 6
    n_cubicles = 2
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
        populate_store(num_resources=g.n_cubicles,
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

# event_position_df = pd.DataFrame([
#                     {'event': 'arrival',
#                      'x':  50, 'y': 300,
#                      'label': "Arrival" },

#                     # Triage - minor and trauma
#                     {'event': 'treatment_wait_begins',
#                      'x':  205, 'y': 170,
#                      'label': "Waiting for Treatment"},

#                     {'event': 'treatment_begins',
#                      'x':  205, 'y': 110,
#                      'resource':'n_cubicles',
#                      'label': "Being Treated"},

#                     {'event': 'depart',
#                      'x':  270, 'y': 70,
#                      'label': "Exit"}

#                 ])

# animate_activity_log(
#         event_log=my_trial.all_event_logs[my_trial.all_event_logs['run']==1],
#         event_position_df= event_position_df,
#         scenario=g(),
#         debug_mode=True,
#         every_x_time_units=1,
#         include_play_button=True,
#         icon_and_text_size=20,
#         gap_between_entities=6,
#         gap_between_rows=15,
#         plotly_height=700,
#         frame_duration=200,
#         plotly_width=1200,
#         override_x_max=300,
#         override_y_max=500,
#         limit_duration=g.sim_duration,
#         wrap_queues_at=25,
#         step_snapshot_max=125,
#         time_display_units="dhm",
#         display_stage_labels=False,
#         add_background_image="Simplest Model Background Image - Horizontal Layout.drawio.png",
#     )