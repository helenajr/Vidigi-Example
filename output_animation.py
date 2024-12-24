import pandas as pd
from sim_animation import g, Trial
from vidigi.animation import animate_activity_log
#from vidigi.animation import reshape_for_animations
#from vidigi.animation import generate_animation_df
#from vidigi.animation import generate_animation

# Create an instance of the Trial class
my_trial = Trial()

# Call the run_trial method of our Trial object
my_trial.run_trial()

display(my_trial.all_event_logs.tail(100))

print(g.n_cubicles)
print(g.patient_inter)

event_position_df = pd.DataFrame([
                    {'event': 'arrival',
                     'x':  50, 'y': 300,
                     'label': "Arrival" },

                    # Triage - minor and trauma
                    {'event': 'treatment_wait_begins',
                     'x':  205, 'y': 170,
                     'label': "Waiting for Treatment"},

                    {'event': 'treatment_begins',
                     'x':  205, 'y': 110,
                     'resource':'n_cubicles',
                     'label': "Being Treated"},

                    {'event': 'depart',
                     'x':  270, 'y': 70,
                     'label': "Exit"}

                ])

animate_activity_log(
        event_log=my_trial.all_event_logs[my_trial.all_event_logs['run']==1],
        event_position_df= event_position_df,
        scenario=g(),
        debug_mode=True,
        every_x_time_units=1,
        include_play_button=True,
        icon_and_text_size=20,
        gap_between_entities=6,
        gap_between_rows=15,
        gap_between_resources=10,
        plotly_height=700,
        frame_duration=200,
        plotly_width=1200,
        override_x_max=300,
        override_y_max=500,
        limit_duration=g.sim_duration,
        wrap_queues_at=25,
        step_snapshot_max=125,
        time_display_units="dhm",
        display_stage_labels=False,
        add_background_image="Simplest Model Background Image - Horizontal Layout.drawio.png",
    )

# step1 = reshape_for_animations(event_log=my_trial.all_event_logs[my_trial.all_event_logs['run']==1])

# step2 = generate_animation_df(full_patient_df=step1,
#                               event_position_df=event_position_df)

# display(my_trial.all_event_logs.tail(100))

# display(step1.tail(100))

# display(step2.tail(100))