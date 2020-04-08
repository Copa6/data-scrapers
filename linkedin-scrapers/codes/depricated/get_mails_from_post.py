# from WebConnectHelper import WebConnect as WC
from decouple import config
import os, time, sys
import pandas as pd
from bs4 import BeautifulSoup
import re

helper_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) +'\\helperclass'
sys.path.append(helper_dir)

from WebConnectHelper import WebConnect as WC


def create_df_and_write(all_emails, output_file, Connector):
	df = pd.DataFrame({
		'Email' : all_emails
	})
	Connector.write_to_csv(df, output_file)

i = init_count = 0

working_dir= os.path.dirname(os.path.dirname(os.path.realpath(__file__)).replace('\\','/'))

u = config('u')
p = config('p')
url = config('url') 

output_file = os.path.normpath(working_dir + '/csv/linkedin_post_data.csv')

Connector = WC("https://www.linkedin.com")

Connector.login(u, p, "login-email", "login-password", "login-submit")
# Connector.goto_url("https://www.linkedin.com/feed/update/urn:li:activity:6382659653465145344/?commentUrn=urn%3Ali%3Acomment%3A(activity%3A6382659653465145344%2C6385031549317898240)")
Connector.goto_url(url)


sort_button_path = '//*[text()="Top Comments"]'
recent_comments_path = '//button[text()="Recent Comments"]'
name_path = '//span[@class="hoverable-link-text"]'
Connector.click_target(sort_button_path, kind='s', by="xpath")
Connector.click_target(recent_comments_path, kind='s', by="xpath")

time.sleep(3)

show_more_id = "show_prev"
clicked_show_more = load_more_element = Connector.click_target(show_more_id, by="id", kind="new")

Connector.click_target(sort_button_path, kind='s', by="xpath")
Connector.click_target(recent_comments_path, kind='s', by="xpath")

while(clicked_show_more):
	clicked_show_more = load_more_element = Connector.click_target(show_more_id, by="id", kind="new")
	# Connector.scroll_page_down()

all_page_html = Connector.get_target_html(target="/html", by="xpath", kind="new")
all_page_soup = BeautifulSoup(all_page_html, 'html.parser')
all_links = [a_element.get('href') for a_element in all_page_soup.find_all('a')]
mail_data = [link for link in all_links if "mailto" in str(link)]

all_mail_ids = []
for mail_id in mail_data:
	all_mail_ids.append(mail_id.split(':')[1])

create_df_and_write(all_mail_ids, output_file, Connector)
print("Written all mails to csv")
# Connector.close_connection()

