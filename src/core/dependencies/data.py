import asyncio

from src.core.dependencies.db import Redis
from src.core.utils.openapi.dataloader import ApiConfig, OpenDataLoader, YearlyDataLoader
from src.core.utils.openapi.datamanager import PolarsDataManager
from src.core.utils.openapi.datasaver import RedisDataSaver

default_data_saver = RedisDataSaver(Redis)

fiscal_data_loader = YearlyDataLoader(
    base_url="http://openapi.openfiscaldata.go.kr",
    paths={"ExpenditureBudgetInit5": {"get": {}}},
    api_config=ApiConfig(request_page="pIndex", request_size="pSize"),
)
gov24_data_loader = OpenDataLoader(
    base_url="http://api.odcloud.kr/api",
    swagger_url="https://infuser.odcloud.kr/api/stages/44436/api-docs?1684891964110",
    api_key="gnaO3hwjphcJRJqAGcEhrX03g+dytgrkPTWBNCMYHXYcg6y0IPlBSgyaqV0IHwS/zRz7n3nGd50Ggh7+8C9/BQ==",
)

fiscal_data_manager = PolarsDataManager(
    fiscal_data_loader,
    default_data_saver,
    path="ExpenditureBudgetInit5",
    params={"Key": "JOPYJ1001603120241215051335MEQZR", "Type": "JSON"},
)

gov24_data_manager = PolarsDataManager(
    gov24_data_loader,
    default_data_saver,
    path="gov24/v3/serviceList",
)

asyncio.run(fiscal_data_manager.init())
