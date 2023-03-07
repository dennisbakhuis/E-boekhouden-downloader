import os
import argparse
from datetime import datetime
from dataclasses import dataclass

from zeep import Client
from zeep.helpers import serialize_object
import pandas as pd


env_username = "EBOEKHOUDEN_USERNAME"
env_security1 = "EBOEKHOUDEN_SECURITY1"
env_security2 = "EBOEKHOUDEN_SECURITY2"
max_mutatie_id = 99999


@dataclass
class Mutaties:
    mutatienr: int
    mutatienrvan: int
    mutatienrtm: int
    factuurnummer: str
    datumvan: str
    datumtm: str

    def export(self):
        return dict(
            MutatieNr=self.mutatienr,
            MutatieNrVan=self.mutatienrvan,
            MutatieNrTm=self.mutatienrtm,
            Factuurnummer=self.factuurnummer,
            DatumVan=self.datumvan,
            DatumTm=self.datumtm,
        )


def get_env_value(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise ValueError("No valid {key} found in environment!")
    return value


def mutaties_to_csv(
    server_url: str,
    username: str,
    security_code_1: str,
    security_code_2: str,
    start_date: str,
    end_date: str,
    output_file: str,
) -> None:
    # Get session
    client = Client(server_url)
    response_object = client.service.OpenSession(
        Username=username,
        SecurityCode1=security_code_1,
        SecurityCode2=security_code_2,
    )
    session_id = response_object.SessionID

    # Get mutaties
    mutatie_filter = Mutaties(0, 0, max_mutatie_id, "", start_date, end_date).export()
    mutaties = client.service.GetMutaties(
        SessionID=session_id,
        SecurityCode2=security_code_2,
        cFilter=mutatie_filter,  # Filter object is required by the API
    )

    # Close session
    client.service.CloseSession(
        SessionID=session_id,
    )

    # Flatten `mutatieregels`
    rows = []
    for mutatie in mutaties.Mutaties.cMutatieList:
        flat_mutatie = dict(serialize_object(mutatie))
        del flat_mutatie["MutatieRegels"]
        for ix, regel in enumerate(mutatie["MutatieRegels"]["cMutatieListRegel"]):
            flat_regel = dict(serialize_object(regel))
            new_mutatie = flat_mutatie.copy() | flat_regel | {"mutatie_regel_id": ix}
            rows.append(new_mutatie)

    # Convert to DataFrame and save to disk
    df = pd.DataFrame(rows)
    df.to_csv(output_file)


def main(arguments=None):
    parser = argparse.ArgumentParser("E-Boekhouden mutatie downloader")
    parser.add_argument(
        "--server-url",
        default="https://soap.e-boekhouden.nl/soap.asmx?wsdl",
        help="URL to E-Boekhouden SOAP API.",
    )
    parser.add_argument(
        "--username",
        default="",
        help="Username used for the E-Boekhouden API.",
    )
    parser.add_argument(
        "--security-code-1",
        default="",
        help="Security code 1 for the SOAP API.",
    )
    parser.add_argument(
        "--security-code-2",
        default="",
        help="Security code 2 for the SOAP API.",
    )
    parser.add_argument(
        "--start-date",
        default="",
        help="Start date to get mutaties in format `yyyy-mm-dd`. Defaults to first month of the year.",
    )
    parser.add_argument(
        "--end-date",
        default="",
        help="End date to get mutaties in format `yyyy-mm-dd`. Defaults to today.",
    )
    parser.add_argument(
        "--output-file",
        default="",
        help="Output CSV file of the Mutaties. Defaults to mutaties_<start_date>_<end_date>.csv.",
    )

    args = parser.parse_args(arguments)
    if not args.username:
        username = get_env_value(env_username)
        security1 = get_env_value(env_security1)
        security2 = get_env_value(env_security2)
    else:
        username = args.username
        security1 = args.security_code_1
        security2 = args.security_code_2

    dt = datetime.now()
    if not args.start_date:
        start_date = f"{dt.year}-01-01"
    else:
        start_date = args.start_date

    if not args.end_date:
        end_date = f"{dt.year}-{dt.month:02}-{dt.day:02}"
    else:
        end_date = args.end_date

    if not args.output_file:
        output_file = f"mutaties_{start_date}_{end_date}.csv"
    else:
        output_file = args.output_file

    mutaties_to_csv(
        server_url=args.server_url,
        username=username,
        security_code_1=security1,
        security_code_2=security2,
        start_date=start_date,
        end_date=end_date,
        output_file=output_file,
    )


if __name__ == "__main__":
    main()
