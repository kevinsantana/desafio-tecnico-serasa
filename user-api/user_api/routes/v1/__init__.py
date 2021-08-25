from math import ceil


def pagination(data: list, qtd: int, offset: int, total: int, url: str) -> dict:
    total = ceil(total / qtd)
    pagination = {
        "result": data,
        "pagination": {
            "next": "",
            "previous": "",
            "first": "",
            "last": "",
            "total": total,
        },
    }
    endpoint, params = url.split("?")
    _, _, *others = params.split("&")
    if len(data) == qtd and offset < total:
        next_params = "&".join([f"qtd={qtd}", f"offset={offset+1}", *others])
        pagination["pagination"]["next"] = f"{endpoint}?{next_params}"
    if offset > 1 and offset <= total:
        previous_parms = "&".join([f"qtd={qtd}", f"offset={offset-1}", *others])
        pagination["pagination"]["previous"] = f"{endpoint}?{previous_parms}"
    last_params = "&".join([f"qtd={qtd}", f"offset={total}", *others])
    first_params = "&".join([f"qtd={qtd}", "offset=1", *others])
    if offset > 1:
        pagination["pagination"]["first"] = f"{endpoint}?{first_params}"
    if offset < total:
        pagination["pagination"]["last"] = f"{endpoint}?{last_params}"
    return pagination
