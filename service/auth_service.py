from fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException
from passlib.context import CryptContext
from model.user import User, RefreshToken
from sqlalchemy.orm import Session
from model.schema import LoginRequest, TokenResponse, SignupRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def get_password_hash(password):
    return pwd_context.hash(password)


def login(request: LoginRequest, db: Session, Authorize: AuthJWT) -> TokenResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)

    # RefreshToken 테이블 갱신
    existing = db.query(RefreshToken).filter(RefreshToken.email == user.email).first()
    if existing:
        existing.token = refresh_token
    else:
        db.add(RefreshToken(email=user.email, token=refresh_token))
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


from model.user import User, LevelEnum


def signup(request: SignupRequest, db: Session):
    # 중복 이메일 체크
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    new_user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        nickname=request.nickname,
        level=LevelEnum(request.level)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


from model.user import RefreshToken

def refresh_token(Authorize: AuthJWT, db: Session) -> str:
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Refresh token이 유효하지 않습니다.")

    current_user = Authorize.get_jwt_subject()
    stored_token = db.query(RefreshToken).filter(RefreshToken.email == current_user).first()

    # DB에 저장된 refresh token과 비교
    if not stored_token or stored_token.token != Authorize._token:
        raise HTTPException(status_code=401, detail="유효하지 않은 refresh token입니다.")

    # 새 access token 발급
    new_access_token = Authorize.create_access_token(subject=current_user)
    return new_access_token


def logout(authorize: AuthJWT, db: Session):
    try:
        authorize.jwt_refresh_token_required()
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token이 유효하지 않습니다.")

    current_user = authorize.get_jwt_subject()
    token_entry = db.query(RefreshToken).filter(RefreshToken.email == current_user).first()

    if token_entry:
        db.delete(token_entry)
        db.commit()
