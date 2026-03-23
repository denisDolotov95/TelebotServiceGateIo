# -*- coding: utf-8 -*-

from app.util import formation_info_by_commands, formation_total_balance_table


class TestUtil:

    def test_formation_info_by_commands(self):
        info_commands = {
            "help": {"info": "список команд"},
            "logs": {
                "info": "логи",
                "commands": {"today": {"info": "логи за сегодня"}},
            },
        }

        returned = formation_info_by_commands(info_commands)
        assert isinstance(returned, str)
        assert "/help - список команд" in returned
        assert "/today - логи за сегодня" in returned

    def test_formation_total_balance_table(self):

        example = {
            "details": {
                "cross_margin": {"amount": "0", "currency": "USDT"},
                "spot": {
                    "currency": "USDT",
                    "amount": "42264489969935775.5160259954878034182418",
                },
                "finance": {
                    "amount": "662714381.70310327810191647181",
                    "currency": "USDT",
                },
                "margin": {
                    "amount": "1259175.664137668554329559",
                    "currency": "USDT",
                    "borrowed": "0.00",
                },
                "quant": {
                    "amount": "591702859674467879.6488202650892478553852",
                    "currency": "USDT",
                },
                "futures": {
                    "amount": "2384175.5606114082065",
                    "currency": "USDT",
                    "unrealised_pnl": "0.00",
                },
                "delivery": {
                    "currency": "USDT",
                    "amount": "1519804.9756702",
                    "unrealised_pnl": "0.00",
                },
                "warrant": {"amount": "0", "currency": "USDT"},
                "cbbc": {"currency": "USDT", "amount": "0"},
            },
            "total": {
                "currency": "USDT",
                "amount": "633967350312281193.068368815439797304437",
                "unrealised_pnl": "0.00",
                "borrowed": "0.00",
            },
        }

        returned = formation_total_balance_table(example)
        assert isinstance(returned, tuple)
        assert len(returned) == 2
        assert isinstance(returned[0], str) and isinstance(returned[1], str)
