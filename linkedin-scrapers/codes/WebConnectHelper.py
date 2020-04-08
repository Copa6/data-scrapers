import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
from bs4 import BeautifulSoup
import re

import pandas as pd

class WebConnect():
	def __init__(self, url):
		self.driver = self.connect_driver()
		self.driver.get(url)
		print("Connected")

	def connect_driver(self):
		# driver = webdriver.Firefox() # Uses geckodriver win64

		# working_dir= os.path.dirname(os.path.dirname(os.path.realpath(__file__)).replace('\\','/'))
		# working_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')
		# gecko = os.path.normpath(working_dir + '/drivers/geckodriver')
		# binary = FirefoxBinary(r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe')
		# driver = webdriver.Firefox(firefox_binary=binary, executable_path=gecko+'.exe') # uses geckodriver win32

		#To connect using custom profile
		# profile = webdriver.FirefoxProfile(os.path.expanduser("C:/Users/ss_0002/AppData/Roaming/Mozilla/Firefox/Profiles/52wbvzqb.default"))
		profile = webdriver.FirefoxProfile()
		profile.set_preference('dom.webnotifications.enabled', False)
		profile.set_preference('browser.link.open_newwindow', 	1)
		profile.set_preference('browser.link.open_newwindow.restriction', 0)
		profile.set_preference('browser.link.open_newwindow.override.external', -1)
		driver = webdriver.Firefox(firefox_profile=profile) 
		# driver = webdriver.Firefox()
		return driver
		
	def extract_target_info(self, target, by):
		if isinstance(target, dict):
			path = target["path"]
			by = target["by"]
		else:
			path = target
			by = by
		return path, by

	def load_element(self, target, by=None, kind="new"):
		elem = None
		i=0
		
		path, by = self.extract_target_info(target, by)
		delay = 5 if kind=="new" else 2
		while((elem is None) and (i<delay)):
			try:
				if by=="xpath":
					elem = self.driver.find_element_by_xpath(path)
				elif by=="id":
					elem = self.driver.find_element_by_id(path)
				elif by=="link_text":
					elem = self.driver.find_element_by_link_text(path)
				elif by=="name":
					elem = self.driver.find_element_by_name(path)
			except:
				time.sleep(1)
				i +=1
		return(elem)

	def check_if_element_exists(self, target, by=None):
		elem = None
		path, by = self.extract_target_info(target, by)
		try:
			if by=="xpath":
				elem = self.driver.find_element_by_xpath(path)
			elif by=="id":
				elem = self.driver.find_element_by_id(path)
			elif by=="link_text":
				elem = self.driver.find_element_by_link_text(path)
			elif by=="name":
				elem = self.driver.find_element_by_name(path)

		except:
			time.sleep(1)
		return elem

	def load_elements(self, target, by=None, kind="new"):
		path, by = self.extract_target_info(target, by)
		elem = None
		i=0
		delay = 5 if kind=="new" else 2
		while((elem is None) and (i<delay)):
			try:
				if by=="xpath":
					elem = self.driver.find_elements_by_xpath(target)
				elif by=="id":
					elem = self.driver.find_elements_by_id(target)
				elif by=="link_text":
					elem = self.driver.find_elements_by_link_text(target)
				elif by=="name":
					elem = self.driver.find_elements_by_name(target)
			except:
				time.sleep(1)
				i +=1
		return(elem)


	def login(self, username, password, id_u, id_p, submit_button=None):
		elem_login = self.driver.find_element_by_id(id_u)
		elem_pw = self.driver.find_element_by_id(id_p)

		elem_login.clear()
		elem_pw.clear()

		elem_login.send_keys(username)
		elem_pw.send_keys(password)
		if submit_button:
			self.click_target(submit_button)
		else:
			elem_pw.send_keys(Keys.ENTER)
		print("logged in")

	
	def search(self, term, id_search):
		elem_search = self.load_by_id(id_search)
		elem_search.clear()
		elem_search.send_keys(term)
		elem_search.send_keys(Keys.ENTER)

	
	def click_target(self, target, by=None, kind="new"):
		elem = self.load_element(target, by, kind)
		if elem is not None:
			try:
				elem.click()
				return True
			except:
				return False
			
		else:
			return False


	def get_target_html(self, target=None, by=None, kind='new', loaded_element=None):
		if loaded_element is None:
			elem = self.load_element(target, by, kind)
		else:
			elem = loaded_element
		if elem is not None:
			return elem.get_attribute("innerHTML")
		else:
			return 0


	def get_target_text(self, target, by=None, kind="new"):
		elem = self.load_element(target, by, kind)
		if elem is not None:
			return elem.get_attribute("innerHTML").strip().lstrip().replace("\n", " ")
		else:
			return 0


	def write_to_div(self, message, target, by=None, kind="new"):
		elem = self.load_element(target, by, kind)
		if elem is not None:
			action = webdriver.ActionChains(self.driver)
			action.move_to_element_with_offset(elem, 10, 3)
			action.click()
			action.send_keys(message)
			action.send_keys(Keys.ENTER)
			action.perform()
			return True
		else:
			return False


	def click_back(self):
		self.driver.execute_script("window.history.go(-1)")

	
	def scroll_page_down(self):
		webdriver.ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()

	
	def scroll_page_up(self):
		webdriver.ActionChains(self.driver).send_keys(Keys.PAGE_UP).perform()


	def scroll_to_bottom(self):
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


	def scroll_up(self, Y):
		script = "window.scrollTo(0,document.body.scrollHeight-" + str(Y) + " )"
		self.driver.execute_script(script) 

		
	def write_to_csv(self, dataframe, f_name):
		dataframe.to_csv(f_name, sep=',', index=False)


	def close_connection(self):
		try:
			self.driver.close()
			return True
		except:
			return False


	def goto_url(self, url):
		self.driver.get(url)


	def switch_tab(self, tab_index):
		self.driver.switch_to.window(self.driver.window_handles[tab_index])


	def cancel_notification_popup(self):
		webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()