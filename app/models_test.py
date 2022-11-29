from datetime import datetime, timezone
from typing import cast
from unittest.mock import create_autospec

from . import factories, models


def test_salmonrunshiftsummary_from_raw():
    raw = {
        "id": "Q29vcEhpc3RvcnlEZXRhaWwtdS1xb21pZm92dG5wanZjaGRndm5tbToyMDIyMTAwMVQwNDAyMTJfNmNlNjZkMGItZGNlNy00ZjUxLWIwYTItNjQ3MzdjOGM2MThk",
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
        "myResult": {"deliverCount": 140, "goldenDeliverCount": 5},
        "memberResults": [
            {"deliverCount": 322, "goldenDeliverCount": 6},
            {"deliverCount": 409, "goldenDeliverCount": 8},
            {"deliverCount": 328, "goldenDeliverCount": 3},
        ],
        "waveResults": [{"waveNumber": 1}],
    }

    user = factories.UserFactory.build()
    rotation = factories.SalmonRunRotationFactory.build()
    got = models.SalmonRunShiftSummary._from_raw(user, rotation, raw)

    want = dict(
        rotation=rotation,
        uploaded_by=user,
        played_at=datetime(2022, 10, 1, 4, 2, 12, tzinfo=timezone.utc),
        splatnet_id="Q29vcEhpc3RvcnlEZXRhaWwtdS1xb21pZm92dG5wanZjaGRndm5tbToyMDIyMTAwMVQwNDAyMTJfNmNlNjZkMGItZGNlNy00ZjUxLWIwYTItNjQ3MzdjOGM2MThk",
        waves_cleared=0,
        grade="Eggsecutive VP",
        grade_points=160,
        grade_point_diff="DOWN",
        golden_eggs_delivered_team=5 + 6 + 8 + 3,
        power_eggs_delivered_team=140 + 322 + 409 + 328,
        golden_eggs_delivered_self=5,
        power_eggs_delivered_self=140,
        king_salmonid="",
        king_salmonid_defeated=False,
    )
    assert got == want


def test_salmonrunshiftplayer_from_raw():
    raw = {
        "player": {
            "__isPlayer": "CoopPlayer",
            "byname": "Iced Squid Jerky",
            "name": "たこだち",
            "nameId": "1923",
            "nameplate": {
                "badges": [
                    {
                        "id": "QmFkZ2UtNTEwMDAwMA==",
                        "image": {
                            "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/badge_img/9e57b2bca3abaa7f78b499cf0023818bd984d77f12abb79c789bb0bcf3c78c0e_0.png?Expires=1673308800\u0026Signature=r16peJ7I0tgeYdV-AyB4ku33ncFi7Ro1n8oyiIoo-wodLmF8v-K58BcfzPnUTwoYb3M8prJmsu7AYCTeSTMkTJKAd9zz2dNymOoBx~237JTg5y5VyHaxUCoqUP3rD~-kVEEF6gmxce3sCbjXK-bsl0~bHtbmRJx6AL~wFD4IH0T9iFHHGEErXmbFXeil5Xwt31ausThADPV6JEdp9Jtq9KMOIh8jWFbcqp0yFCJuin-EZ6IyIKSHSyFMeGwzwYyp9B9ksQjeJ6NEyNJhC0iKTuvE1VsNk5TaivyPjIlVsu5Dhcaa2qt4u1Uf7xeWLB2gYxjKGLTzjAEgDkjI2edyIQ__\u0026Key-Pair-Id=KNBS2THMRC385"
                        },
                    },
                    {
                        "id": "QmFkZ2UtNTIxMDAwMA==",
                        "image": {
                            "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/badge_img/04fde46780d0b327ecbe31a4bcebf068d27c8bb345af6288bd5bee92da8ce41b_0.png?Expires=1673308800\u0026Signature=QEE7ZxNwC5cjpOXd8CQ97oBB5XFMhrDz~5kRkPlFzXdyzrhQvcas7Q3BKQ4a8CTddcYA7Fiy~-GhTJlM8CgMlLAOVlm7yAIHpJeSpt-bV6HhipVRptYUeyoqipAdun7NUatMi05wvsYg0y93lqPBOTn-T-RssZCAgwdx~hvIiTiklqHp28ODByTUKf8~mUQ9QqKpVDc3Di4j20eOqqP~IA2svJ-PTCqYY2yE3X~dbuLsBeZ8b-g0ATtSQLhCWjSCXzMEza-DYhxnmfaipXB4NsKUSmC8bXIlrJArU8AdcRUDtvE50i-Cic5PX2~z6YmbwMj2W0HweQmHYOcH4XZJ9A__\u0026Key-Pair-Id=KNBS2THMRC385"
                        },
                    },
                    {
                        "id": "QmFkZ2UtMzEwMzAwMQ==",
                        "image": {
                            "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/badge_img/6e8d95d4f39c9f1a4dff137247c6d4103082a07d73d64cfea4cfbb787b5b12c8_0.png?Expires=1673308800\u0026Signature=Hlh77IElP-RmaxU5Z8F0Yt-oUHBUw~EACuVlUIrXxJz8KzXpthnvX17jvMJhV0Lkyneuj4o1CLO8Ldexy4k0zqrF12WZvwaewVUWc6AOV7mC~48AX0Qb1Jti1JvwLBDmUmZYkcKGKzI2AlzMSGu3K5u9PGJ9FIwQXq9FI8BC7a4WfnofrDgvpyOp8HXuoZhtJ1MdLCnW4WCVfya6MFgHJAwvLa6SRomkZ2eM9Lf0rD3cDOe9jXQndCCB-mrZxpzBvRrnjZDE2U75Q9MJ3-DMQqANpO2c--KRUENksPQD3B8NtQ6sO7Beh~b1XWRAfQ3yNg3TmkrBInSGu5aHAnxqcQ__\u0026Key-Pair-Id=KNBS2THMRC385"
                        },
                    },
                ],
                "background": {
                    "textColor": {"a": 1.0, "b": 1.0, "g": 1.0, "r": 1.0},
                    "image": {
                        "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/npl_img/ef8a9390e1a4ee4da709c69cf572586b57b80100f521b16a9d8f2c1b764b0dd9_0.png?Expires=1673308800\u0026Signature=P3pMSyXl7Qf3pk7JhwVPu3CK~DzhT-JK1IvnDcIidPD3~AB5qA~KvANlAdXzFjnjNGxHPU19jI7N24Czx2mjsA4lYOrHhV8derjXeQj48R4gDDuQOLrV1M6Fo15-tBeOKJ8bC8fVpvkwglbAOW628CRPmZauJDsOe~AlRD~IQJuyTcPgKkIQnafVXpTD~3VUDZmhZn6z5Vx0Y21MHfOZLWz4QxEo5o7Heqoyywi~Co88om1SYldPdLNkJkD~ATV7yrHCnxrskgxW~oykb1p6GH1VA24pprZ-mbzktsfkzmWptGq5qrEbpCaPz~6-IKU-sWDgwGBTmJEjfFHVE9hlnw__\u0026Key-Pair-Id=KNBS2THMRC385"
                    },
                    "id": "TmFtZXBsYXRlQmFja2dyb3VuZC0yMDAx",
                },
            },
            "uniform": {
                "name": "Pink Slopsuit",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/coop_skin_img/61acba988871d0e9ce259138cde62f9b8f83bb8014ef14c9abb3acf0aa38c51f_0.png?Expires=1673308800\u0026Signature=HqT~L04YOtagIXnn2MjcF8DYW-CNlULEoXsWoy42uszR2AxNjPJ9TLyRFNOsTfiFoVid4Y4bSZZWY63B1BiporI9C9gsUFVDEvJBWilu7JXNE078zHcgthAhRgazkD1KWbJEzEpvTMkVXCaa3a2KP-PqxRm6faAmFU7Jg-AuoCgwwOAeWqLAX7-Svx7YR0~ywK2UM6a3ZqQDdEUy3ge3LB8XNAT~P~lW-DLlDCLJmVMy4gi1uGOduSDOYvpn8JaIXNz4BzjazRUsgJfL2wtUEc5bI0qQHlymfN3D7At7mq5xmWM04uISirIfGqB28oFInDGQCLoaFRaaaeNvcAW~2g__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "Q29vcFVuaWZvcm0tNA==",
            },
            "id": "Q29vcFBsYXllci11LXFvbWlmb3Z0bnBqdmNoZGd2bm1tOjIwMjIxMDAxVDA0MDIxMl82Y2U2NmQwYi1kY2U3LTRmNTEtYjBhMi02NDczN2M4YzYxOGQ6dS1xb21pZm92dG5wanZjaGRndm5tbQ==",
            "species": "OCTOLING",
        },
        "weapons": [
            {
                "name": ".96 Gal",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/weapon_illust/fe2b351799aa48fcb48154299ff0ccf0b0413fc291ffc49456e93db29d2f1db5_0.png?Expires=1673308800\u0026Signature=JOO1SIQShGbpFDQMIbzhdcjd~ArvENJcinA~c1H9y7oVLtMhMBmhSj5GUhKwJQq9ptvnNDsjBrCBjyU1qLCmEXFOrVo5HZ1pSP-kb6oc9pDwSg6hhzRUQMHm5~xOp1-NdbVnizQdSOgoGch6fzUwAWUzoctXG8kx8cMGqA9~etPGyAjsQLabpjyKHNuj7hfvPfOsrLBalT~k8cVPRs1Rz821LnED3-OqOKYMYQ2W43KP-SRyf4LDHJSaF3mP9TAqwKmxLULpbn1s3ZW9bZRMpNQ3fUpuVjW4BMcM1LInepGwrv2A5140ZNyl43Aln-T2vnqvzujv0Irf0IrK1r-rqA__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
            }
        ],
        "specialWeapon": {
            "name": "Booyah Bomb",
            "image": {
                "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/bd327d1b64372dedefd32adb28bea62a5b6152d93aada5d9fc4f669a1955d6d4_0.png?Expires=1673308800\u0026Signature=bSQSnCd92kGh99thLfoiCuUUzghDBY-j1UHVcHCgaV3umcufZUWCXq-Lj2Hn1z3na4ocHdZZGluqVA2Ql~wnSF0XfA-6NG5h8yJ95wUz8Oscc7EWU66e1sZhQslQFnvsjTcbsFzliwt5nQuCXk1f2fGUbZLuTVKSZ1ExtzLvWR-RbzrtW5TtY3Xzsci5lqHGF-fkFLKaOrY6CRax-PgSqW~BydRucyxY4paVjjlJja-k765qzMcr0M~jUO-~27x17f2AeL5vp1CRne1YilO9OsCMOIHMv798T5h8dgwgTrgQAWjU-W7qgNhvcwWq8recETIxUoJjs1gXIl8wAeX76Q__\u0026Key-Pair-Id=KNBS2THMRC385"
            },
            "weaponId": 20012,
        },
        "defeatEnemyCount": 0,
        "deliverCount": 140,
        "goldenAssistCount": 0,
        "goldenDeliverCount": 5,
        "rescueCount": 1,
        "rescuedCount": 2,
    }

    shift = cast(models.SalmonRunShiftSummary, object())
    got = models.SalmonRunShiftPlayer._from_raw(shift, raw, is_uploader=True)
    want = {
        "bosses_defeated": 0,
        "golden_eggs_assisted": 0,
        "golden_eggs_delivered": 5,
        "is_uploader": True,
        "power_eggs_delivered": 140,
        "shift": shift,
        "special_weapon": "Booyah Bomb",
        "splatnet_id": "Q29vcFBsYXllci11LXFvbWlmb3Z0bnBqdmNoZGd2bm1tOjIwMjIxMDAxVDA0MDIxMl82Y2U2NmQwYi1kY2U3LTRmNTEtYjBhMi02NDczN2M4YzYxOGQ6dS1xb21pZm92dG5wanZjaGRndm5tbQ==",
        "teammates_rescued": 1,
        "times_rescued": 2,
    }
    assert got == want


def test_salmonrunwave_from_raw_normal():
    raw = {
        "waveNumber": 3,
        "waterLevel": 2,
        "eventWave": None,
        "deliverNorm": 28,
        "goldenPopCount": 63,
        "teamDeliverCount": 38,
        "specialWeapons": [
            {
                "name": "Crab Tank",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/680379f8b83e5f9e033b828360827bc2f0e08c34df1abcc23de3d059fe2ac435_0.png?Expires=1673308800\u0026Signature=lJ~IKvNG9KOfzA9wF5qSGlG7JN9Mmop5TqT88magIDJ64phb74fkUV1Z7c0u6xIkXydPcbAgez-voKG15lw2YJuv20yrgZP~tLUDhk~R2FQR5YpQEChc7Egd8Ogj8Bb4ACWMRLDyJiyKOm1Gr5A4CHVcF10TrSESP4qyoCXuHk4C2vNkJ8zx8-BOOS8wkfsZ6eo1YDfdfQ4yjgcg5OvLdk4Umw3yUxwaoBDIlP8vtX0Xt84gZHGVrzaeCUstfGiQr4Xrf~JBtS1GO4eElo9iUQELf~UDTLLkHYUhXm627gVeQ2Izm-LXjEEBW6sUQYkh-VEuMcEUlQk8I7tJF3GLWw__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxMg==",
            },
            {
                "name": "Crab Tank",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/680379f8b83e5f9e033b828360827bc2f0e08c34df1abcc23de3d059fe2ac435_0.png?Expires=1673308800\u0026Signature=lJ~IKvNG9KOfzA9wF5qSGlG7JN9Mmop5TqT88magIDJ64phb74fkUV1Z7c0u6xIkXydPcbAgez-voKG15lw2YJuv20yrgZP~tLUDhk~R2FQR5YpQEChc7Egd8Ogj8Bb4ACWMRLDyJiyKOm1Gr5A4CHVcF10TrSESP4qyoCXuHk4C2vNkJ8zx8-BOOS8wkfsZ6eo1YDfdfQ4yjgcg5OvLdk4Umw3yUxwaoBDIlP8vtX0Xt84gZHGVrzaeCUstfGiQr4Xrf~JBtS1GO4eElo9iUQELf~UDTLLkHYUhXm627gVeQ2Izm-LXjEEBW6sUQYkh-VEuMcEUlQk8I7tJF3GLWw__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxMg==",
            },
            {
                "name": "Inkjet",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/252059408283fbcb69ca9c18b98effd3b8653ab73b7349c42472281e5a1c38f9_0.png?Expires=1673308800\u0026Signature=hhTQl-3msKlQry7IrIg-Zzotyr1z-eEM-D-UEfjRUXbj~9RvbDT2LckGMTcgDKjSd7N922chycHe5RgPMUN-cJLRxwuH6Dg3cdyZIhBITmXEyT3Lh7iTZ8Mlqc3QCn9Hsr3EcsULZTb4mNUuZsWdnPoY0NPkmr4vkvbOdV6wivbvnx1aHqGZHmnLIzFZz5ZbASNn5VEfSqO31U-ACDu~CsRZKH9vNQDTwguWDZBoke0t6kvnYY4vb11i-~dDSJpRQL0raeA0bXQ04oJFtsBjRcV1n-0JBE0kFpW8iC5yL1~6LvF443AJvmhlTWq3eM~Lk0BMb5mp3rjTk0ghImbsIw__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxMA==",
            },
            {
                "name": "Killer Wail 5.1",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/fa8d49e8c850ee69f0231976208a913384e73dc0a39e6fb00806f6aa3da8a1ee_0.png?Expires=1673308800\u0026Signature=eQ7ZkvlDltvePOqSW8IGtrYTwPhU3z0ru1eUJdHL50XRY6B8Sbk9hDim~fLStgaRjC4E0svRgN1JzEjLnYB6c4pvaMcBGRc21vty~7eHLat~Pp7yxKm2xYduUSMkYjCC69fUs-lWbElXO6eHgkkkBDSa8ufU4~A~unTR4-RXDUbf-RrMQ9Iureu8NTL4WppdgMOZW5pq-7YLBTpAjqZYKVsettfLwdcZiNqCCGqbGDX4v9Q8-xQt49wlEn8WsbbyMyxlecEhzqcBRGmXrw0iSSYnnAvXKmpUt23c1y8CjOtatC6mtCFxG~hjEHCN4V993CxHv6vFrAVmHkZc2ATw4Q__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "U3BlY2lhbFdlYXBvbi0yMDAwOQ==",
            },
            {
                "name": "Killer Wail 5.1",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/fa8d49e8c850ee69f0231976208a913384e73dc0a39e6fb00806f6aa3da8a1ee_0.png?Expires=1673308800\u0026Signature=eQ7ZkvlDltvePOqSW8IGtrYTwPhU3z0ru1eUJdHL50XRY6B8Sbk9hDim~fLStgaRjC4E0svRgN1JzEjLnYB6c4pvaMcBGRc21vty~7eHLat~Pp7yxKm2xYduUSMkYjCC69fUs-lWbElXO6eHgkkkBDSa8ufU4~A~unTR4-RXDUbf-RrMQ9Iureu8NTL4WppdgMOZW5pq-7YLBTpAjqZYKVsettfLwdcZiNqCCGqbGDX4v9Q8-xQt49wlEn8WsbbyMyxlecEhzqcBRGmXrw0iSSYnnAvXKmpUt23c1y8CjOtatC6mtCFxG~hjEHCN4V993CxHv6vFrAVmHkZc2ATw4Q__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "U3BlY2lhbFdlYXBvbi0yMDAwOQ==",
            },
            {
                "name": "Triple Inkstrike",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/380e541b5bc5e49d77ff1a616f1343aeba01d500fee36aaddf8f09d74bd3d3bc_0.png?Expires=1673308800\u0026Signature=Tmz7uneGddwCQAY2kRHloLLiA-tSYuGJ-qBvPSZSgB~eg1V9acYh-4i5BWIQsW22lngqih2DInc9UotgxPKdZ9nLQuzblQur2luUG~EjQ8lqDO5NbpkHI54mlyPXz~wVPgRQtreVYhxS3IsA8eRfOE0WEnD3cWQIpcw2Qrzm2SSRAlKFJaOLohtdk6TjjGX782Bglf--kdBif31xC-A5S8s1Fxjy7-Cvj843yCCu~7~M5rOq8hqgJJK8KVyEQjxGRgxN8ud~yXX~seyMLpavUxZBi4MqSyTc9vy4aDiZHzUjWYJwv7gF4eSNPPmmHpKjMtImyLhbflwuPk-huJ6UFg__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxNA==",
            },
            {
                "name": "Triple Inkstrike",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/380e541b5bc5e49d77ff1a616f1343aeba01d500fee36aaddf8f09d74bd3d3bc_0.png?Expires=1673308800\u0026Signature=Tmz7uneGddwCQAY2kRHloLLiA-tSYuGJ-qBvPSZSgB~eg1V9acYh-4i5BWIQsW22lngqih2DInc9UotgxPKdZ9nLQuzblQur2luUG~EjQ8lqDO5NbpkHI54mlyPXz~wVPgRQtreVYhxS3IsA8eRfOE0WEnD3cWQIpcw2Qrzm2SSRAlKFJaOLohtdk6TjjGX782Bglf--kdBif31xC-A5S8s1Fxjy7-Cvj843yCCu~7~M5rOq8hqgJJK8KVyEQjxGRgxN8ud~yXX~seyMLpavUxZBi4MqSyTc9vy4aDiZHzUjWYJwv7gF4eSNPPmmHpKjMtImyLhbflwuPk-huJ6UFg__\u0026Key-Pair-Id=KNBS2THMRC385"
                },
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxNA==",
            },
        ],
    }

    shift = create_autospec(models.SalmonRunShiftSummary)
    shift.waves_cleared = 3
    got = models.SalmonRunWave._from_raw(shift, raw)
    want = {
        "cleared": True,
        "event": "",
        "golden_egg_quota": 28,
        "golden_eggs_delivered": 38,
        "number": 3,
        "shift": shift,
        "specials_used": [
            "Crab Tank",
            "Crab Tank",
            "Inkjet",
            "Killer Wail 5.1",
            "Killer Wail 5.1",
            "Triple Inkstrike",
            "Triple Inkstrike",
        ],
        "water_level": 2,
    }
    assert got == want


def test_salmonrunwave_from_raw_king_salmonid():
    raw = {
        "eventWave": None,
        "waterLevel": 2,
        "waveNumber": 4,
        "deliverNorm": None,
        "goldenPopCount": 21,
        "specialWeapons": [
            {
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxMg==",
                "name": "Crab Tank",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/680379f8b83e5f9e033b828360827bc2f0e08c34df1abcc23de3d059fe2ac435_0.png?Expires=1673308800&Signature=lJ~IKvNG9KOfzA9wF5qSGlG7JN9Mmop5TqT88magIDJ64phb74fkUV1Z7c0u6xIkXydPcbAgez-voKG15lw2YJuv20yrgZP~tLUDhk~R2FQR5YpQEChc7Egd8Ogj8Bb4ACWMRLDyJiyKOm1Gr5A4CHVcF10TrSESP4qyoCXuHk4C2vNkJ8zx8-BOOS8wkfsZ6eo1YDfdfQ4yjgcg5OvLdk4Umw3yUxwaoBDIlP8vtX0Xt84gZHGVrzaeCUstfGiQr4Xrf~JBtS1GO4eElo9iUQELf~UDTLLkHYUhXm627gVeQ2Izm-LXjEEBW6sUQYkh-VEuMcEUlQk8I7tJF3GLWw__&Key-Pair-Id=KNBS2THMRC385"
                },
            },
            {
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxNA==",
                "name": "Triple Inkstrike",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/380e541b5bc5e49d77ff1a616f1343aeba01d500fee36aaddf8f09d74bd3d3bc_0.png?Expires=1673308800&Signature=Tmz7uneGddwCQAY2kRHloLLiA-tSYuGJ-qBvPSZSgB~eg1V9acYh-4i5BWIQsW22lngqih2DInc9UotgxPKdZ9nLQuzblQur2luUG~EjQ8lqDO5NbpkHI54mlyPXz~wVPgRQtreVYhxS3IsA8eRfOE0WEnD3cWQIpcw2Qrzm2SSRAlKFJaOLohtdk6TjjGX782Bglf--kdBif31xC-A5S8s1Fxjy7-Cvj843yCCu~7~M5rOq8hqgJJK8KVyEQjxGRgxN8ud~yXX~seyMLpavUxZBi4MqSyTc9vy4aDiZHzUjWYJwv7gF4eSNPPmmHpKjMtImyLhbflwuPk-huJ6UFg__&Key-Pair-Id=KNBS2THMRC385"
                },
            },
            {
                "id": "U3BlY2lhbFdlYXBvbi0yMDAxMA==",
                "name": "Inkjet",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/252059408283fbcb69ca9c18b98effd3b8653ab73b7349c42472281e5a1c38f9_0.png?Expires=1673308800&Signature=hhTQl-3msKlQry7IrIg-Zzotyr1z-eEM-D-UEfjRUXbj~9RvbDT2LckGMTcgDKjSd7N922chycHe5RgPMUN-cJLRxwuH6Dg3cdyZIhBITmXEyT3Lh7iTZ8Mlqc3QCn9Hsr3EcsULZTb4mNUuZsWdnPoY0NPkmr4vkvbOdV6wivbvnx1aHqGZHmnLIzFZz5ZbASNn5VEfSqO31U-ACDu~CsRZKH9vNQDTwguWDZBoke0t6kvnYY4vb11i-~dDSJpRQL0raeA0bXQ04oJFtsBjRcV1n-0JBE0kFpW8iC5yL1~6LvF443AJvmhlTWq3eM~Lk0BMb5mp3rjTk0ghImbsIw__&Key-Pair-Id=KNBS2THMRC385"
                },
            },
            {
                "id": "U3BlY2lhbFdlYXBvbi0yMDAwOQ==",
                "name": "Killer Wail 5.1",
                "image": {
                    "url": "https://api.lp1.av5ja.srv.nintendo.net/resources/prod/special_img/blue/fa8d49e8c850ee69f0231976208a913384e73dc0a39e6fb00806f6aa3da8a1ee_0.png?Expires=1673308800&Signature=eQ7ZkvlDltvePOqSW8IGtrYTwPhU3z0ru1eUJdHL50XRY6B8Sbk9hDim~fLStgaRjC4E0svRgN1JzEjLnYB6c4pvaMcBGRc21vty~7eHLat~Pp7yxKm2xYduUSMkYjCC69fUs-lWbElXO6eHgkkkBDSa8ufU4~A~unTR4-RXDUbf-RrMQ9Iureu8NTL4WppdgMOZW5pq-7YLBTpAjqZYKVsettfLwdcZiNqCCGqbGDX4v9Q8-xQt49wlEn8WsbbyMyxlecEhzqcBRGmXrw0iSSYnnAvXKmpUt23c1y8CjOtatC6mtCFxG~hjEHCN4V993CxHv6vFrAVmHkZc2ATw4Q__&Key-Pair-Id=KNBS2THMRC385"
                },
            },
        ],
        "teamDeliverCount": None,
    }

    shift = create_autospec(models.SalmonRunShiftSummary)
    shift.king_salmonid_defeated = False
    got = models.SalmonRunWave._from_raw(shift, raw)
    want = {
        "cleared": False,
        "event": "",
        "golden_egg_quota": -1,
        "golden_eggs_delivered": -1,
        "number": 4,
        "shift": shift,
        "specials_used": ["Crab Tank", "Triple Inkstrike", "Inkjet", "Killer Wail 5.1"],
        "water_level": 2,
    }
    assert got == want
