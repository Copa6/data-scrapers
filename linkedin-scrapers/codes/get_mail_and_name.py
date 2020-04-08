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
fname = config('fname')
url = config('url')

output_file = os.path.normpath(working_dir + f"/csv/{fname}.csv")

Connector = WC()

sign_in_path = '//a[text()="Sign in"]'
Connector.click_target(sign_in_path, kind='s', by='xpath')

Connector.click_target(sign_in_path, kind='s', by='xpath')
Connector.login(u, p, "username", "password", '//button[text()="Sign in"]')
# Connector.goto_url("https://www.linkedin.com/feed/update/urn:li:activity:6382659653465145344/?commentUrn=urn%3Ali%3Acomment%3A(activity%3A6382659653465145344%2C6385031549317898240)")
# Connector.goto_url("https://www.linkedin.com/feed/update/activity:6402141301369856000/")
# Connector.goto_url("https://www.linkedin.com/posts/saloni-barelia-60611180_campusplacements-panindia-autogram-activity-6580352476703223808-joJn/")


sort_button_path = '//*[text()="Most Relevant"]'
recent_comments_path = '//*[text()="Most Recent"]'
name_path = '//span[@class="hoverable-link-text"]'
mail_comment_path = '//div[contains(@class,"comments-comment-item__inline-show-more-text feed-shared-inline-show-more-text ember-view")]/p'



time.sleep(3)

show_more_id = '//*[text()="Load more comments"]'
sort_button_clicked = Connector.click_target(sort_button_path, kind='new', by="xpath")
recent_comments_clicked = Connector.click_target(recent_comments_path, kind='new', by="xpath")


print(f"Clicked Sort button - {sort_button_clicked}")
print(f"Clicked Recent button - {recent_comments_clicked}")

while not (recent_comments_clicked and sort_button_clicked):
	time.sleep(3)
	sort_button_clicked = Connector.click_target(sort_button_path, kind='s', by="xpath")
	recent_comments_clicked = Connector.click_target(recent_comments_path, kind='s', by="xpath")
	# clicked_show_more = load_more_element = Connector.click_target(show_more_id, by="xpath", kind="new")
	print(f"Clicked Sort button - {sort_button_clicked}")
	print(f"Clicked Recent button - {recent_comments_clicked}")

Connector.scroll_to_bottom()
clicked_show_more = load_more_element = Connector.click_target(show_more_id, by="xpath", kind="new")
show_more_exists = Connector.check_if_element_exists(show_more_id, by="xpath", kind="new")
print(f"Clicked Show more - {clicked_show_more}")
print(f"Show more exists - {show_more_exists}")
while not clicked_show_more:
	time.sleep(1)
	Connector.scroll_to_bottom()
	print("Could not click show more. Re Click")
	clicked_show_more = load_more_element = Connector.click_target(show_more_id, by="xpath", kind="new")

while(clicked_show_more or show_more_exists):
	try:
		clicked_show_more = load_more_element = Connector.click_target(show_more_id, by="xpath", kind="new")
		Connector.scroll_to_bottom()
		show_more_exists = Connector.check_if_element_exists(show_more_id, by="xpath", kind="new")
	except:
		print('Loaded all comments')
	# Connector.scroll_page_down()

all_names = Connector.load_elements(name_path, by="xpath", kind="new")
all_emails = Connector.load_elements(mail_comment_path, by="xpath", kind="new")

# print(all_names)

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

