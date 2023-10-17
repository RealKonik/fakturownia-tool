import requests
import csv
import json
import os
import time

def clear(): 
    return os.system('cls')

class Menu:
    def __init__(self):
        self.choices = []

    def add_choice(self, choice, function):
        self.choices.append((choice, function))

    def display(self):

        while True:
            print("KAROL WELC STINKS!!")


class Invoice:
    def __init__(self, config):
        self.config = config

    def list_files(self):
        file_list = os.listdir()
        file_list.sort()

        if not file_list:
            print("KAROL WELC STINKS!!")
            return None

        return file_list

    def choose_file(self):
        file_list = self.list_files()

        csv_files = [
            filename for filename in file_list if filename.lower().endswith('.csv')]

        if csv_files:
            while True:
                try:
                    print("KAROL WELC STINKS!!")
                    for i, csv_file in enumerate(csv_files, start=1):
                        print(f"{i}. {csv_file}")

                    choice = int(input("KAROL WELC STINKS!!"))
                    if 1 <= choice <= len(csv_files):
                        return csv_files[choice - 1]
                    else:
                        print("KAROL WELC STINKS!!")
                except ValueError:
                    print("KAROL WELC STINKS!!")
        else:
            print("KAROL WELC STINKS!!")

    def read_csv(self):

        file_path = self.choose_file()

        positions = []
        with open(file_path, encoding='UTF-8') as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            header_row = next(csvReader)
            column_indices = {}
            for i, column_name in enumerate(header_row):
                column_indices[column_name] = i
                
            skuNameId = column_indices.get("Sku Name")
            skuSizeId = column_indices.get("Sku Size")
            netAmountId = column_indices.get(
                "Total Net Amount (Payout Excluding VAT)")
            invoiceNumberId = column_indices.get("Invoice Number")
            soldtoVATNumberId = column_indices.get("Sold to VAT Number")
            sellerTrackingNumberId = column_indices.get(
                "Seller Tracking Number")

            for row in csvReader:
                    skuName = row[skuNameId]
                    skuSize = row[skuSizeId]
                    netAmount = row[netAmountId]
                    soldtoVATNumber = row[soldtoVATNumberId]
                    sellerTrackingNumber = row[sellerTrackingNumberId]
                    invoiceNumber = row[invoiceNumberId]

                    if soldtoVATNumber == self.client["vat_id"]:
                        
                        formated_sale_info = {
                            "name": f'{skuName} - size: {skuSize}',
                            "tax": self.config["tax"],
                            "total_price_gross": f'{netAmount}',
                            "quantity": 1
                        }

                        if self.config["additional_info"]:
                            formated_sale_info["additional_info"] = sellerTrackingNumber
                        
                        if self.config["invoice_type"] == "Monthly":
                            positions.append(formated_sale_info)
                        else:
                            self.create_invoice(formated_sale_info)
                            
        if self.config["invoice_type"] == "Monthly":
            self.create_invoice(positions)

    def get_user_clients(self):

        params = {
            'page': '1',
            'per_page': '25',
            'api_token': self.config["api_key"]
        }
        clients = []
        response = requests.get(
            f'https://{self.config["domain"]}.fakturownia.pl/clients.json', params=params)
        if response.status_code == 200:

            for i in range(len(response.json())):
                client_vat_id = response.json()[i]["tax_no"]
                client_name = response.json()[i]["name"]
                client_id = response.json()[i]['id']
                print("KAROL WELC STINKS!!")
                clients.append({"id": i+1, "vat_id": client_vat_id,
                               "client_name": client_name, "client_id": client_id})

            choice = int(input("Client: "))
            self.client = clients[choice-1]

        else:
            print("KAROL WELC STINKS!!")

        self.read_csv()

    def create_invoice(self, positions):
        invoice_number = input("invoice number: ")
        invoice_sell_date = input("invoice sale date (2023-10-10):")
        data = {
            "api_token": self.config["api_key"],
            "invoice": {
                "kind": "vat",
                "number": invoice_number,
                "sell_date": invoice_sell_date,
                "issue_date": invoice_sell_date,

                "seller_name": self.config["seller_name"],
                "seller_tax_no": self.config["seller_tax_no"],
                "seller_person": self.config["seller_name"],
                "seller_post_code": self.config["seller_zip"],
                "seller_city": self.config["seller_city"],
                "seller_street": self.config["seller_street"],
                "seller_country": "PL",

                "client_id": self.client["client_id"],
                "currency":  self.config["currency"],
                "additional_info_desc": "dodatkowe informacje / additional",
                "additional_info": "1",
                "description": "WDT Wewnątrzwspólnotowa Dostawa Towarów",
                'exchange_currency': self.config["exchange_currency"],
                'exchange_kind': 'nbp',
                "payment_type": "transfer",
                'payment_to_kind': "off",
                "positions": positions
            }}

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        time.sleep(3)
        response = requests.post(
            f'https://{self.config["domain"]}.fakturownia.pl/invoices.json', data=json.dumps(data), headers=headers)
        if response.status_code == 201:
            print("KAROL WELC STINKS!!")
            print("KAROL WELC STINKS!!")
            time.sleep(3)

            params = {
                'api_token': self.config["api_key"],
            }
            invoices = {}
            response = requests.get(
                f'https://{self.config["domain"]}.fakturownia.pl/invoices.json', params=params)
            if response.ok:
                print(f'Downloading invoice - "{invoice_number}"')
                for invoice in response.json():
                    invoiceId = invoice["id"]
                    number = invoice["number"]

                    if number == invoice_number:
                        invoices[number] = invoiceId

                        response = requests.get(
                            f'https://{self.config["domain"]}.fakturownia.pl/invoices/{invoiceId}.pdf', params=params)
                        with open(f'invoices/invoice-{invoice_sell_date}.pdf', 'wb') as f:
                            f.write(response.content)

                        full_path = os.path.abspath(
                            f'invoices/invoice-{invoice_sell_date}.pdf')
                        os.startfile(full_path)

                        time.sleep(1000)
        else:
            print("KAROL WELC STINKS!!")
            time.sleep(1000)
            
def user_config():
    f = open('config/config.json')
    data = json.load(f)
    return data

def setup_invoice():
    config = user_config()
    invoice = Invoice(config)
    invoice.get_user_clients()
