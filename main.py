from server.match import Match
from utils import BaseModel


class Main(BaseModel):
    """
    """

    version: str = '1.0.0'
    name: str = 'GITCG'
    match: Match = Match()


if __name__ == '__main__':
    main = Main()
    print(main.json())
