from src.app.open_fiscal.model.fiscal import FiscalData
from src.app.open_fiscal.repository.fiscal import FiscalRepository
from src.app.open_fiscal.service.fiscal import FiscalService
from src.core.config import settings
from src.core.dependencies.db import Redis
from src.core.utils.openapi.data_loader import ApiConfig, FiscalDataLoader, OpenDataLoader
from src.core.utils.openapi.data_manager import PolarsDataManager
from src.core.utils.openapi.data_saver import RedisDataSaver

default_data_saver = RedisDataSaver(Redis)

fiscal_data_loader = FiscalDataLoader(
    base_url="http://openapi.openfiscaldata.go.kr",
    paths={"ExpenditureBudgetInit5": {"get": {}}},
    api_config=ApiConfig(request_page="pIndex", request_size="pSize"),
)
fiscal_data_manager = PolarsDataManager(
    fiscal_data_loader,
    default_data_saver,
    path="ExpenditureBudgetInit5",
    params={"Key": settings.open_fiscal_data_api.key, "Type": "JSON"},
)

gov24_service_loader = OpenDataLoader(
    base_url="http://api.odcloud.kr/api",
    swagger_url="https://infuser.odcloud.kr/api/stages/44436/api-docs?1684891964110",
    api_key=settings.gov_24_data_api.key,
)
gov24_service_list_manager = PolarsDataManager(
    gov24_service_loader,
    default_data_saver,
    path="/gov24/v3/serviceList",
)
gov24_service_detail_manager = PolarsDataManager(
    gov24_service_loader,
    default_data_saver,
    path="/gov24/v3/serviceDetail",
)
gov24_service_conditions_manager = PolarsDataManager(
    gov24_service_loader,
    default_data_saver,
    path="/gov24/v3/supportConditions",
)

fiscal_data = FiscalData(fiscal_data_manager)
fiscal_repository = FiscalRepository(fiscal_data)
fiscal_service = FiscalService(fiscal_repository)
