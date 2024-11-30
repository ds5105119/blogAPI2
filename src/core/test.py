from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, insert, select
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
Base = declarative_base()


class User(Base):
    __tablename__ = "user_account"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)

    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


Base.metadata.create_all(engine)

with engine.connect() as conn:
    stmt = insert(User).values(
        [
            {"name": "spongebob", "fullname": "Spongebob Squarepants"},
            {"name": "abc", "fullname": "abc"},
        ]
    )
    result = conn.execute(stmt)
    conn.commit()


with engine.connect() as conn:
    stmt = select(User.fullname).where(User.name == "spongebobx")
    result = conn.execute(stmt)
    print(result.all())
