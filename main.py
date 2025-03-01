import sys
import pygame
import time
import os
import copy
import tracemalloc
import heapq
from itertools import count


# ----------------- XỬ LÝ ĐỐI SỐ DÒNG LỆNH -----------------
if len(sys.argv) < 2:
    print("Usage: python main.py [dfs|heuristic]")
    sys.exit(1)

mode = sys.argv[1]
if mode not in ("dfs", "heuristic"):
    print("Invalid mode. Use 'dfs' or 'heuristic'.")
    sys.exit(1)

# Đặt thư mục lưu file dựa theo mode
if mode == "dfs":
    TESTCASE_DIR = os.path.join("dfs", "testcase")
    OUTPUT_DIR = os.path.join("dfs", "output")
    PERFORMANCE_DIR = os.path.join("dfs", "performance")
    title_mode = "DFS Thuần"
else:  # heuristic -> sử dụng A* Search
    TESTCASE_DIR = os.path.join("heuristic", "testcase")
    OUTPUT_DIR = os.path.join("heuristic", "output")
    PERFORMANCE_DIR = os.path.join("heuristic", "performance")
    title_mode = "A* Search"

# Tạo các thư mục nếu chưa tồn tại
os.makedirs(TESTCASE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PERFORMANCE_DIR, exist_ok=True)

# ----------------- CÁC HẰNG SỐ TOÀN CỤC -----------------
BOARD_SIZE = 8          # Số ô theo chiều ngang và dọc
CELL_SIZE = 80          # Kích thước mỗi ô bàn cờ (pixel)
SIDEBAR_WIDTH = 120     # Chiều rộng sidebar chứa danh sách quân cờ
MARGIN_LEFT = SIDEBAR_WIDTH  # Bàn cờ bắt đầu sau sidebar

FILE_LABEL_HEIGHT = 40  # Chiều cao vùng hiển thị file (a-h) bên dưới bàn cờ
RANK_LABEL_WIDTH = 40   # Chiều rộng vùng hiển thị rank (1-8) bên phải bàn cờ

# ----------------- HÀM XỬ LÝ TRẠNG THÁI BÀN CỜ -----------------
def state_to_key(state):
    """Chuyển trạng thái bàn cờ thành key hashable để lưu visited."""
    return frozenset((r, c, piece) for (r, c), piece in state.items())

def board_state_to_string(state, board_size):
    s = ""
    s += "    " + " ".join(chr(ord('a') + col) for col in range(board_size)) + "\n"
    for r in range(board_size):
        rank = board_size - r
        s += f" {rank}  "
        for c in range(board_size):
            s += state.get((r, c), ".") + " "
        s += "\n"
    return s

def convert_coord(pos, board_size):
    row, col = pos
    file_letter = chr(ord('a') + col)
    rank = board_size - row
    return f"{file_letter}{rank}"

# ----------------- HÀM DI CHUYỂN VÀ TÌM KIẾM -----------------
def get_king_moves(state, pos, board_size):
    moves = []
    r, c = pos
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            if (nr, nc) in state:
                moves.append((pos, (nr, nc)))
    return moves

def get_knight_moves(state, pos, board_size):
    moves = []
    r, c = pos
    knight_deltas = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                     (1, 2), (1, -2), (-1, 2), (-1, -2)]
    for dr, dc in knight_deltas:
        nr, nc = r + dr, c + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            if (nr, nc) in state:
                moves.append((pos, (nr, nc)))
    return moves

def get_rook_moves(state, pos, board_size):
    moves = []
    r, c = pos
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while 0 <= nr < board_size and 0 <= nc < board_size:
            if (nr, nc) in state:
                moves.append((pos, (nr, nc)))
                break
            nr += dr
            nc += dc
    return moves

def get_bishop_moves(state, pos, board_size):
    moves = []
    r, c = pos
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while 0 <= nr < board_size and 0 <= nc < board_size:
            if (nr, nc) in state:
                moves.append((pos, (nr, nc)))
                break
            nr += dr
            nc += dc
    return moves

def get_queen_moves(state, pos, board_size):
    return get_rook_moves(state, pos, board_size) + get_bishop_moves(state, pos, board_size)

def get_pawn_moves(state, pos, board_size):
    moves = []
    r, c = pos
    directions = [(-1, -1), (-1, 1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            if (nr, nc) in state:
                moves.append((pos, (nr, nc)))
    return moves

def get_moves_for_piece(state, pos, board_size):
    piece = state[pos]
    if piece == 'K':
        return get_king_moves(state, pos, board_size)
    elif piece == 'N':
        return get_knight_moves(state, pos, board_size)
    elif piece == 'R':
        return get_rook_moves(state, pos, board_size)
    elif piece == 'B':
        return get_bishop_moves(state, pos, board_size)
    elif piece == 'Q':
        return get_queen_moves(state, pos, board_size)
    elif piece == 'P':
        return get_pawn_moves(state, pos, board_size)
    return []

def get_all_moves(state, board_size):
    moves = []
    for pos in state:
        moves.extend(get_moves_for_piece(state, pos, board_size))
    return moves

def apply_move(state, move):
    new_state = state.copy()
    start, end = move
    piece = new_state[start]
    del new_state[start]
    if end in new_state:
        del new_state[end]
    new_state[end] = piece
    return new_state

# ----------------- HÀM DFS -----------------
def dfs_plain(state, board_size, path, visited):
    """DFS thuần không sắp xếp theo heuristic."""
    if len(state) == 1:
        return path
    key = state_to_key(state)
    if key in visited:
        return None
    visited.add(key)
    moves = get_all_moves(state, board_size)
    for move in moves:
        new_state = apply_move(state, move)
        result = dfs_plain(new_state, board_size, path + [move], visited)
        if result is not None:
            return result
    return None

# ----------------- HÀM HEURISTIC -----------------
def heuristic(state):
    """
    Ước lượng số nước đi cần thực hiện để đạt trạng thái chỉ còn 1 quân:
    bằng số quân cờ hiện tại trừ 1.
    """
    return len(state) - 1

# ----------------- HÀM TÌM KIẾM A* -----------------
def a_star_search(initial_state, board_size):
    """
    Tìm lời giải sử dụng thuật toán A*.
    Mỗi nước đi có chi phí 1, sử dụng hàm heuristic là số quân cờ hiện tại trừ 1.
    """
    open_list = []
    closed = {}
    counter = count()  # Bộ đếm để đảm bảo các phần tử có thứ tự duy nhất
    
    initial_g = 0
    initial_h = heuristic(initial_state)
    initial_f = initial_g + initial_h
    heapq.heappush(open_list, (initial_f, initial_g, next(counter), initial_state, []))
    
    while open_list:
        f, g, _, state, path = heapq.heappop(open_list)
        if len(state) == 1:
            return path
        key = state_to_key(state)
        if key in closed and closed[key] <= g:
            continue
        closed[key] = g
        moves = get_all_moves(state, board_size)
        for move in moves:
            new_state = apply_move(state, move)
            new_g = g + 1
            new_h = heuristic(new_state)
            new_f = new_g + new_h
            new_path = path + [move]
            new_key = state_to_key(new_state)
            if new_key not in closed or new_g < closed[new_key]:
                heapq.heappush(open_list, (new_f, new_g, next(counter), new_state, new_path))
    
    return None  # Không tìm được lời giải

def solve_chess_ranger(initial_state, board_size, algorithm):
    visited = set()
    return algorithm(initial_state, board_size, [], visited) if algorithm == dfs_plain else algorithm(initial_state, board_size)

# ----------------- HÀM GHI FILE -----------------
def write_testcase_file(initial_state, board_size):
    os.makedirs(TESTCASE_DIR, exist_ok=True)
    file_index = 1
    while True:
        filename = os.path.join(TESTCASE_DIR, f"{mode}-testcase-{file_index}.txt")
        if not os.path.exists(filename):
            break
        file_index += 1
    with open(filename, "w", encoding="utf-8") as f:
        for pos, piece in sorted(initial_state.items(), key=lambda x: (x[0][0], x[0][1])):
            f.write(f"{piece}{convert_coord(pos, board_size)}\n")
    print(f"Đã ghi file testcase: {filename}")

def write_output_file(initial_state, solution, board_size):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_index = 1
    while True:
        filename = os.path.join(OUTPUT_DIR, f"{mode}-output-{file_index}.txt")
        if not os.path.exists(filename):
            break
        file_index += 1
    with open(filename, "w", encoding="utf-8") as f:
        if solution:
            header = ("Chuỗi nước đi tìm được (A* Search):" if mode == "heuristic"
                      else "Chuỗi nước đi tìm được (DFS Thuần):")
            f.write(header + "\n")
            state = copy.deepcopy(initial_state)
            move_lines = []
            step_lines = []
            step_lines.append("Quá trình giải từng bước:")
            step_lines.append("Bàn cờ ban đầu:")
            step_lines.append(board_state_to_string(state, board_size))
            for i, move in enumerate(solution, start=1):
                start, end = move
                piece = state[start]
                move_lines.append(f"{i}. Từ {piece}{convert_coord(start, board_size)} đến {convert_coord(end, board_size)}")
                state = apply_move(state, move)
                step_lines.append(f"\nSau nước đi {i} từ {convert_coord(start, board_size)} đến {convert_coord(end, board_size)}:")
                step_lines.append(board_state_to_string(state, board_size))
            f.write("\n".join(move_lines))
            f.write("\n\n")
            f.write("\n".join(step_lines))
        else:
            f.write("Không tìm được lời giải.\n")
    print(f"Đã ghi file output: {filename}")

def write_performance_file(time_taken, memory_used):
    os.makedirs(PERFORMANCE_DIR, exist_ok=True)
    file_index = 1
    while True:
        filename = os.path.join(PERFORMANCE_DIR, f"performance-{mode}-{file_index}.txt")
        if not os.path.exists(filename):
            break
        file_index += 1
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Thời gian chạy: {time_taken:.4f} s\n")
        f.write(f"Bộ nhớ tiêu thụ: {memory_used:.2f} MB\n")
    
# ----------------- HÀM ĐO PERFORMANCE & TRẢ VỀ KẾT QUẢ -----------------
def solve_and_measure(initial_state, board_size, algorithm):
    tracemalloc.start()
    start_time = time.perf_counter()
    
    solution = solve_chess_ranger(initial_state, board_size, algorithm)
    
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    time_taken = end_time - start_time
    memory_used = peak / (1024 * 1024)  # MB
    
    write_performance_file(time_taken, memory_used)
    
    return solution, time_taken, memory_used


# ----------------- HÀM XỬ LÝ PYGAME -----------------
def load_piece_images():
    pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
    images = {}
    for piece in pieces:
        filename = os.path.join("assets", f"w{piece}.png")
        try:
            image = pygame.image.load(filename)
            images[f"w{piece}"] = pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))
        except pygame.error as e:
            print(f"Lỗi tải {filename}: {e}")
    return images

def draw_board(screen, board_size, state, cell_size, images):
    colors = [(231, 205, 187), (141, 103, 94)]
    for r in range(board_size):
        for c in range(board_size):
            color = colors[(r + c) % 2]
            rect = pygame.Rect(MARGIN_LEFT + c * cell_size, r * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)
    for (r, c), piece in state.items():
        key = f"w{piece.upper()}"
        if key in images:
            pos = (MARGIN_LEFT + c * cell_size, r * cell_size)
            screen.blit(images[key], pos)

def draw_sidebar(screen, available_pieces, images, selected_piece):
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, screen.get_height())
    pygame.draw.rect(screen, (220, 220, 220), sidebar_rect)
    for idx, piece in enumerate(available_pieces):
        pos = (20, 20 + idx * (CELL_SIZE + 10))
        key = f"w{piece}"
        if key in images:
            screen.blit(images[key], pos)
        if selected_piece == piece:
            highlight_rect = pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (255, 0, 0), highlight_rect, 3)

def draw_solve_button(screen, solve_button_rect):
    pygame.draw.rect(screen, (0, 200, 0), solve_button_rect)
    font = pygame.font.Font(None, 24)
    text = font.render("Solve", True, (255, 255, 255))
    text_rect = text.get_rect(center=solve_button_rect.center)
    screen.blit(text, text_rect)

def draw_clear_button(screen, clear_button_rect):
    pygame.draw.rect(screen, (200, 0, 0), clear_button_rect)
    font = pygame.font.Font(None, 24)
    text = font.render("Clear", True, (255, 255, 255))
    text_rect = text.get_rect(center=clear_button_rect.center)
    screen.blit(text, text_rect)

def draw_coordinates(screen, board_size, cell_size):
    font = pygame.font.Font(None, 24)
    for c in range(board_size):
        letter = chr(ord('a') + c)
        x = MARGIN_LEFT + c * cell_size + cell_size / 2
        y = board_size * cell_size + FILE_LABEL_HEIGHT / 2
        text = font.render(letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
    for r in range(board_size):
        rank_number = r + 1
        x = MARGIN_LEFT + board_size * cell_size + RANK_LABEL_WIDTH / 2
        y = (board_size - 1 - r) * cell_size + cell_size / 2
        text = font.render(str(rank_number), True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

def animate_moves(screen, board_size, initial_state, solution, cell_size, images, solve_button_rect, clear_button_rect):
    state = copy.deepcopy(initial_state)
    print("Bàn cờ ban đầu:")
    print(board_state_to_string(state, board_size))
    for move in solution:
        start, end = move
        piece = state.pop(start)
        if end in state:
            del state[end]
        state[end] = piece
        draw_board(screen, board_size, state, cell_size, images)
        draw_sidebar(screen, available_pieces, images, selected_piece)
        draw_solve_button(screen, solve_button_rect)
        draw_clear_button(screen, clear_button_rect)
        draw_coordinates(screen, board_size, cell_size)
        pygame.display.flip()
        print(f"\nSau nước đi từ {convert_coord(start, board_size)} đến {convert_coord(end, board_size)}:")
        print(board_state_to_string(state, board_size))
        time.sleep(1)

# ----------------- BIẾN TOÀN CỤC -----------------
available_pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
selected_piece = None

# ----------------- HÀM MAIN -----------------
def main():
    global available_pieces, selected_piece
    pygame.init()
    screen_width = MARGIN_LEFT + BOARD_SIZE * CELL_SIZE + RANK_LABEL_WIDTH
    screen_height = BOARD_SIZE * CELL_SIZE + FILE_LABEL_HEIGHT
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"Chess Ranger - {title_mode}")
    images = load_piece_images()
    
    initial_state = {}  # Bàn cờ ban đầu rỗng
    solve_button_rect = pygame.Rect(10, len(available_pieces) * (CELL_SIZE + 10) + 30, 100, 40)
    clear_button_rect = pygame.Rect(10, solve_button_rect.bottom + 10, 100, 40)
    
    running = True
    clock = pygame.time.Clock()
    solution = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for idx, piece in enumerate(available_pieces):
                    icon_rect = pygame.Rect(20, 20 + idx * (CELL_SIZE + 10), CELL_SIZE, CELL_SIZE)
                    if icon_rect.collidepoint(mouse_pos):
                        selected_piece = piece
                        break

                if solve_button_rect.collidepoint(mouse_pos):
                    print("Đang tìm lời giải...")
                    write_testcase_file(initial_state, BOARD_SIZE)
                    # Đo hiệu năng của lần chạy hiện tại và ghi vào file performance
                    if mode == "heuristic":
                        # Sử dụng A* Search
                        solution, t, mem = solve_and_measure(initial_state, BOARD_SIZE, a_star_search)
                    else:
                        solution, t, mem = solve_and_measure(initial_state, BOARD_SIZE, dfs_plain)

                    print(f"Time: {t:.4f} s, Memory: {mem:.2f} MB")
                    
                    if solution:
                        print("Tìm được lời giải!")
                        write_output_file(initial_state, solution, BOARD_SIZE)
                        animate_moves(screen, BOARD_SIZE, initial_state, solution, CELL_SIZE, images, solve_button_rect, clear_button_rect)
                    else:
                        write_output_file(initial_state, solution, BOARD_SIZE)
                        print("Không tìm được lời giải!")
                        
                if clear_button_rect.collidepoint(mouse_pos):
                    print("Clear board!")
                    initial_state.clear()
                    
                board_rect = pygame.Rect(MARGIN_LEFT, 0, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)
                if board_rect.collidepoint(mouse_pos):
                    col = (mouse_pos[0] - MARGIN_LEFT) // CELL_SIZE
                    row = mouse_pos[1] // CELL_SIZE
                    if event.button == 1 and selected_piece is not None:
                        initial_state[(row, col)] = selected_piece
                    elif event.button == 3:
                        if (row, col) in initial_state:
                            del initial_state[(row, col)]
            
        screen.fill((200, 200, 200))
        draw_sidebar(screen, available_pieces, images, selected_piece)
        draw_board(screen, BOARD_SIZE, initial_state, CELL_SIZE, images)
        draw_solve_button(screen, solve_button_rect)
        draw_clear_button(screen, clear_button_rect)
        draw_coordinates(screen, BOARD_SIZE, CELL_SIZE)
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    main()
