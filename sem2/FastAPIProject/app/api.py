from fastapi import FastAPI, HTTPException, Response, Depends, Request
from sqlalchemy import select
import jwt

from app.models import UserModel
from app.schemas import UserEmPasSchema, EncodeResponse, Data
from app.cruds import SessionDep
from app.core import security, config
from app.services import Coding


app = FastAPI()

@app.post("/sign-up/", tags=["Регистрация нового пользователя"], summary="Регистрация нового пользователя",
          description="Создает нового пользователя и возвращает токен доступа.")
async def sign_up(data: UserEmPasSchema, session: SessionDep):
    # Проверяем, существует ли уже пользователь с таким email
    query = select(UserModel).where(UserModel.email == data.email)
    result = await session.execute(query)
    existing_user = result.scalars().first()

    # Возбуждаем исключение в случае, когда пользователь с таким email уже зарегистрирован
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже зарегистрирован.")

    # Добавляем нового пользователя
    new_user = UserModel(
        email=data.email,
        password=data.password,
    )
    session.add(new_user)
    await session.commit()

    # Генерируем токен для нового пользователя с помощью AuthX
    access_token = security.create_access_token(uid=str(new_user.id))

    return {"message": "Добавлен новый пользователь",
            "id": new_user.id, "email": new_user.email, "token": access_token}


@app.post("/login/", tags=["Вход в систему"], summary="Авторизация пользователя",
          description="Авторизует пользователя и возвращает токен доступа.")
async def login(data: UserEmPasSchema, session: SessionDep, response: Response):
    # Проверяем, существует ли уже пользователь с таким email и верен ли его пароль
    query = select(UserModel).where((UserModel.email == data.email) & (UserModel.password == data.password))
    result = await session.execute(query)
    existing_user = result.scalars().first()

    # Возбуждаем исключение в случае, когда пользователь с таким email не зарегистрирован
    if not existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email не зарегистрирован.")

    # Генерируем новый токен для пользователя с помощью AuthX
    access_token = security.create_access_token(uid=str(existing_user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)

    return {"message": "Пользователь авторизован. Сгенерирован новый токен для пользователя",
            "id": existing_user.id, "email": existing_user.email, "token": access_token}


@app.get("/users/me/", tags=["Получение информации о текущем пользователе"], summary="Получение данных пользователя",
         description="Возвращает данные текущего авторизованного пользователя.")
async def user_data(request: Request, session: SessionDep):
    # Извлечение токена из cookie
    access_token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)

    if not access_token:
        raise HTTPException(status_code=401, detail="Токен доступа отсутствует: пользователь не авторизован")

    try:
        # Декодирование токена
        decoded_token = jwt.decode(access_token, config.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("sub")

        # Поиск пользователя в базе данных
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден.")

        return {"id": user.id, "email": user.email}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")


@app.post("/encode", response_model=EncodeResponse, dependencies=[Depends(security.access_token_required)],
          tags=["Манипуляции с данными"], summary="Кодирование данных",
          description="Кодирует и шифрует данные с использованием алгоритма Хаффмана.")
def encode(data: Data):
    huffman_coding = Coding()
    return huffman_coding.compress_and_encrypt(data)


@app.post("/decode", dependencies=[Depends(security.access_token_required)],
          tags=["Манипуляции с данными"], summary="Декодирование данных",
          description="Декодирует и расшифровывает данные с использованием алгоритма Хаффмана.")
def decode(data: EncodeResponse):
    huffman_coding = Coding()
    return huffman_coding.decrypt_and_decompress(data)
