from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


data = [
    {"URL":None, "ProductID":"B005UKT9LG", "ProductName":"Colors-Shadow-Cosmetic-Shimmer-Eyeshadow-Palette"},
    {"URL":None, "ProductID":"B0029ERWH4", "ProductName":"SHANY-Cosmetics-Natural-Eyeshadow-Palette"},
    {"URL":"https://www.amazon.com/Julep-Eyeshadow-101-Powder-Palette/dp/B0CHDBQ3KW/", "ProductID":None, "ProductName":None},
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
        
    def RETRIEVE(self):
        if not self.URL:
            self.URL = self.URL_Template.format(self.ProductName, self.ProductID)
        self.DRIVER.get(self.URL)
        
        WebDriverWait(self.DRIVER, 20).until(EC.presence_of_all_elements_located((By.XPATH, self.DefaultSeller)))
        SoldBy = self.DRIVER.find_elements(By.XPATH, self.DefaultSeller)
        
        if SoldBy: 
            if "Amazon" not in SoldBy[0].text:
                self.Sellers.append({"Seller":SoldBy[0].text, "SellerURL":SoldBy[0].get_attribute("href")})
                
        WebDriverWait(self.DRIVER, 20).until(EC.presence_of_element_located((By.XPATH, self.OfferListings)))
        self.DRIVER.find_element(By.XPATH, self.OfferListings).click()
        
        WebDriverWait(self.DRIVER, 30).until(EC.presence_of_all_elements_located((By.XPATH, self.SellerAnchor)))
        Sellers = self.DRIVER.find_elements(By.XPATH, self.SellerAnchor)
        Sellers = [self.Sellers.append({"Seller":x.text, "SellerURL":x.get_attribute("href")}) for x in Sellers if "Amazon" not in x.text] 
    
    def RUN(self):
        for data in self.Data:
            self.URL = data["URL"]
            self.ProductName = data["ProductName"]
            self.ProductID = data["ProductID"]
            try: self.RETRIEVE()
            except: pass 
        self.Save()  
    
    def Save(self):
        with open('data.json','w') as file:
            json.dump({"data":self.Sellers}, file)


driver = webdriver.Chrome()
Seller(driver, data).RUN()