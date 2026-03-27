from sqlalchemy import or_, desc, asc, func
from sqlalchemy.orm import Query
from typing import List, Type, Any

class QueryBuilder:
    def __init__(self, model: Type[Any], query: Query, params: dict):
        self.model = model
        self.query = query               
        self.params = params 
        self.primary_key = "id"

    def search(self, fields: List[str]):
        search_term = self.params.get("search_term")
        if search_term:
            conditions = []
            for field in fields:
                attr = getattr(self.model, field)
                conditions.append(attr.ilike(f"%{search_term}%"))
            self.query = self.query.filter(or_(*conditions))
        return self

    
    def filter(self):
        exclude_fields = ['search_term', 'sort', 'limit', 'page', 'fields']
        filters = {k: v for k, v in self.params.items() if k not in exclude_fields and v is not None}
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                attr = getattr(self.model, key)
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False

                self.query = self.query.filter(attr == value)
        return self

    def sort(self):
        sort_param = self.params.get("sort", "-created_at")
        sort_fields = sort_param.split(",")
        
        for field in sort_fields:
            if field.startswith("-"):
                name = field[1:]
                if hasattr(self.model, name):
                    self.query = self.query.order_by(desc(getattr(self.model, name)))
            else:
                if hasattr(self.model, field):
                    self.query = self.query.order_by(asc(getattr(self.model, field)))
        return self

    def paginate(self):
        page = int(self.params.get("page", 1))
        limit = int(self.params.get("limit", 10))
        skip = (page - 1) * limit
        
        self.query = self.query.offset(skip).limit(limit)
        return self
    
    def fields(self, fields_list: List[str] = None):
        fields_param = self.params.get("fields")
        
        if fields_list:
            requested_fields = fields_list
        elif fields_param:
            requested_fields = fields_param.split(",")
        else:
            return self 

        entities = []
        for field in requested_fields:
            if hasattr(self.model, field):
                entities.append(getattr(self.model, field))
        
        if entities:
            self.query = self.query.with_entities(*entities)
            
        return self

    
    def execute(self, db):
        total = db.query(func.count(getattr(self.model, self.primary_key))).filter(*self.query.whereclause).scalar() if self.query.whereclause is not None else db.query(self.model).count()        
        results = self.query.all()
        if results and hasattr(results[0], "_asdict"):
            results = [row._asdict() for row in results]

        
        page = int(self.params.get("page", 1))
        limit = int(self.params.get("limit", 10))
        
        return {
            "data": results,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
