from fastapi import FastAPI
from contextlib import asynccontextmanager


from core.models import Base
from core.views.user import router as user_router
from core.views.auth import router as auth_router
from core.views.post import router as post_router
from core.views.comment import router as comment_router
from core.settings.database import database_helper


@asynccontextmanager
async def lifespan(app:FastAPI):
    await database_helper.create_tables(Base)
    yield
    await database_helper.dispose()
        

app = FastAPI(
    title="SoloProjectFastAPI",
    version="0.1.1",
    lifespan=lifespan
)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(post_router)
app.include_router(comment_router)



@app.get("/")
async def home():
    return {"message": "hello"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)