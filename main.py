#!/usr/bin/env python
# -*- coding: utf-8 -*-

import websocket
import math
try:
    import thread
except ImportError:
    import _thread as thread
import time


def show_board(a):
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j]["type"] in ["head","body"]:
                print(str(a[i][j]["snake_number"]), end="")
            elif a[i][j]["type"] == "head":
                print(a[i][j]["dir"], end="")
            else:
                print(a[i][j]["sym"].replace('☼', '#').replace('▲', '0').replace('◄', '0').replace('►', '0')\
                .replace('▼', '0')\
                .replace('║', 'o').replace('═', 'o').replace('╙', 'o').replace('╘', 'o') \
                .replace('╓', 'o').replace('╕', 'o') \
                .replace('╗', 'o').replace('╝', 'o').replace('╔', 'o').replace('╚', 'o')  \
                .replace('☻', 'X') \
                .replace('☺', '$')
                  ,end="")
        print()


wall_symbol = "☼"
apple_symbol = "☺"
stone_symbol = "☻"
body_symbols = ["║","═",'╙','╘','╓','╕','╗','╝','╔','╚']
tail_symbols = ['╙','╘','╓','╕']
head_symbols = ['▲','◄','►','▼']

def on_message(ws, message):
    print(len(message)-len("board="))
    board_input = message[6:]

    length = int(math.sqrt(len(message)-len("board=")))
    # ----------------- GET SNAKE LENGTH
    snake_length = 0
    for symbol in body_symbols + head_symbols:
        snake_length += board_input.count(symbol)
    print("Snake length:",snake_length)

    # ----------------- Create an array of cells (objects)
    a = []
    ii=0
    jj=0
    head_i = 0
    head_j = 0
    for i in range(length):
        a.append([])
        for j in range(length):
            sym = board_input[i*length+j]
            cell = {"type":"none", "number": 0, "sym": sym, "dir":"none", "snake_number": 0}
            if sym in head_symbols:
                cell["type"] = "head"
                cell["dir"] = ("U", "L", "R", "D")[head_symbols.index(sym)]
                ii = i
                jj = j
                head_i = i
                head_j = j
            if sym in body_symbols:
                cell["type"] = "body"
            if sym == wall_symbol:
                cell["type"] = "wall"
            if sym == stone_symbol:
                cell["type"] = "stone"
            if sym == apple_symbol:
                cell["type"] = "apple"
            if sym == " ":
                cell["type"] = "empty"
            a[-1].append(cell)

    # -------------------------------- DETECT SNAKE
    k= snake_length
    a[ii][jj]["snake_number"] = k
    came_from = ""
    while (a[ii][jj]["sym"] not in tail_symbols) and (k>=0):
        go = ""
        if a[ii][jj]["type"] == "head":
            if a[ii][jj]["dir"] == "U":
                go="D"
            if a[ii][jj]["dir"] == "D":
                go="U"
            if a[ii][jj]["dir"] == "L":
                go="R"
            if a[ii][jj]["dir"] == "R":
                go="L"
        elif a[ii][jj]["type"] == "body":
            if a[ii][jj]["sym"] == "║" and came_from == "U":
                go="D"
            elif a[ii][jj]["sym"] == "║" and came_from == "D":
                go="U"
            elif a[ii][jj]["sym"] == "═" and came_from == "L":
                go="R"
            elif a[ii][jj]["sym"] == "═" and came_from == "R":
                go="L"
            elif a[ii][jj]["sym"] == "╗" and came_from == "L":
                go="D"
            elif a[ii][jj]["sym"] == "╗" and came_from == "D":
                go="L"
            elif a[ii][jj]["sym"] == "╝" and came_from == "L":
                go="U"
            elif a[ii][jj]["sym"] == "╝" and came_from == "U":
                go="L"
            elif a[ii][jj]["sym"] == '╔' and came_from == "D":
                go = "R"
            elif a[ii][jj]["sym"] == '╔' and came_from == "R":
                go = "D"
            elif a[ii][jj]["sym"] == '╚' and came_from == "U":
                go = "R"
            elif a[ii][jj]["sym"] == '╚' and came_from == "R":
                go = "U"
        if go == "U":
            ii -= 1
            came_from = "D"
        elif go == "D":
            ii += 1
            came_from = "U"
        elif go == "R":
            jj += 1
            came_from = "L"
        elif go == "L":
            jj -= 1
            came_from = "R"

        k -= 1
        a[ii][jj]["snake_number"] = k
        if k < 0:
            print("SOMETHING'S WRONG WITH DETECTING SNAKE")


    m = []
    for i in range(length):
        m.append([])
        for j in range(length):
            m[-1].append(-1)
    m[head_i][head_j] = 1
    k = 1

    # -------------------------------------- DIJKSTRA

    changes = True
    while changes:
        changes = False
        for i in range(length):
            for j in range(length):
                if m[i][j] == k:
                    if i > 0 and m[i-1][j] == -1 and safe(i-1,j,a,k-1):
                        m[i-1][j] = k+1
                        changes = True
                    if j > 0 and m[i][j-1] == -1 and safe(i,j-1,a,k-1):
                        m[i][j-1] = k+1
                        changes = True
                    if i < len(m)-1 and m[i+1][j] == -1 and safe(i+1,j,a,k-1):
                        m[i+1][j] = k+1
                        changes = True
                    if j < len(m[i])-1 and m[i][j+1] == -1 and safe(i,j+1,a,k-1):
                        m[i][j+1] = k+1
                        changes = True
        k += 1
    for i in range(length):
        for j in range(length):
            print(str(m[i][j]).ljust(3), end="")
        print()

    # ----------------------------- FIND APPLE
    apple_i = 0
    apple_j = 0
    for i in range(length):
        for j in range(length):
            if a[i][j]["type"] == "apple":
                apple_i = i
                apple_j = j
                ii = i
                jj = j
    k = m[apple_i][apple_j]
    if k == -1: # no apple found :(
        maximum = 0
        for i in range(length):
            for j in range(length):
                if m[i][j] > maximum:
                    maximum = m[i][j]
                    apple_i = i
                    apple_j = j
                    ii = i
                    jj = j
    k = m[apple_i][apple_j]
    direction = "RIGHT" # By default
    while k != 1:
        if ii > 0 and m[ii - 1][jj] == k - 1:
            ii -= 1
            direction = "DOWN"
        elif jj > 0 and m[ii][jj - 1] == k - 1:
            jj -= 1
            direction = "RIGHT"
        elif ii < len(m)-1 and m[ii + 1][jj] == k - 1:
            ii += 1
            direction = "UP"
        elif jj < len(m[ii])-1 and m[ii][jj + 1] == k - 1:
            jj += 1
            direction = "LEFT"
        k -= 1

    show_board(a)
    ws.send(direction)


def safe(i,j,a,k):
    if a[i][j]["sym"] in body_symbols + head_symbols:
        if a[i][j]["snake_number"] >= k:
            return False
    if a[i][j]["sym"] in [stone_symbol, wall_symbol]:
        return False
    return True

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    pass


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://codenjoy.astanajug.net:8080/codenjoy-contest/ws?user=timurbakibayev@gmail.com&code=1526207402717100265",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()