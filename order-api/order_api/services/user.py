from order_api.config import envs

import requests


def get_user_by_id(id_user: int):
    user_url = f"{envs.USER_API_ADDRESS}/v1/{id_user}"
    response = requests.get(url=user_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Falha ao recuperar usuário")
