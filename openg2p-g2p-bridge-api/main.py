#!/usr/bin/env python3

# ruff: noqa: I001

from openg2p_g2p_bridge_api.app import Initializer
from openg2p_fastapi_common.ping import PingInitializer
from openg2p_g2p_bridge_api.controllers import proof_controller

initializer = Initializer()
PingInitializer()

app = initializer.return_app()

app.include_router(proof_controller.router)

if __name__ == "__main__":
    initializer.main()
