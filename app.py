from fasthtml.common import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv
from assistant import Assistant
import json

# Load the environment variables from the .env file
load_dotenv()

# Get the Spotify API credentials from the environment variables
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Initialize the Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to scrape songs from a Spotify playlist
def scrape_playlist(playlist_url):
    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    playlist = sp.playlist(playlist_id)
    playlist_name = playlist['name']
    results = sp.playlist_tracks(playlist_id)
    songs = []
    artists = []
    for track in results['items']:
        song_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        songs.append(song_name)
        artists.append(artist_name)

    while results['next']:
        results = sp.next(results)
        for track in results['items']:
            song_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            songs.append(song_name)
            artists.append(artist_name)

    df = pd.DataFrame({'Song': songs, 'Artist': artists})
    return df, playlist_name

# ... (rest of the code remains the same until urlEnter function) ...


# Initialize FastHTML app
app = FastHTML()
assistantRC = Assistant("RC")

# Define the home route
@app.get("/")
def home():
    return Title("Is your Spotify Playlist Racist?"), Main(
        H1("Enter Spotify Playlist URL", style="font-family: Arial, sans-serif; color: #333; text-align: center;"),
        Form(
            Input(type="text", name="url", placeholder="Paste Spotify URL here...", style="width: 100%; padding: 8px; margin: 10px 0; box-sizing: border-box;"),
            Button("Submit", type="submit", style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer;"),
            action="/urlEnter", method="post", hx_post="/urlEnter", hx_target="#output", hx_swap="innerHTML"
        ),
        Div(id="output", style="margin-top: 20px; font-family: Arial, sans-serif;"),
        Script(src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.1/chart.min.js"),
        Style("""
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loader {
                border: 5px solid #f3f3f3;
                border-top: 5px solid #3498db;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
        """),
        Script("""
            document.querySelector('form').addEventListener('submit', function() {
                document.getElementById('output').innerHTML = '<div class="loader"></div><p>Processing... Please wait.</p>';
            });
        """)
    )


# Function to handle URL entry
@app.post("/urlEnter")
def urlEnter(url: str):
    print(f"URL Entered: {url}")
    df, playlist_name = scrape_playlist(url)
    csv_buffer = StringIO()
    df[df.columns[-1]].to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    # Process the data as needed with your assistantRC or other logic
    csv_rc = assistantRC.chat(csv_string)
    # Convert csv_rc to a pandas DataFrame
    csv_df = pd.read_csv(StringIO(csv_rc))
    print(csv_df)
    print(df)

    # Append csv_df to df
    last_column = csv_df[csv_df.columns[-1]]
    df[csv_df.columns[-1]] = last_column.values

    # Prepare data for Chart.js and race category table
    if 'Race' in df.columns:
        race_counts = df['Race'].value_counts()
        race_labels = race_counts.index.tolist()
        race_values = race_counts.tolist()
        race_data = {
            'labels': race_labels,
            'values': race_values
        }
        race_data_json = json.dumps(race_data)
        
        # Create race category occurrence table
        race_table = pd.DataFrame({'Race': race_labels, 'Count': race_values})
        race_table_html = race_table.to_html(index=False, classes="table table-striped")
    else:
        race_data_json = json.dumps({'labels': [], 'values': []})
        race_table_html = "<p>No race data available.</p>"

    print(race_data_json)
    # Prepare the HTML content with Chart.js
    return f"""
        <h2>Analysis for playlist: {playlist_name}</h2>
        <div style="max-height: 400px; overflow-y: auto;">
            {df.to_html(index=False, classes="table table-striped")}
        </div>
        <style>
            .table-container {{
                max-height: 200px;
                overflow-y: auto;
            }}
            .table-container table {{
                width: 100%;
            }}
            .table-container thead th {{
                position: sticky;
                top: 0;
                background-color: #fff;
                z-index: 1;
            }}
        </style>
        <h3>Race Category Occurrences:</h3>
        {race_table_html}
        <h3>Pie chart of 'Race' column:</h3>
        <div style="width: 50%; margin: auto;">
            <canvas id="pieChart"></canvas>
        </div>
        <script>
            (function() {{
                // Destroy the previous chart if it exists
                if (window.myChart) {{
                    window.myChart.destroy();
                }}
                const ctx = document.getElementById('pieChart').getContext('2d');
                const data = {race_data_json};
                window.myChart = new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: data.labels,
                        datasets: [{{
                            data: data.values,
                            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
                            hoverOffset: 4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {{
                            legend: {{
                                position: 'top',
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        return context.label + ': ' + context.raw;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }})();
        </script>
    """

# Serve the app
serve()
