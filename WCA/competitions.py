from bs4 import BeautifulSoup
import urllib.request, re, json, shutil, smtplib, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--password', help="Password for email account", required=True)
args = parser.parse_args()

sender_email = "notifications@clairefang.com"
sender_password = args.password

def sendEmail(competitions):
    try:
        server= smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)

        sent_from = sender_email
        to = ["adayke10@gmail.com", "claireffang@hotmail.com", "alanypke8@gmail.com", "yke@yanke.org"]
        # to = ["adayke10@gmail.com"]
        subject = "NEW WCA COMPS"
        body = "New WCA competitions: \n"
        url = "https://www.worldcubeassociation.org/competitions?utf8=%E2%9C%93&region=all&search=washington&state=present&year=all+years&from_date=&to_date=&delegate=&display=list"

        for comp in competitions:
            body += f" - When: {comp['date']} ~~~ Where: {comp['location']}\n\n"

        email_text = """\
From: %s
To: %s
Subject: %s

%s \n
Click Here to see details: %s \n
        """ % (sent_from, ", ".join(to), subject, body, url)
        print(email_text)

        server.sendmail(sent_from, to, email_text)

        server.close()
    except Exception as e:
        print("Something went wrong... :D", e)

class Competition(dict):
    def __init__(self, date, location):
        dict.__init__(self, date=date, location=location)
    
def get_competitions():
    competition_list = []

    with urllib.request.urlopen("https://www.worldcubeassociation.org/competitions?utf8=%E2%9C%93&region=all&search=washington&state=present&year=all+years&from_date=&to_date=&delegate=&display=list") as wca:
        page = wca.read()
        soup = BeautifulSoup(page, "html.parser")
        
        elems = soup.find_all("li", class_="list-group-item not-past")

        for element in elems:
            new_elem = element.get_text().strip()
            
            date = re.search(r"[a-zA-Z]{3} \d+, \d{4}", new_elem)
            location = re.search(r"United States, [a-zA-Z]+, Washington", new_elem)
                
            if date and location:
                date_text = date.group()
                location_text = location.group()
                # print(date_text)
                # print(location_text)
                competition_list.append(Competition(date_text, location_text))
    
    return competition_list

competition_list = get_competitions()

for competition in competition_list:
    print(competition)

with open("WCA/newCompetitions.json", "w") as newCompetitions_file:
    json.dump(competition_list, newCompetitions_file)

with open("WCA/oldCompetitions.json", "r") as oldCompetitions_file:
    old_competitions_list = json.load(oldCompetitions_file)

    if old_competitions_list == competition_list:
        print("No new competitions.")
    else:
        print("New competitions!")
        sendEmail(competition_list)

shutil.copyfile("WCA/newCompetitions.json", "WCA/oldCompetitions.json")
