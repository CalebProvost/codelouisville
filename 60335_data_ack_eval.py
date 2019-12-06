### To Do: ###
## slice out the cycles:
# - [*] Use the negative values in the ambient air column to determine the cycles
# - [*] Find the start and end points of the cycles
# - [*] With the start and end points found, slice out those values (dynamically) to make a cycle
# - [*] Print out the average value per column for each cycle
# - [*] Print out the max value per column for each cycle
# - [*] Display the peak cycles differently than the rest
# - [*] Export results, accounting for ambient offset, to an html file
# - [*] Export and append results of 2% difference to the html file
# - [*] Export and append results of just the max values to the html file

import pandas as pd
import numpy as np
import webbrowser
import os


### Function to display peak cycles differently from the rest ###
# highlight the maximum in a Series or DataFrame
def highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series yellow.
    '''
    attr = 'background-color: {}'.format(color)
    data = data.replace('%','', regex=True).astype(float) # remove % and cast to float
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)


# color the values red if the delta 2 difference is above 2%
def notate_over_delta(val):
    '''
    Colors the values in a Series red if delta is over 2%.
    '''
    color = 'red' if val > 2 else 'black'
    return 'color: %s' % color


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


### Print out the max value per column for each cycle ###

# Using the dictionary of cycles, create a dictionary containing only the max values of each row 
max_dict = {}
# Assign max values
for num in range(len(cycle_end_sliced)):
    key_max_name = "cycle_max_"+str(num+1)
    key_num_name = "cycle_num_"+str(num+1)
    max_dict[key_max_name] = cycle_dict[key_num_name].astype(float).max().to_frame().transpose()


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


### Manipulate Data ###

## Calculate the % diff of averages in each cycle ##
mean_delta = df = pd.DataFrame()
for count in range(len(mean_dict)):
    if count+2 > len(mean_dict):
        break
    cycle2 = mean_dict["cycle_mean_"+str(count+2)]
    cycle1 = mean_dict["cycle_mean_"+str(count+1)]
    delta = (abs( cycle2 - cycle1 ) / cycle1 ) * 100
    mean_delta = mean_delta.append(delta, ignore_index = True)
    mean_delta.index += 1

## Calculate the % diff of max values in each cycle ##
max_delta = df = pd.DataFrame()
for count in range(len(max_dict)):
    if count+2 > len(max_dict):
        break
    cycle2 = max_dict["cycle_max_"+str(count+2)]
    cycle1 = max_dict["cycle_max_"+str(count+1)]
    delta = (abs( cycle2 - cycle1 ) / cycle1 ) * 100
    max_delta = max_delta.append(delta, ignore_index = True)
    max_delta.index += 1

## Max Values Offset from Max Ambient Value ##
offset_max = df = pd.DataFrame()
for count in range(len(mean_dict)):
    name = "cycle_max_"+str(count+1)
    degree_diff = float(max_dict[name][select_ambient]) - float(75)
    ambient_offset = max_dict[name] + degree_diff
    max_dict[name][select_ambient] = float(75) # reset_ambient
    offset_max = offset_max.append(ambient_offset, ignore_index = True)


### Display the peak cycles highlighted differently ###

## Style Manipulated Data and Merge for one Report ##

offset_results = offset_max.style\
                .apply(highlight_max,)\
                .set_caption('<h1>Peak Values per Cycle with Ambient Offset</h1>')
offset_report = offset_results.render()

mean_delta_results = mean_delta.style\
                .applymap(notate_over_delta)\
                .apply(highlight_max, color="MediumPurple")\
                .set_caption('<h1>Average of Each Cycle as Delta 2</h1>')
mean_delta_report = mean_delta_results.render()

max_delta_results = max_delta.style\
                .applymap(notate_over_delta)\
                .apply(highlight_max, color="DeepSkyBlue")\
                .set_caption('<h1>Max of Each Cycle as Delta 2</h1>')
max_delta_report = max_delta_results.render()

all_max_results = all_max.style\
                .apply(highlight_max, color="OliveDrab")\
                .set_caption('<h1>Peak Value of all Cycles</h1>')
all_max_report = all_max_results.render()

report = offset_report + mean_delta_report + max_delta_report + all_max_report


#render dataframe as html
# html = results.render()
html = report

#write html to file
html_file = file+".html"
text_file = open(html_file, "w")
text_file.write(html)
text_file.close()

# ## Open results in browser
# url = 'file:/' + os.path.realpath(html_file)
# webbrowser.open(url, new=2)  # open in new tab

#write html to file for auto execution
auto_html = "url.html"
open_file = open(auto_html, "w")
open_file.write(html)
open_file.close()
