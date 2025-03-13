# TikTok Research Tool

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-orange)

Công cụ nghiên cứu TikTok là một ứng dụng web giúp thu thập và phân tích dữ liệu từ nền tảng TikTok. Ứng dụng cho phép người dùng thu thập dữ liệu dựa trên tên người dùng hoặc hashtag, lưu trữ kết quả và xuất dữ liệu dưới nhiều định dạng khác nhau.

## 📋 Mục lục

- [Tính năng](#tính-năng)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Tài liệu yêu cầu sản phẩm (PRD)](#tài-liệu-yêu-cầu-sản-phẩm-prd)
- [Hướng phát triển](#hướng-phát-triển)
- [Đóng góp](#đóng-góp)
- [Giấy phép](#giấy-phép)

## ✨ Tính năng

- Thu thập dữ liệu video từ TikTok dựa trên tên người dùng hoặc hashtag
- Tùy chỉnh các tham số thu thập: thời gian chạy, số lượng video tối đa, tốc độ cuộn
- Lưu trữ kết quả vào file JSON
- Xem danh sách các file dữ liệu đã lưu
- Xuất dữ liệu ra định dạng JSON hoặc CSV
- Giao diện người dùng thân thiện sử dụng Bootstrap

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.7+
- Pip (trình quản lý gói của Python)

### Bước cài đặt

1. Clone repository này:
   ```bash
   git clone https://github.com/yourusername/tiktok-research-tool.git
   cd tiktok-research-tool
   ```

2. Tạo và kích hoạt môi trường ảo:
   ```bash
   # Trên macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # Trên Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Cài đặt các gói phụ thuộc:
   ```bash
   pip install flask flask-cors
   ```

4. Chạy ứng dụng:
   ```bash
   python app.py
   ```

5. Mở trình duyệt và truy cập địa chỉ: `http://127.0.0.1:5000`

## 🔍 Sử dụng

### Thu thập dữ liệu

1. Truy cập tab "Data Collection"
2. Nhập tên người dùng TikTok hoặc hashtag cần thu thập
3. Tùy chỉnh các tham số (thời gian chạy, số lượng video, tốc độ cuộn)
4. Tích vào "Save results to file" nếu muốn lưu kết quả
5. Nhấn "Start Data Collection" để bắt đầu

### Xem và quản lý file đã lưu

1. Truy cập tab "Saved Files"
2. Danh sách các file JSON đã lưu sẽ hiển thị
3. Nhấn "View" để xem nội dung file
4. (Chức năng "Delete" sẽ được bổ sung trong các phiên bản tương lai)

### Xuất dữ liệu

1. Sau khi thu thập hoặc xem file dữ liệu
2. Nhấn nút "Export" ở góc phải giao diện kết quả
3. Chọn định dạng xuất: JSON hoặc CSV
4. File sẽ được tải về thiết bị của bạn

## 📁 Cấu trúc dự án

```
tiktok-research-tool/
├── app.py                  # Ứng dụng Flask chính
├── data/                   # Thư mục lưu trữ dữ liệu thu thập
├── templates/              # Templates HTML
│   └── index.html          # Giao diện người dùng
├── static/                 # Tài nguyên tĩnh (sẽ bổ sung sau)
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript
├── venv/                   # Môi trường ảo Python
└── README.md               # Tài liệu hướng dẫn
```

## 📑 Tài liệu yêu cầu sản phẩm (PRD)

### 1. Mục tiêu sản phẩm

TikTok Research Tool là một ứng dụng nghiên cứu nhằm giúp người dùng thu thập và phân tích dữ liệu từ nền tảng TikTok. Sản phẩm hướng đến các nhà nghiên cứu, nhà tiếp thị, nhà phân tích xu hướng và những người quan tâm đến dữ liệu mạng xã hội.

### 2. Người dùng mục tiêu

- Nhà nghiên cứu mạng xã hội
- Chuyên gia tiếp thị và xây dựng thương hiệu
- Nhà phân tích xu hướng
- Content creator muốn nghiên cứu thị trường
- Sinh viên và giáo viên trong lĩnh vực truyền thông

### 3. Yêu cầu chức năng

#### 3.1. Thu thập dữ liệu

| ID | Yêu cầu | Mức độ ưu tiên | Trạng thái |
|----|---------|----------------|------------|
| F1.1 | Thu thập dữ liệu dựa trên tên người dùng | Cao | Hoàn thành |
| F1.2 | Thu thập dữ liệu dựa trên hashtag | Cao | Hoàn thành |
| F1.3 | Tùy chỉnh thời gian chạy | Trung bình | Hoàn thành |
| F1.4 | Tùy chỉnh số lượng video tối đa | Trung bình | Hoàn thành |
| F1.5 | Tùy chỉnh tốc độ cuộn | Thấp | Hoàn thành |
| F1.6 | Thu thập từ nhiều nguồn cùng lúc | Thấp | Chưa triển khai |
| F1.7 | Lên lịch thu thập tự động | Thấp | Chưa triển khai |

#### 3.2. Quản lý dữ liệu

| ID | Yêu cầu | Mức độ ưu tiên | Trạng thái |
|----|---------|----------------|------------|
| F2.1 | Lưu kết quả vào file JSON | Cao | Hoàn thành |
| F2.2 | Xem danh sách file đã lưu | Cao | Hoàn thành |
| F2.3 | Xem nội dung file | Cao | Hoàn thành |
| F2.4 | Xuất dữ liệu dạng JSON | Cao | Hoàn thành |
| F2.5 | Xuất dữ liệu dạng CSV | Trung bình | Hoàn thành |
| F2.6 | Xóa file đã lưu | Thấp | Chưa triển khai |
| F2.7 | Tìm kiếm trong dữ liệu đã lưu | Thấp | Chưa triển khai |
| F2.8 | Lưu trữ trong cơ sở dữ liệu | Thấp | Chưa triển khai |

#### 3.3. Phân tích dữ liệu

| ID | Yêu cầu | Mức độ ưu tiên | Trạng thái |
|----|---------|----------------|------------|
| F3.1 | Thống kê cơ bản (lượt thích, chia sẻ, bình luận) | Trung bình | Chưa triển khai |
| F3.2 | Phân tích xu hướng theo thời gian | Thấp | Chưa triển khai |
| F3.3 | Biểu đồ trực quan | Thấp | Chưa triển khai |
| F3.4 | Phân tích văn bản trong video | Thấp | Chưa triển khai |

#### 3.4. Giao diện người dùng

| ID | Yêu cầu | Mức độ ưu tiên | Trạng thái |
|----|---------|----------------|------------|
| F4.1 | Giao diện đơn giản, dễ sử dụng | Cao | Hoàn thành |
| F4.2 | Hiển thị trạng thái thu thập | Cao | Hoàn thành |
| F4.3 | Hiển thị kết quả dạng bảng | Cao | Hoàn thành |
| F4.4 | Giao diện đáp ứng trên nhiều thiết bị | Trung bình | Hoàn thành |
| F4.5 | Dark mode | Thấp | Chưa triển khai |

### 4. Yêu cầu phi chức năng

#### 4.1. Hiệu suất

| ID | Yêu cầu | Mức độ ưu tiên | Trạng thái |
|----|---------|----------------|------------|
| NF1.1 | Thời gian phản hồi nhanh (< 2 giây) | Cao | Hoàn thành |
| NF1.2 | Xử lý đồng thời nhiều người dùng | Thấp | Chưa triển khai |
| NF1.3 | Tối ưu sử dụng bộ nhớ | Trung bình | Đang triển khai |

#### 4.2. Bảo mật

| ID | Yêu cầu | Mức độ ưu tiên | Trạng thái |
|----|---------|----------------|------------|
| NF2.1 | Bảo vệ dữ liệu người dùng | Cao | Chưa triển khai |
| NF2.2 | Tuân thủ quy định của TikTok | Cao | Đang triển khai |
| NF2.3 | Xác thực người dùng | Thấp | Chưa triển khai |

#### 4.3. Khả năng mở rộng

| ID | Yêu cầu | Mức độ ưu tiên | Trạng thái |
|----|---------|----------------|------------|
| NF3.1 | Kiến trúc module dễ mở rộng | Cao | Hoàn thành |
| NF3.2 | API cho bên thứ ba | Thấp | Chưa triển khai |
| NF3.3 | Khả năng tích hợp với các công cụ khác | Thấp | Chưa triển khai |

### 5. Sơ đồ luồng người dùng

```
1. Truy cập ứng dụng
   │
   ├─── 2a. Tab "Data Collection"
   │     │
   │     ├─── 3a. Nhập tham số (username/hashtag)
   │     │
   │     ├─── 4a. Cấu hình (thời gian, số lượng, tốc độ)
   │     │
   │     ├─── 5a. Bắt đầu thu thập
   │     │
   │     └─── 6a. Xem kết quả / Xuất dữ liệu
   │
   └─── 2b. Tab "Saved Files"
         │
         ├─── 3b. Xem danh sách file
         │
         ├─── 4b. Chọn file để xem
         │
         └─── 5b. Xem dữ liệu / Xuất dữ liệu
```

## 🚧 Hướng phát triển

### Giai đoạn 1: Cải thiện cơ bản (ngắn hạn)

- Thêm chức năng xóa file đã lưu
- Cải thiện UI/UX
- Thêm tùy chọn proxy để tránh bị chặn
- Thêm trang đăng nhập cơ bản

### Giai đoạn 2: Phân tích dữ liệu (trung hạn)

- Thêm biểu đồ phân tích cơ bản (lượt thích, bình luận, chia sẻ)
- Thêm phân tích xu hướng theo thời gian
- Tích hợp cơ sở dữ liệu (MongoDB hoặc SQLite)
- Thêm chức năng tìm kiếm và lọc dữ liệu

### Giai đoạn 3: Chức năng nâng cao (dài hạn)

- Tích hợp AI để phân tích nội dung video
- Thêm tính năng so sánh dữ liệu giữa các tài khoản
- Xây dựng API cho bên thứ ba
- Hỗ trợ thu thập từ nhiều nền tảng mạng xã hội khác
- Tích hợp hệ thống báo cáo và thông báo

## 💡 Kỹ năng cần thiết để phát triển

### Kỹ năng cơ bản

- **Python**: Ngôn ngữ lập trình chính của dự án
- **Flask**: Framework web được sử dụng cho backend
- **HTML/CSS/JavaScript**: Phát triển frontend
- **Git**: Quản lý mã nguồn

### Kỹ năng nâng cao

- **Selenium/Playwright**: Tự động hóa trình duyệt để thu thập dữ liệu
- **MongoDB/SQL**: Lưu trữ và quản lý dữ liệu
- **Data Analysis**: Pandas, NumPy để phân tích dữ liệu
- **Visualization**: Chart.js, D3.js để tạo biểu đồ
- **React/Vue.js**: Nâng cấp frontend sang SPA hiện đại

## 👥 Đóng góp

Đóng góp và đề xuất đều được hoan nghênh! Vui lòng làm theo các bước sau:

1. Fork repository
2. Tạo nhánh tính năng mới (`git checkout -b feature/amazing-feature`)
3. Commit thay đổi của bạn (`git commit -m 'Add some amazing feature'`)
4. Push lên nhánh (`git push origin feature/amazing-feature`)
5. Mở Pull Request

## 📄 Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

---

Được tạo bởi [Your Name] - [your.email@example.com] 