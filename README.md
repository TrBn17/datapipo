# Local Lakehouse Baseline

Repo này là baseline tối thiểu cho một local lakehouse chạy trên máy cá nhân. Mục tiêu là giữ đúng những thứ gần như lúc nào cũng cần:
- hạ tầng local để mô phỏng object storage và query engine
- cấu hình engine để cùng đọc một lakehouse
- vùng dữ liệu theo tầng `bronze`, `silver`, `gold`
- một script ingest mẫu để kiểm tra luồng ETL trên dữ liệu thật


## Thành phần chính

- `MinIO`: object storage local, đóng vai trò S3-compatible storage
- `Iceberg REST catalog`: metadata service cho bảng Iceberg
- `Spark`: engine để ETL nặng, tạo bảng, backfill, maintenance
- `Trino`: engine để query/ad-hoc analytics
- `lakehouse/`: chỗ đặt dữ liệu theo tầng nghiệp vụ

## Cấu trúc repo

```text
.
├─ .env.example
├─ docker-compose.yml
├─ Makefile
├─ README.md
├─ infra/
│  ├─ spark/
│  │  └─ conf/
│  │     └─ spark-defaults.conf
│  └─ trino/
│     └─ catalog/
│        └─ iceberg.properties
├─ lakehouse/
│  ├─ bronze/
│  ├─ silver/
│  └─ gold/
├─ sample/
│  └─ moltbook_top1000_posts.xlsx
└─ scripts/
   └─ extract_moltbook_sample.ps1
```

## Vai trò từng thư mục

- `infra/`
  Chứa cấu hình cố định cho engine. Đây là phần nên ít thay đổi và được version control rõ ràng.

- `lakehouse/bronze/`
  Dữ liệu raw hoặc gần raw nhất. Nên ưu tiên append-only, ít biến đổi logic.

- `lakehouse/silver/`
  Dữ liệu đã chuẩn hóa kiểu dữ liệu, đặt tên cột, xử lý null, deduplicate, và làm sạch nghiệp vụ.

- `lakehouse/gold/`
  Dữ liệu phục vụ phân tích, báo cáo, dashboard, hoặc feature-ready outputs.

- `sample/`
  Nơi đặt dữ liệu mẫu để test pipeline hoặc mô phỏng nguồn vào thật.

- `scripts/`
  Nơi đặt các script vận hành nhỏ nhưng hữu ích thường xuyên, ví dụ ingest source file, seed dữ liệu, bootstrap namespace.

## Luồng dữ liệu chuẩn nên giữ

1. Nguồn vào đi vào `bronze`
2. Làm sạch và chuẩn hóa sang `silver`
3. Tổng hợp và đóng gói nghiệp vụ sang `gold`
4. Spark và Trino cùng truy cập lakehouse qua Iceberg catalog

Nếu sau này thêm code ETL thật, vẫn nên bám đúng luồng này. Tránh nhảy cóc từ raw sang mart trừ khi đó là pipeline tạm.

## Cách chạy hạ tầng

1. Copy `.env.example` thành `.env`
2. Khởi động service:
   - `docker compose up -d`
3. Kiểm tra:
   - MinIO Console: `http://localhost:9001`
   - Trino: `http://localhost:8080`
   - Iceberg REST: `http://localhost:8181`

Lệnh rút gọn:
- `make up`
- `make down`

## Cách dùng file mẫu

Script [scripts/extract_moltbook_sample.ps1](C:\Users\Admin\spark\scripts\extract_moltbook_sample.ps1) đọc workbook [sample/moltbook_top1000_posts.xlsx](C:\Users\Admin\spark\sample\moltbook_top1000_posts.xlsx) và ghi ra ba tầng local:

- `lakehouse/bronze/`
- `lakehouse/silver/`
- `lakehouse/gold/`

Chạy:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/extract_moltbook_sample.ps1
```

Hoặc:
```powershell
make extract
```

## Quy ước mở rộng repo sau này

Khi bắt đầu làm ETL thật, chỉ thêm những phần này nếu đã cần:
- `src/etl/ingestion/` khi có từ 2 nguồn dữ liệu trở lên
- `src/etl/transforms/` khi transform không còn phù hợp viết bằng script nhỏ
- `dbt/` khi đã chốt dùng dbt làm lớp transform chính
- `sql/` khi query nghiệp vụ cần quản lý riêng
- `tests/` khi đã có logic cần regression protection

Nguyên tắc là thêm theo nhu cầu thật, không dựng framework trước.

## Những gì repo này cố tình không giữ

- sample app Python
- dbt project mẫu
- unit test mẫu
- code transform giả lập không gắn với nghiệp vụ
- artifact sinh ra từ mỗi lần chạy local

Mục tiêu là nhìn vào repo và hiểu ngay:
1. hạ tầng nằm ở đâu
2. dữ liệu nằm ở đâu
3. script vận hành nằm ở đâu
4. mở rộng tiếp từ đâu khi nghiệp vụ rõ hơn
