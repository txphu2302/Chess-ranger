# Chess Ranger

Chess Ranger là một biến thể của cờ vua truyền thống với các quy tắc đặc biệt, cùng công cụ giải tự động sử dụng các thuật toán tìm kiếm.

## Luật chơi

1. Các quân cờ di chuyển như trong cờ vua chuẩn (xe, mã, tượng, hậu, vua, tốt).
2. Chỉ được thực hiện nước đi bắt quân (không có nước đi bình thường).
3. Có thể bắt cả vua (khác với cờ vua truyền thống).
4. Mục tiêu: Kết thúc trò chơi với chỉ một quân cờ duy nhất trên bàn cờ.

## Thuật toán giải

Chương trình hỗ trợ hai phương pháp giải:

1. **DFS Thuần**: Sử dụng thuật toán Depth-First Search cơ bản để tìm kiếm lời giải.
2. **A*** **Search**: Sử dụng thuật toán A* với hàm heuristic đơn giản (số quân cờ hiện tại trừ 1) để tìm lời giải tối ưu hơn.

## Cấu trúc thư mục

```
chess-ranger/
│── main.py          # Chương trình chính
│── assets/          # Lưu trữ hình ảnh quân cờ
│── dfs/             # Kết quả khi sử dụng thuật toán DFS
│   │── testcase/    # Trạng thái quân cờ ban đầu
│   │── output/      # Kết quả dưới dạng txt
│   │── performance/ # Thông tin về hiệu năng thuật toán
│
│── heuristic/       # Kết quả khi sử dụng thuật toán A*
│   │── testcase/    # Trạng thái quân cờ ban đầu
│   │── output/      # Kết quả dưới dạng txt
│   │── performance/ # Thông tin về hiệu năng thuật toán
│
│── README.md        # Tài liệu này
│── requirement.txt  # Thư viện cần cài đặt
```

## Cài đặt

Clone repository về máy:
```bash
git clone https://github.com/txphu2302/Chess-ranger
```

Dẫn vào thư mục Chess-ranger:
```bash
cd Chess-ranger
```

Trước khi chạy chương trình, hãy cài đặt các thư viện cần thiết bằng cách chạy lệnh sau:
```bash
pip install -r requirement.txt
```

## Cách sử dụng

Chạy chương trình với một trong hai chế độ:

```bash
# Chế độ DFS thuần
python main.py dfs

# Chế độ A* Search
python main.py heuristic
```

### Giao diện đồ họa

1. **Đặt quân cờ**: 
   - Chọn quân cờ từ thanh bên trái
   - Click chuột trái vào ô trên bàn cờ để đặt quân
   - Click chuột phải để xóa quân

2. **Giải bài toán**:
   - Nhấn "Solve" để tìm lời giải
   - Nhấn "Clear" để xóa tất cả quân cờ trên bàn

3. **Kết quả**:
   - Chương trình sẽ hiển thị và lưu lại các nước đi từng bước
   - Thông tin về hiệu năng thuật toán (thời gian chạy, bộ nhớ tiêu thụ) được ghi lại

### File đầu ra

Khi giải một bài toán, chương trình sẽ tạo ra ba loại file:

1. **Testcase**: Lưu trạng thái ban đầu của bàn cờ
2. **Output**: Lưu chuỗi nước đi và diễn biến từng bước
3. **Performance**: Lưu thông tin về thời gian chạy và bộ nhớ tiêu thụ

## Đặc điểm kỹ thuật

- **Board**: Bàn cờ 8x8 tiêu chuẩn
- **Coordinate**: Sử dụng hệ tọa độ cờ vua chuẩn (a1-h8)
- **Pieces**: Tất cả các quân cờ vua chuẩn (K, Q, R, B, N, P)
- **Đo hiệu năng**: Thời gian thực thi và bộ nhớ tiêu thụ được ghi lại để so sánh các thuật toán

## Đóng góp

Nếu bạn muốn đóng góp cho dự án, vui lòng tạo một pull request hoặc mở issue trên GitHub.

## Giấy phép

Dự án này được phát hành dưới giấy phép MIT.
