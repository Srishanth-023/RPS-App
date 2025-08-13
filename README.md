# RPS-App


**RPS Ultra**🚀


**ABOUT THE PROJECT**

RPS Ultra is a modern, web-based Rock, Paper, Scissors game where you challenge a smart AI using your webcam. This project leverages real-time computer vision to detect your hand gestures, creating an interactive and engaging gameplay experience. The application is built with a Python and Django backend and is fully configured for deployment on the web.


**FEATURES**✨

Real-Time Gesture Recognition: Uses your webcam to instantly recognize rock, paper, and scissors gestures.

Adaptive AI Opponent: The AI doesn't just play randomly. It uses a second-order Markov model to learn your patterns based on your last two moves, making it a challenging opponent to beat.

Dynamic User Interface: A fully themed, animated interface from the welcome screen to the game arena, creating an immersive experience.

"First to 5" Gameplay: The first player to win 5 rounds is crowned the champion.

Live on the Web: The project is configured for easy deployment on Render, allowing anyone to play.


**TECH STACK**🛠️

Backend: Python, Django

Computer Vision: OpenCV, cvzone, MediaPipe

Frontend: HTML, CSS, JavaScript

Server: Daphne

Deployment: Render


**HOW TO PLAY** 🎮

Visit the live application URL.

Enter your name on the welcome screen to start.

Allow the browser to access your webcam.

On the game screen, wait for the countdown.

Make your move (rock, paper, or scissors) when the counter says "SHOOT!"

The first player to reach 5 points wins the match!