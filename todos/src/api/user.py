from fastapi import Depends, HTTPException, Body, APIRouter, BackgroundTasks

from cache import redis_client
from database.orm import User
from database.repository import UserRepository
from schema.request import SignUpRequest, LogInRequest, CreateOTPRequest, VerifyOTPRequest
from schema.response import UserSchema, JWTResponse
from security import get_access_token
from service.user import UserService

router = APIRouter(prefix="/users")

@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
        req_body: SignUpRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends()
) -> UserSchema:

    # 1. body 에서 온 password -> 암호화 bcrypt
    hashed_password: str = user_service.hash_password(
        plain_password = req_body.password
    )

    # 2. 암호화 된 password 와 입력받은 username orm 객채화
    user: User = User.create(
        username = req_body.username,
        hashed_password = hashed_password
    )

    # 3. orm 객채를 DB에 저장
    user: User = user_repo.save_user(user = user)

    return UserSchema.from_orm(user)

@router.post("/log-in")
def user_log_in_handler(
        req_body: LogInRequest,
        user_repo: UserRepository = Depends(),
        user_service: UserService = Depends()
):
    # 입력 받은 username 으로 조회
    user: User | None = user_repo.get_user_by_username(username= req_body.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 조회 성공시 password 비교
    verified: bool = user_service.verify_password(
        plain_password= req_body.password,
        hashed_password= user.password
    )
    if not verified:
        raise HTTPException(status_code=401, detail="Not Authorized")

    # 비교 True
    access_token: str = user_service.create_jwt(username= user.username)
    return JWTResponse(access_token= access_token)

# otp 프로세스
# 회원가입 이후 이메일 인증을 한다
@router.post("/email/otp")
def create_otp_handler(
        req_body: CreateOTPRequest,
        user_service: UserService = Depends(),
        # _ 으로 변수명을 설정하면 메서드 내에 호출이 없더라도 Depends가 실행됨
        # temp : str = Depends(get_access_token) 이렇게 설정하면 메서드 내에 호출이 없어 Depends 실행 안됨
        _: str = Depends(get_access_token)
):
    # 1. access token 을 통해 정상적인 로그인 사용자인지 확인
    # 해당 메서드는 없으면 오지도 못함

    # 2. otp 생성 4자릿수 난수
    otp: int = user_service.create_otp()

    # 3. redis 3분동안 저장
    redis_client.set(
        name= req_body.email,
        value= otp
    )
    redis_client.expire(
        name= req_body.email,
        time= 3 * 60
    )

    return {"otp": otp}

@router.post("/email/otp/verify")
def verity_otp_handler(
        req_body: VerifyOTPRequest,
        background_tasks: BackgroundTasks,
        access_token: str = Depends(get_access_token),
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends()
) -> UserSchema:

    # 2. request body 의 email 의 값으로 redis 조회 주의: redis의 반환 값은 전부 str 임
    otp: str | None = redis_client.get(name= req_body.email)
    if not otp:
        raise HTTPException(status_code=400, detail="Bad request")

    if int(otp) != req_body.otp:
        raise HTTPException(status_code=400, detail="Bad request")

    # 3. otp 인증완료
    username = user_service.decode_jwt(access_token= access_token)
    user: User | None = user_repo.get_user_by_username(username= username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 사용자 이메일로 인증완료 메세지 날림
    # 해당 task 성공 여부를 떠나서 그냥 하는것 => background task 로 처리
    background_tasks.add_task(
        user_service.send_email_to_user,
        "test@naver.com"
    )

    return UserSchema.from_orm(user)