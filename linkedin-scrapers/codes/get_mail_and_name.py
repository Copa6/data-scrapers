# from WebConnectHelper import WebConnect as WC
from decouple import config
import os, time, sys
import pandas as pd
from bs4 import BeautifulSoup
import re

# helper_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) +'\\helperclass'
# sys.path.append(helper_dir)

from WebConnectHelper import WebConnect as WC


def create_df_and_write(all_emails, all_names, output_file, Connector):
	df = pd.DataFrame({
		'Email' : all_emails,
		'Name'	: all_names
	})
	Connector.write_to_csv(df, output_file)

i = init_count = 0
names=[]
emails=[]

working_dir= os.path.dirname(os.path.dirname(os.path.realpath(__file__)).replace('\\','/'))

u = config('u')
p = config('p')
fname = config('save_to')
url = config('url')

output_file = os.path.normpath(working_dir + f"/csv/{fname}.csv")

Connector = WC(url)

# Clickable paths
sign_in_button = {"path": '//a[text()="Sign in"]', "by": 'xpath'}
login_button = {"path": '//button[text()="Sign in"]', "by": 'xpath'}
sort_button = {"path": '//*[text()="Most Relevant"]', "by": 'xpath'}
show_more_button = {"path": '//*[text()="Load more comments"]', "by": 'xpath'}
recent_comments_button = {"path": '//*[text()="Most Recent"]', "by": 'xpath'}
user_name_element = {"path": '//span[@class="hoverable-link-text"]', "by": 'xpath'}
mail_comment_element = {
"path": '//div[contains(@class,"comments-comment-item__inline-show-more-text feed-shared-inline-show-more-text ember-view")]/p',
"by": 'xpath'
}

Connector.click_target(sign_in_button, kind='s')
Connector.login(u, p, "username", "password", login_button)

# name
# mail_comment_path = '//div[contains(@class,"comments-comment-item__inline-show-more-text feed-shared-inline-show-more-text ember-view")]/p'

# Wait for the page to load before performing next action
time.sleep(3)

sort_button_clicked = Connector.click_target(sort_button)
recent_comments_clicked = Connector.click_target(recent_comments_button)
print(f"Clicked Sort button successfully - {sort_button_clicked}")
print(f"Clicked Recent button successfully - {recent_comments_clicked}")

# If the clicks are not successful, wait and try clicking again to get comments in the right order
while not (recent_comments_clicked and sort_button_clicked):
	time.sleep(3)
	sort_button_clicked = Connector.click_target(sort_button, kind='search')
	recent_comments_clicked = Connector.click_target(recent_comments_button, kind='search')
	print(f"Clicked Sort button successfully - {sort_button_clicked}")
	print(f"Clicked Recent button successfully - {recent_comments_clicked}")


Connector.scroll_to_bottom()
clicked_show_more = Connector.click_target(show_more_button) 
show_more_exists = Connector.check_if_element_exists(show_more_button)
print(f"Clicked Show more successfully - {clicked_show_more}")
print(f"Show more exists successfully - {show_more_exists}")

# If unable to click show more after sorting comments, wait and retry
while not clicked_show_more:
	time.sleep(1)
	Connector.scroll_to_bottom()
	print("Could not click show more. Re Click")
	clicked_show_more = Connector.click_target(show_more_button, kind="search") 

# Continue clicking the "Load more comments" link, till all comments are loaded
while(clicked_show_more or show_more_exists):
	try:
		clicked_show_more = Connector.click_target(show_more_button)
		Connector.scroll_to_bottom()
		show_more_exists = Connector.check_if_element_exists(show_more_button)
	except Exception as e:
		print(e)
		pass
print('Loaded all comments')

all_names = Connector.load_elements(user_name_element)
all_emails = Connector.load_elements(mail_comment_element)

if all_names is not None:
	for i, name in enumerate(all_names):
		# print(name)
		try:
			email = all_emails[i].find_element_by_xpath(".//a")
		except:
			email=None

		if email is not None:
			email_id = Connector.get_target_html(loaded_element=email, by='xpath', kind='old')
			user_name = Connector.get_target_html(loaded_element=name, by='xpath', kind='old')
			if '<span' not in email_id and 'http' not in email_id:
				names.append(user_name)
				emails.append(email_id)


create_df_and_write(emails, names, output_file, Connector)
print("Written all mails to csv")
Connector.close_connection()

