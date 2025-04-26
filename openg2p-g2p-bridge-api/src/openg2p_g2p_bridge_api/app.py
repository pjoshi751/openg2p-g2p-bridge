# ruff: noqa: E402
import asyncio
import logging

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer as BaseInitializer
from openg2p_g2p_bridge_models.models import (
    AccountStatement,
    DisbursementEnvelope,
    DisbursementEnvelopeBatchStatus,
    Proof,
)

from .controllers import (
    AccountStatementController,
    DisbursementController,
    DisbursementEnvelopeController,
    DisbursementEnvelopeStatusController,
    DisbursementStatusController,
    proof_controller,
)
from .controllers.proof import proof_controller
from .services import (
    AccountStatementService,
    DisbursementEnvelopeService,
    DisbursementEnvelopeStatusService,
    DisbursementService,
    DisbursementStatusService,
)

_logger = logging.getLogger(_config.logging_default_logger_name)


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        super().initialize()
        # Remove incorrect router registration
        # self.app.include_router(proof_controller.router)
        
        # Initialize services and other controllers
        DisbursementEnvelopeService()
        DisbursementService()
        AccountStatementService()
        DisbursementStatusService()
        DisbursementEnvelopeStatusService()
        DisbursementEnvelopeController().post_init()
        DisbursementController().post_init()
        AccountStatementController().post_init()
        DisbursementStatusController().post_init()
        DisbursementEnvelopeStatusController().post_init()

    def migrate_database(self, args):
        super().migrate_database(args)

        async def migrate():
            _logger.info("Migrating database")
            await DisbursementEnvelope.create_migrate()
            await DisbursementEnvelopeBatchStatus.create_migrate()
            await AccountStatement.create_migrate()
            await Proof.create_migrate()

        asyncio.run(migrate())
