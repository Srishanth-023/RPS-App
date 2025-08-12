# game/consumers.py

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .views import _decode_image_from_base64, ai_predict, get_winner, update_transition, move_to_int, int_to_move, detector

game_states = {}
WINNING_SCORE = 5

def _get_move_from_image(img):
    """
    Analyzes an image to find a hand gesture.

    Returns:
        A tuple containing the move string, a list of landmark coordinates, 
        and the bounding box coordinates.
    """
    hands, _ = detector.findHands(img, draw=False)
    if hands:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        move = None
        if fingers == [0, 0, 0, 0, 0]:
            move = "rock"
        elif fingers == [1, 1, 1, 1, 1]:
            move = "paper"
        elif fingers == [0, 1, 1, 0, 0]:
            move = "scissors"
        
        return move, hand.get('lmList', []), hand.get('bbox', [])
        
    return None, [], []


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        game_states[self] = {
            "status": "idle",
            "last_frame": None,
            "scores": [0, 0],
            "prev_move": None,
            "game_loop_task": None
        }

    async def disconnect(self, close_code):
        state = game_states.get(self)
        if state and state.get("game_loop_task"):
            state["game_loop_task"].cancel()
        if self in game_states:
            del game_states[self]

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        state = game_states.get(self)
        if not state:
            return

        if message_type == 'start_game':
            if state["status"] != "playing":
                state["status"] = "playing"
                state["scores"] = [0, 0]
                state["prev_move"] = None
                state["game_loop_task"] = asyncio.create_task(self.game_loop())

        elif message_type == 'frame':
            state["last_frame"] = data.get('image')

    async def game_loop(self):
        state = game_states.get(self)
        if not state:
            return

        while max(state["scores"]) < WINNING_SCORE:
            try:
                # Countdown
                for i in range(3, -1, -1):
                    await self.send(text_data=json.dumps({'type': 'countdown', 'value': i}))
                    await asyncio.sleep(1)

                game_update = {'type': 'game_update', 'error': 'No hand detected'}

                if state.get("last_frame"):
                    img = _decode_image_from_base64(state["last_frame"])
                    if img is not None:
                        player_move, landmarks, bbox = _get_move_from_image(img)

                        # Always include landmark data in the update
                        game_update['landmarks'] = landmarks
                        game_update['bbox'] = bbox

                        if player_move:
                            player_move_int = move_to_int[player_move]
                            ai_move_int = ai_predict()
                            update_transition(state["prev_move"], player_move_int)
                            state["prev_move"] = player_move_int
                            ai_move = int_to_move[ai_move_int]
                            winner = get_winner(player_move, ai_move)

                            if winner == 'player':
                                state["scores"][1] += 1
                            elif winner == 'ai':
                                state["scores"][0] += 1
                            
                            game_update.update({
                                'error': None,
                                'player_move': player_move,
                                'ai_move': ai_move,
                                'scores': state["scores"]
                            })
                
                await self.send(text_data=json.dumps(game_update))

            except Exception as e:
                print(f"Error in game loop: {e}")
                await self.send(text_data=json.dumps({'type': 'game_update', 'error': 'A processing error occurred.'}))
                await asyncio.sleep(3)
        
        # Game Over
        state["status"] = "game_over"
        final_winner = "Player" if state["scores"][1] > state["scores"][0] else "AI"
        await self.send(text_data=json.dumps({'type': 'game_over', 'winner': final_winner}))