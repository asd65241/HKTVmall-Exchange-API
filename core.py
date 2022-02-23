import requests
import pandas as pd
import datetime
import json
import pathlib
import os

class HKTVmallToolkit:
    """HKTVmallToolKit.

    This module used to interact with the HKTVmall Exchange backend, which used mainly for inventory and order management

    """
    def __init__(self,location="sales-record/",username=os.environ['HKTV_USERNAME'],pwd=os.environ['HKTV_PWD'],merchant=os.environ['HKTV_MERCHANT_CODE']):
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
        self.location = location
        self.username = username
        self.pwd = pwd
        self.merchant = merchant

        # Create the location 
        path = pathlib.Path(location)
        if not path.exists():
            # Create the location
            os.mkdir(location)

    def __getHKTVmallDailySales(self,date,cookies,location,chuck_size=512):
        """__getHKTVmallDailySales

        The method will get the daily sales excel from the HKTVmall

        Args:
            date        (str) : The date of the report you want to get in the format of {yyyymmdd} (i.e. 20220212)
            cookies     (dict): The cookies contains PHPSESSID
            location    (str) : The saving location (path) of the sales report
            chuck_size  (int) : The chuck size of the file

        Return:
            filePath (str): The location of the report
        """
        try:
            url = "https://exchange.hktvmall.com/merchant/reports/download_report.php"
            merchant = self.merchant
            fileName = f"ECOM-EXCH_DAILY_ORDER_{merchant}_{date}.xlsx"
            r = requests.post(url, data={"fileName": fileName, "reportDataPath": "../merchant_reports/"}, cookies=cookies, stream=True)
            
            if r.text.startswith("File Not Exist"):
                raise Exception(f"The file {fileName} not exist")

            filePath = location + fileName
            with open(filePath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chuck_size): 
                    f.write(chunk)
                return filePath
        except Exception as msg:
            print(msg)
            return False

    def __getDay(self,last=1):
        """__getDay

        The method will return the date of n day before today.

        Args:
            last (int): How many day before to to day (e.g today is 20220210, if last=1, then return 20220209)

        Return:
            date (str): The date string in the format of {yyyymmdd}
        """
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=last)

        return yesterday.strftime('%Y%m%d')

    def __loginHKTVmall(self):
        """__loginHKTVmall

        The method will login to https://exchange.hktvmall.com and return the session cookies

        Return:
            cookies (dict): The PHPSESSID cookies (i.e. {"PHPSESSID": "xxxxxxxxxxx"})
        """
        url = "https://exchange.hktvmall.com/merchant/shared/login.php"
        username = self.username
        pwd = self.pwd
        
        r = requests.post(url, data={'username': username, 'pwd':pwd})
        
        # Get PHPSESSID
        for c in r.cookies:
            if c.name == "PHPSESSID":
                return {c.name:c.value}
        return False

    def getSalesND(self,date=0):
        target_date = self.__getDay(date)
        return self.getSales(target_date)

    def getSales(self,date=""):
        """getSales

        The method will return the daily sales of a given day

        Args:
            date (int): The date of the sales report in the format of {yyyymmdd}

        Return:
            sales (list): The list of dict of each row of the sales listed items
        """
        if date == "":
            date = self.__getDay()
        cookies = self.__loginHKTVmall()
        if cookies == False:
            raise Exception("Unable to Login")
        fileName = self.__getHKTVmallDailySales(date=date,cookies=cookies,location=self.location)

        print(fileName)

        try:
            df = pd.read_excel(fileName,skiprows=4)
        except Exception as msg:
            try:
                os.remove(fileName)
            except:
                pass
            raise Exception("Cannot read excel",msg)
        result = df.to_json(orient="table")
        parsed = json.loads(result)

        return parsed["data"]

if __name__ == '__main__':
    tbox = HKTVmallToolkit()

    sales_data = tbox.getSales()
    print(sales_data)