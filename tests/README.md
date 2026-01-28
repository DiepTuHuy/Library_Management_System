# Library Management System - Test Suite

Bộ test toàn diện cho hệ thống quản lý thư viện, bao gồm unit tests, integration tests, và test fixtures.

## Cấu trúc thư mục

```
tests/
├── conftest.py                 # Pytest configuration và fixtures
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_user_controller.py       # User management tests
│   ├── test_book_controller.py       # Book management tests
│   ├── test_borrow_controller.py     # Book borrowing tests
│   └── test_fine_controller.py       # Fine management tests
└── integration/                # Integration tests
    ├── __init__.py
    ├── test_system_workflows.py      # Complete workflow tests
    └── test_gui_integration.py       # GUI component tests
```

## Cài đặt

### Các dependencies cần thiết

```bash
pip install pytest pytest-cov mongomock customtkinter
```

### Cấu hình môi trường

Các test sử dụng `mongomock` để mock MongoDB, không cần MongoDB thực tế chạy.

## Chạy Tests

### Chạy tất cả tests
```bash
pytest
```

### Chạy unit tests chỉ
```bash
pytest tests/unit/
```

### Chạy integration tests chỉ
```bash
pytest tests/integration/
```

### Chạy test cụ thể
```bash
pytest tests/unit/test_user_controller.py
```

### Chạy test cụ thể trong file
```bash
pytest tests/unit/test_user_controller.py::TestUserRegistration::test_register_user_success
```

### Chạy với coverage report
```bash
pytest --cov=src --cov-report=html
```

### Chạy với verbose output
```bash
pytest -v
```

### Chạy theo marker
```bash
pytest -m unit
pytest -m integration
```

## Test Coverage

### Unit Tests

#### test_user_controller.py (18 tests)
- **TestUserRegistration**: Kiểm tra đăng ký người dùng
  - ✓ Đăng ký thành công
  - ✓ Email trùng lặp
  - ✓ Đăng ký admin/librarian
  
- **TestUserLogin**: Kiểm tra đăng nhập
  - ✓ Đăng nhập thành công
  - ✓ Email không hợp lệ
  - ✓ Mật khẩu sai
  
- **TestUserModel**: Kiểm tra mô hình User
  - ✓ Tạo user
  - ✓ Lưu và lấy dữ liệu
  - ✓ Xóa mềm (soft delete)
  
- **TestUserRoles**: Kiểm tra các vai trò người dùng
  - ✓ Admin role
  - ✓ Librarian role
  - ✓ Member role

#### test_book_controller.py (20 tests)
- **TestBookAddition**: Kiểm tra thêm sách
  - ✓ Thêm sách thành công
  - ✓ Số lượng 0
  - ✓ Số lượng mặc định
  
- **TestBookRetrieval**: Kiểm tra lấy sách
  - ✓ Lấy theo ID
  - ✓ Sách không tồn tại
  - ✓ Tìm kiếm theo tiêu đề
  
- **TestBookUpdate**: Kiểm tra cập nhật sách
  - ✓ Cập nhật số lượng
  - ✓ Cập nhật thông tin chi tiết
  
- **TestBookAvailability**: Kiểm tra tính sẵn có
  - ✓ Số lượng sẵn có
  - ✓ Giảm số lượng
  - ✓ Tăng số lượng

#### test_borrow_controller.py (18 tests)
- **TestBorrowBook**: Kiểm tra mượn sách
  - ✓ Mượn thành công
  - ✓ Sách không tồn tại
  - ✓ Không còn bản sao
  - ✓ Không mượn cùng sách 2 lần
  
- **TestReturnBook**: Kiểm tra trả sách
  - ✓ Trả thành công
  - ✓ Record không tồn tại
  - ✓ Đã trả rồi
  
- **TestBorrowDueDate**: Kiểm tra thời hạn trả
  - ✓ Due date là 14 ngày
  - ✓ Kiểm tra quá hạn

#### test_fine_controller.py (18 tests)
- **TestFineCreation**: Kiểm tra tạo phạt
  - ✓ Tạo phạt thành công
  - ✓ Phạt sách quá hạn
  
- **TestFinePayment**: Kiểm tra thanh toán phạt
  - ✓ Thanh toán thành công
  - ✓ Thanh toán một phần
  - ✓ Phạt đã được trả rồi
  
- **TestFineStatus**: Kiểm tra trạng thái phạt
  - ✓ Phạt chưa thanh toán
  - ✓ Đánh dấu đã thanh toán

### Integration Tests

#### test_system_workflows.py (8 test classes)
- **TestCompleteUserWorkflow**: Luồng đăng ký và đăng nhập
- **TestCompleteBorrowWorkflow**: Luồng mượn-trả sách
- **TestMultipleConcurrentBorrows**: Nhiều người mượn cùng lúc
- **TestDatabasePersistence**: Kiểm tra lưu trữ dữ liệu

#### test_gui_integration.py (5 test classes)
- **TestLoginViewIntegration**: Kiểm tra LoginView
- **TestDashboardIntegration**: Kiểm tra Dashboards
- **TestFormSubmissionIntegration**: Kiểm tra submit form

## Fixtures (conftest.py)

### Database Fixtures
- `mock_db`: Mock MongoDB database
- `mock_db_with_data`: Database với dữ liệu mẫu

### User Fixtures
- `sample_user`: User thường (member)
- `sample_admin`: User admin
- `sample_librarian`: User librarian

### Book Fixtures
- `sample_book`: 1 cuốn sách
- `sample_books`: Nhiều cuốn sách

### Borrow Fixtures
- `sample_borrow_record`: Record mượn sách
- `sample_fine`: Record phạt

### Controller Fixtures
- `user_controller`: UserController instance
- `book_controller`: BookController instance
- `borrow_controller`: BorrowController instance
- `fine_controller`: FineController instance

## Viết Test Mới

### Ví dụ Unit Test

```python
def test_new_feature(self, user_controller, mock_db):
    """Test new feature"""
    result = user_controller.some_method()
    
    assert result["success"] is True
    assert "expected_key" in result
```

### Ví dụ Integration Test

```python
def test_complete_workflow(self, user_controller, book_controller, mock_db):
    """Test complete workflow"""
    
    # Step 1
    result1 = user_controller.register_user(...)
    assert result1["success"] is True
    
    # Step 2
    result2 = book_controller.add_book(...)
    assert result2["success"] is True
```

## Best Practices

1. **Isolation**: Mỗi test phải độc lập và có thể chạy riêng lẻ
2. **Clarity**: Tên test phải miêu tả rõ ràng what is being tested
3. **Fixtures**: Sử dụng fixtures để setup dữ liệu test
4. **Assertions**: Kiểm tra kết quả mong muốn rõ ràng
5. **Coverage**: Cố gắng cover tất cả use cases

## Troubleshooting

### Test fails vì mongomock not found
```bash
pip install mongomock
```

### Test fails vì missing dependencies
```bash
pip install -r requirements-dev.txt
```

### Clear pytest cache
```bash
pytest --cache-clear
```

## Continuous Integration

Các test nên chạy trước mỗi commit:

```bash
# Pre-commit hook
pytest && git commit
```

## Reports

### HTML Coverage Report
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Results
```bash
pytest --tb=short -v > test_results.txt
```

## Liên hệ

Nếu gặp vấn đề với tests, vui lòng:
1. Kiểm tra test output cẩn thận
2. Chạy test cụ thể để debug
3. Kiểm tra fixtures được load đúng
