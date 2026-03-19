from dotenv import load_dotenv
from usp.tree import sitemap_tree_for_homepage

from url_validator import url_checker

load_dotenv()

def create_sitemap(url: str) -> list[str]:
    """ 
    This function takes a url from user and fetches the sitemap of that website and returns a list containing all the urls in the sitemap. 
    """
    
    url_exists= url_checker(url)
    if url_exists:
        print("starting to scrape all the URLs from the website ...")
        tree= sitemap_tree_for_homepage(url)
        
        URLs= [page.url for page in tree.all_pages()]
        sites= len(URLs)
        print(f"successfully fetched the sitemap of the website with {sites} URLs.")
        return URLs
    else:
        print("There was an issue with the given url. Please check the url and try again.")

if __name__ == "__main__":
    url= input("Enter a url: ")
    sitemap= create_sitemap(url)
    print(sitemap)
    # print(len(sitemap))