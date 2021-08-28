from order_api.app import start_application


def start():
    print(__package__, " started.")


if __name__ == "__main__":
    start_application()
    # uvicorn.run(app, host="0.0.0.0", port=7000)
