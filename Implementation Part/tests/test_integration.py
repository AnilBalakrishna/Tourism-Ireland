import os
import sys
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import threading
from flask_testing import LiveServerTestCase

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, DATA_FILE

# Test data file
TEST_INTEGRATION_FILE = "data/test_integration_attractions.json"

class IntegrationTest(LiveServerTestCase):
    def create_app(self):
        """Create Flask app for testing"""
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 5000
        app.config['DATA_FILE'] = TEST_INTEGRATION_FILE
        return app
    
    def setUp(self):
        """Set up the test environment"""
        # Create test data file
        os.makedirs(os.path.dirname(TEST_INTEGRATION_FILE), exist_ok=True)
        with open(TEST_INTEGRATION_FILE, 'w') as f:
            json.dump([], f)
        
        # Set up Chrome options for headless testing
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def tearDown(self):
        """Tear down the test environment"""
        self.driver.quit()
        
        # Clean up test file
        if os.path.exists(TEST_INTEGRATION_FILE):
            os.remove(TEST_INTEGRATION_FILE)
    
    def test_end_to_end_crud(self):
        """Test all CRUD operations through the UI"""
        self.driver.get(self.get_server_url())
        
        # ===== Create =====
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "createNewBtn"))
        )
        
        # Click the Add New button
        self.driver.find_element(By.ID, "createNewBtn").click()
        
        # Wait for modal to appear
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "attractionModal"))
        )
        
        # Fill out the form
        self.driver.find_element(By.ID, "attractionName").send_keys("Cliffs of Moher")
        self.driver.find_element(By.ID, "attractionLocation").send_keys("County Clare")
        self.driver.find_element(By.ID, "attractionDescription").send_keys("Stunning sea cliffs on the west coast of Ireland that rise to a height of 214 meters.")
        self.driver.find_element(By.ID, "attractionRating").send_keys("4.8")
        self.driver.find_element(By.ID, "attractionImage").send_keys("https://example.com/cliffs.jpg")
        self.driver.find_element(By.ID, "attractionWebsite").send_keys("https://www.cliffsofmoher.ie")
        
        # Save the attraction
        self.driver.find_element(By.ID, "saveAttractionBtn").click()
        
        # Wait for the attraction to appear in the list
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "attraction-card"))
        )
        
        # Verify the attraction was created
        attraction_cards = self.driver.find_elements(By.CLASS_NAME, "attraction-card")
        self.assertEqual(len(attraction_cards), 1)
        self.assertIn("Cliffs of Moher", self.driver.page_source)
        self.assertIn("County Clare", self.driver.page_source)
        
        # ===== Read =====
        # Click the View button for the attraction
        self.driver.find_element(By.CLASS_NAME, "view-btn").click()
        
        # Wait for modal to appear with data
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "modalTitle"), "View Attraction")
        )
        
        # Verify the attraction details
        self.assertEqual(
            self.driver.find_element(By.ID, "attractionName").get_attribute("value"),
            "Cliffs of Moher"
        )
        self.assertEqual(
            self.driver.find_element(By.ID, "attractionLocation").get_attribute("value"),
            "County Clare"
        )
        
        # Close the modal
        self.driver.find_element(By.CLASS_NAME, "btn-close").click()
        
        # ===== Update =====
        # Click the Edit button for the attraction
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "attractionModal"))
        )
        self.driver.find_element(By.CLASS_NAME, "edit-btn").click()
        
        # Wait for modal to appear
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "modalTitle"), "Edit Attraction")
        )
        
        # Update the name
        name_field = self.driver.find_element(By.ID, "attractionName")
        name_field.clear()
        name_field.send_keys("Cliffs of Moher - Updated")
        
        # Update the rating
        rating_field = self.driver.find_element(By.ID, "attractionRating")
        rating_field.clear()
        rating_field.send_keys("5.0")
        
        # Save the updated attraction
        self.driver.find_element(By.ID, "saveAttractionBtn").click()
        
        # Wait for the page to refresh
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "attractionModal"))
        )
        
        # Verify the attraction was updated
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element_value((By.ID, "searchInput"), "")
        )
        self.assertIn("Cliffs of Moher - Updated", self.driver.page_source)
        
        # ===== Delete =====
        # Click the Delete button for the attraction
        self.driver.find_element(By.CLASS_NAME, "delete-btn").click()
        
        # Wait for confirmation modal to appear
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "deleteModal"))
        )
        
        # Confirm deletion
        self.driver.find_element(By.ID, "confirmDeleteBtn").click()
        
        # Wait for the page to refresh
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "deleteModal"))
        )
        
        # Verify the attraction was deleted by checking for the no attractions message
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "noAttractionsMessage"))
        )
        
        # Check the actual file to make sure it's empty
        with open(TEST_INTEGRATION_FILE, 'r') as f:
            attractions = json.load(f)
        
        self.assertEqual(len(attractions), 0)
    
    def test_search_and_sort(self):
        """Test search and sort functionality"""
        # Add test data directly to the file
        attractions = [
            {
                "id": "1",
                "name": "Dublin Castle",
                "location": "Dublin",
                "description": "Historic castle in Dublin",
                "rating": 4.0,
                "created_at": "2023-01-01T00:00:00"
            },
            {
                "id": "2",
                "name": "Blarney Castle",
                "location": "Cork",
                "description": "Famous for the Blarney Stone",
                "rating": 4.8,
                "created_at": "2023-01-02T00:00:00"
            },
            {
                "id": "3",
                "name": "Giants Causeway",
                "location": "County Antrim",
                "description": "Natural rock formation",
                "rating": 4.5,
                "created_at": "2023-01-03T00:00:00"
            }
        ]
        
        with open(TEST_INTEGRATION_FILE, 'w') as f:
            json.dump(attractions, f)
        
        # Load the page
        self.driver.get(self.get_server_url())
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "attraction-card"))
        )
        
        # Verify all three attractions are shown
        attraction_cards = self.driver.find_elements(By.CLASS_NAME, "attraction-card")
        self.assertEqual(len(attraction_cards), 3)
        
        # Test search functionality
        search_input = self.driver.find_element(By.ID, "searchInput")
        search_input.send_keys("Dublin")
        self.driver.find_element(By.ID, "searchBtn").click()
        
        # Wait for results to update
        time.sleep(1)
        
        # Verify only Dublin Castle is shown
        attraction_cards = self.driver.find_elements(By.CLASS_NAME, "attraction-card")
        self.assertEqual(len(attraction_cards), 1)
        self.assertIn("Dublin Castle", self.driver.page_source)
        self.assertNotIn("Blarney Castle", self.driver.page_source)
        
        # Clear search
        search_input.clear()
        self.driver.find_element(By.ID, "searchBtn").click()
        
        # Wait for results to update
        time.sleep(1)
        
        # Test sort functionality - sort by rating desc
        sort_select = self.driver.find_element(By.ID, "sortSelect")
        sort_select.send_keys("Rating")
        
        order_select = self.driver.find_element(By.ID, "orderSelect")
        order_select.send_keys("Descending")
        
        self.driver.find_element(By.ID, "sortBtn").click()
        
        # Wait for results to update
        time.sleep(1)
        
        # Get the order of attractions
        attraction_cards = self.driver.find_elements(By.CLASS_NAME, "attraction-card")
        
        # The first should be Blarney Castle (highest rating)
        self.assertIn("Blarney Castle", attraction_cards[0].text)
        
        # The last should be Dublin Castle (lowest rating)
        self.assertIn("Dublin Castle", attraction_cards[2].text)
