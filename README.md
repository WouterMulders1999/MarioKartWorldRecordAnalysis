# Mario Kart World Record Analysis
This repo contains the source code for the [Mario Kart 7 World Record Analysis app](https://mariokartworldrecordanalysis-cz2n83nsuer7ckxmj3ezee.streamlit.app/).
Under the hood, this code retrieves data from the [official world record history](https://mkwrs.com/mk7/) for each course in the game.

In Mario Kart 7, players aim to complete a course by driving three laps as fast as possible. The app shows three plots, where the x-axis represents total times (the sum of all three lap times)
and the y-axis shows individual lap times (graph 1 being for lap 1, graph 2 being for lap 2 and graph 3 being for lap 3). This gives insight into the improvements over time of both the lap times and total times
throughout the history of Mario Kart 7.

Interestingly enough, most graphs show a clear linear trend. Therefore the app also contains a fun tool to predict what time a player can get based on one or more lap times.
For instance, players who have just started learning a new track can use this tool can see what kind of time to expect given some of their lap times.
Or when a player unfortunately fails a run on the third lap, the tool can be used to receive an estimate of what time they could have gotten.

For some more visually interesting graphs and statistics, I refer to the Mario Kart 7 PowerBI dashboards. These dashboards include various visuals, highlighting
strategies used on various tracks in the game.

