from sqlalchemy import Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass

class ProductsEntity(Base):
    """
    A class to represent the Products table in the database.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True)
    jira_issues: Mapped["JiraIssuesEntity"] = relationship(back_populates="product")


class JiraIssuesEntity(Base):
    """
    A class to represent the JiraIssues table in the database.
    """

    __tablename__ = "jiraissues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_id: Mapped[int]= mapped_column(Integer, ForeignKey('products.id'))
    product: Mapped["ProductsEntity"] = relationship(back_populates="jira_issues")
    issue_key: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    project: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    issue_type: Mapped[str] = mapped_column(String, nullable=False)
    customer_escaped: Mapped[bool] = mapped_column(Boolean, nullable=False)
    date_created: Mapped[Date] = mapped_column(Date, nullable=False)
    last_updated: Mapped[Date] = mapped_column(Date, nullable=False)
