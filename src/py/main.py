from src.py import game as hangman
import asyncio
import json
import random
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse


app = FastAPI()
app.mount("/inc/static", StaticFiles(directory="src/inc/static"), name="static")
templates = Jinja2Templates(directory="src/inc/templates")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/hangman/singleplayer/local/", response_class=HTMLResponse)
async def hangman_singleplayer(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("game/hangman/singleplayer_local.html", {"request": request})


@app.websocket("/hangman/singleplayer/ws")
async def hangman_singleplayer_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    idx_player_you = 0
    try:
        game = hangman.Hangman()
        words = []
        with open('src/inc/static/hangman_words.json', encoding='utf-8') as fin:
            words = json.load(fin)
        word_to_guess = random.choice(words)
        state = hangman.HangmanGameState(
            word_to_guess=word_to_guess, phase=hangman.GamePhase.RUNNING, guesses=[], incorrect_guesses=[])
        game.set_state(state)
        while True:
            state = game.get_player_view(idx_player_you)
            game.print_state()
            state = game.get_player_view(idx_player_you)
            list_action = game.get_list_action()
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = [action.model_dump() for action in list_action]
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)
            if state.phase == hangman.GamePhase.FINISHED:
                break
            if len(list_action) > 0:
                data = await websocket.receive_json()
                if data['type'] == 'action':
                    action = hangman.GuessLetterAction.model_validate(data['action'])
                    game.apply_action(action)
                    print(action)
    except WebSocketDisconnect:
        print('DISCONNECTED')
