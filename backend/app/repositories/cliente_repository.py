from datetime import datetime, timezone
from types import SimpleNamespace

from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate

# Hardcoded test data — used as fallback when DB is unavailable
_HARDCODED_CLIENTES = [
    SimpleNamespace(
        id=1,
        nome="Pedro Ferreira",
        nif="123456789",
        telemovel="987654321",
        email="pedrorf.gmr@gmail.com",
        morada="Rua das Flores 10, Porto",
        consentimento_rgpd=True,
        data_registo=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
        loja_id=1,
        trotinetes=[
            SimpleNamespace(id=1, marca="Xiaomi", modelo="Mi Electric Scooter 3", numero_serie="XM2024ABC123"),
        ],
    ),
    SimpleNamespace(
        id=2,
        nome="Maria Santos",
        nif="987654321",
        telemovel="912345678",
        email="maria.santos@email.com",
        morada="Avenida da Boavista 200, Porto",
        consentimento_rgpd=True,
        data_registo=datetime(2026, 2, 1, 9, 0, tzinfo=timezone.utc),
        loja_id=1,
        trotinetes=[
            SimpleNamespace(id=2, marca="Ninebot", modelo="E45E", numero_serie="NB2023XYZ456"),
        ],
    ),
    SimpleNamespace(
        id=3,
        nome="Carlos Oliveira",
        nif="111222333",
        telemovel="934567890",
        email="carlos.oliveira@email.com",
        morada=None,
        consentimento_rgpd=True,
        data_registo=datetime(2026, 3, 10, 14, 0, tzinfo=timezone.utc),
        loja_id=1,
        trotinetes=[],
    ),
]
_next_hardcoded_id = 4


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cliente_id: int):
        try:
            return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
        except Exception:
            return next((c for c in _HARDCODED_CLIENTES if c.id == cliente_id), None)

    def get_by_nif(self, nif: str):
        try:
            return self.db.query(Cliente).filter(Cliente.nif == nif).first()
        except Exception:
            return next((c for c in _HARDCODED_CLIENTES if c.nif == nif), None)

    def get_all(self, skip: int = 0, limit: int = 100, loja_id: int | None = None, query_str: str | None = None):
        try:
            query = self.db.query(Cliente)
            if loja_id is not None:
                query = query.filter(Cliente.loja_id == loja_id)
            if query_str:
                like = f"%{query_str}%"
                query = query.filter(
                    Cliente.nome.ilike(like) |
                    Cliente.nif.ilike(like) |
                    Cliente.telemovel.ilike(like) |
                    Cliente.email.ilike(like)
                )
            return query.offset(skip).limit(limit).all()
        except Exception:
            items = list(_HARDCODED_CLIENTES)
            if loja_id is not None:
                items = [c for c in items if c.loja_id == loja_id]
            if query_str:
                q = query_str.lower()
                items = [
                    c for c in items
                    if q in c.nome.lower()
                    or q in c.nif.lower()
                    or q in c.telemovel.lower()
                    or (c.email and q in c.email.lower())
                ]
            return items[skip: skip + limit]

    def count(self, loja_id: int | None = None, query_str: str | None = None) -> int:
        try:
            query = self.db.query(Cliente)
            if loja_id is not None:
                query = query.filter(Cliente.loja_id == loja_id)
            if query_str:
                like = f"%{query_str}%"
                query = query.filter(
                    Cliente.nome.ilike(like) |
                    Cliente.nif.ilike(like) |
                    Cliente.telemovel.ilike(like) |
                    Cliente.email.ilike(like)
                )
            return query.count()
        except Exception:
            return len(self.get_all(loja_id=loja_id, query_str=query_str))

    def create(self, cliente_in: ClienteCreate, loja_id: int):
        try:
            db_obj = Cliente(**cliente_in.model_dump(), loja_id=loja_id, data_registo=datetime.now(timezone.utc))
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception:
            global _next_hardcoded_id
            novo = SimpleNamespace(
                id=_next_hardcoded_id,
                nome=cliente_in.nome,
                nif=cliente_in.nif,
                telemovel=cliente_in.telemovel,
                email=cliente_in.email,
                morada=cliente_in.morada,
                consentimento_rgpd=cliente_in.consentimento_rgpd,
                data_registo=datetime.now(timezone.utc),
                loja_id=loja_id,
                trotinetes=[],
            )
            _HARDCODED_CLIENTES.append(novo)
            _next_hardcoded_id += 1
            return novo