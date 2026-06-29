from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "companies"

    corp_code: Mapped[str] = mapped_column(String(8), primary_key=True)
    stock_code: Mapped[str] = mapped_column(String(6), nullable=False, unique=True, index=True)
    corp_name: Mapped[str] = mapped_column(String(200), nullable=False)
    market: Mapped[str | None] = mapped_column(String(10))
    sector: Mapped[str | None] = mapped_column(String(100), index=True)
    industry: Mapped[str | None] = mapped_column(String(150), index=True)
    dart_modify_date: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ScreeningRun(Base):
    __tablename__ = "screening_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sector: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(150))
    fiscal_year_end: Mapped[int] = mapped_column(nullable=False)
    history_years: Mapped[int] = mapped_column(nullable=False, default=5)
    fs_div_preference: Mapped[str] = mapped_column(String(3), nullable=False, default="CFS")
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    company_count: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(String)

    companies: Mapped[list["ScreeningRunCompany"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    financials: Mapped[list["CompanyFinancialsCalculated"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class ScreeningRunCompany(Base):
    __tablename__ = "screening_run_companies"

    screening_run_id: Mapped[int] = mapped_column(
        ForeignKey("screening_runs.id", ondelete="CASCADE"), primary_key=True
    )
    corp_code: Mapped[str] = mapped_column(ForeignKey("companies.corp_code"), primary_key=True)

    run: Mapped[ScreeningRun] = relationship(back_populates="companies")


class CompanyFinancialsCalculated(Base):
    __tablename__ = "company_financials_calculated"
    __table_args__ = (
        UniqueConstraint(
            "screening_run_id", "corp_code", "fiscal_year", "reprt_code", name="uq_cfc_run_corp_year_reprt"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    screening_run_id: Mapped[int] = mapped_column(ForeignKey("screening_runs.id", ondelete="CASCADE"), index=True)
    corp_code: Mapped[str] = mapped_column(ForeignKey("companies.corp_code"), index=True)
    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    reprt_code: Mapped[str] = mapped_column(String(5), nullable=False, default="11011")
    fs_div_used: Mapped[str | None] = mapped_column(String(3))

    revenue: Mapped[float | None] = mapped_column(Numeric)
    gross_profit: Mapped[float | None] = mapped_column(Numeric)
    operating_income: Mapped[float | None] = mapped_column(Numeric)
    net_income: Mapped[float | None] = mapped_column(Numeric)
    total_assets: Mapped[float | None] = mapped_column(Numeric)
    total_liabilities: Mapped[float | None] = mapped_column(Numeric)
    total_equity: Mapped[float | None] = mapped_column(Numeric)

    operating_cash_flow: Mapped[float | None] = mapped_column(Numeric)
    capex: Mapped[float | None] = mapped_column(Numeric)
    depreciation_amortization: Mapped[float | None] = mapped_column(Numeric)
    depreciation_source: Mapped[str | None] = mapped_column(String(20))
    free_cash_flow: Mapped[float | None] = mapped_column(Numeric)
    reinvestment_ratio_capex_da: Mapped[float | None] = mapped_column(Numeric)
    reinvestment_ratio_capex_ocf: Mapped[float | None] = mapped_column(Numeric)

    short_term_borrowings: Mapped[float | None] = mapped_column(Numeric)
    long_term_borrowings: Mapped[float | None] = mapped_column(Numeric)
    total_debt: Mapped[float | None] = mapped_column(Numeric)
    debt_to_equity: Mapped[float | None] = mapped_column(Numeric)
    equity_impaired: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_convertible_instruments: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    convertible_instruments_value: Mapped[float | None] = mapped_column(Numeric)

    revenue_growth_yoy: Mapped[float | None] = mapped_column(Numeric)
    gross_profit_growth_yoy: Mapped[float | None] = mapped_column(Numeric)
    operating_income_growth_yoy: Mapped[float | None] = mapped_column(Numeric)
    net_income_growth_yoy: Mapped[float | None] = mapped_column(Numeric)
    revenue_cagr_5y: Mapped[float | None] = mapped_column(Numeric)
    gross_profit_cagr_5y: Mapped[float | None] = mapped_column(Numeric)
    operating_income_cagr_5y: Mapped[float | None] = mapped_column(Numeric)
    net_income_cagr_5y: Mapped[float | None] = mapped_column(Numeric)

    gross_margin: Mapped[float | None] = mapped_column(Numeric)
    operating_margin: Mapped[float | None] = mapped_column(Numeric)
    net_margin: Mapped[float | None] = mapped_column(Numeric)
    gross_margin_change_yoy: Mapped[float | None] = mapped_column(Numeric)
    operating_margin_change_yoy: Mapped[float | None] = mapped_column(Numeric)
    net_margin_change_yoy: Mapped[float | None] = mapped_column(Numeric)

    # Shares / dilution
    shares_outstanding: Mapped[float | None] = mapped_column(Numeric)
    share_count_change_yoy: Mapped[float | None] = mapped_column(Numeric)

    # Window-level (5y) deltas, repeated on each year row
    gross_margin_change_5y: Mapped[float | None] = mapped_column(Numeric)
    operating_margin_change_5y: Mapped[float | None] = mapped_column(Numeric)
    net_margin_change_5y: Mapped[float | None] = mapped_column(Numeric)
    share_count_change_5y: Mapped[float | None] = mapped_column(Numeric)
    total_debt_change_5y: Mapped[float | None] = mapped_column(Numeric)

    # Three-pillar investment scorecard (0/1/2 per pillar, 0-6 overall)
    score_margin_growth: Mapped[int | None] = mapped_column(Integer)
    score_low_dilution: Mapped[int | None] = mapped_column(Integer)
    score_capital_efficiency: Mapped[int | None] = mapped_column(Integer)
    score_overall: Mapped[int | None] = mapped_column(Integer)

    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped[ScreeningRun] = relationship(back_populates="financials")


class DartApiCallLog(Base):
    __tablename__ = "dart_api_call_log"

    call_date: Mapped[date] = mapped_column(Date, primary_key=True)
    call_count: Mapped[int] = mapped_column(nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
