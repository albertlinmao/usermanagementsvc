with open("src/models/schemas.py", "r") as f:
    content = f.read()
content = content.replace("admin_user_id: UUID", "admin_user_id: Optional[UUID] = None")
with open("src/models/schemas.py", "w") as f:
    f.write(content)
