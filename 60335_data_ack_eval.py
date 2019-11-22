### To Do: ###
## slice out the cycles:
# - [*] Use the negative values in the ambient air column to determine the cycles
# - [*] Find the start and end points of the cycles
# - [*] With the start and end points found, slice out those values (dynamically) to make a cycle
# - [*] Print out the average value per column for each cycle
# - [*] Print out the max value per column for each cycle
# - [*] Display the peak cycles differently than the rest
# - [ ] Display "Testing Complete" when two cycles follow the peak without becoming the new peak 

import pandas as pd
import numpy as np
import webbrowser
import os

### Function to display peak cycles differently from the rest ###
# highlight the maximum in a Series or DataFrame
def highlight_max(data, color='yellow'):
    attr = 'background-color: {}'.format(color)
    #remove % and cast to float
    data = data.replace('%','', regex=True).astype(float)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)

# local file:
file = input("NOTE: The file must be .csv format and located in the same directory as this program.\nEnter the name of the file: ")
file = file+".csv"
database1 = pd.read_csv(file)[23:] # ignores invalid rows

# reset the name of the columns
headers = database1.iloc[0]
header = []
for index in range(len(headers)):
    header.append(headers[index])
database1.columns = header

# remove row with column headers and reset index
database1 = database1.reset_index(drop=True)
database1 = database1[1:]


### Find the start and end points of the cycles ###

print(database1.columns) # finding the correct column that has the ambient air label
select_ambient = input("Enter the name of the column for the room's ambient temperature: ")
database1[select_ambient] = database1[select_ambient].astype(float)
ambient = database1[select_ambient] # assign all values in ambient column to variable

## Set start point ##
cycle_start = ambient[ambient < 0].index+1
cycle_start_sliced = cycle_start[:-1]

## Set end point ##
cycle_end = ambient[ambient < 0].index
cycle_end_sliced = cycle_end[1:]

# Remove double negative indicators (false cycles)
for count in range(len(cycle_start_sliced)):
    if len(cycle_start_sliced) > count:
        if cycle_start_sliced[count] == cycle_end_sliced[count]:
            cycle_start_sliced = cycle_start_sliced.drop(cycle_start_sliced[count])
            cycle_end_sliced = cycle_end_sliced.drop(cycle_end_sliced[count])

print("Number of cycles found:",len(cycle_start_sliced),"\n")

### With the start and end points found, slice out those values (dynamically) to make a cycle ###

# Create a dictionary of each cycle as its own dataframe (ie: cycle_dict={[cycle_1:dataframe], ...} 
cycle_dict = {}
for num in range(len(cycle_end_sliced)):
    key_name = "cycle_num_"+str(num+1)
    cycle_dict[key_name] = database1.iloc[cycle_start_sliced[num]:cycle_end_sliced[num]]


### Print out the average value per column for each cycle ###

# Using the dictionary of cycles, create a dictionary containing only the mean values of each row 
mean_dict = {}
# Assign max values
for num in range(len(cycle_start_sliced)):
    key_mean_name = "cycle_mean_"+str(num+1)
    key_num_name = "cycle_num_"+str(num+1)
    mean_dict[key_mean_name] = cycle_dict[key_num_name].astype(float).mean().to_frame().transpose()

# # Display mean of cycles
# border = "-"*120
# for count in range(len(mean_dict)):
#     name = "cycle_mean_"+str(count+1)
#     print(border,"\nAverages of Cycle #",count+1,"\n",border)
#     display(mean_dict[name])

### Print out the max value per column for each cycle ###

# Using the dictionary of cycles, create a dictionary containing only the max values of each row 
max_dict = {}
# Assign max values
for num in range(len(cycle_end_sliced)):
    key_max_name = "cycle_max_"+str(num+1)
    key_num_name = "cycle_num_"+str(num+1)
    max_dict[key_max_name] = cycle_dict[key_num_name].astype(float).max().to_frame().transpose()

# # Display max of cycles
# for count in range(len(max_dict)):
#     name = "cycle_max_"+str(count+1)
#     print(border,"\nMax Value of Cycle #",count+1,"\n",border)
#     display(max_dict[name])

### Display the peak cycles differently than the rest ###

## Merge all cycles of mean values into one dataframe ##
all_mean = df = pd.DataFrame()
for count in range(len(mean_dict)):
    name = "cycle_mean_"+str(count+1)
    #print(border,"\nAverages of Cycle #",count+1,"\n",border)
    all_mean = all_mean.append(mean_dict[name], ignore_index = True)
print(all_mean)

## Merge all cycles of max values into one dataframe ##
all_max = df = pd.DataFrame()
for count in range(len(mean_dict)):
    name = "cycle_max_"+str(count+1)
    #print(border,"\nAverages of Cycle #",count+1,"\n",border)
    all_max = all_max.append(max_dict[name], ignore_index = True)
print(all_max)

### Display the peak cycles highlighted differently ###

results = all_max.style.apply(highlight_max)

#render dataframe as html
html = results.render()

#write html to file
html_file = file+".html"
text_file = open(html_file, "w")
text_file.write(html)
text_file.close()

## Open results in browser
url = 'file://' + os.path.realpath(html_file)
webbrowser.open(url, new=2)  # open in new tab
