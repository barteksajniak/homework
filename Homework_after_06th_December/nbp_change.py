import argparse
from operator import itemgetter

import requests


def get_courses(currency_code, days):
    req = requests.get(
        f"http://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/last/{days}/?format=json"
    )
    data = req.json()
    return [x["mid"] for x in data["rates"]], data["currency"]


def calc_statistics(currency_list, days):
    res = {}
    for currency_code in currency_list:
        values, full_name = get_courses(currency_code, days)
        change = values[-1] / values[0]
        res[currency_code] = {
            "change": change,
            "course": values[-1],
            "full_name": full_name,
        }
    return res


def print_table(data):
    max_name_len = max((len(x["full_name"]) for x in data))
    horizontal_line = "+" + "-" * (max_name_len + 2) + (2 * ("+" + 15 * "-")) + "+"
    name_format = "| {:" + str(max_name_len) + "} |"
    header_format = name_format + 2 * " {:>13} |"
    line_format = name_format + " {:>13} | {:>13.5} |"
    print(horizontal_line)
    print(header_format.format("Nazwa", "Kurs", "Zmiana"))
    print(horizontal_line.replace("-", "="))
    for el in data:
        print(line_format.format(el["full_name"], el["course"], el["change"]))
        print(horizontal_line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("currency", nargs="+")
    parser.add_argument("--days", default=10, type=int, dest="days")
    args = parser.parse_args()
    res = calc_statistics(args.currency, args.days)
    ordered = sorted(res.values(), key=itemgetter("change"))
    print_table(ordered)


if __name__ == "__main__":
    main()
