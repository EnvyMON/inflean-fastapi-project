from sqlalchemy.orm import declarative_base
from sqlalchemy import Boolean, Integer, String, Column

from schema.request import CreateToDoRequest

Base = declarative_base()

class ToDo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"ToDo(id = {self.id}, contents = {self.contents}, is_done = {self.is_done})"

    @classmethod
    def create(cls, request: CreateToDoRequest) -> "ToDo":
        return cls(
            contents= request.contents,
            is_done= request.is_done
        )

    def done(self):
        self.is_done = True
        return self

    def undone(self):
        self.is_done = False
        return self