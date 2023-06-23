import pandas as pd
from datetime import datetime, timedelta
import csv

class SurgeryScheduler:
    def __init__(self, num_rooms, rest_time):
        self.num_rooms = num_rooms
        self.rest_time = rest_time
        self.schedule = pd.DataFrame(columns=['', 'room_id', 'anesthetist_id', 'start_time', 'end_time'])
        self.updates = pd.DataFrame(columns=['', 'room_id', 'anesthetist_id', 'start_time', 'end_time'])
        self.waiting_list = pd.DataFrame(columns=['Surgery ID', 'Start Time', 'End Time'])

    def allocate_anesthesiologists(self, surgeries):
        surgeries = sorted(surgeries, key=lambda x: x[1])

        for surgery in surgeries:
            start_time = datetime.strptime(surgery[1], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(surgery[2], '%Y-%m-%d %H:%M:%S')

            available_anesthesiologists = self.schedule[
                (self.schedule['end_time'] <= start_time - timedelta(minutes=self.rest_time))]
            available_anesthesiologists_same_room = self.schedule[(self.schedule['end_time'] == start_time) ]
            if len(available_anesthesiologists_same_room) > 0:
                anesthesiologist = available_anesthesiologists_same_room.iloc[0]['anesthetist_id']
                room = available_anesthesiologists_same_room.iloc[0]['room_id']

                self.schedule.loc[(self.schedule['anesthetist_id'] == anesthesiologist) & (self.schedule['room_id'] == room), 'end_time'] = end_time
                self.schedule.loc[(self.schedule['anesthetist_id'] == anesthesiologist) & (self.schedule['room_id'] == room), 'start_time'] = start_time

                self.updates.loc[len(self.updates)] = [surgery[0], room, anesthesiologist, start_time, end_time]
            elif len(available_anesthesiologists) > 0:
                anesthesiologist = available_anesthesiologists.iloc[0]['anesthetist_id']
                room = available_anesthesiologists.iloc[0]['room_id']

                self.schedule.loc[(self.schedule['anesthetist_id'] == anesthesiologist) & (self.schedule['room_id'] == room), 'end_time'] = end_time
                self.schedule.loc[(self.schedule['anesthetist_id'] == anesthesiologist) & (self.schedule['room_id'] == room), 'start_time'] = start_time

                self.updates.loc[len(self.updates)] = [surgery[0], room, anesthesiologist, start_time, end_time]
            else:
                if len(self.schedule) < self.num_rooms:
                    room = len(self.schedule) % self.num_rooms
                    anesthesiologist = len(self.schedule)

                    self.schedule.loc[len(self.schedule)] = [surgery[0], room, anesthesiologist, start_time, end_time]

                    self.updates.loc[len(self.updates)] = [surgery[0], room, anesthesiologist, start_time, end_time]
                else:
                    self.waiting_list.loc[len(self.waiting_list)] = [surgery[0], start_time, end_time]

    def get_schedule(self):
        return self.schedule

    def get_updates(self):
        return self.updates


def read_surgeries_from_csv(filename):
    surgeries = []
    #i=0
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            surgery_id = int(row[0])
            start_time = row[1]
            end_time = row[2]
            surgeries.append([surgery_id, start_time, end_time])
    return surgeries


def plot_day_schedule(schedule):
    import colorcet as cc
    import seaborn as sns
    from matplotlib import pyplot as plt
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(w=2 * 9.5, h=2 * 5)
    fig.tight_layout(pad=1.7)

    resources = set(schedule['anesthetist_id'])
    resources = sorted(resources)
    resource_mapping = {resource: i for i, resource in enumerate(resources)}

    intervals_start = (schedule.start_time - schedule.start_time.dt.floor('d')).dt.total_seconds().div(3600)
    intervals_end = (schedule.end_time - schedule.start_time.dt.floor('d')).dt.total_seconds().div(3600)

    intervals = list(zip(intervals_start, intervals_end))

    palette = sns.color_palette(cc.glasbey_dark, n_colors=len(schedule))
    palette = [(color[0] * 0.9, color[1] * 0.9, color[2] * 0.9) for color in palette]
    cases_colors = {case_id: palette[i] for i, case_id in enumerate(set(schedule['room_id']))}

    for i, (resource_on_block_id, resource, evt) in enumerate(
            zip(schedule['room_id'], schedule['anesthetist_id'], intervals)):
        txt_to_print = str(i)
        ax.barh(resource_mapping[resource], width=evt[1] - evt[0], left=evt[0], linewidth=1, edgecolor='black',
                color=cases_colors[resource_on_block_id])
        ax.text((evt[0] + evt[1] - 0.07 * len(str(txt_to_print))) / 2, resource_mapping[resource], txt_to_print,
                name='Arial', color='white', va='center')

    ax.set_yticks(range(len(resources)))
    ax.set_yticklabels([f'{resource}' for resource in resources])

    ax.set_ylabel('anesthetist_id'.replace('_', ' '))

    ax.title.set_text(f'Total {len(set(schedule["anesthetist_id"]))} anesthetists')
    plt.show()

