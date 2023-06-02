import pydantic


class BaseModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid  # default forbid extra fields


if __name__ == "__main__":
    pass
