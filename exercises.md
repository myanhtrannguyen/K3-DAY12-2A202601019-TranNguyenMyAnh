# Phiếu Phản Ánh — K3 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng mẫu in nghiêng bên dưới mỗi câu bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: ..........................  Mã học viên: ..........................

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Khi chạy test CP1, tôi thấy `Settings(_env_file=None)` ném `ValidationError` ngay khi không có `AGENT_API_KEY`. Nếu tôi deploy lên Railway mà quên khai báo biến này, lỗi sẽ lộ ra lúc deploy thay vì service mở ra với khóa `changeme` mà ai cũng đoán được. Nhờ vậy tôi không vô tình đưa một endpoint `/ask` có thể bị người lạ dùng để tiêu quota của mình lên Internet.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> Một dòng tôi lấy được từ container là: `{"event": "ask_completed", "level": "info", "timestamp": "2026-08-10T16:55:41.031384+00:00", "user_id": "reflection-070bc33c23d449d3842710d63f6ec0ff", "tokens_in": 2, "tokens_out": 35, "cost_usd": 2.13e-05}`. Với JSON này tôi có thể lọc tất cả request của một `user_id` để điều tra, và cộng/truy vấn trường `cost_usd` hoặc token để theo dõi chi phí. `print("đã trả lời xong")` chỉ là văn bản, không có trường chuẩn để máy lọc hay tính toán đáng tin cậy.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.2 GB |
| Multi-stage | 234 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> Chênh lệch xấp xỉ 966 MB. Bản một stage mang base image Python đầy đủ cùng các layer cài đặt dependency và những phần chỉ cần trong lúc build. Bản multi-stage dùng `python:3.11-slim`; stage runtime chỉ nhận virtualenv đã cài và hai thư mục `app/`, `utils/`, nên không mang theo cache pip, công cụ build và các file phát triển không cần để chạy service.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi sửa một ký tự trong `app/main.py` rồi build lại, layer `COPY requirements.txt` và `pip install` được dùng lại từ cache; layer `COPY app ./app` và layer xuất image phía sau nó chạy lại. Tôi đã thấy các layer builder/virtualenv hiện `CACHED` trong output build. Nếu `COPY . .` đứng trước `pip install`, thay đổi ở `main.py` làm hash của toàn bộ context đổi, nên layer `pip install` cũng mất cache và phải cài lại dependency dù `requirements.txt` không đổi.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> Một lỗi cho phép chạy lệnh tùy ý trong Python có thể cho kẻ tấn công một shell trong container. Nếu process là root, họ đã có toàn quyền với filesystem và process của container; khi container lại có cấu hình nguy hiểm như Docker socket/volume nhạy cảm, đặc quyền hoặc một lỗ hổng kernel, họ có thể leo sang quyền cao trên host. `USER appuser` làm process ứng dụng bắt đầu bằng user không đặc quyền, nên shell đó không tự ghi được các vùng root-owned hay có quyền root trong container. Nó không thay thế việc vá lỗi hay cấu hình Docker an toàn, nhưng chặn bước leo thang dễ nhất.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> Tối đa là 20 request trong khoảng hai giây: gửi 10 request ở 12:00:59, rồi gửi tiếp 10 request ở 12:01:00 hoặc 12:01:01. Bộ đếm theo phút đồng hồ reset khi sang phút mới nên cả hai nhóm đều có vẻ dưới 10/phút. Sliding window của bài luôn nhìn lại đúng 60 giây trước thời điểm gọi nên request thứ 11 sẽ bị chặn.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> Rate limit giới hạn tốc độ request theo cửa sổ 60 giây; cost guard giới hạn tổng tiền theo từng user và tháng. Ví dụ, một user vẫn còn quota request trong phút nhưng đã chi gần hoặc vượt ngân sách tháng thì rate limiter cho qua còn cost guard trả 402. Ngược lại, user gửi request nhỏ, rất rẻ lần thứ 11 trong một phút khi ngân sách tháng vẫn còn nhiều: cost guard có thể cho qua, nhưng rate limiter trả 429.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> Nếu endpoint chung kiểm tra Redis, Redis mất kết nối thì cả ba container đều trả 503 cho health probe. Orchestrator/load balancer coi chúng không khỏe, ngừng gửi traffic hoặc restart lần lượt các container. Trong 30 giây đó service không phục vụ được dù process Python vốn vẫn sống; các lần restart còn tạo thêm tải lúc Redis đang lỗi. Tách `/health` chỉ kiểm tra process giúp container không bị restart hàng loạt, còn `/ready` trả 503 để load balancer biết chưa nên gửi request phụ thuộc Redis.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Tôi chạy lại stack với `--scale agent=3` và gửi ba request cùng user qua Nginx; `history_length` nhận được là `0`, `2`, rồi `4`. Mỗi lượt lưu thêm message user và assistant, còn Redis là dữ liệu chung nên dù request rơi vào replica nào số vẫn tăng đều. Nếu mỗi container dùng dict Python riêng, số này phụ thuộc replica được Nginx chọn: có thể quay về 0 khi sang instance chưa gặp user đó, hoặc chỉ tăng theo lịch sử cục bộ của từng instance.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> Khi deploy Railway, build hoàn tất nhưng healthcheck báo `Attempt #1 failed with service unavailable` rồi `1/1 replicas never became healthy`. Tôi đọc log thấy không có lỗi build, sau đó kiểm tra `railway.toml`: `startCommand` truyền `--port $PORT`. Với Dockerfile, Railway chạy start command theo exec form nên biến này không được shell mở rộng; Uvicorn không nhận được port số để khởi động. Tôi sửa thành `sh -c 'exec uvicorn app.main:app --host 0.0.0.0 --port $PORT'`, để shell mở rộng port do Railway cấp trước khi gọi Uvicorn.
