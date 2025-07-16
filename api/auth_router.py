from fastapi import Depends, APIRouter
from fastapi_jwt_auth import AuthJWT
from model.schema import LoginRequest, TokenResponse, SignupRequest
from service.auth_service import login, signup
from model.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login_user(request: LoginRequest,
               db: Session = Depends(get_db),
               Authorize: AuthJWT = Depends()):
    return login(request, db, Authorize)


@router.post("/signup")
def signup_user(request: SignupRequest, db: Session = Depends(get_db)):
    signup(request, db)
    return {"message": "회원가입 성공"}


from fastapi import Header
from service.auth_service import refresh_token


@router.post("/refresh")
def refresh_access_token(authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    new_access_token = refresh_token(authorize, db)
    return {"access_token": new_access_token}


from service.auth_service import logout

@router.post("/logout")
def logout_user(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    logout(Authorize, db)
    return {"message": "로그아웃 완료"}

