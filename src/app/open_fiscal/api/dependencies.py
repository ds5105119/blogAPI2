from src.app.open_fiscal.model.fiscal import FiscalData
from src.app.open_fiscal.repository.fiscal import FiscalRepository
from src.app.open_fiscal.service.fiscal import FiscalService
from src.core.dependencies.data import fiscal_data_manager

fiscal_data = FiscalData(fiscal_data_manager)
fiscal_repository = FiscalRepository(fiscal_data)
fiscal_service = FiscalService(fiscal_repository)
