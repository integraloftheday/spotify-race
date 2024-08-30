from fasthtml.common import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv
from assistant import Assistant
import json
import random

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
    # Validate the URL format
    if not re.match(r'https?://open\.spotify\.com/playlist/[a-zA-Z0-9]+', playlist_url):
        raise ValueError("Invalid Spotify playlist URL format")

    playlist_id = playlist_url.split('/')[-1].split('?')[0]
    try:
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
        results = sp.playlist_tracks(playlist_id)
        songs = []
        artists = []
        for track in results['items']:
            if track['track']:  # Check if track is not None
                song_name = track['track']['name']
                artist_name = track['track']['artists'][0]['name']
                songs.append(song_name)
                artists.append(artist_name)

        while results['next']:
            results = sp.next(results)
            for track in results['items']:
                if track['track']:  # Check if track is not None
                    song_name = track['track']['name']
                    artist_name = track['track']['artists'][0]['name']
                    songs.append(song_name)
                    artists.append(artist_name)

        df = pd.DataFrame({'Song': songs, 'Artist': artists})
        return df, playlist_name
    except spotipy.exceptions.SpotifyException as e:
        raise ValueError(f"Error accessing Spotify playlist: {str(e)}")

# Initialize FastHTML app
app = FastHTML()
assistantRC = Assistant("RC")
def generate_humor_response(race_table):
    total = race_table['Count'].sum()
    race_table['Percentage'] = (race_table['Count'] / total) * 100

    responses = {
        'White': [
            "This playlist needs sunscreen!",
            "Have you ever heard of Kendrick?",
            "Is this the soundtrack for a farmer's market?",
            "Ah, the sweet sound of privilege."
        ],
        'Black': [
            "This playlist's got more soul than a foot locker.",
            "Warning: May cause spontaneous dance battles.",
            "You've got the funk. No, really, you should get that checked.",
            "This playlist is brought to you by the letter 'R' for Rhythm."
        ],
        'Asian': [
            "This playlist is more packed than a Tokyo subway.",
            "Careful, this mix might be too spicy for some.",
            "Is this K-pop or J-pop? Wait, don't tell me, I'll guess!",
            "This playlist has more layers than a bao bun."
        ],
        'Latino': [
            "This playlist is hotter than your abuela's salsa recipe.",
            "Warning: May cause spontaneous salsa dancing.",
            "Is this playlist legal? Because it's got me feeling loco.",
            "This mix is spicier than a jalapeño eating contest."
        ],
        'Indian':[
            "Not just Bollywood...",
            "Warning: May cause spontaneous garba dancing.",
            "Is your playlist on a hunger strike? ",
            "This mix is so Indian, it's outsourcing other playlists",
            "Hello can I help with your computer?"
        ]
    }

    dominant_race = race_table.loc[race_table['Percentage'].idxmax()]
    if dominant_race['Percentage'] >= 70:
        return random.choice(responses.get(dominant_race['Race'], ["Wow, that's quite a mix!"]))
    else:
        return "Your playlist is a melting pot of musical diversity!"

# Initialize FastHTML app
app = FastHTML()
assistantRC = Assistant("RC")

# Define the home route
@app.get("/")
def home():
    return Title("Is Your Spotify Playlist Racist?"), Main(
        H1("Is Your Spotify Playlist Racist?", style="font-family: Arial, sans-serif; color: #333; text-align: center;"),
        H3("Enter your Spotify playlist URL below:", style="font-family: Arial, sans-serif; color: #666; text-align: center;"),
        Form(
            Input(type="text", name="url", placeholder="Paste Spotify URL here...", style="width: 100%; padding: 8px; margin: 10px 0; box-sizing: border-box;"),
            Button("Analyze", type="submit", style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer;"),
            action="/urlEnter", method="post", hx_post="/urlEnter", hx_target="#output", hx_swap="innerHTML"
        ),
        Div(id="loading-overlay", style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1000;"),
        Div(id="loading-message", style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: white; padding: 20px; border-radius: 5px; z-index: 1001; text-align: center;"),
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
            var loadingMessages = [
                "Triangulating song contents...",
                "Passing to virtual agent...",
                "Analyzing musical vibes...",
                "Decoding hidden messages...",
                "Consulting the rhythm oracle...",
                "Calibrating genre detectors..."
            ];
            var currentMessageIndex = 0;

            function showNextMessage() {
                var messageElement = document.getElementById('loading-message');
                messageElement.innerHTML = '<div class="loader"></div><p>' + loadingMessages[currentMessageIndex] + '</p>';
                currentMessageIndex = (currentMessageIndex + 1) % loadingMessages.length;
            }

            document.querySelector('form').addEventListener('submit', function() {
                document.getElementById('loading-overlay').style.display = 'block';
                document.getElementById('loading-message').style.display = 'block';
                showNextMessage();
                setInterval(showNextMessage, 1500);
            });

            function toggleBreakdown() {
                var breakdownDiv = document.getElementById('breakdown');
                if (breakdownDiv.style.display === 'none') {
                    breakdownDiv.style.display = 'block';
                    drawPieChart();
                } else {
                    breakdownDiv.style.display = 'none';
                }
            }
            
            function drawPieChart() {
                if (!window.myChart) {
                    const ctx = document.getElementById('pieChart').getContext('2d');
                    const data = JSON.parse(document.getElementById('race-data').textContent);
                    window.myChart = new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                data: data.values,
                                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
                                hoverOffset: 4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: {
                                legend: {
                                    position: 'top',
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            return context.label + ': ' + context.raw;
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
            }
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
        
        # Generate humor response
        humor_response = generate_humor_response(race_table)
    else:
        race_data_json = json.dumps({'labels': [], 'values': []})
        race_table_html = "<p>No race data available.</p>"
        humor_response = "Hmm, this playlist is as mysterious as a mime in a house of mirrors!"

    print(race_data_json)
    
    # Prepare the HTML content with humor response and breakdown toggle
    return f"""
        <script>
            document.getElementById('loading-overlay').style.display = 'none';
            document.getElementById('loading-message').style.display = 'none';
        </script>
        <h2>Analysis for playlist: {playlist_name}</h2>
        <h3>Our totally scientific and not at all biased analysis says:</h3>
        <p style="font-size: 1.2em; font-weight: bold;">{humor_response}</p>
        <button onclick="toggleBreakdown()" style="margin-top: 20px; background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer;">Toggle Breakdown</button>
        <div id="breakdown" style="display: none;">
            <h3>Race Category Occurrences:</h3>
            {race_table_html}
            <h3>Pie chart of 'Race' column:</h3>
            <div style="width: 50%; margin: auto;">
                <canvas id="pieChart"></canvas>
            </div>
            <h3>Song List:</h3>
            <div style="max-height: 400px; overflow-y: auto;">
                {df.to_html(index=False, classes="table table-striped")}
            </div>
        </div>
        <div id="race-data" style="display: none;">{race_data_json}</div>
    """

# Serve the app
serve()