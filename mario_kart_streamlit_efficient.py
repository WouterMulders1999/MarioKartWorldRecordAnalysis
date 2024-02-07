import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.linear_model import LinearRegression
import streamlit as st
import re
import altair as alt

# Function to scrape data for a specific track
def scrape_track_data(track_name, track_url):
    response = requests.get(track_url)
    soup = BeautifulSoup(response.text, "html.parser")

    data = {"Track": [], "TotalTime": [], "Lap1": [], "Lap2": [], "Lap3": []}

    # Find the second table on the page
    second_table = soup.find_all("table")[7]

    for row in second_table.find_all("tr")[1:]:
        columns = row.find_all("td")
        lap1_str = columns[5].text.strip()
        lap2_str = columns[6].text.strip()
        lap3_str = columns[7].text.strip()

        # Check if any lap time is '???' or not a valid lap time
        if not re.match(r'^\d+\.\d{3}$', lap1_str) \
                or not re.match(r'^\d+\.\d{3}$', lap2_str) \
                or not re.match(r'^\d+\.\d{3}$', lap3_str):
            continue

        # Extract and convert lap times to seconds
        lap1 = preprocess_lap_time(lap1_str)
        lap2 = preprocess_lap_time(lap2_str)
        lap3 = preprocess_lap_time(lap3_str)

        total_time = lap1 + lap2 + lap3

        data["Track"].append(track_name)
        data["TotalTime"].append(total_time)
        data["Lap1"].append(lap1)
        data["Lap2"].append(lap2)
        data["Lap3"].append(lap3)

    return pd.DataFrame(data)


# Function to preprocess LapTime values and convert to seconds
def preprocess_lap_time(lap_time_str):
    print("Input Lap Time:", lap_time_str)
    # Check if the input string matches the format (e.g., 27.189)
    if re.match(r'^\d+\.\d{3}$', lap_time_str):
        # Extract seconds and milliseconds using regular expressions
        seconds, milliseconds = map(int, lap_time_str.split('.'))
        lap_time_seconds = seconds + milliseconds / 1000
        print("Processed Lap Time:", lap_time_seconds)
        return lap_time_seconds
    else:
        print("Invalid Lap Time Format")
        return None

# Function to scrape data for all tracks
@st.cache_data
def scrape_all_tracks_data():
    track_names = ['Toad+Circuit', 'Daisy+Hills', 'Cheep+Cheep+Lagoon', 'Shy+Guy+Bazaar', 'Wuhu+Loop', 'Mario+Circuit', 'Music+Park', 'Rock+Rock+Mountain', 'Piranha+Plant+Slide', 'Wario+Shipyard', 'Neo+Bowser+City', 'Maka+Wuhu', 'DK+Jungle', "Rosalina's+Ice World", "Bowser's+Castle", 'Rainbow+Road', 'N64+Luigi+Raceway', 'GBA+Bowser+Castle+1', 'Wii+Mushroom+Gorge', "DS+Luigi's+Mansion", 'N64+Koopa+Troopa Beach', 'SNES+Mario+Circuit+2', 'Wii+Coconut+Mall', 'DS+Waluigi+Pinball', 'N64+Kalimari+Desert', 'DS+DK+Pass', 'GCN+Daisy+Cruiser', 'Wii+Maple+Treeway', 'Wii+Koopa+Cape', 'GCN+Dino+Dino+Jungle', 'DS+Airship+Fortress', 'SNES+Rainbow+Road', 'Wuhu+Loop+(Glitch)', 'Maka+Wuhu+(Glitch)', 'DK+Jungle+(Glitch)', 'GBA+Bowser+Castle+1+(Glitch)', 'GCN+Daisy+Cruiser+(Glitch)', 'Neo+Bowser+City+(Glitch)', 'Wii+Maple+Treeway+(Glitch)', 'Wii+Koopa+Cape+(Glitch)', "DS+Luigi's+Mansion+(Glitch)", 'Shy+Guy+Bazaar+(Glitch)', 'GCN+Dino+Dino+Jungle+(Glitch)', 'Wario+Shipyard+(Glitch)', 'DS+Airship+Fortress+(Glitch)', 'DS+DK+Pass+(Glitch)', 'Rainbow+Road+(Glitch)', 'Toad+Circuit', 'Daisy+Hills', 'Cheep+Cheep+Lagoon', 'Shy+Guy+Bazaar', 'Wuhu+Loop', 'Mario+Circuit', 'Music+Park', 'Rock+Rock+Mountain', 'Piranha+Plant+Slide', 'Wario+Shipyard', 'Neo+Bowser+City', 'Maka+Wuhu', 'DK+Jungle', 'Rosalina%27s+Ice+World', 'Bowser%27s+Castle', 'Rainbow+Road', 'N64+Luigi+Raceway', 'GBA+Bowser+Castle+1', 'Wii+Mushroom+Gorge', 'DS+Luigi%27s+Mansion', 'N64+Koopa+Troopa+Beach', 'SNES+Mario+Circuit+2', 'Wii+Coconut+Mall', 'DS+Waluigi+Pinball', 'N64+Kalimari+Desert', 'DS+DK+Pass', 'GCN+Daisy+Cruiser', 'Wii+Maple+Treeway', 'Wii+Koopa+Cape', 'GCN+Dino+Dino+Jungle', 'DS+Airship+Fortress', 'SNES+Rainbow+Road', 'Wuhu+Loop+%28Glitch%29', 'Maka+Wuhu+%28Glitch%29', 'DK+Jungle+%28Glitch%29', 'GBA+Bowser+Castle+1+%28Glitch%29', 'GCN+Daisy+Cruiser+%28Glitch%29', 'Neo+Bowser+City+%28Glitch%29', 'Wii+Maple+Treeway+%28Glitch%29', 'Wii+Koopa+Cape+%28Glitch%29', 'DS+Luigi%27s+Mansion+%28Glitch%29', 'Shy+Guy+Bazaar+%28Glitch%29', 'GCN+Dino+Dino+Jungle+%28Glitch%29', 'Wario+Shipyard+%28Glitch%29', 'DS+Airship+Fortress+%28Glitch%29', 'DS+DK+Pass+%28Glitch%29', 'Rainbow+Road+%28Glitch%29']

    dataframes = []
    for track_name in track_names:
        track_url = "https://mkwrs.com/mk7/display.php?track=" + track_name
        track_df = scrape_track_data(track_name, track_url)
        dataframes.append(track_df)

    return pd.concat(dataframes, ignore_index=True)

# Function to perform linear regression and plot results
def regression_and_plot(df, track):
    track_data = df[df["Track"] == track].reset_index(drop=True)

    # Create a DataFrame for plotting
    plot_data = pd.DataFrame({
        'TotalTime': track_data['TotalTime'].values.ravel(),
        'Lap1': track_data['Lap1'],
        'Lap2': track_data['Lap2'],
        'Lap3': track_data['Lap3']
    })

    # Iterate over each lap and total time combination
    for lap in ['Lap1', 'Lap2', 'Lap3']:
        # Calculate domain for x-axis
        x_min = plot_data['TotalTime'].min()
        x_max = plot_data['TotalTime'].max()

        # Calculate domain for y-axis
        y_min = plot_data[lap].min()
        y_max = plot_data[lap].max()

        scatter = alt.Chart(plot_data).mark_circle().encode(
            x=alt.X('TotalTime', scale=alt.Scale(domain=(x_min, x_max))),
            y=alt.Y(lap, scale=alt.Scale(domain=(y_min, y_max))),
            tooltip=['TotalTime', lap]
        )

        reg_line = alt.Chart(plot_data).mark_line().transform_regression(
            'TotalTime', lap
        ).encode(
            x='TotalTime',
            y=alt.Y(lap, scale=alt.Scale(domain=(y_min, y_max))),
            tooltip=['TotalTime', lap]
        )

        # Combine scatter plot and regression line
        combined_plot = (scatter + reg_line).properties(
            width=300,
            height=200,
            title=f"{lap} Regression"
        )

        # Display the plot
        st.altair_chart(combined_plot, use_container_width=True)

# Function to predict total time based on lap times
def predict_total_time(df, track, lap1=None, lap2=None, lap3=None):
    track_data = df[df["Track"] == track].reset_index(drop=True)
    
    # Case: Only Lap 1 is provided
    if lap1 is not None and lap2 is None and lap3 is None:
        model = LinearRegression()
        X = track_data[['Lap1']]
        model.fit(X, track_data['TotalTime'])
        return model.predict([[lap1]])[0]
    
    # Case: Only Lap 2 is provided
    elif lap1 is None and lap2 is not None and lap3 is None:
        model = LinearRegression()
        X = track_data[['Lap2']]
        model.fit(X, track_data['TotalTime'])
        return model.predict([[lap2]])[0]
    
    # Case: Only Lap 3 is provided
    elif lap1 is None and lap2 is None and lap3 is not None:
        model = LinearRegression()
        X = track_data[['Lap3']]
        model.fit(X, track_data['TotalTime'])
        return model.predict([[lap3]])[0]
    
    # Case: Lap 1 and Lap 2 are provided
    elif lap1 is not None and lap2 is not None and lap3 is None:
        model = LinearRegression()
        X = track_data[['Lap1', 'Lap2']]
        model.fit(X, track_data['TotalTime'])
        return model.predict([[lap1, lap2]])[0]
    
    # Case: Lap 1 and Lap 3 are provided
    elif lap1 is not None and lap2 is None and lap3 is not None:
        model = LinearRegression()
        X = track_data[['Lap1', 'Lap3']]
        model.fit(X, track_data['TotalTime'])
        return model.predict([[lap1, lap3]])[0]
    
    # Case: Lap 2 and Lap 3 are provided
    elif lap1 is None and lap2 is not None and lap3 is not None:
        model = LinearRegression()
        X = track_data[['Lap2', 'Lap3']]
        model.fit(X, track_data['TotalTime'])
        return model.predict([[lap2, lap3]])[0]
    
    # Case: All three laps are provided
    elif lap1 is not None and lap2 is not None and lap3 is not None:
        return lap1 + lap2 + lap3
    
    # Case: None of the laps are provided
    else:
        return None

def format_time(total_time_seconds):
    minutes = int(total_time_seconds) // 60
    seconds = int(total_time_seconds) % 60
    milliseconds = int((total_time_seconds - int(total_time_seconds)) * 1000)
    return f"{minutes}'{seconds:02d}\"{milliseconds:03d}"

# Main Streamlit app
def main():
    st.title("Mario Kart 7 World Records Analysis")

    track_df = scrape_all_tracks_data()

    selected_track = st.selectbox("Select Track:", track_df["Track"].unique(), key="select_track")

    regression_and_plot(track_df, selected_track)
    
    # Input lap times
    st.write("Here you can enter one or more of your lap times (formatted as xx.xxx) and receive a prediction of what time you could get with such a lap.")
    lap1_input = st.text_input('Enter Lap 1 Time (e.g. 27.189)', '', key="lap1_input")
    lap2_input = st.text_input('Enter Lap 2 Time (e.g. 27.189)', '', key="lap2_input")
    lap3_input = st.text_input('Enter Lap 3 Time (e.g. 27.189)', '', key="lap3_input")
    
    # Button to predict total time
    if st.button('Predict Total Time', key="predict_button"):
        # Preprocess lap times
        lap1 = preprocess_lap_time(lap1_input)
        lap2 = preprocess_lap_time(lap2_input)
        lap3 = preprocess_lap_time(lap3_input)
        
        if lap1 is not None or lap2 is not None or lap3 is not None:
            # Predict total time
            predicted_total_time = predict_total_time(track_df, selected_track, lap1, lap2, lap3)
            st.write(f'Predicted Total Time: {format_time(predicted_total_time)}')
        else:
            st.write('Invalid lap time format. Please enter lap times in seconds (e.g., 27.189)')

if __name__ == "__main__":
    main()
