import pygame
import time
import os
import copy

# ----------------- CÁC HẰNG SỐ TOÀN CỤC -----------------
BOARD_SIZE = 8          # Số ô theo chiều ngang và dọc
CELL_SIZE = 80          # Kích thước mỗi ô bàn cờ (pixel)
SIDEBAR_WIDTH = 120     # Chiều rộng sidebar chứa danh sách quân cờ
MARGIN_LEFT = SIDEBAR_WIDTH  # Bàn cờ bắt đầu sau sidebar

FILE_LABEL_HEIGHT = 40  # Chiều cao vùng hiển thị file (a-h) bên dưới bàn cờ
RANK_LABEL_WIDTH = 40   # Chiều rộng vùng hiển thị rank (1-8) bên phải bàn cờ

# ----------------- HÀM XỬ LÝ TRẠNG THÁI BÀN CỜ -----------------
def state_to_key(state):
    """Chuyển đổi trạng thái bàn cờ thành key hashable (frozenset) để lưu visited."""
    return frozenset((r, c, piece) for (r, c), piece in state.items())

def board_state_to_string(state, board_size):
    """
    Trả về chuỗi thể hiện trạng thái bàn cờ dạng text, có nhãn tọa độ.
    Ví dụ:
         a b c d e f g h
      8  . K . . . . . .
      7  . . . R . . . .
      6  . . . . . . . .
      5  . . N . . . . .
      4  . . . . . . . .
      3  . . . . . . . .
      2  . . . . . . . .
      1  . . . . . . . .
    """
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
    """Chuyển tọa độ (row, col) sang ký hiệu bàn cờ, ví dụ: (5,2) -> "c3"."""
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

def dfs(state, board_size, path, visited):
    if len(state) == 1:
        return path
    key = state_to_key(state)
    if key in visited:
        return None
    visited.add(key)
    moves = get_all_moves(state, board_size)
    for move in moves:
        new_state = apply_move(state, move)
        result = dfs(new_state, board_size, path + [move], visited)
        if result is not None:
            return result
    return None

def solve_chess_ranger(initial_state, board_size):
    visited = set()
    return dfs(initial_state, board_size, [], visited)

# ----------------- HÀM GHI FILE -----------------
def write_testcase_file(initial_state, board_size):
    """
    Ghi trạng thái bàn cờ ban đầu vào file trong thư mục 'testcase'
    với mỗi dòng có định dạng: <Piece><Coordinate> (ví dụ: "Kb8").
    Chỉ ghi thông tin ban đầu (initial state).
    Nếu file đã tồn tại, tự động tăng số thứ tự.
    """
    os.makedirs("testcase", exist_ok=True)
    file_index = 1
    while True:
        filename = os.path.join("testcase", f"dfs-testcase-{file_index}.txt")
        if not os.path.exists(filename):
            break
        file_index += 1

    with open(filename, "w", encoding="utf-8") as f:
        for pos, piece in sorted(initial_state.items(), key=lambda x: (x[0][0], x[0][1])):
            f.write(f"{piece}{convert_coord(pos, board_size)}\n")
    print(f"Đã ghi file testcase: {filename}")

def write_output_file(initial_state, solution, board_size):
    """
    Ghi kết quả lời giải (chuỗi nước đi và quá trình giải từng bước) vào file
    trong thư mục 'output'.
    Nếu file đã tồn tại, tự động tăng số thứ tự.
    """
    os.makedirs("output", exist_ok=True)
    file_index = 1
    while True:
        filename = os.path.join("output", f"dfs-output-{file_index}.txt")
        if not os.path.exists(filename):
            break
        file_index += 1

    with open(filename, "w", encoding="utf-8") as f:
        if solution:
            f.write("Chuỗi nước đi tìm được:\n")
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

# ----------------- HÀM XỬ LÝ PYGAME -----------------
def load_piece_images():
    """
    Tải ảnh quân cờ từ thư mục 'assets' với tên file dạng "wK.png", "wQ.png",...
    Chuyển kích thước ảnh về (80,80).
    """
    pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
    images = {}
    for piece in pieces:
        filename = os.path.join("assets", f"w{piece}.png")
        try:
            image = pygame.image.load(filename)
            images[f"w{piece}"] = pygame.transform.scale(image, (80, 80))
        except pygame.error as e:
            print(f"Lỗi tải {filename}: {e}")
    return images

def draw_board(screen, board_size, state, cell_size, images):
    """
    Vẽ bàn cờ (bắt đầu từ tọa độ (MARGIN_LEFT, 0)) và các quân cờ đã đặt.
    """
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
    """Vẽ sidebar chứa danh sách quân cờ để người dùng lựa chọn."""
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, screen.get_height())
    pygame.draw.rect(screen, (220, 220, 220), sidebar_rect)
    for idx, piece in enumerate(available_pieces):
        pos = (20, 20 + idx * (80 + 10))
        key = f"w{piece}"
        if key in images:
            screen.blit(images[key], pos)
        if selected_piece == piece:
            highlight_rect = pygame.Rect(pos[0], pos[1], 80, 80)
            pygame.draw.rect(screen, (255, 0, 0), highlight_rect, 3)

def draw_solve_button(screen, solve_button_rect):
    """Vẽ nút 'Solve' tại vị trí xác định."""
    pygame.draw.rect(screen, (0, 200, 0), solve_button_rect)
    font = pygame.font.Font(None, 24)
    text = font.render("Solve", True, (255, 255, 255))
    text_rect = text.get_rect(center=solve_button_rect.center)
    screen.blit(text, text_rect)

def draw_clear_button(screen, clear_button_rect):
    """Vẽ nút 'Clear' tại vị trí xác định."""
    pygame.draw.rect(screen, (200, 0, 0), clear_button_rect)
    font = pygame.font.Font(None, 24)
    text = font.render("Clear", True, (255, 255, 255))
    text_rect = text.get_rect(center=clear_button_rect.center)
    screen.blit(text, text_rect)

def draw_coordinates(screen, board_size, cell_size):
    """Vẽ tọa độ: file (a-h) bên dưới và rank (1-8) bên phải."""
    font = pygame.font.Font(None, 24)
    # Vẽ file (a-h) bên dưới bàn cờ
    for c in range(board_size):
        letter = chr(ord('a') + c)
        x = MARGIN_LEFT + c * cell_size + cell_size / 2
        y = board_size * cell_size + FILE_LABEL_HEIGHT / 2
        text = font.render(letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)
    # Vẽ rank (1-8) bên phải, từ dưới lên
    for r in range(board_size):
        rank_number = r + 1  # rank 1 ở dưới, rank 8 ở trên
        x = MARGIN_LEFT + board_size * cell_size + RANK_LABEL_WIDTH / 2
        # Tính tọa độ y: hàng dưới cùng (board index 7) hiển thị rank 1, hàng trên cùng (board index 0) hiển thị rank 8
        y = (board_size - 1 - r) * cell_size + cell_size / 2
        text = font.render(str(rank_number), True, (0, 0, 0))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

def animate_moves(screen, board_size, initial_state, solution, cell_size, images, solve_button_rect, clear_button_rect):
    """Hiển thị hoạt cảnh các nước đi được tìm ra."""
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

# Các biến toàn cục cho danh sách quân cờ và quân được chọn
available_pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
selected_piece = None

# ----------------- HÀM MAIN -----------------
def main():
    global available_pieces, selected_piece
    pygame.init()
    # Cập nhật kích thước cửa sổ bao gồm cả sidebar, tọa độ bên dưới và bên phải
    screen_width = MARGIN_LEFT + BOARD_SIZE * CELL_SIZE + RANK_LABEL_WIDTH
    screen_height = BOARD_SIZE * CELL_SIZE + FILE_LABEL_HEIGHT
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Chess Ranger - Tạo câu đố của bạn")
    images = load_piece_images()
    
    initial_state = {}  # Bàn cờ ban đầu rỗng
    
    # Định nghĩa nút "Solve" và "Clear" (đặt trong sidebar)
    solve_button_rect = pygame.Rect(10, len(available_pieces) * (80 + 10) + 30, 100, 40)
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
                    icon_rect = pygame.Rect(20, 20 + idx * (80 + 10), 80, 80)
                    if icon_rect.collidepoint(mouse_pos):
                        selected_piece = piece
                        break

                if solve_button_rect.collidepoint(mouse_pos):
                    print("Đang tìm lời giải...")
                    write_testcase_file(initial_state, BOARD_SIZE)
                    solution = solve_chess_ranger(initial_state, BOARD_SIZE)
                    if solution:
                        print("Tìm được lời giải!")
                        write_output_file(initial_state, solution, BOARD_SIZE)
                        animate_moves(screen, BOARD_SIZE, initial_state, solution, CELL_SIZE, images, solve_button_rect, clear_button_rect)
                    else:
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
