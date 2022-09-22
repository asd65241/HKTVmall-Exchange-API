import requests
import pandas as pd
import datetime
import json
import pathlib
import os
from bs4 import BeautifulSoup
from bs2json import bs2json

from decorator import Error_Handler


class HKTVmallToolkit:
    """HKTVmallToolKit.

    This module used to interact with the HKTVmall Exchange backend, which used mainly for inventory and order management

    """
    @Error_Handler
    def __init__(self, username, pwd, merchant, location="sales-record/", maxRetry=5):
        """__init__

        The method initialize the object with its location, username, password and merchant id

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            location (str): The destination of the sales report will be.
            username (str): The login username used to login https://exchange.hktvmall.com
            pwd      (str): The login password used to login https://exchange.hktvmall.com
            merchant (str): The merchant id of your HKTVmall store that start with H (i.e. HXXXXXXX)
        """
        self.username = username
        self.pwd = pwd
        self.merchant = merchant
        self.location = location
        self.maxRetry = maxRetry
        self.converter = bs2json()

        # login to HKTVmall
        for count in range(self.maxRetry):
            try:
                self.cookies = self.__loginHKTVmall()
                break
            except:
                raise Exception(
                    f"[Try: {count+1}] Can't not login to HKTVmall")

        if self.cookies == "":
            raise Exception("No cookies found")

        # Create the location
        path = pathlib.Path(location)
        if not path.exists():
            # Create the location
            os.mkdir(location)

    @Error_Handler
    def __getHKTVmallDailySales(self, date, location, chuck_size=512):
        """__getHKTVmallDailySales

        The method will get the daily sales excel from the HKTVmall

        Args:
            date        (str) : The date of the report you want to get in the format of {yyyymmdd} (i.e. 20220212)
            location    (str) : The saving location (path) of the sales report
            chuck_size  (int) : The chuck size of the file

        Return:
            filePath (str): The location of the report
        """

        # fileName = f"ECOM-EXCH_DAILY_ORDER_{self.merchant}_{date}.xlsx"
        fileName = self.__getFileNameGivenDate(date)
        url = "https://exchange.hktvmall.com/merchant/reports/download_report.php"

        for _ in range(self.maxRetry):
            r = requests.post(url, data={"fileName": fileName, "reportDataPath": "../merchant_reports/"}, cookies={"PHPSESSID": self.cookies}, stream=True)

            if len(r.history) != 0:
                # The page got redirected: login crediential not working
                print("Cookies not working! Getting a new one")
                self.cookies = self.__loginHKTVmall()

            else:
                # Succesfully Login, then break the for loop
                break

        if r.text.startswith("File Not Exist"):
            raise Exception(f"The file {fileName} not exist")

        filePath = location + fileName

        with open(filePath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chuck_size):
                f.write(chunk)
            return filePath

    @Error_Handler
    def __getDay(self, last=1):
        """__getDay

        The method will return the date of n day before today.

        Args:
            last (int): How many day before to to day (e.g today is 20220210, if last=1, then return 20220209)

        Return:
            date (str): The date string in the format of {yyyymmdd}
        """
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=last)

        return yesterday.strftime("%Y%m%d")

    @Error_Handler
    def __loginHKTVmall(self):
        """__loginHKTVmall

        The method will login to https://exchange.hktvmall.com and return the session cookies

        Return:
            cookies (str): The PHPSESSID
        """
        url = "https://exchange.hktvmall.com/merchant/shared/login.php"
        username = self.username
        pwd = self.pwd

        r = requests.post(url, data={'username': username, 'pwd': pwd})

        # Get PHPSESSID
        for c in r.cookies:
            if c.name == "PHPSESSID":
                return c.value

        return Exception("Unable to Login")

    @Error_Handler
    def __getFileNameGivenDate(self, datestring):
        """__getFileNameGivenDate

        The method will return the file name of the sales report given the date

        Args:
            datestring (str): The date string in the format of {yyyymmdd}

        Return:
            fileName (str): The file name of the sales report
        """

        # Parse the webpage
        URL = "https://exchange.hktvmall.com/merchant/reports/daily_order_report.php"
        r = requests.get(URL,cookies={"PHPSESSID": self.cookies})

        soup = BeautifulSoup(r.content, 'html.parser')

        # Get the html
        report_options = soup.find_all('form', {"name":"downloadReport"})

        # Convert HTML to JSON
        report_options = self.converter.convertAll(report_options,join=True)

        # Filename table
        table = report_options[0]["form"]

        # Get the filename
        for idx, row in enumerate(table):
            try:
                fileName = row["input"]["input"][0]["attributes"]["value"]

                # Check if datestring is in the filename
                if datestring in fileName:
                    return fileName
            except:
                pass
        # Cannot find filename
        return None


    @Error_Handler
    def getSalesND(self, date=0):
        target_date = self.__getDay(date)
        return self.getSales(target_date)

    @Error_Handler
    def getSales(self, date=""):
        """getSales

        The method will return the daily sales of a given day

        Args:
            date (int): The date of the sales report in the format of {yyyymmdd}

        Return:
            sales (list): The list of dict of each row of the sales listed items
        """
        if date == "":
            date = self.__getDay()

        fileName = self.__getHKTVmallDailySales(
            date=date, location=self.location)

        try:
            df = pd.read_excel(fileName, skiprows=4)
        except Exception as msg:
            try:
                os.remove(fileName)
            except:
                pass
            raise Exception("Cannot read excel", msg)
        result = df.to_json(orient="table")
        parsed = json.loads(result)

        return parsed["data"]

    @Error_Handler
    def getAllSalesND(self, date=0):
        sales_report = []

        for day in range(1,date+1):
            target_date = self.__getDay(day)
            print(target_date)
            sales_report += self.getSales(target_date)

        return sales_report

    @Error_Handler
    def getAllSales(self, start_date_str=None, end_date_str=None):

        try:

            sales_report = []

            start_date = datetime.datetime.strptime(start_date_str, "%Y%m%d").date()
            
            if end_date_str:
                end_date = datetime.date.today()
            else:
                end_date = datetime.datetime.strptime(end_date_str, "%Y%m%d").date()

            delta = end_date - start_date
            delta = delta.days

            for day in range(1,delta+1):
                target_date = self.__getDay(day)
                print(target_date)
                sales_report += self.getSales(target_date)

            return sales_report
        except Exception as msg:
            print(msg)



if __name__ == '__main__':
    try:
        tbox = HKTVmallToolkit(username="H7225001_SM",
                               pwd="nW$$$47777", merchant="H7225001")
        sales_data = tbox.getSales()
        print(sales_data)
    except Exception as msg:
        print(msg)
