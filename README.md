# Spotify Playlist Scraper

This Streamlit app allows you to scrape songs from a Spotify playlist and display them in a table.

## Prerequisites

- Python 3.6 or higher installed on your computer
- Spotify API credentials (client ID and client secret)
- Spotify playlist URL

## Installation

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/morriswong/spotify-playlist.git
   ```

2. Navigate to the project directory:
   ```
   cd spotify-playlist
   ```

3. Create a virtual environment (optional but recommended):
   - On Windows:
     ```
     python -m venv venv
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project directory and add your Spotify API credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. The app will open in your browser.

3. Enter the Spotify playlist URL in the input field.

4. Click the "Scrape Playlist" button.

5. The app will scrape the songs from the playlist, save them in a CSV file named `playlist.csv`, and display the playlist as a table below the input field.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the Apache License 2.0, See the [LICENSE](LICENSE) file for details.
