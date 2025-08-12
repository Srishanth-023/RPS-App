import json
import random
import cv2
import base64
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# --- NEW: Upgraded AI Logic & State ---
# We now track a history of moves to enable a smarter model.
player_move_history = []
# This matrix maps a sequence of TWO moves to the next one (9 possible pairs -> 3 outcomes)
second_order_transition_matrix = np.ones((9, 3)) / 3

# --- Constants (No changes) ---
move_to_int = {'rock': 1, 'paper': 2, 'scissors': 3}
int_to_move = {1: 'rock', 2: 'paper', 3: 'scissors'}
beat_map = {1: 2, 2: 3, 3: 1}
detector = HandDetector(maxHands=1, detectionCon=0.8)

# --- HELPER FUNCTIONS (No changes here) ---
def _get_move_from_image(img):
    hands, _ = detector.findHands(img, draw=False)
    if hands:
        fingers = detector.fingersUp(hands[0])
        if fingers == [0, 0, 0, 0, 0]: return "rock"
        if fingers == [1, 1, 1, 1, 1]: return "paper"
        if fingers == [0, 1, 1, 0, 0]: return "scissors"
    return None

def _decode_image_from_base64(image_data_string):
    try:
        image_data = image_data_string.split(',')[1]
        decoded_image = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded_image, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except (IndexError, base64.binascii.Error):
        return None

# --- NEW: Upgraded AI Prediction and Learning Functions ---

def get_sequence_index(move1, move2):
    """Converts a pair of moves (e.g., rock, paper) into a single index (0-8)."""
    return (move1 - 1) * 3 + (move2 - 1)

def update_second_order_transition(history):
    """Updates the AI's memory based on the player's last three moves."""
    global second_order_transition_matrix
    if len(history) < 3:
        return # Need at least 3 moves to establish a pattern of two -> one

    # The sequence is the two moves BEFORE the most recent one
    sequence_index = get_sequence_index(history[-3], history[-2])
    # The outcome is the player's most recent move
    outcome_index = history[-1] - 1
    
    second_order_transition_matrix[sequence_index, outcome_index] += 1
    
    # Normalize to keep probabilities between 0 and 1
    row_sum = np.sum(second_order_transition_matrix[sequence_index])
    if row_sum > 0:
        second_order_transition_matrix[sequence_index] /= row_sum

def ai_predict_upgraded(history):
    """Predicts the AI's move using the upgraded model."""
    # If we don't have enough history, or sometimes just to be unpredictable, play randomly.
    if len(history) < 2 or random.random() < 0.33:
        return random.randint(1, 3)

    # Get the last two moves to predict the third
    last_two_moves_index = get_sequence_index(history[-2], history[-1])
    
    # Predict player's next move based on their history
    predicted_player_move = np.argmax(second_order_transition_matrix[last_two_moves_index]) + 1
    
    # Return the move that beats the prediction
    return beat_map[predicted_player_move]

def get_winner(player_move, ai_move):
    if player_move == ai_move: return 'tie'
    winning_combos = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    if winning_combos.get(player_move) == ai_move: return 'player'
    return 'ai'

# --- DJANGO VIEWS (No changes to Django logic) ---

def home_view(request):
    """Renders the username entry page."""
    return render(request, 'game/home.html')

def start_game_view(request):
    """Handles form submission and redirects to a URL with the username."""
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            return redirect('game_page', username=username)
    return redirect('home')

def index(request, username):
    """Renders the game page, getting the username from the URL."""
    # Reset AI state for each new game
    global player_move_history, second_order_transition_matrix
    player_move_history = []
    second_order_transition_matrix = np.ones((9, 3)) / 3
    
    context = {
        'username': username
    }
    return render(request, 'game/index.html', context)

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

    # --- Play the game using the UPGRADED AI ---
    global player_move_history
    player_move_int = move_to_int[player_move_str]
    
    # The AI predicts based on the history BEFORE the current move is added
    ai_move_int = ai_predict_upgraded(player_move_history)
    
    # Now add the current move to history and update the AI's brain
    player_move_history.append(player_move_int)
    update_second_order_transition(player_move_history)
    
    ai_move_str = int_to_move[ai_move_int]
    winner = get_winner(player_move_str, ai_move_str)

    return JsonResponse({
        'player_move': player_move_str,
        'ai_move': ai_move_str,
        'winner': winner,
    })
