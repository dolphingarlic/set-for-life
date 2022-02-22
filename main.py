import time
import os
import sys
import itertools

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import networkx as nx


COLOURS = {
    '#008002': 1,  # Green
    '#ff0101': 2,  # Red
    '#800080': 3,  # Purple
}

SHAPES = {
    '#diamond': 1,
    '#oval': 2,
    '#squiggle': 3
}


def connect_chrome():
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('log-level=3')
    options.add_argument("--incognito")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if os.environ.get('GOOGLE_CHROME_BIN') != None:
        options.binary_location = os.environ['GOOGLE_CHROME_BIN']
    driver = webdriver.Chrome(
        executable_path=os.environ['CHROMEDRIVER_PATH'], options=options)
    return driver


if __name__ == '__main__':
    print('Connecting to Chrome...')
    browser = connect_chrome()
    print('Connected to Chrome!')
    try:
        url = 'https://setwithfriends.com/'
        browser.get(url)
        time.sleep(3)

        # Create a new game (after an optional delay)
        browser.find_element(
            By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textPrimary"]').click()
        browser.find_element(
            By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-fullWidth"]').click()
        if len(sys.argv) == 2:
            time.sleep(float(sys.argv[1]))
        else:
            time.sleep(2)
        browser.find_element(
            By.XPATH, '//button[@class="MuiButtonBase-root MuiButton-root MuiButton-contained MuiButton-containedPrimary MuiButton-containedSizeLarge MuiButton-sizeLarge MuiButton-fullWidth"]').click()

        while True:
            try:
                # Get all active cards
                cards = browser.find_elements(
                    By.XPATH, '//div[@class="MuiPaper-root MuiPaper-elevation1 MuiPaper-rounded"]/div[contains(@style, "visibility: visible;")]/div')
                # Map cards to card tuples
                card_tuples = {}
                for card in cards:
                    shapes = card.find_elements(By.TAG_NAME, 'svg')
                    shape_data = shapes[0].find_elements(By.TAG_NAME, 'use')
                    if shape_data[0].get_attribute('fill') == 'transparent':
                        pattern = 1
                    elif shape_data[0].get_attribute('mask') == 'url(#mask-stripe)':
                        pattern = 2
                    else:
                        pattern = 3

                    card_tuples[(
                        len(shapes),  # Count
                        COLOURS[shape_data[1].get_attribute(
                            'stroke')],  # Colour
                        SHAPES[shape_data[0].get_attribute('href')],  # Shape
                        pattern,  # Pattern
                    )] = card

                # Find all triples
                sets = []
                for triple in itertools.combinations(card_tuples, 3):
                    if [sum(attr) % 3 for attr in zip(*triple)] == [0, 0, 0, 0]:
                        sets.append(triple)

                # If there are no sets, retry
                if len(sets) == 0:
                    continue

                # Maximum independent set
                g = nx.Graph()
                g.add_nodes_from(sets)
                for pair in itertools.combinations(sets, 2):
                    if any(card in pair[1] for card in pair[0]):
                        g.add_edge(*pair)
                        g.add_edge(*pair[::-1])
                independent_sets = nx.algorithms.maximal_independent_set(g)

                # Click the sets
                for set in independent_sets:
                    try:
                        webdriver.ActionChains(browser).send_keys(
                            Keys.ESCAPE).perform()
                        for card in set:
                            card_tuples[card].click()
                    except:
                        continue

                # Wait for the transition
                time.sleep(0.1)
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(e)
        browser.close()
