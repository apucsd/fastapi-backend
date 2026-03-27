from app.utils.exceptions import AppException
from app.models.user import User
from app.utils.data import get_update_data
from app.utils.query_builder import QueryBuilder


class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, user):
        existing = self.db.query(User).filter(User.email == user.email).first()
        if existing:
            raise AppException(status_code=400, message="Email already registered")

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email):
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self, user_id, updated_user):

        existing = self.get_user_by_id(user_id)
        if not existing:
            raise AppException(status_code=404, message="User not found")

        update_data = get_update_data(updated_user)

        for key, value in update_data.items():
            if key != "id":
                setattr(existing, key, value)

        self.db.commit()
        self.db.refresh(existing)
        return existing

    def get_all_users(self, query_params: dict):
        base_query = self.db.query(User)
        
        builder = QueryBuilder(User, base_query, query_params)
        result = builder.search(["name", "email"]).filter().sort().paginate().fields(['id', 'name', 'email']).execute(self.db)
        return result
