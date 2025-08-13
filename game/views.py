import json
import random
import cv2
import base64
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# --- VOM AI Model State ---
player_move_history = []
move_patterns = {}
MAX_ORDER = 5
STATISTICAL_SIGNIFICANCE_THRESHOLD = 1

# --- Constants ---
move_to_int = {'rock': 1, 'paper': 2, 'scissors': 3}
int_to_move = {1: 'rock', 2: 'paper', 3: 'scissors'}
beat_map = {1: 2, 2: 3, 3: 1}
detector = HandDetector(maxHands=1, detectionCon=0.8)

# --- HELPER FUNCTIONS ---
def _decode_image_from_base64(image_data_string):
    try:
        image_data = image_data_string.split(',')[1]
        decoded_image = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded_image, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except (IndexError, base64.binascii.Error):
        return None

# --- VOM AI Prediction and Learning Functions ---
def update_vom_patterns(history):
    global move_patterns
    if not history:
        return
    outcome = history[-1]
    outcome_index = outcome - 1
    for order in range(1, MAX_ORDER + 1):
        if len(history) > order:
            pattern = tuple(history[-(order + 1):-1])
            if pattern not in move_patterns:
                move_patterns[pattern] = np.zeros(3)
            move_patterns[pattern][outcome_index] += 1

def ai_predict_vom(history):
    for order in range(min(len(history), MAX_ORDER), 0, -1):
        pattern_to_check = tuple(history[-order:])
        if pattern_to_check in move_patterns and np.sum(move_patterns[pattern_to_check]) > STATISTICAL_SIGNIFICANCE_THRESHOLD:
            prediction_counts = move_patterns[pattern_to_check]
            predicted_player_move = np.argmax(prediction_counts) + 1
            return beat_map[predicted_player_move]
    return random.randint(1, 3)

def get_winner(player_move, ai_move):
    if player_move == ai_move: return 'tie'
    winning_combos = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    if winning_combos.get(player_move) == ai_move: return 'player'
    return 'ai'

# --- DJANGO VIEWS ---
def home_view(request):
    return render(request, 'game/home.html')

def start_game_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            return redirect('game_page', username=username)
    return redirect('home')

def index(request, username):
    global player_move_history, move_patterns
    player_move_history = []
    move_patterns = {}
    context = {'username': username}
    return render(request, 'game/index.html', context)

@csrf_exempt
def annotate_only_frame(request):
    """
    A lightweight view that only performs hand detection and annotation.
    It does NOT run any game logic. Built for speed to be called repeatedly.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    data = json.loads(request.body)
    img = _decode_image_from_base64(data.get('image', ''))

    if img is None:
        return JsonResponse({'error': 'Invalid image data'}, status=400)

    # Use draw=True to get the annotated image back from the detector.
    _, img_with_annotations = detector.findHands(img, draw=True)

    # Encode the annotated image back to Base64 to send to the frontend.
    _, buffer = cv2.imencode('.jpg', img_with_annotations)
    annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
    annotated_image_data_url = f"data:image/jpeg;base64,{annotated_image_base64}"

    # Return only the annotated image.
    return JsonResponse({'annotated_image': annotated_image_data_url})

@csrf_exempt
def analyze_frame(request):
    """
    Receives the final image, runs game logic, and returns the result.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    data = json.loads(request.body)
    img = _decode_image_from_base64(data.get('image', ''))

    if img is None:
        return JsonResponse({'error': 'Invalid image data'}, status=400)

    # Final detection and annotation for the result screen
    hands, img_with_annotations = detector.findHands(img, draw=True)
    
    player_move_str = None
    if hands:
        fingers = detector.fingersUp(hands[0])
        if fingers == [0, 0, 0, 0, 0]: player_move_str = "rock"
        elif fingers == [1, 1, 1, 1, 1]: player_move_str = "paper"
        elif fingers == [0, 1, 1, 0, 0]: player_move_str = "scissors"

    if not player_move_str:
        return JsonResponse({'error': 'No hand detected or invalid gesture.'})

    # Game Logic
    global player_move_history
    player_move_int = move_to_int[player_move_str]
    ai_move_int = ai_predict_vom(player_move_history)
    player_move_history.append(player_move_int)
    update_vom_patterns(player_move_history)
    ai_move_str = int_to_move[ai_move_int]
    winner = get_winner(player_move_str, ai_move_str)

    # Encode the final annotated image for the result display
    _, buffer = cv2.imencode('.jpg', img_with_annotations)
    annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
    annotated_image_data_url = f"data:image/jpeg;base64,{annotated_image_base64}"

    return JsonResponse({
        'player_move': player_move_str,
        'ai_move': ai_move_str,
        'winner': winner,
        'annotated_image': annotated_image_data_url,
    })