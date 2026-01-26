from pymongo import MongoClient



client = MongoClient("mongodb://localhost:27017/")
db = client["library_db"]

user_col = db["User"]

def get_next_user_id():
    last = user_col.find_one(sort=[("_id", -1)])
    return (last["_id"] + 1) if last else 1

def register_user(username, password, full_name, email):
    if user_col.find_one({"username": username}):
        return False, "Username đã tồn tại"

    new_user = {
        "_id": get_next_user_id(),
        "username": username,
        "user_password": password,
        "full_name": full_name,
        "email": email,
        "user_role": "USER",
        "is_active": True
    }

    user_col.insert_one(new_user)
    return True, "Đăng ký thành công"

