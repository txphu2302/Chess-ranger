# Chess Ranger

Chess Ranger là một biến thể của cờ vua truyền thống với các quy tắc đặc biệt.

## Luật chơi
1. Các quân cờ di chuyển như trong cờ vua chuẩn (xe, mã, tượng, hậu, vua, tốt).
2. Chỉ được thực hiện nước đi bắt quân (không có nước đi bình thường).
3. Có thể bắt cả vua (khác với cờ vua truyền thống).
4. Mục tiêu: Kết thúc trò chơi với chỉ một quân cờ duy nhất trên bàn cờ.

## Cấu trúc thư mục
```
chess-ranger/
│── main.py          # Chương trình chính
│── assets/          # Lưu trữ hình ảnh quân cờ
│── output/          # Kết quả dưới dạng txt
│── testcase/        # Trạng thái quân cờ ban đầu
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
Chạy chương trình bằng lệnh:
```bash
python main.py
```
- **Input:** Đặt quân cờ trong cửa sổ pygame và trạng thái quân cờ được lưu trong `testcase/`.
- **Output:** Kết quả sẽ được lưu trong thư mục `output/`.

## Đóng góp
Nếu bạn muốn đóng góp cho dự án, vui lòng tạo một pull request hoặc mở issue trên GitHub.

## Giấy phép
Dự án này được phát hành dưới giấy phép MIT.

