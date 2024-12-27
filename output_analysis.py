import pandas as pd
import numpy as np
from sim_animation import g, Trial

#overwrite g class - while we are messing around
g.patient_inter = 1
g.mean_n_consult_time = 6
g.n_cubicles = 2
g.sim_duration = 120
g.number_of_runs = 5

# Create an instance of the Trial class
my_trial = Trial()

# Call the run_trial method of our Trial object
my_trial.run_trial()

print("Raw results from the model - 1 row per event")
display(my_trial.all_event_logs.tail(100))

display(my_trial.all_event_logs.head(50))

#call my dataframe seomthing sensible
my_df = my_trial.all_event_logs

#find all unique values
unique_events = np.unique(my_df["event"])
print(unique_events)

#select only certain columns
print(my_df.columns) #shows you which are regular columns and which are index
my_selection = my_df[["patient", "event", "time", "run"]]
my_selection.head()
#pivot0.drop(columns="event", inplace=True)

#select only certain rows (pandas method)
my_selection_rows = my_selection[(my_selection["patient"] < 10) & (my_selection["run"] < 2)] #could use.loc but also works without it
my_selection_rows.head(100)

#pivot so 1 row per patient per run
pivot0 = my_selection_rows.pivot(index=["patient","run"], columns="event", values="time")
pivot0 = (pivot0.reset_index()
                .rename_axis(None,axis=1))

pivot0.head()

#making calculated columns
pivot0["total_los"] = pivot0["depart"] - pivot0["arrival"]
pivot0["q_time"] = pivot0["treatment_begins"] - pivot0["treatment_wait_begins"]
pivot0["treatment_time"] = pivot0["treatment_complete"] - pivot0["treatment_begins"]
                                 
pivot0.tail()

#creating a summary table by run
summary = pivot0.groupby("run").agg(
    mean_qtime=("q_time", "mean"),
    sd_qtime=("q_time", "std"),
    sum_value=("q_time", "sum"),
    arrivals=("patient", "count"), # arrivals
    under_2=(("q_time", lambda x: (x < 2).sum()))
).reset_index()

summary.head()


#create a histogram of waiting times


#create a box and whisker of waiting times per run


#create a plot of waiting times over time