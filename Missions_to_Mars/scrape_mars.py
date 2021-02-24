# import all dependencies (probably imported too many but won't hurt)
from splinter import Browser
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
import requests
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pandas as pd
import pymongo

def scrape():
# open browser and visit url
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    html = browser.html
    soup = bs(html,'html.parser')

    # read through html code to pull titles and texts for news headlines
    titles = soup.find_all('div', class_='list_text')
    news_titles = []
    news_ps = []
    news_dates = []
    for title in titles:  
        titulos = title.find('div',class_='content_title').text
        news_titles.append(titulos)
        fechas = title.find('div', class_='list_date').text
        news_dates.append(fechas)
        texto = title.find('div',class_='article_teaser_body').text
        news_ps.append(texto)
        #print(titulos)
        #print(fechas)
        #print(texto)

    # assign variables to desired headline and text
    news_title = news_titles[0]
    news_date = news_dates[0]
    news_p = news_ps[0]

    #print(news_title)
    #print(news_p)

    # open browser and visit JPL url
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    jpl_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(jpl_url)
    html = browser.html
    soup = bs(html,'html.parser')

    # find featured image and assign to variable
    imagen = soup.find_all('img')[1]["src"]
    featured_image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/' + imagen
    featured_image_url

    # use pandas to import facts table into dataframe 
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    facts_df = tables[0]
    facts_df.columns = ['Description','Measurement']
    facts_df = facts_df.set_index('Description')

    # convert dataframe to html
    facts_html = facts_df.to_html()
    facts_html = facts_html.replace('\n','')
    facts_df.to_html('facts.html')

    # open browser and visit link to hemisphere name and image links
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemi_url)
    html = browser.html
    soup = bs(html,'html.parser')

    # find image links and hemisphere titles and assign to list
    img_urls = []
    hemi_titles = []
    base_url = 'https://astrogeology.usgs.gov'

    hemis = soup.find_all('div', class_='description')

    for hemi in hemis:
        link = hemi.find('a')
        href = link['href']
        hemi_name = hemi.a.find('h3')
        hemi_title = hemi_name.text
        hemi_titles.append(hemi_title)
        img_link = base_url + href
        img_urls.append(img_link)
            
    #print(img_urls)
    #print(hemi_titles)

    # pull enhanced images into list
    hemi_images = []
    for liga in img_urls:
        url = liga
        browser.visit(liga)
        html = browser.html
        soup = bs(html,'html.parser')
        link_imagen = soup.find('img', class_='wide-image')
        enhanced_link = link_imagen['src']
        enhanced_img = base_url + enhanced_link
        hemi_images.append(enhanced_img)

    # create dictionary with hemisphere names and images
    hemisphere_image_urls = [{"title": hemi_titles[0], "img_url": hemi_images[0]},{"title": hemi_titles[1], "img_url": hemi_images[1]},{"title": hemi_titles[2], "img_url": hemi_images[2]},{"title": hemi_titles[3], "img_url": hemi_images[3]}]


    mars_dict = {}
    mars_dict["n_title"] = news_title
    mars_dict["n_text"] = news_p
    mars_dict["featured_img"] = featured_image_url
    mars_dict["table"] = facts_html
    mars_dict["hemis"] = hemisphere_image_urls

    # create function that returns the mars_dict
    return mars_dict