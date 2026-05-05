import pytest
import uuid
from sqlalchemy import Column, String
from models.base import Base

def test_base_model_attributes():
    class DummyModel(Base):
        __tablename__ = "dummy_table"
        name = Column(String)

    instance = DummyModel(name="test")
    
    mapper = DummyModel.__mapper__
    assert "id" in mapper.columns
    assert "created_at" in mapper.columns
    assert "updated_at" in mapper.columns
    assert "name" in mapper.columns

    id_column = mapper.columns["id"]
    assert id_column.primary_key is True
    # Test that default arg is a callable named uuid4
    assert callable(id_column.default.arg)
    assert id_column.default.arg.__name__ == "uuid4"
    
    assert issubclass(DummyModel, Base)
