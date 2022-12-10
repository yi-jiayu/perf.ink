import base64
from datetime import timezone

import pytest


@pytest.fixture
def shift_id_factory(faker):
    def _shift_id_factory():
        uuid = faker.uuid4()
        played_at = faker.date_time(tzinfo=timezone.utc).strftime("%Y%m%dT%H%M%S")
        decoded_shift_id = (
            f"CoopHistoryDetail-u-qomifovtnpjvchdgvnmm:{played_at}_{uuid}"
        )
        shift_id = base64.standard_b64encode(decoded_shift_id.encode("utf-8")).decode(
            "utf-8"
        )
        return shift_id

    return _shift_id_factory


@pytest.fixture
def raw_salmon_run_shift_factory(shift_id_factory):
    def _raw_salmon_run_shift_factory():
        return {
            "id": shift_id_factory(),
            "weapons": [
                {
                    "name": "Splash-o-matic",
                    "image": {
                        "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/weapon_illust/25e98eaba1e17308db191b740d9b89e6a977bfcd37c8dc1d65883731c0c72609_0.png?Expires=1673308800\u0026Signature=oT~sZrjysaFT4vhqRBi23kbeUMrU5BzkEkLATBie0DuSg2TYmZ0rnzV4hy4q4OUN639s4sA~4wsucLK7gphIa3ZxgL2RBaXulgiFZ7ymuHjUMBJEB-Kb8loL50PrPxhVvPPCFxiYt2v~MHbctVcBYI4nyc1kKTJgcStaYdFlWH9pNd6~wuxua29yf1CEKCWX1FkPuxCYLyqNGPT1yaWYFfaQ7Nlm2osGbbR4tL4EMhPMl~RqgN1rdejKji-uKlujOZL8Ra1zGq9uqHjgB7rttWyuGoBqkzYPMbN~Fnrf4iZcLvt0ztL9vHRh9wZ9DNOgco1soryeO5b5VZ8EG9zhLA__\u0026Key-Pair-Id=KNBS2THMRC385"
                    },
                },
                {
                    "name": "Octobrush",
                    "image": {
                        "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/weapon_illust/ce0bb38588e497586a60f16e0aca914f181f42be29953742fd4a55a97e2ebd22_0.png?Expires=1673308800\u0026Signature=wVh~7K0iqMEKhy0bWsfVv3Q~tvIjmSJLQRvFAabA2zo5k~RhSPpA8DBUi92YQx~-uzgzh7tfOye-zh6HdPSLNY5DXieWe~ln5ccLS77xFUuomms-X5iOw4mGVcuxzhA6sn-5x1-66Zk3RPyAe-R84vWIalp~fr1YuZa2EeD2iWevZ~hYU~WGSjUoZD4RZBNNoXNAJVS8PnLmTxmX60necYA7t6l6GJ6j0yM4vDYl9Ua6cup5ufkZEMdRbjLCxZTX8mkJOTIxpgBXKIHUBAydrB-pA7kK40GcG8UxEusVXqfDQt7-0uqofi~hWSVpwoo~rhGmFg3lG6Do3U~S71aNmg__\u0026Key-Pair-Id=KNBS2THMRC385"
                    },
                },
                {
                    "name": "Bloblobber",
                    "image": {
                        "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/weapon_illust/0199e455872acba1ab8ef0040eca7f41afca48c1f9ad2c5d274323d6dbc49133_0.png?Expires=1673308800\u0026Signature=gwOoXon3bfcCiA7lkqsp0f-gnsI20AADIgMoeru7nA2zNhzxVUKi4EeebNFEUfN7X1kX3QJZpW9F44qhvLL4x8rbG724eUkFaL4mmDNy5wO-lgvrfO4~lZOzyXzTZLK8fNhs8gX8eIklQG~UOxZyoZibv0hXFSyWNHiYT6TkPxYNjRr4Ey1SF21WaZbsLXtcwszQ6IaqxjcW9kWwow4eoLGKK6SKnw4VTa1jgYaH7ZA3TJbiBhk9g9NGBNm9FG-ebRzRl1UD1noJZNyHAGBMcaUFzRfTmcne9KFHOuIN-CwSEm2DNUuiKRggjxDWoTOxPuAMiMMlNHkx3M8pSu5xgg__\u0026Key-Pair-Id=KNBS2THMRC385"
                    },
                },
                {
                    "name": ".96 Gal",
                    "image": {
                        "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/weapon_illust/fe2b351799aa48fcb48154299ff0ccf0b0413fc291ffc49456e93db29d2f1db5_0.png?Expires=1673308800\u0026Signature=JOO1SIQShGbpFDQMIbzhdcjd~ArvENJcinA~c1H9y7oVLtMhMBmhSj5GUhKwJQq9ptvnNDsjBrCBjyU1qLCmEXFOrVo5HZ1pSP-kb6oc9pDwSg6hhzRUQMHm5~xOp1-NdbVnizQdSOgoGch6fzUwAWUzoctXG8kx8cMGqA9~etPGyAjsQLabpjyKHNuj7hfvPfOsrLBalT~k8cVPRs1Rz821LnED3-OqOKYMYQ2W43KP-SRyf4LDHJSaF3mP9TAqwKmxLULpbn1s3ZW9bZRMpNQ3fUpuVjW4BMcM1LInepGwrv2A5140ZNyl43Aln-T2vnqvzujv0Irf0IrK1r-rqA__\u0026Key-Pair-Id=KNBS2THMRC385"
                    },
                },
            ],
            "nextHistoryDetail": None,
            "previousHistoryDetail": {
                "id": "Q29vcEhpc3RvcnlEZXRhaWwtdS1xb21pZm92dG5wanZjaGRndm5tbToyMDIyMTAwMVQwMzUzMDBfODE4MGFhZmYtNmExNi00M2EzLTk4MmItMjYyNWIyMzNjMDdl"
            },
            "resultWave": 1,
            "coopStage": {"name": "Gone Fission Hydroplant", "id": "Q29vcFN0YWdlLTc="},
            "afterGrade": {"name": "Eggsecutive VP", "id": "Q29vcEdyYWRlLTg="},
            "afterGradePoint": 160,
            "gradePointDiff": "DOWN",
            "bossResult": None,
            "myResult": {"deliverCount": 140},
            "memberResults": [
                {"deliverCount": 322},
                {"deliverCount": 409},
                {"deliverCount": 328},
            ],
            "waveResults": [{"teamDeliverCount": 22}],
        }

    return _raw_salmon_run_shift_factory
