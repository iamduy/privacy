# Privacy policies

Chính sách bảo mật cho các game, phục vụ qua GitHub Pages: https://iamduy.github.io/privacy/

## Cấu trúc

```
games/<slug>.json     cấu hình + nội dung riêng của từng game
locales/<lang>.json   câu chữ dùng chung cho mọi game (en, vi, ...)
assets/style.css      giao diện dùng chung
build.py              sinh HTML — chạy: python3 build.py
```

Các file sinh ra (được commit, đừng sửa tay):

- `<slug>/en.html`, `<slug>/vi.html` — trang chính sách, ví dụ `color-flood/en.html`
- `<slug>/index.html` — chuyển hướng sang ngôn ngữ đầu tiên
- `index.html` — danh sách tất cả game
- `en.html`, `vi.html` ở gốc — chuyển hướng tới Color Flood (`"legacy_root": true`) để link cũ trên store không bị hỏng

## Thêm game mới

1. Copy `games/color-flood.json` thành `games/<slug>.json` (slug sẽ là đường dẫn URL).
2. Sửa các trường:
   - `name`, `effective_date` (YYYY-MM-DD), `developer`, `contact_email`
   - `languages`: các ngôn ngữ cần sinh, mỗi ngôn ngữ phải có trong `locales/` và trong `text`
   - `ads`: `"admob"` hoặc `null` (không quảng cáo)
   - `privacy_options_in_app`: `true` nếu trong game có mục **Cài đặt → Tùy chọn quyền riêng tư** (UMP consent)
   - `reset_progress_in_app`: `true` nếu trong game có mục **Cài đặt → Đặt lại tiến trình** (xoá dữ liệu trên máy)
   - `min_age`: độ tuổi tối thiểu
   - bỏ `legacy_root` (chỉ Color Flood dùng)
   - `text.<lang>.intro`: đoạn giới thiệu game
   - `text.<lang>.local_data`: dữ liệu lưu trên máy (đứng đầu câu "... chỉ được lưu trên thiết bị của bạn")
   - `text.<lang>.extra_sections` (tuỳ chọn): `[{"heading": "...", "html": "<p>...</p>"}]` cho phần riêng như mua trong ứng dụng, Firebase...
3. `python3 build.py`, mở `<slug>/en.html` kiểm tra, rồi commit.

Link khai báo trên App Store / Google Play: `https://iamduy.github.io/privacy/<slug>/en.html`.

Thêm SDK mới (ví dụ Firebase Analytics) dùng cho nhiều game: thêm câu chữ vào `locales/*.json` và một nhánh trong `policy_page()` của `build.py`, giống cách `admob` đang làm.
