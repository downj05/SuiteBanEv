# models.py
from sqlalchemy import Column, Integer, BIGINT, String, ForeignKey, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from time import time as timestamp

Base = declarative_base()

# helper function
def get_matching_records(session, model, **conditions):
    query = session.query(model).filter(
        or_(*[getattr(model, field) == value for field, value in conditions.items()])
    )
    return query.all()

class Ban(Base):
    __tablename__ = 'bans'

    id = Column(Integer, primary_key=True)
    steam64 = Column(BIGINT)
    hwid1 = Column(String(64), nullable=True)
    hwid2 = Column(String(64), nullable=True)
    hwid3 = Column(String(64), nullable=True)
    ip = Column(String(64), nullable=True)
    time = Column(Integer, default=timestamp())
    duration = Column(Integer, default=-1)
    reason = Column(String(256), nullable=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    server = relationship("Server", back_populates="bans")
    def is_permanent(self):
        return self.duration <= 0
    
    def is_expired(self):
        return self.time + self.duration <= timestamp()
    
    @classmethod
    def get_matching_bans(cls, session, steam64, hwid1, hwid2, hwid3, ip, server_id=None):
        """Get all bans matching the given criteria. If server_id is None, all servers are searched. Otherwise, only bans from the given server are searched."""
        if server_id == None:
            return get_matching_records(session, cls, steam64=steam64, hwid1=hwid1, hwid2=hwid2, hwid3=hwid3, ip=ip)
        return get_matching_records(session, cls, steam64=steam64, hwid1=hwid1, hwid2=hwid2, hwid3=hwid3, ip=ip, server_id=server_id)

    def __repr__(self):
        return f"<Ban(steam64={self.steam64}, hwid={self.hwid1, self.hwid2, self.hwid3}, ip={self.ip}, reason={self.reason})>"
    
class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    ip = Column(String(64))
    port = Column(Integer)
    bans = relationship("Ban", back_populates="server")
    def __repr__(self):
        return f"<Server(name={self.name}, ip={self.ip}, port={self.port})>"
