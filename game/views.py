import json
import random
import cv2
import base64
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# --- AI LOGIC & STATE MANAGEMENT ---
# In a production app, this state would be stored in a database or cache.
transition_matrix = np.ones((3, 3)) / 3
prev_move = None
move_to_int = {'rock': 1, 'paper': 2, 'scissors': 3}
int_to_move = {1: 'rock', 2: 'paper', 3: 'scissors'}
beat_map = {1: 2, 2: 3, 3: 1}

# --- CV & AI HELPER FUNCTIONS ---
detector = HandDetector(maxHands=1, detectionCon=0.8)

def _get_move_from_image(img):
    """Analyzes an image and returns the detected hand gesture as a string."""
    hands, _ = detector.findHands(img, draw=False)
    if hands:
        fingers = detector.fingersUp(hands[0])
        if fingers == [0, 0, 0, 0, 0]: return "rock"
        if fingers == [1, 1, 1, 1, 1]: return "paper"
        if fingers == [0, 1, 1, 0, 0]: return "scissors"
    return None

def _decode_image_from_base64(image_data_string):
    """Decodes a Base64 image string into an OpenCV image array."""
    try:
        image_data = image_data_string.split(',')[1]
        decoded_image = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded_image, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except (IndexError, base64.binascii.Error):
        return None

def update_transition(previous_move_int, current_move_int):
    """Updates the Markov transition matrix."""
    global transition_matrix
    if previous_move_int is not None:
        transition_matrix[previous_move_int - 1, current_move_int - 1] += 1
    for i in range(3):
        row_sum = np.sum(transition_matrix[i])
        if row_sum > 0:
            transition_matrix[i] /= row_sum

def ai_predict():
    """Predicts the AI's next move based on the Markov model."""
    if prev_move is None or random.random() < 0.3:
        return random.randint(1, 3)
    predicted_player_move = np.argmax(transition_matrix[prev_move - 1]) + 1
    return beat_map[predicted_player_move]

def get_winner(player_move, ai_move):
    """Determines the winner of the round."""
    if player_move == ai_move:
        return 'tie'
    winning_combos = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    if winning_combos.get(player_move) == ai_move:
        return 'player'
    return 'ai'

# --- DJANGO VIEWS ---

def index(request):
    """Renders the main HTML page for the game."""
    return render(request, 'game/index.html')

@csrf_exempt
def analyze_frame(request):
    """Receives an image, detects the hand gesture, and plays a round."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    data = json.loads(request.body)
    img = _decode_image_from_base64(data.get('image', ''))

    if img is None:
        return JsonResponse({'error': 'Invalid image data'}, status=400)

    player_move_str = _get_move_from_image(img)

    if not player_move_str:
        return JsonResponse({'error': 'No hand detected or invalid gesture.'})

    # --- Play the game with the detected move ---
    global prev_move
    player_move_int = move_to_int[player_move_str]
    ai_move_int = ai_predict()
    update_transition(prev_move, player_move_int)
    prev_move = player_move_int
    ai_move_str = int_to_move[ai_move_int]
    winner = get_winner(player_move_str, ai_move_str)

    return JsonResponse({
        'player_move': player_move_str,
        'ai_move': ai_move_str,
        'winner': winner,
    })