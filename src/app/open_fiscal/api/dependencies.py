from src.app.open_fiscal.repository.fiscal import FiscalRepository
from src.app.open_fiscal.service.fiscal import FiscalService
from src.core.dependencies.fiscal import fiscal_data_manager

fiscal_repository = FiscalRepository(fiscal_data_manager)
fiscal_service = FiscalService(fiscal_repository)
