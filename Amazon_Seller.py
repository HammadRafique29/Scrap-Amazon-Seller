from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from threading import Thread
import json
import os
import csv

data = [
    {"URL":"https://www.amazon.com/Jaclyn-Luxe-Legacy-Eyeshadow-Palette/dp/B0CFD7FXXV/", "ProductID":None, "ProductName":None},
    {"URL":"https://www.amazon.com/Too-Faced-Natural-Eyeshadow-Palette/dp/B0852SZ4XN/", "ProductID":None, "ProductName":None},
    {"URL":"https://www.amazon.com/NYX-PROFESSIONAL-MAKEUP-Ultimate-Eyeshadow/dp/B01IW02HYG/", "ProductID":None, "ProductName":None},
]

class Seller():
    def __init__(self, driver, data):
        self.DRIVER = driver
        self.Data = data
        self.URL_Template = "https://www.amazon.com/{}/dp/{}/"
        self.Sellers = []
        self.XPATHS()
    
    def XPATHS(self):
        self.OfferListings = "//a[contains(@href,'/offer-listing')]"
        self.DefaultSeller = "//a[contains(@href,'/gp/help/seller')]"
        self.SellerAnchor = "//div[@id='aod-offer']//div[@id='aod-offer-soldBy']//a"
        self.SellerDetails = "//div[contains(@id,'page-section-detail-seller-info')]//span"
        
    def RETRIEVE_SELLER(self):
        if not self.URL:
            self.URL = self.URL_Template.format(self.ProductName, self.ProductID)

        self.DRIVER.get(self.URL)
        
        WebDriverWait(self.DRIVER, 20).until(EC.presence_of_all_elements_located((By.XPATH, self.DefaultSeller)))
        SoldBy = self.DRIVER.find_elements(By.XPATH, self.DefaultSeller)
        
        if SoldBy: 
            if "Amazon" not in SoldBy[0].text:
                self.Sellers.append({"Seller":SoldBy[0].text, "SellerURL":SoldBy[0].get_attribute("href")})
                
        WebDriverWait(self.DRIVER, 15).until(EC.presence_of_element_located((By.XPATH, self.OfferListings)))
        self.DRIVER.find_element(By.XPATH, self.OfferListings).click()
        
        WebDriverWait(self.DRIVER, 15).until(EC.presence_of_all_elements_located((By.XPATH, self.SellerAnchor)))
        Sellers = self.DRIVER.find_elements(By.XPATH, self.SellerAnchor)
        Sellers = [x for x in Sellers if "Amazon" not in x.text]
        
        def StartFetching():
            self.RETRIEVE_SELLER_DETAILS(Sellers)
            
        Thread(target=StartFetching()).start() 
    
    def RETRIEVE_SELLER_DETAILS(self, Sellers):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        Driver = webdriver.Chrome(options=chrome_options)

        for seller in Sellers:
            url = seller.get_attribute("href")
            Driver.get(url)
            
            while True:
                try:
                    WebDriverWait(Driver, 7).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href,'/dogsof')]")))
                    SellersDetail = Driver.find_element(By.XPATH, "//a[contains(@href,'/dogsof')]")
                    Driver.get(url)
                except: break
            
            WebDriverWait(Driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'Visit the')]")))
            StoreName = Driver.find_element(By.XPATH, "//a[contains(text(),'Visit the')]")
            WebDriverWait(Driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, self.SellerDetails)))
            SellersDetail = Driver.find_elements(By.XPATH, self.SellerDetails)
            SellersDetail = [x.text for x in SellersDetail if x.text not in ["Business Name:", "Business Address:"]]
            
            if len(SellersDetail)==6:
                sellerData = [
                {   "Seller_Name": seller.text,
                    "Business_Name": SellersDetail[0],
                    "Address": SellersDetail[1],
                    "Detail": SellersDetail[2:],
                    "City": SellersDetail[2],
                    "State": SellersDetail[3],
                    "Zip": SellersDetail[4],
                    "Country": SellersDetail[5],
                    "Phone": None,
                    "Email": None,
                    "SellerDetailsUrl": url,
                    "SellerProductUrl": StoreName.get_attribute("href"),
                }]
            elif len(SellersDetail)>6:
                sellerData = [
                {   "Seller_Name": seller.text,
                    "Business_Name": SellersDetail[0],
                    "Address": SellersDetail[1],
                    "Detail": SellersDetail[2:],
                    "City": None,
                    "State": None,
                    "Zip": None,
                    "Country": None,
                    "Phone": None,
                    "Email": None,
                    "SellerDetailsUrl": url,
                    "SellerProductUrl": StoreName.get_attribute("href"),
                }]
            print(SellersDetail)
            self.SaveCSV(sellerData)
            
    def RUN(self):
        for data in self.Data:
            self.URL = data["URL"]
            self.ProductName = data["ProductName"]
            self.ProductID = data["ProductID"]
            try: self.RETRIEVE_SELLER()
            except: pass 
        self.Save()  
    
    def Save(self):
        with open('data.json','w') as file:
            json.dump({"data":self.Sellers}, file)
            
    def SaveCSV(self, DATA):
        csv_file = "SellerData.csv"
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                "Seller_Name", "Business_Name", "Address", "Detail", "City", "State", "Zip",
                "Country", "Phone", "Email", "SellerDetailsUrl", "SellerProductUrl"
            ])
            if not file_exists or file.tell() == 0: writer.writeheader()
            for row in DATA:
                writer.writerow(row)


driver = webdriver.Chrome()
obj = Seller(driver, data)
obj.RUN()
