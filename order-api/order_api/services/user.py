import requests

from order_api.config import envs
from order_api.exceptions import ErrorDetails
from order_api.exceptions.order import UserNotFoundException


def get_user_by_id(id_user: int):
    user_url = f"{envs.USER_API_ADDRESS}/v1/user/{id_user}"
    response = requests.get(url=user_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise UserNotFoundException(
            status=404,
            error="Not Found",
            message="Usuário não encontrado",
            error_details=[
                ErrorDetails(
                    message=f"O usuário {id_user} não foi encontrado na base"
                ).to_dict()
            ],
        )
