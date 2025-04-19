import requests
import csv
from bs4 import BeautifulSoup
from sklearn.preprocessing import LabelEncoder

base_url = "https://krisha.kz/prodazha/kvartiry/astana/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_ad_data(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка загрузки страницы: {url}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    def extract_data(selector):
        element = soup.find("div", {"data-name": selector})
        return element.find(class_="offer__advert-short-info").get_text(strip=True) if element else "Не найдено"
    
    price = soup.find(class_="offer__price").get_text(strip=True) if soup.find(class_="offer__price") else "Не найдено"
    location = soup.find(class_="offer__location").get_text(strip=True) if soup.find(class_="offer__location") else "Не найдено"
    
    city, region = location.replace("показать на карте", "").split(", ") if ", " in location else (location, "Не найдено")
    
    house_type = extract_data("flat.building")
    complex_name = extract_data("map.complex")
    year = extract_data("house.year")
    
    floor_info = extract_data("flat.floor").split(" из ")
    floor = floor_info[0] if len(floor_info) > 0 else "Не найдено"
    total_floors = floor_info[1] if len(floor_info) > 1 else "Не найдено"
    
    square = extract_data("live.square").replace(" м²", "").split(",")[0]
    
    toilet = extract_data("flat.toilet")
    
    return [price, city, region, house_type, complex_name, year, floor, total_floors, square, toilet]

def get_ad_links(page_number):
    page_url = f"{base_url}?page={page_number}"
    response = requests.get(page_url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка загрузки списка объявлений на странице {page_number}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    ad_elements = soup.find_all("a", class_="a-card__image")
    links = ["https://krisha.kz" + ad["href"] for ad in ad_elements if "href" in ad.attrs]
    return links

all_ad_links = []
for page_number in range(1, 10):
    all_ad_links.extend(get_ad_links(page_number))

data_list = []
for link in all_ad_links:
    data = extract_ad_data(link)
    if data:
        data_list.append(data)

city_encoder = LabelEncoder()
region_encoder = LabelEncoder()

cities = [data[1] for data in data_list]
regions = [data[2] for data in data_list]

encoded_cities = city_encoder.fit_transform(cities)
encoded_regions = region_encoder.fit_transform(regions)

house_type_encoder = LabelEncoder()

house_types = [data[3] for data in data_list]
encoded_house_types = house_type_encoder.fit_transform(house_types)

with open("krisha_data.csv", mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=",")
    writer.writerow(["Цена", "Город", "Регион (Encoded)", "Тип дома (Encoded)", "Жилой комплекс", "Год постройки", "Этаж", "Всего этажей", "Площадь", "Санузел"])
    
    for i, data in enumerate(data_list):
        writer.writerow([data[0], data[1], encoded_regions[i], encoded_house_types[i]] + data[4:6] + data[7:])

print("Данные успешно собраны и сохранены в krisha_data.csv")