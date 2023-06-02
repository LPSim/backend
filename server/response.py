from utils import BaseModel


class ResponseBase(BaseModel):
    pass


Responses = ResponseBase | ResponseBase
