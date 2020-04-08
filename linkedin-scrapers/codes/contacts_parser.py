from WebConnectHelper import WebConnect as WC
from decouple import config
import os, time
import pandas as pd
from bs4 import BeautifulSoup
import re

def create_df_and_write(all_names, all_desigs, all_comp, all_educ, all_loc, all_phone, all_emails, output_file, Connector):
	df = pd.DataFrame({
		'Name' : all_names,
		'Designation' : all_desigs,
		'Company' : all_comp,
		'Education' : all_educ,
		'Location' : all_loc,
		'Phone' : all_phone,
		'Email' : all_emails
	})
	Connector.write_to_csv(df, output_file)

received=1827
scroll_count = 0


u = config('u')
p = config('p')
url = config('base_url')
fname = config('save_to')

working_dir= os.path.dirname(os.path.dirname(os.path.realpath(__file__)).replace('\\','/'))
output_file = os.path.normpath(working_dir + f"/csv/{fname}.csv")

Connector = WC(url)
Connector.login(u, p, "login-email", "login-password", "login-submit")

networks_path = '//a[@href="/mynetwork/"]'
num_connect_path = '//div[@class="mn-connections connections-container Elevation-2dp"]/h2'

# base_person_path = '/html/body/div[5]/div[5]/div[3]/div[2]/div/div[2]/div/ul/div/li['
base_person_path = '//div[contains(@class, \'mn-connections connections-container\')]/li['
end_person_path = ']/div[1]/a'

# person_data_base = '/html/body/div[5]/div[5]/div[4]/div/div/div/div[2]/div[1]/div[2]/section/div[2]/div[1]'
name_path = "//h1[contains(@class, \'pv-top-card-section__name\')]"
desig_path = "//h2[contains(@class, \'pv-top-card-section__headline\')]"
comp_path = "//h3[contains(@class, \'pv-top-card-section__company\')]"   
educ_path = "//h3[contains(@class, \'pv-top-card-section__school\')]"
location_path = "//h3[contains(@class, \'pv-top-card-section__location\')]"
email_path = "//header[text()=\'Email\']/../div/a"
phone_path = "//header[text()=\'Phone\']/../ul"

show_more_button = '//button[contains(@class,\'contact-see-more-less\')]'

all_names = []
all_desigs = []
all_comp = []
all_educ = []
all_loc = []
all_emails=[]
all_phone=[]


_ =Connector.click_target(networks_path, by="xpath", kind="s")
_ =Connector.click_target("See all", by="link_text", kind="new")



num_connections = Connector.get_target_text(num_connect_path, by="xpath", kind="s").replace(",","").split(" ")
# print(num_connections)
# print(num_connections[0])
i=received
reloaded = False
while i <= int(num_connections[0])+1:
	ret_val = Connector.click_target(base_person_path + str(i) + end_person_path, by="xpath", kind="s")
	if ret_val:
		try:
			name = Connector.get_target_text(name_path, by="xpath", kind="s")
			desig = Connector.get_target_text(desig_path, by="xpath", kind="s")
			company = Connector.get_target_text(comp_path, by="xpath", kind="s")
			educ = Connector.get_target_text(educ_path, by="xpath", kind="s")
			location = Connector.get_target_text(location_path, by="xpath", kind="s")

			_ =Connector.click_target(show_more_button,  by="xpath", kind="s")
			email = Connector.get_target_text(email_path, by="xpath", kind="s")
			phone_element = Connector.load_element(phone_path, by="xpath", kind="s")
			if phone_element is not None:
				phone_html = phone_element.get_attribute("innerHTML")
				phone_soup = BeautifulSoup(phone_html, "html.parser")
				phone_spans = phone_soup.find_all("span")
				phone_data = [data.get_text().replace("\n", "")for data in phone_spans]
				phone_numbers = [ re.findall(r'\d+', phone) for phone in phone_data ][0]
				phone = ''
				for numbers in phone_numbers:
					phone += str(numbers) + ','

				phone = phone[:-1]
			else:
				phone='0'



			print(str(i) + ': ' + str(name))
			# print(desig)
			# print(company)
			# print(educ)
			# print(location)
			all_names.append(name)
			all_desigs.append(desig)
			all_comp.append(company)
			all_educ.append(educ)
			all_loc.append(location)
			all_emails.append(email)
			all_phone.append(phone)
			Connector.click_back()
			scroll_count = 0
			reloaded = False
			i += 1
		except Exception as e:
			print(e)
			print(i)
			create_df_and_write(all_names, all_desigs, all_comp, all_educ, all_loc, all_phone, all_emails, output_file, Connector)		
			_ =Connector.click_target(networks_path, by="xpath", kind="s")
			_ =Connector.click_target("See all", by="link_text", kind="new")


	else:
		print("Scrolling")
		create_df_and_write(all_names, all_desigs, all_comp, all_educ, all_loc, all_phone, all_emails, output_file, Connector)		

		if i >= 19:
			time.sleep(0.5)
			Connector.scroll_page_down()
			scroll_count +=1
			if len(all_names)==0 or reloaded:
				for _ in range(int(i/19)):
					Connector.scroll_page_down()
					scroll_count += 1
					if scroll_count >=25:
						Connector.scroll_page_up()
						time.sleep(1)
						scroll_count = 0
			elif scroll_count>=50:
				_ =Connector.click_target(networks_path, by="xpath", kind="s")
				_ =Connector.click_target("See all", by="link_text", kind="new")
				reloaded = True
				scroll_count=0

			else:
				if scroll_count >=25:
					if len(all_names)==0 or reloaded:
						scroll_count = 0
						Connector.scroll_page_up()
						time.sleep(1)
					else:
						_ =Connector.click_target(networks_path, by="xpath", kind="s")
						_ =Connector.click_target("See all", by="link_text", kind="new")
						reloaded = True
						scroll_count=0
				else:
					Connector.scroll_page_down()
					scroll_count += 1

				# time.sleep(1)
			

create_df_and_write(all_names, all_desigs, all_comp, all_educ, all_loc, all_phone, all_emails, output_file, Connector)		

	
print('written_all_data')
print('Closing Connection now')
Connector.close_connection()		

