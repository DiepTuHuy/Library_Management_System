# Library Management System - Comprehensive Navigation Flow Analysis

**Ngày phân tích**: 26 January 2026  
**Trạng thái**: Chi tiết đầy đủ cho mỗi role

---

## 📊 TỔNG QUAN HỆ THỐNG NAVIGATION

```
┌─────────────────────────────────────────────────────────────┐
│                      ENTRY POINTS                           │
├─────────────────────────────────────────────────────────────┤
│  Login.html ◄────────────► Register.html ◄────► ForgotPassword.html
│      │
│      ├─► (Valid Credentials)
│      │
│      ├──────► ADMIN DASHBOARD
│      ├──────► LIBRARIAN DASHBOARD  
│      ├──────► MEMBER DASHBOARD
│      └──────► GUEST DASHBOARD
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 LEVEL 1: ROOT NAVIGATION (Authentication)

### 1.1 Login.html (Entry Point)
**Mục đích**: Xác thực người dùng  
**Trường nhập liệu**: Email, Password  
**Nút hành động**:
- **"Login"** → Xác thực → Điều hướng đến Dashboard của role tương ứng
- **"Register"** → Link tới [Register.html](Register.html)
- **"Forgot Password"** → Link tới [ForgotPassword.html](ForgotPassword.html)

**Navigation paths**:
```
Login.html → {Admin/Overview.html, Librarian/Overview.html, Member/Overview.html, Guest/Guest.html}
Login.html → Register.html
Login.html → ForgotPassword.html
```

### 1.2 Register.html (New User Registration)
**Mục đích**: Đăng ký tài khoản mới  
**Trường nhập liệu**: Email, Password, Full Name, Phone  
**Nút hành động**:
- **"Register"** → Tạo tài khoản → Điều hướng tới [Login.html](Login.html)
- **"Back to Login"** → Link tới [Login.html](Login.html)

**Navigation paths**:
```
Register.html → Login.html
```

### 1.3 ForgotPassword.html (Password Recovery)
**Mục đích**: Khôi phục mật khẩu  
**Trường nhập liệu**: Email  
**Nút hành động**:
- **"Send Reset Email"** → Gửi email → Quay lại [Login.html](Login.html)
- **"Back to Login"** → Link tới [Login.html](Login.html)

**Navigation paths**:
```
ForgotPassword.html → Login.html
```

---

## 👨‍💼 LEVEL 2: ADMIN ROLE NAVIGATION FLOW

### 2.1 Admin Overview Dashboard
**File**: [Admin/Overview.html](Admin/Overview.html)  
**Mục đích**: Trang chủ quản trị viên - Quản lý toàn bộ hệ thống

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER                                                     │
│  [Logo] [Title]              [Profile] [Settings] [Logout]  │
├─────────────────────────────────────────────────────────────┤
│  SIDEBAR / TAB NAVIGATION                                   │
│  ├─ Dashboard (Thống kê chung)                             │
│  ├─ Quản lý User (ManageUser)                              │
│  ├─ Quản lý Sách (ManageBook)                              │
│  ├─ Thêm Sách (AddBook)                                    │
│  ├─ Thêm User (AddUser)                                    │
│  └─ Báo cáo (Reports)                                      │
├─────────────────────────────────────────────────────────────┤
│  MAIN CONTENT AREA                                          │
│  [Dashboard Statistics Cards]                              │
│  [Recent Activities]                                        │
│  [Quick Actions]                                           │
└─────────────────────────────────────────────────────────────┘
```

**Navigation Elements**:

| Link/Button | Target | Loại |
|-------------|--------|------|
| Dashboard | Stay on Overview | Tab |
| Quản lý User | [ManageUser.html](Admin/ManageUser.html) | Tab |
| Quản lý Sách | [ManageBook.html](Admin/ManageBook.html) | Tab |
| Thêm Sách | [AddBook.html](Admin/AddBook.html) | Tab |
| Thêm User | [AddUser.html](Admin/AddUser.html) | Tab |
| Báo cáo | Reports Submenu | Tab |
| Profile Icon | Profile Page | Button |
| Settings Icon | Settings Page | Button |
| Logout | [Login.html](Login.html) | Button |

**Reports Submenu** (từ Overview):
```
Reports
├─ Báo cáo Mượn Sách → ReportBorrow.html
├─ Báo cáo Danh Mục → ReportCategory.html
├─ Báo cáo Sách Quá Hạn → ReportLate.html
└─ Báo cáo Sách Phổ Biến → ReportTopBook.html
```

---

### 2.2 Admin - Quản lý User
**File**: [Admin/ManageUser.html](Admin/ManageUser.html)  
**Mục đích**: Xem, chỉnh sửa, xóa user

**Navigation**:
- **Breadcrumb**: Dashboard > Quản lý User
- **Back Button**: Quay lại [Admin/Overview.html](Admin/Overview.html)
- **Add User Button**: Link tới [Admin/AddUser.html](Admin/AddUser.html)
- **Edit Row**: Mở modal hoặc điều hướng tới edit page
- **Logout**: [Login.html](Login.html)

---

### 2.3 Admin - Quản lý Sách
**File**: [Admin/ManageBook.html](Admin/ManageBook.html)  
**Mục đích**: Xem, chỉnh sửa, xóa sách

**Navigation**:
- **Breadcrumb**: Dashboard > Quản lý Sách
- **Back Button**: Quay lại [Admin/Overview.html](Admin/Overview.html)
- **Add Book Button**: Link tới [Admin/AddBook.html](Admin/AddBook.html)
- **Edit Row**: Mở modal hoặc edit page
- **Logout**: [Login.html](Login.html)

---

### 2.4 Admin - Thêm User
**File**: [Admin/AddUser.html](Admin/AddUser.html)  
**Mục đích**: Tạo user mới

**Navigation**:
- **Breadcrumb**: Dashboard > Quản lý User > Thêm User
- **Back Button**: Quay lại [Admin/ManageUser.html](Admin/ManageUser.html)
- **Cancel Button**: Quay lại [Admin/ManageUser.html](Admin/ManageUser.html)
- **Submit Button**: Lưu → Quay lại [Admin/ManageUser.html](Admin/ManageUser.html)
- **Logout**: [Login.html](Login.html)

---

### 2.5 Admin - Thêm Sách
**File**: [Admin/AddBook.html](Admin/AddBook.html)  
**Mục đích**: Tạo sách mới

**Navigation**:
- **Breadcrumb**: Dashboard > Quản lý Sách > Thêm Sách
- **Back Button**: Quay lại [Admin/ManageBook.html](Admin/ManageBook.html)
- **Cancel Button**: Quay lại [Admin/ManageBook.html](Admin/ManageBook.html)
- **Submit Button**: Lưu → Quay lại [Admin/ManageBook.html](Admin/ManageBook.html)
- **Logout**: [Login.html](Login.html)

---

### 2.6 Admin - Báo cáo Mượn Sách
**File**: [Admin/ReportBorrow.html](Admin/ReportBorrow.html)  
**Mục đích**: Báo cáo chi tiết lịch sử mượn sách

**Navigation**:
- **Breadcrumb**: Dashboard > Báo cáo > Mượn Sách
- **Back Button**: Quay lại [Admin/Overview.html](Admin/Overview.html) hoặc Reports
- **Export Button**: Xuất PDF/Excel
- **Logout**: [Login.html](Login.html)

---

### 2.7 Admin - Báo cáo Danh Mục
**File**: [Admin/ReportCategory.html](Admin/ReportCategory.html)  
**Mục đích**: Thống kê sách theo danh mục

**Navigation**:
- **Breadcrumb**: Dashboard > Báo cáo > Danh Mục
- **Back Button**: Quay lại [Admin/Overview.html](Admin/Overview.html)
- **Export Button**: Xuất PDF/Excel
- **Logout**: [Login.html](Login.html)

---

### 2.8 Admin - Báo cáo Sách Quá Hạn
**File**: [Admin/ReportLate.html](Admin/ReportLate.html)  
**Mục đích**: Danh sách sách bị quá hạn

**Navigation**:
- **Breadcrumb**: Dashboard > Báo cáo > Quá Hạn
- **Back Button**: Quay lại [Admin/Overview.html](Admin/Overview.html)
- **View User Details**: Link tới [Admin/ManageUser.html](Admin/ManageUser.html)
- **Export Button**: Xuất PDF/Excel
- **Logout**: [Login.html](Login.html)

---

### 2.9 Admin - Báo cáo Sách Phổ Biến
**File**: [Admin/ReportTopBook.html](Admin/ReportTopBook.html)  
**Mục đích**: Top sách được mượn nhiều nhất

**Navigation**:
- **Breadcrumb**: Dashboard > Báo cáo > Sách Phổ Biến
- **Back Button**: Quay lại [Admin/Overview.html](Admin/Overview.html)
- **View Details**: Link tới [Admin/ManageBook.html](Admin/ManageBook.html)
- **Export Button**: Xuất PDF/Excel
- **Logout**: [Login.html](Login.html)

---

## 📚 LEVEL 3: LIBRARIAN ROLE NAVIGATION FLOW

### 3.1 Librarian Overview Dashboard
**File**: [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html)  
**Mục đích**: Trang chủ thủ thư - Quản lý mượn/trả sách

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER                                                     │
│  [Logo] [Title]              [Profile] [Settings] [Logout]  │
├─────────────────────────────────────────────────────────────┤
│  SIDEBAR / TAB NAVIGATION                                   │
│  ├─ Dashboard (Thống kê)                                    │
│  ├─ Sách Đang Mượn (BorrowingBooks)                         │
│  ├─ Sách Đang Trả (Returning)                               │
│  ├─ Thêm Sách (AddBook)                                     │
│  ├─ Quản lý Sách (ManageBooks)                              │
│  ├─ Thêm User (AddUser)                                     │
│  ├─ Quản lý User (ManageUser)                               │
│  └─ Báo cáo (Reports)                                       │
├─────────────────────────────────────────────────────────────┤
│  MAIN CONTENT AREA                                          │
│  [Today's Statistics]                                       │
│  [Pending Operations]                                       │
└─────────────────────────────────────────────────────────────┘
```

**Navigation Elements**:

| Link/Button | Target | Loại |
|-------------|--------|------|
| Dashboard | Stay on Overview | Tab |
| Sách Đang Mượn | [Librarian/BorrowingBooks.html](Librarian/BorrowingBooks.html) | Tab |
| Sách Đang Trả | [Librarian/Returning.html](Librarian/Returning.html) | Tab |
| Thêm Sách | [Librarian/AddBook.html](Librarian/AddBook.html) | Tab |
| Quản lý Sách | [Librarian/ManageBooks.html](Librarian/ManageBooks.html) | Tab |
| Thêm User | [Librarian/AddUser.html](Librarian/AddUser.html) | Tab |
| Quản lý User | [Librarian/ManageUser.html](Librarian/ManageUser.html) | Tab |
| Báo cáo | Reports Submenu | Tab |
| Profile Icon | Profile Page | Button |
| Settings Icon | Settings Page | Button |
| Logout | [Login.html](Login.html) | Button |

**Reports Submenu**:
```
Reports
├─ Báo cáo Mượn Sách → ReportBorrow.html
├─ Báo cáo Danh Mục → ReportCategory.html
├─ Báo cáo Sách Quá Hạn → ReportLate.html
└─ Báo cáo Sách Phổ Biến → ReportTopBook.html
```

---

### 3.2 Librarian - Sách Đang Mượn
**File**: [Librarian/BorrowingBooks.html](Librarian/BorrowingBooks.html)  
**Mục đích**: Quản lý sách được mượn, kiểm tra

**Navigation**:
- **Breadcrumb**: Dashboard > Sách Đang Mượn
- **Back Button**: Quay lại [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html)
- **Check In Book**: Link tới [Librarian/CheckinCard.html](Librarian/CheckinCard.html)
- **View Details**: Link tới [Librarian/CheckinDetail.html](Librarian/CheckinDetail.html)
- **Logout**: [Login.html](Login.html)

---

### 3.3 Librarian - Sách Đang Trả
**File**: [Librarian/Returning.html](Librarian/Returning.html)  
**Mục đích**: Quản lý sách được trả lại

**Navigation**:
- **Breadcrumb**: Dashboard > Sách Đang Trả
- **Back Button**: Quay lại [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html)
- **Process Return**: Link tới [Librarian/CheckinCard.html](Librarian/CheckinCard.html)
- **Logout**: [Login.html](Login.html)

---

### 3.4 Librarian - Kiểm Tra Thẻ Mượn
**File**: [Librarian/CheckinCard.html](Librarian/CheckinCard.html)  
**Mục đích**: Quét thẻ/barcode để kiểm tra nhập sách

**Navigation**:
- **Breadcrumb**: Dashboard > Kiểm Tra Thẻ
- **Back Button**: Quay lại [Librarian/BorrowingBooks.html](Librarian/BorrowingBooks.html) hoặc [Librarian/Returning.html](Librarian/Returning.html)
- **View Full Details**: Link tới [Librarian/CheckinDetail.html](Librarian/CheckinDetail.html)
- **Logout**: [Login.html](Login.html)

---

### 3.5 Librarian - Chi Tiết Kiểm Tra
**File**: [Librarian/CheckinDetail.html](Librarian/CheckinDetail.html)  
**Mục đích**: Xem chi tiết đầy đủ của lần kiểm tra

**Navigation**:
- **Breadcrumb**: Dashboard > Kiểm Tra > Chi Tiết
- **Back Button**: Quay lại [Librarian/CheckinCard.html](Librarian/CheckinCard.html)
- **Confirm/Process**: Cập nhật trạng thái → Quay lại danh sách
- **Logout**: [Login.html](Login.html)

---

### 3.6 Librarian - Thêm Sách
**File**: [Librarian/AddBook.html](Librarian/AddBook.html)  
**Mục đích**: Tạo bản ghi sách mới

**Navigation**:
- **Breadcrumb**: Dashboard > Thêm Sách
- **Back Button**: Quay lại [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html)
- **Cancel**: Quay lại [Librarian/ManageBooks.html](Librarian/ManageBooks.html)
- **Submit**: Lưu → [Librarian/ManageBooks.html](Librarian/ManageBooks.html)
- **Logout**: [Login.html](Login.html)

---

### 3.7 Librarian - Quản lý Sách
**File**: [Librarian/ManageBooks.html](Librarian/ManageBooks.html)  
**Mục đích**: Xem, chỉnh sửa, xóa sách

**Navigation**:
- **Breadcrumb**: Dashboard > Quản lý Sách
- **Back Button**: Quay lại [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html)
- **Add Book**: Link tới [Librarian/AddBook.html](Librarian/AddBook.html)
- **Edit Row**: Chỉnh sửa bản ghi
- **Logout**: [Login.html](Login.html)

---

### 3.8 Librarian - Thêm User
**File**: [Librarian/AddUser.html](Librarian/AddUser.html)  
**Mục đích**: Tạo thành viên mới

**Navigation**:
- **Breadcrumb**: Dashboard > Thêm User
- **Back Button**: Quay lại [Librarian/ManageUser.html](Librarian/ManageUser.html)
- **Cancel**: Quay lại [Librarian/ManageUser.html](Librarian/ManageUser.html)
- **Submit**: Lưu → [Librarian/ManageUser.html](Librarian/ManageUser.html)
- **Logout**: [Login.html](Login.html)

---

### 3.9 Librarian - Quản lý User
**File**: [Librarian/ManageUser.html](Librarian/ManageUser.html)  
**Mục đích**: Xem, chỉnh sửa, xóa thành viên

**Navigation**:
- **Breadcrumb**: Dashboard > Quản lý User
- **Back Button**: Quay lại [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html)
- **Add User**: Link tới [Librarian/AddUser.html](Librarian/AddUser.html)
- **Edit Row**: Chỉnh sửa bản ghi
- **Logout**: [Login.html](Login.html)

---

### 3.10 Librarian - Báo cáo
**Files**: ReportBorrow.html, ReportCategory.html, ReportLate.html, ReportTopBook.html

**Navigation Pattern** (giống với Admin reports):
- **Breadcrumb**: Dashboard > Báo cáo > [Report Type]
- **Back Button**: Quay lại [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html)
- **Export Button**: Xuất PDF/Excel
- **Logout**: [Login.html](Login.html)

---

## 👤 LEVEL 4: MEMBER ROLE NAVIGATION FLOW

### 4.1 Member Overview Dashboard
**File**: [Member/Overview.html](Member/Overview.html)  
**Mục đích**: Trang chủ thành viên - Quản lý sách mượn cá nhân

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER                                                     │
│  [Logo] [Title]              [Profile] [Settings] [Logout]  │
├─────────────────────────────────────────────────────────────┤
│  SIDEBAR / TAB NAVIGATION                                   │
│  ├─ Dashboard (Tổng quan)                                   │
│  ├─ Sách Của Tôi (MyBook)                                   │
│  ├─ Tìm Kiếm Sách (SearchBook)                              │
│  ├─ Lịch Sử (History)                                       │
│  ├─ Chi Tiết Mượn (BorrowDetail)                            │
│  └─ Hồ Sơ (Profile)                                         │
├─────────────────────────────────────────────────────────────┤
│  MAIN CONTENT AREA                                          │
│  [My Borrowed Books]                                        │
│  [Return Dates]                                             │
│  [My Fines/Notifications]                                   │
└─────────────────────────────────────────────────────────────┘
```

**Navigation Elements**:

| Link/Button | Target | Loại |
|-------------|--------|------|
| Dashboard | Stay on Overview | Tab |
| Sách Của Tôi | [Member/MyBook.html](Member/MyBook.html) | Tab |
| Tìm Kiếm Sách | [Member/SearchBook.html](Member/SearchBook.html) | Tab |
| Lịch Sử | [Member/History.html](Member/History.html) | Tab |
| Chi Tiết Mượn | [Member/BorrowDetail.html](Member/BorrowDetail.html) | Tab |
| Hồ Sơ | [Member/Profile.html](Member/Profile.html) | Tab |
| Profile Icon | [Member/Profile.html](Member/Profile.html) | Button |
| Settings Icon | Settings Page | Button |
| Logout | [Login.html](Login.html) | Button |

---

### 4.2 Member - Sách Của Tôi
**File**: [Member/MyBook.html](Member/MyBook.html)  
**Mục đích**: Xem danh sách sách đang mượn

**Navigation**:
- **Breadcrumb**: Dashboard > Sách Của Tôi
- **Back Button**: Quay lại [Member/Overview.html](Member/Overview.html)
- **View Details**: Link tới [Member/BookDetail.html](Member/BookDetail.html)
- **Renew Book**: Action trong trang
- **Logout**: [Login.html](Login.html)

---

### 4.3 Member - Tìm Kiếm Sách
**File**: [Member/SearchBook.html](Member/SearchBook.html)  
**Mục đích**: Tìm kiếm sách có sẵn

**Navigation**:
- **Breadcrumb**: Dashboard > Tìm Kiếm Sách
- **Back Button**: Quay lại [Member/Overview.html](Member/Overview.html)
- **Search Results**: Link tới [Member/BookDetail.html](Member/BookDetail.html) cho từng sách
- **View Details**: Link tới [Member/BookDetail.html](Member/BookDetail.html)
- **Logout**: [Login.html](Login.html)

---

### 4.4 Member - Chi Tiết Sách
**File**: [Member/BookDetail.html](Member/BookDetail.html)  
**Mục đích**: Xem chi tiết sách và tùy chọn mượn

**Navigation**:
- **Breadcrumb**: Dashboard > Tìm Kiếm > Chi Tiết Sách (hoặc Sách Của Tôi > Chi Tiết)
- **Back Button**: Quay lại trang trước (MyBook hoặc SearchBook)
- **Borrow Button**: Mượn sách → [Member/BorrowDetail.html](Member/BorrowDetail.html)
- **Return Button**: Trả sách (nếu đang mượn)
- **Logout**: [Login.html](Login.html)

---

### 4.5 Member - Chi Tiết Mượn
**File**: [Member/BorrowDetail.html](Member/BorrowDetail.html)  
**Mục đích**: Xem chi tiết lịch sử mượn/trả sách

**Navigation**:
- **Breadcrumb**: Dashboard > Chi Tiết Mượn
- **Back Button**: Quay lại [Member/Overview.html](Member/Overview.html)
- **View Book Details**: Link tới [Member/BookDetail.html](Member/BookDetail.html)
- **Export History**: Xuất lịch sử
- **Logout**: [Login.html](Login.html)

---

### 4.6 Member - Lịch Sử
**File**: [Member/History.html](Member/History.html)  
**Mục đích**: Xem lịch sử tất cả hoạt động

**Navigation**:
- **Breadcrumb**: Dashboard > Lịch Sử
- **Back Button**: Quay lại [Member/Overview.html](Member/Overview.html)
- **View Details**: Link tới [Member/BorrowDetail.html](Member/BorrowDetail.html)
- **Filter/Search**: Tìm kiếm trong lịch sử
- **Logout**: [Login.html](Login.html)

---

### 4.7 Member - Hồ Sơ
**File**: [Member/Profile.html](Member/Profile.html)  
**Mục đích**: Quản lý thông tin cá nhân

**Navigation**:
- **Breadcrumb**: Dashboard > Hồ Sơ
- **Back Button**: Quay lại [Member/Overview.html](Member/Overview.html)
- **Edit Profile**: Chỉnh sửa thông tin
- **Change Password**: Link tới Change Password page
- **My Fines**: Link tới Fines page
- **Logout**: [Login.html](Login.html)

---

## 👥 LEVEL 5: GUEST ROLE NAVIGATION FLOW

### 5.1 Guest Dashboard
**File**: [Guest/Guest.html](Guest/Guest.html)  
**Mục đích**: Trang chủ khách - Chỉ xem danh sách sách

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (Minimal)                                           │
│  [Logo] [Title]              [Search] [Login] [Register]    │
├─────────────────────────────────────────────────────────────┤
│  MAIN CONTENT AREA                                          │
│  [Featured Books]                                           │
│  [Book Catalog (Read-only)]                                 │
│  [Categories]                                               │
└─────────────────────────────────────────────────────────────┘
```

**Navigation Elements**:

| Link/Button | Target | Loại |
|-------------|--------|------|
| Logo | Stay on Guest | Link |
| Search | Search Results (Guest view) | Input |
| Book Cards | [Guest/BorrowDetail.html](Guest/BorrowDetail.html) | Card |
| Categories | Filter books | Filter |
| Login Button | [Login.html](Login.html) | Button |
| Register Button | [Register.html](Register.html) | Button |

---

### 5.2 Guest - Chi Tiết Mượn (Thông tin Sách)
**File**: [Guest/BorrowDetail.html](Guest/BorrowDetail.html)  
**Mục đích**: Xem thông tin sách (không thể mượn trực tiếp)

**Navigation**:
- **Breadcrumb**: Home > Sách > Chi Tiết
- **Back Button**: Quay lại [Guest/Guest.html](Guest/Guest.html)
- **Login to Borrow**: Link tới [Login.html](Login.html)
- **Register**: Link tới [Register.html](Register.html)

---

## 🗺️ COMPREHENSIVE NAVIGATION MATRIX

```
START
  ├─ Login.html
  │    ├─ Valid → Admin/Overview.html
  │    ├─ Valid → Librarian/Overviewhtml.html
  │    ├─ Valid → Member/Overview.html
  │    ├─ Valid → Guest/Guest.html
  │    ├─ Register link → Register.html
  │    └─ Forgot Password link → ForgotPassword.html
  │
  ├─ Register.html
  │    └─ Back → Login.html
  │
  └─ ForgotPassword.html
       └─ Back → Login.html

ADMIN ROLE
  └─ Admin/Overview.html (Hub)
       ├─ → Admin/ManageUser.html
       │    ├─ → Admin/AddUser.html
       │    └─ ← Back
       ├─ → Admin/ManageBook.html
       │    ├─ → Admin/AddBook.html
       │    └─ ← Back
       ├─ → Reports Menu
       │    ├─ → Admin/ReportBorrow.html
       │    ├─ → Admin/ReportCategory.html
       │    ├─ → Admin/ReportLate.html
       │    └─ → Admin/ReportTopBook.html
       └─ Logout → Login.html

LIBRARIAN ROLE
  └─ Librarian/Overviewhtml.html (Hub)
       ├─ → Librarian/BorrowingBooks.html
       │    └─ → Librarian/CheckinCard.html
       │         └─ → Librarian/CheckinDetail.html
       ├─ → Librarian/Returning.html
       │    └─ → Librarian/CheckinCard.html
       ├─ → Librarian/ManageBooks.html
       │    └─ → Librarian/AddBook.html
       ├─ → Librarian/ManageUser.html
       │    └─ → Librarian/AddUser.html
       ├─ → Reports Menu (4 pages)
       └─ Logout → Login.html

MEMBER ROLE
  └─ Member/Overview.html (Hub)
       ├─ → Member/MyBook.html
       │    └─ → Member/BookDetail.html
       ├─ → Member/SearchBook.html
       │    └─ → Member/BookDetail.html
       │         ├─ Borrow → Member/BorrowDetail.html
       │         └─ Return → Update
       ├─ → Member/BorrowDetail.html
       ├─ → Member/History.html
       └─ → Member/Profile.html
            └─ Logout → Login.html

GUEST ROLE
  └─ Guest/Guest.html (Limited Hub)
       ├─ → Guest/BorrowDetail.html
       │    ├─ Login link → Login.html
       │    └─ Register link → Register.html
       ├─ Login Button → Login.html
       └─ Register Button → Register.html
```

---

## 📋 DANH SÁCH HTML FILES CẦN UPDATE

### ✅ Files Hiện Tại (21 files)

**Authentication (3)**:
- [x] [Login.html](Login.html) - Cần thêm navigation links
- [x] [Register.html](Register.html) - Cần thêm navigation links  
- [x] [ForgotPassword.html](ForgotPassword.html) - Cần thêm navigation links

**Admin (9)**:
- [x] [Admin/Overview.html](Admin/Overview.html) - Tab navigation
- [x] [Admin/ManageUser.html](Admin/ManageUser.html) - Back link, Add link
- [x] [Admin/ManageBook.html](Admin/ManageBook.html) - Back link, Add link
- [x] [Admin/AddUser.html](Admin/AddUser.html) - Breadcrumb, Back link
- [x] [Admin/AddBook.html](Admin/AddBook.html) - Breadcrumb, Back link
- [x] [Admin/ReportBorrow.html](Admin/ReportBorrow.html) - Breadcrumb, Back link
- [x] [Admin/ReportCategory.html](Admin/ReportCategory.html) - Breadcrumb, Back link
- [x] [Admin/ReportLate.html](Admin/ReportLate.html) - Breadcrumb, Back link
- [x] [Admin/ReportTopBook.html](Admin/ReportTopBook.html) - Breadcrumb, Back link

**Librarian (14)**:
- [x] [Librarian/Overviewhtml.html](Librarian/Overviewhtml.html) - Tab navigation ⚠️ (Typo: Overviewhtml → Overview)
- [x] [Librarian/BorrowingBooks.html](Librarian/BorrowingBooks.html) - Back link
- [x] [Librarian/Returning.html](Librarian/Returning.html) - Back link
- [x] [Librarian/CheckinCard.html](Librarian/CheckinCard.html) - Back link, Details link
- [x] [Librarian/CheckinDetail.html](Librarian/CheckinDetail.html) - Breadcrumb, Back link
- [x] [Librarian/AddBook.html](Librarian/AddBook.html) - Breadcrumb, Back link
- [x] [Librarian/ManageBooks.html](Librarian/ManageBooks.html) - Back link, Add link
- [x] [Librarian/AddUser.html](Librarian/AddUser.html) - Breadcrumb, Back link
- [x] [Librarian/ManageUser.html](Librarian/ManageUser.html) - Back link, Add link
- [x] [Librarian/ReportBorrow.html](Librarian/ReportBorrow.html) - Breadcrumb, Back link
- [x] [Librarian/ReportCategory.html](Librarian/ReportCategory.html) - Breadcrumb, Back link
- [x] [Librarian/ReportLate.html](Librarian/ReportLate.html) - Breadcrumb, Back link
- [x] [Librarian/ReportTopBook.html](Librarian/ReportTopBook.html) - Breadcrumb, Back link

**Member (7)**:
- [x] [Member/Overview.html](Member/Overview.html) - Tab navigation
- [x] [Member/MyBook.html](Member/MyBook.html) - Back link, Details link
- [x] [Member/SearchBook.html](Member/SearchBook.html) - Back link, Details link
- [x] [Member/BookDetail.html](Member/BookDetail.html) - Breadcrumb, Back link
- [x] [Member/BorrowDetail.html](Member/BorrowDetail.html) - Back link
- [x] [Member/History.html](Member/History.html) - Back link
- [x] [Member/Profile.html](Member/Profile.html) - Back link

**Guest (2)**:
- [x] [Guest/Guest.html](Guest/Guest.html) - Login/Register links
- [x] [Guest/BorrowDetail.html](Guest/BorrowDetail.html) - Back link, Login link

---

## 🎯 NAVIGATION PATTERNS TO IMPLEMENT

### Pattern 1: Logout from Any Page
```html
<!-- Trong header của mỗi dashboard -->
<a href="/logout" class="logout-btn">Logout</a>
<!-- Điều hướng tới Login.html -->
```

### Pattern 2: Breadcrumb Navigation
```html
<!-- Ví dụ: Dashboard > Quản lý User > Thêm User -->
<nav class="breadcrumb">
    <a href="/admin">Dashboard</a> >
    <a href="/admin/manage-user">Quản lý User</a> >
    <span>Thêm User</span>
</nav>
```

### Pattern 3: Tab Navigation (Dashboard Hub)
```html
<!-- Ví dụ: Admin Overview tabs -->
<div class="tabs">
    <a href="#" class="tab active">Dashboard</a>
    <a href="/admin/manage-user" class="tab">Quản lý User</a>
    <a href="/admin/manage-book" class="tab">Quản lý Sách</a>
    <a href="/admin/add-book" class="tab">Thêm Sách</a>
    <!-- ... -->
</div>
```

### Pattern 4: Action Buttons
```html
<!-- Back Button -->
<button onclick="history.back()" class="btn-secondary">← Quay lại</button>

<!-- Link Button -->
<a href="/target-page" class="btn-primary">Hành động</a>

<!-- Form Submit -->
<button type="submit" class="btn-primary">Lưu</button>
<button type="reset" class="btn-secondary">Hủy</button>
```

### Pattern 5: Modal Navigation (Optional)
```html
<!-- Chỉnh sửa trong modal -->
<button class="edit-btn" data-modal="edit-user">Chỉnh sửa</button>

<!-- Modal close → Quay lại trang hiện tại -->
<button class="close-modal" onclick="closeModal()">Đóng</button>
```

---

## 🔄 NAVIGATION STATE MANAGEMENT

### Session Management
- Session phải track role của user
- Chuyển hướng tự động nếu session hết (→ Login.html)
- Prevent direct access nếu không có quyền

### URL Structure (Recommended)
```
/auth/login
/auth/register
/auth/forgot-password
/admin/dashboard
/admin/manage-user
/admin/manage-book
/librarian/dashboard
/member/dashboard
/guest
```

### Back Button Logic
```javascript
// Simple: history.back()
// Advanced: Track navigation stack
// Fallback: Redirect to dashboard
```

---

## 📝 IMPLEMENTATION CHECKLIST

### Phase 1: Header/Navigation Component (Mỗi role)
- [ ] Add header with logo
- [ ] Add navigation menu/tabs
- [ ] Add logout button
- [ ] Add profile icon
- [ ] Add breadcrumb (nếu cần)

### Phase 2: Link Implementation
- [ ] Update mỗi page với correct links
- [ ] Kiểm tra tất cả links hoạt động
- [ ] Add back buttons
- [ ] Add next/previous buttons (nếu có)

### Phase 3: Breadcrumb Integration
- [ ] Add breadcrumb component
- [ ] Cập nhật structure cho tất cả pages
- [ ] Test breadcrumb navigation

### Phase 4: Session & Security
- [ ] Add session checking
- [ ] Implement automatic logout
- [ ] Redirect unauthorized access
- [ ] Add user info display

### Phase 5: Testing
- [ ] Test mỗi navigation path
- [ ] Kiểm tra mobile responsiveness
- [ ] Test logout functionality
- [ ] Verify role-based access

---

## 🚀 RECOMMENDED IMPLEMENTATION ORDER

1. **Step 1**: Fix Librarian overview file (Overviewhtml.html → Overview.html)
2. **Step 2**: Create reusable Header/Navigation component
3. **Step 3**: Create Breadcrumb component
4. **Step 4**: Update Authentication pages (Login, Register, ForgotPassword)
5. **Step 5**: Update Admin pages (Overview first, then others)
6. **Step 6**: Update Librarian pages
7. **Step 7**: Update Member pages
8. **Step 8**: Update Guest pages
9. **Step 9**: Test all navigation flows
10. **Step 10**: Add session management & security

---

## 📊 SUMMARY STATISTICS

- **Total HTML Pages**: 21 pages
- **Total Navigation Paths**: 50+ unique paths
- **Roles Covered**: 4 (Admin, Librarian, Member, Guest)
- **Authentication Pages**: 3
- **Dashboard Hubs**: 4
- **Management Pages**: 12
- **Report Pages**: 8
- **Detail Pages**: 4

---

**Cuối cùng**: Document này cung cấp roadmap chi tiết cho việc implement comprehensive navigation system cho Library Management System. Hãy bắt đầu từ Phase 1 và follow theo thứ tự để đảm bảo consistency và completeness.
