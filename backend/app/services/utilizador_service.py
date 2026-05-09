from __future__ import annotations

from fastapi import HTTPException, status

from app.schemas.common import DataResponse, PaginatedResponse
from app.schemas.utilizador import UtilizadorCreate, UtilizadorResponse
from app.services.auth_service import _MOCK_USERS
from app.services.loja_service import get_nome as _get_loja_nome
from app.core.security import hash_password

_next_id = max((u["id"] for u in _MOCK_USERS), default=0) + 1


def listar_utilizadores(
    page: int,
    page_size: int,
) -> PaginatedResponse[UtilizadorResponse]:
    total = len(_MOCK_USERS)
    pages = max(1, -(-total // page_size))
    start = (page - 1) * page_size

    itens = _MOCK_USERS[start : start + page_size]

    return PaginatedResponse[UtilizadorResponse](
        data=[UtilizadorResponse(**u) for u in itens],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def criar_utilizador(body: UtilizadorCreate) -> DataResponse[UtilizadorResponse]:
    global _next_id
    
    email_lower = body.email.lower()
    if any(u["email"].lower() == email_lower for u in _MOCK_USERS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": "Email já registado no sistema.", "code": "DUPLICATE_ENTRY"},
        )
        
    novo = {
        "id": _next_id,
        "nome": body.nome,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "perfil": body.perfil,
        "loja_id": body.loja_id,
        "loja_nome": _get_loja_nome(body.loja_id) if body.loja_id else None,
        "ativo": body.ativo,
    }
    _MOCK_USERS.append(novo)
    _next_id += 1
    
    return DataResponse[UtilizadorResponse](
        data=UtilizadorResponse(**novo),
        message="Utilizador criado com sucesso."
    )