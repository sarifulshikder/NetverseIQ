from decimal import Decimal
"""RADIUS Plugin — SQLAlchemy Models (FreeRADIUS Schema)"""
from datetime import datetime
from sqlalchemy import Numeric, String, Boolean, DateTime, Text, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional


def register_models(Base):
    """Register RADIUS models with the shared SQLAlchemy Base."""

    class RadCheck(Base):
        __tablename__ = "radcheck"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        username: Mapped[str] = mapped_column(String(64), index=True)
        attribute: Mapped[str] = mapped_column(String(64))
        op: Mapped[str] = mapped_column(String(2), default="==")
        value: Mapped[str] = mapped_column(String(253))

    class RadReply(Base):
        __tablename__ = "radreply"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        username: Mapped[str] = mapped_column(String(64), index=True)
        attribute: Mapped[str] = mapped_column(String(64))
        op: Mapped[str] = mapped_column(String(2), default="=")
        value: Mapped[str] = mapped_column(String(253))

    class RadUserGroup(Base):
        __tablename__ = "radusergroup"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        username: Mapped[str] = mapped_column(String(64), index=True)
        groupname: Mapped[str] = mapped_column(String(64), index=True)
        priority: Mapped[int] = mapped_column(Integer, default=1)

    class RadGroupCheck(Base):
        __tablename__ = "radgroupcheck"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        groupname: Mapped[str] = mapped_column(String(64), index=True)
        attribute: Mapped[str] = mapped_column(String(64))
        op: Mapped[str] = mapped_column(String(2), default="==")
        value: Mapped[str] = mapped_column(String(253))

    class RadGroupReply(Base):
        __tablename__ = "radgroupreply"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        groupname: Mapped[str] = mapped_column(String(64), index=True)
        attribute: Mapped[str] = mapped_column(String(64))
        op: Mapped[str] = mapped_column(String(2), default="=")
        value: Mapped[str] = mapped_column(String(253))

    class RadAcct(Base):
        __tablename__ = "radacct"
        radacctid: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
        acctsessionid: Mapped[str] = mapped_column(String(64), index=True)
        acctuniqueid: Mapped[str] = mapped_column(String(32), unique=True)
        username: Mapped[str] = mapped_column(String(64), index=True)
        groupname: Mapped[str] = mapped_column(String(64), default="")
        realm: Mapped[str] = mapped_column(String(64), default="")
        nasipaddress: Mapped[str] = mapped_column(String(15), index=True)
        nasportid: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
        nasporttype: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        acctstarttime: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        acctupdatetime: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        acctstoptime: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
        acctinterval: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        acctsessiontime: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        acctauthentic: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        connectinfo_start: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
        connectinfo_stop: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
        acctinputoctets: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
        acctoutputoctets: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
        calledstationid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
        callingstationid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
        acctterminatecause: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        servicetype: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        framedprotocol: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
        framedipaddress: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)

    class Nas(Base):
        __tablename__ = "nas"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        nasname: Mapped[str] = mapped_column(String(128), index=True)
        shortname: Mapped[str] = mapped_column(String(32))
        type: Mapped[str] = mapped_column(String(30), default="other")
        ports: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        secret: Mapped[str] = mapped_column(String(60))
        server: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
        community: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
        description: Mapped[Optional[str]] = mapped_column(String(200), default="RADIUS Client")

    return {
        "RadCheck": RadCheck,
        "RadReply": RadReply,
        "RadUserGroup": RadUserGroup,
        "RadGroupCheck": RadGroupCheck,
        "RadGroupReply": RadGroupReply,
        "RadAcct": RadAcct,
        "Nas": Nas
    }
