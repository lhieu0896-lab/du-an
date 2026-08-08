import pandas as pd

# Tạo tập dữ liệu tin tức mẫu gồm các chuyên mục
data = [
    {
        "title": "Doanh nghiệp công nghệ tăng tốc ứng dụng AI",
        "category": "Công nghệ",
        "content": "Trí tuệ nhân tạo (AI) đang trở thành công cụ cốt lõi giúp các doanh nghiệp tối ưu hóa quy trình sản xuất và vận hành. Các giải pháp AI tự động hóa và xử lý ngôn ngữ tự nhiên được áp dụng rộng rãi trong chăm sóc khách hàng, phân tích dữ liệu và dự báo thị trường. Nhiều chuyên gia nhận định việc đầu tư vào AI giúp doanh nghiệp tăng trưởng năng suất đáng kể."
    },
    {
        "title": "Thị trường bất động sản ghi nhận tín hiệu phục hồi",
        "category": "Kinh tế",
        "content": "Báo cáo quý II cho thấy thị trường bất động sản đã có bước chuyển biến tích cực nhờ các chính sách tháo gỡ khó khăn về mặt pháp lý và dòng vốn tín dụng được khai thông. Lượng giao dịch ở phân khúc căn hộ chung cư tăng trưởng ổn định. Giá bán duy trì mức hợp lý và được dự báo sẽ tiếp tục có chiều hướng tốt."
    },
    {
        "title": "Đội tuyển Việt Nam tích cực chuẩn bị cho giải đấu lớn",
        "category": "Thể thao",
        "content": "Ban huấn luyện đội tuyển bóng đá quốc gia đã công bố danh sách tập trung ngắn hạn nhằm chuẩn bị cho vòng loại giải vô địch châu Á. Các cầu thủ nòng cốt duy trì phong độ tốt tại giải quốc nội. Huấn luyện viên trưởng nhấn mạnh việc cải thiện thể lực và khả năng phối hợp nhóm sẽ là ưu tiên hàng đầu."
    }
]

df = pd.DataFrame(data)
df.to_csv("dataset.csv", index=False, encoding="utf-8-sig")
print("✅ Đã tạo thành công file dataset.csv!")