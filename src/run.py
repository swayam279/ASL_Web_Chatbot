import time

from crawler import scrape
from sitemap import create_sitemap

start= time.time()
url= input("Enter a url: ")
sitemap= create_sitemap(url)

result= scrape(sitemap)

end= time.time()
print(result)

print(f'\n\nThe total time taken was: {end - start}')