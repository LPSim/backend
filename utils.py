import pydantic


class BaseModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid  # default forbid extra fields


def get_instance_from_type_unions(types, args):
    """
    Get instance from type unions.
    """
    class TempClass(BaseModel):
        obj: types
    return TempClass(obj = args).obj


if __name__ == "__main__":
    pass
