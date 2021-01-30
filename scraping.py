from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
   # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = hemisphere_data(browser)
   # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": hemisphere_image_urls
}
   # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    try:
        PREFIX = "https://web.archive.org/web/20181114023740"
        url = f'{PREFIX}/https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        browser.visit(url)
        article = browser.find_by_tag('article').first['style']
        article_background = article.split("_/")[1].replace('");',"")
        return f'{PREFIX}_if/{article_background}'
    except:
        return 'https://www.nasa.gov/sites/default/files/styles/full_width_feature/public/thumbnails/image/pia22486-main.jpg'
 
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere_data(browser):
    try:
        url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(url)

    # 2. Create a list to hold the images and titles.
        hemisphere_image_urls = []
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
        html = browser.html
        image_data = soup(html,"html.parser")
        #Get Hemisphere Image URLs to visit
        urls = image_data.find_all("div",class_="item")
        #Loop through the hemishere URLs to find the URL for the full resolution images
        for url in urls:
            # Build the f string for the image URLs from previous step
            image_url = f'https://astrogeology.usgs.gov{url.find("a")["href"]}'
            # Visit the full image link
            browser.visit(image_url)
            html = browser.html
            page2 = soup(html,"html.parser")
            # Get the Full Image Link
            link = page2.find("div",class_="downloads").find("a")["href"]
            # Get the Image Title
            title = page2.find("h2", class_="title").get_text()
            #Create the dictionary to hold the results
            hemispheres = {"img_url":link, "title":title}
            hemisphere_image_urls.append(hemispheres)
     # 4. Return the list that holds the dictionary of each image url and title.
        return hemisphere_image_urls
    except BaseException:
        return None
    
    

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())