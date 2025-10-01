import pygame
import time
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pyowm

# --- Configuration ---
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
CALENDAR_API_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
WEATHER_LOCATION = "Indianapolis, US"
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# --- Pygame setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Code HUD")
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Drawing and typing variables ---
drawing_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
is_drawing = False
current_color = RED
current_text = ""
typing_mode = False

# --- API Clients ---
def get_calendar_events():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", CALENDAR_API_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", CALENDAR_API_SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    service = build("calendar", "v3", credentials=creds)
    now = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    events_result = service.events().list(calendarId="primary", timeMin=now, maxResults=5, singleEvents=True, orderBy="startTime").execute()
    events = events_result.get("items", [])
    return events

def get_weather():
    try:
        owm = pyowm.OWM(WEATHER_API_KEY)
        weather_mgr = owm.weather_manager()
        observation = weather_mgr.weather_at_place(WEATHER_LOCATION)
        weather = observation.weather
        return weather
    except Exception as e:
        return f"Error fetching weather: {e}"

# --- Drawing functions ---
def draw_line(surface, color, start_pos, end_pos):
    pygame.draw.line(surface, color, start_pos, end_pos, 5)

# --- Main game loop ---
def main():
    last_weather_update = 0
    weather_data = "Fetching weather..."
    
    last_calendar_update = 0
    calendar_events = []

    running = True
    while running:
        # Update data every 30 minutes
        if time.time() - last_weather_update > 1800:
            weather_data = get_weather()
            last_weather_update = time.time()
            
        if time.time() - last_calendar_update > 1800:
            calendar_events = get_calendar_events()
            last_calendar_update = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Drawing logic
            if event.type == pygame.MOUSEBUTTONDOWN and not typing_mode:
                if event.button == 1:
                    is_drawing = True
            if event.type == pygame.MOUSEBUTTONUP and not typing_mode:
                if event.button == 1:
                    is_drawing = False
            if event.type == pygame.MOUSEMOTION and is_drawing:
                draw_line(drawing_surface, current_color, event.pos, pygame.mouse.get_pos())
            
            # Typing logic
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t: # Toggle typing mode with 't' key
                    typing_mode = not typing_mode
                if typing_mode:
                    if event.key == pygame.K_RETURN:
                        current_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        current_text = current_text[:-1]
                    else:
                        current_text += event.unicode

        # --- Drawing background ---
        screen.fill(BLACK)
        screen.blit(drawing_surface, (0, 0))

        # --- Display Time ---
        time_text = font.render(time.strftime("%H:%M:%S"), True, WHITE)
        screen.blit(time_text, (10, 10))

        # --- Display Weather ---
        if isinstance(weather_data, str):
            weather_text = font.render(weather_data, True, WHITE)
            screen.blit(weather_text, (10, 50))
        else:
            weather_description = weather_data.detailed_status
            temperature = weather_data.temperature("fahrenheit")["temp"]
            weather_text = font.render(f"{WEATHER_LOCATION}: {weather_description}, {temperature}°F", True, WHITE)
            screen.blit(weather_text, (10, 50))
        
        # --- Display Calendar ---
        y_offset = 100
        for event in calendar_events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_text = font.render(f"{start} - {event['summary']}", True, WHITE)
            screen.blit(event_text, (10, y_offset))
            y_offset += 30
            
        # --- Display Typing input ---
        if typing_mode:
            typing_label = font.render("Typing Mode:", True, GREEN)
            typing_box = font.render(current_text, True, WHITE)
            screen.blit(typing_label, (10, SCREEN_HEIGHT - 50))
            screen.blit(typing_box, (150, SCREEN_HEIGHT - 50))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
