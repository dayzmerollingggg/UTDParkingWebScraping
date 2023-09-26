import pandas as pd
import matplotlib.pyplot as plt

for i in range(1, 3):
    filename = f"table_{i}.csv"
    df = pd.read_csv(filename)
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Hour'].astype(str) + ':' + df['Minute'].astype(str))
    permit_types = ['Gold Permit', 'Orange Permit', 'Purple Permit', 'Pay-By-Space Permit']

    timelines = {}

    for permit_type in permit_types:
        permit_df = df[df['Permit Type'] == permit_type]
        permit_df = permit_df.groupby(pd.Grouper(key='Datetime', freq='H')).sum()
        timelines[permit_type] = permit_df['Spaces Left']


for permit_type, timeline in timelines.items():
    plt.plot(timeline.index, timeline.values, label=permit_type)

plt.xlabel('Time')
plt.ylabel('Available Spaces')
plt.title('Available Spaces by Permit Type')
plt.legend()
plt.show()

