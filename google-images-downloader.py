#!/usr/bin/env python

from selenium import webdriver
from urllib import request

import argparse
import os
import json
import ssl
import imghdr

download_path = "./result"

possible_extensions = {"jpg", "jpeg", "png", "gif"}

headers = {
    b'User-Agent': b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"
}

ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)


def download_image(image_url, image_type, image_prefix, image_postfix):
    print("Downloading image: " + image_url)

    if image_type not in possible_extensions:
        image_type = "jpg"

    if not os.path.isdir(download_path + "/" + image_prefix):
        os.mkdir(download_path + "/" + image_prefix)

    raw_img = request.urlopen(request.Request(image_url, headers, method='GET'), context=ssl_context).read()

    image_file_name = image_prefix + "_" + str(image_postfix) + "." + image_type
    image_path = download_path + "/" + image_prefix + "/" + image_file_name

    with open(image_path, 'wb') as f:
        f.write(raw_img)

    print("Downloaded: " + image_file_name)

    if not imghdr.what(image_path):
        os.remove(image_path)
        raise IOError("Image validation failed")


def main(search_query, limit=50):
    if not os.path.exists(download_path):
        print("Download path `%s` not found, will create new folder" % download_path)
        os.mkdir(download_path)

    download_url = "https://www.google.co.in/search?q=" + '+'.join(search_query) + "&source=lnms&tbm=isch"

    print("Will download from url: " + download_url)

    print("Creating new web driver")
    driver = webdriver.Chrome()
    driver.get(download_url)

    images = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
    print("Total images: %d" % len(images))

    images = images[:limit]

    limit = len(images)

    print("Will download %d images" % len(images))

    downloaded_image_counter = 0

    for image in images:
        inner_html_json = json.loads(image.get_attribute('innerHTML'))
        image_url = inner_html_json['ou']
        image_type = inner_html_json['ity']

        try:
            download_image(image_url, image_type, "_".join(search_query).lower(), downloaded_image_counter + 1)
            downloaded_image_counter += 1
            print("Downloaded %d of %d" % (downloaded_image_counter, limit))
        except Exception as e:
            print("Failed to download image: " + str(e))

    print("Successfully downloaded %d of %d images" % (downloaded_image_counter, limit))

    print("Closing web driver")
    driver.quit()


if __name__ == "__main__":
    os.environ["PATH"] += os.pathsep + os.getcwd()

    parser = argparse.ArgumentParser(description="Download some images from google")
    parser.add_argument('search_query', metavar='QUERY', nargs="*", type=str, help="a query for the search")
    parser.add_argument('--limit', type=int, default=50, help="defines, how many images should be downloaded")
    parser.add_argument('--dst', type=str, default="./result",
                        help="defines path by which downloaded files should be saved")

    args = parser.parse_args()

    if not args.search_query:
        print("Cannot perform script, query is empty")
        exit(0)

    download_path = os.path.abspath(args.dst)

    main(args.search_query, args.limit)
