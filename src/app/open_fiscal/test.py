import json

import pandas as pd
import requests

from src.core.config import settings


def get_fiscal_data(year: str):
    df = pd.DataFrame()
    prefix = "ExpenditureBudgetInit5"
    url = "https://openapi.openfiscaldata.go.kr/" + prefix
    params = {
        "Key": settings.open_fiscal_data_api.key,
        "Type": "json",
        "pIndex": "1",
        "pSize": "1",
        "FSCL_YY": year,
    }

    head = requests.get(url, params=params)
    head = json.loads(head.json())

    try:
        data = head[prefix][0]["head"]
        data_len = data[0]["list_total_count"]
        params["pSize"] = "1000"
    except KeyError:
        raise ValueError("CAN NOT FIND DATA")

    for i in range(1, data_len // 1000 + 2):
        params["pIndex"] = str(i)
        result = requests.get(url, params=params).json()
        result = json.loads(result)
        result = result[prefix][1]["row"]
        result = pd.DataFrame(result)
        df = pd.concat([df, result])

    df = df.sort_values(
        by=["OFFC_NM", "Y_YY_DFN_MEDI_KCUR_AMT"],
        ignore_index=True,
    )

    return df


if __name__ == "__main__":
    print(
        get_fiscal_data("2020").pivot_table(
            values="Y_YY_DFN_MEDI_KCUR_AMT",
            index="OFFC_NM",
            aggfunc="sum",
        )
    )
