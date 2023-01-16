from django.core.management.base import BaseCommand, CommandError
import requests
import csv
from ... import models

class Command(BaseCommand):
    help = 'This command populates the "Symbol" table with tickers.'

    def add_arguments(self, parser):
        pass 

    def handle(self, *args, **options):
        models.Symbol.objects.all().delete()
        api_token = 'WWF2YGNBXK210E9A'
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_token}'
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for i in range(len(my_list)):
                ticker = models.Symbol()
                ticker.name = my_list[i][0]
                ticker.save()

            self.stdout.write(self.style.SUCCESS('Successfully populated the "Symbol" table with active stocks and ETFs as of the latest trading day.'))