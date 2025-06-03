import numpy as np

# from PIL import Image

# for testing. open 10x22 image of board where black == empty space, white == space occupied by piece.
# img = Image.open("grid.png").convert("L")
# ny = img.height
# nx = img.width
# grid = np.array(img, dtype="int")
# grid = grid // 255
# grid = np.flip(grid, axis=0) # flip vertically
# print(grid)

offsets = {'o': [[(0, 0)], [(0, -1)], [(-1, -1)], [(-1, 0)]],
           'i': [[(0, 0), (-1, 0), (2, 0), (-1, 0), (2, 0)],
                 [(-1, 0), (0, 0), (0, 0), (0, 1), (0, -2)],
                 [(-1, 1), (1, 1), (-2, 1), (1, 0), (-2, 0)],
                 [(0, 1), (0, 1), (0, 1), (0, -1), (0, 2)]],
           'a': [[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
                 [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                 [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
                 [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)]]}
piece_squares = {'o': [(0, 0), (1, 0), (0, 1), (1, 1)],
                 'i': [(-1, 0), (0, 0), (1, 0), (2, 0)],
                 'j': [(-1, 0), (0, 0), (1, 0), (-1, 1)],
                 'l': [(-1, 0), (0, 0), (1, 0), (1, 1)],
                 's': [(-1, 0), (0, 0), (0, 1), (1, 1)],
                 't': [(-1, 0), (0, 0), (1, 0), (0, 1)],
                 'z': [(0, 0), (1, 0), (-1, 1), (0, 1)]}
acts = {'l': (-1, 0, 0),    # move left
        'r': (1, 0, 0),     # move right
        'd': (0, -1, 0),    # move down or wait
        'c': (0, 0, 1),     # rotate clockwise
        'a': (0, 0, 3)}     # rotate anti-clockwise


def check_move(grid, piece, pos, a_kwd):
    if piece == 'o':
        o_i = 'o'
    elif piece == 'i':
        o_i = 'i'
    else:
        o_i = 'a'
    p_offsets = offsets[o_i]
    # print(p_offsets)
    squares = piece_squares[piece]
    action = acts[a_kwd]
    r = (pos[2] + action[2]) % 4
    # print(pos[2], "->", r)
    if r == 0:
        squares_r = squares
    elif r == 1:
        squares_r = [(j, -i) for (i, j) in squares]
    elif r == 2:
        squares_r = [(-i, -j) for (i, j) in squares]
    elif r == 3:
        squares_r = [(-j, i) for (i, j) in squares]
    if action[2] == 0:
        x = pos[0] + action[0]
        y = pos[1] + action[1]
        for (i, j) in squares_r:
            # print(x+i, y+j)
            if (x + i) < 0 or (x + i) >= 10 or (y + j) < 0:
                # print("out of bounds")
                return False
            if (y + j) >= 22:
                continue
            if grid[y + j, x + i] == 1:
                # print("overlap")
                return False
        return x, y, r
    else:
        for k in range(5):
            x = pos[0] + p_offsets[pos[2]][k][0] - p_offsets[r][k][0]
            y = pos[1] + p_offsets[pos[2]][k][1] - p_offsets[r][k][1]
            success = True
            # print(x, y)
            for (i, j) in squares_r:
                # print(x+i, y+j)
                if (x + i) < 0 or (x + i) >= 10 or (y + j) < 0:
                    # print("out of bounds")
                    success = False
                    break
                if (y + j) >= 22:
                    continue
                if grid[y + j, x + i] == 1:
                    # print("overlap")
                    success = False
                    break
            if success:
                return x, y, r
        return False


def find_all_paths(grid, piece):
    spawn_y = int(np.argmax(np.all(grid == 0, axis=1))) + 2
    spawn = (4, spawn_y, 0)
    searched = {spawn: ""}
    finals = {}
    queue = [spawn]
    while len(queue) > 0:
        pos = queue.pop(0)
        # print(pos, end=" ")
        for action in ['l', 'r', 'c', 'a']:
            res = check_move(grid, piece, pos, action)
            if res and res not in searched.keys():
                searched[res] = searched[pos] + action
                queue.append(res)
                # print(action, end="")
        res = check_move(grid, piece, pos, 'd')
        if not res:
            finals[pos] = "dddddddddddddddddddddd"[:22-spawn_y] + searched[pos]
        elif res not in searched.keys():
            searched[res] = searched[pos] + 'd'
            queue.append(res)
            # print('d', end="")
    #     print()
    # print()
    return finals
