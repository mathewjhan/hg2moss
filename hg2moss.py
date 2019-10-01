from bs4 import BeautifulSoup
import mechanicalsoup
import mosspy
import webbrowser
import os

def login(browser, email, password):
    browser.open("https://www.hypergrade.com/login")
    browser.select_form('form[role="form"]')
    browser["email"] = email
    browser["pwd"] = password
    return browser.submit_selected()

def getMap(html, courseCode, assignmentName):
    assignments = {}
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('div', {'id':courseCode})
    for assignment in soup.find_all('div', {'class' : 'assignment'}):
        aName = assignment.find('span', {'class': 'assignment_name'}).get_text().lower()
        if(aName != "new assignment"): assignments[aName] = int(assignment.find('input', {'type':'hidden'})["value"])
    return assignments

def scrape(browser, ID, assignment):
    browser.open("https://www.hypergrade.com/grades")

    links = browser.links(url_regex=("(^approve)*?("+str(ID)+")"))
    for x in links:
        browser.open("https://www.hypergrade.com/" + x['href'])
        soup = browser.get_current_page()
        name = soup.find("div", {"class": "col-sm-4 text-center"}).get_text().strip()
        try:
            browser.download_link(link="getFile", file="Student Submissions" +os.sep + assignment + os.sep + name + ".java")
        except mechanicalsoup.utils.LinkNotFoundError:
            print("Code not found for: %s" %name.lower().title())

def main():
    # Replace these values
    userid=0000000 #for MOSS
    email ="EMAIL"
    password = "REDACTED"
    # for each class in hypergrade
    courseCodes = [10000, 20000]

    assignmentIDs = list();
    m = mosspy.Moss(userid, "java")

    assignment = input("Assignment name: ").lower()

    print()

    try:
        os.mkdir(os.getcwd() + os.sep + "Student Submissions")
        print("Student Submissions directory not found. \nCreated in: %s" %os.getcwd())
    except FileExistsError:
        print("Student Submissions directory found.")

    print()

    browser = mechanicalsoup.StatefulBrowser()

    html = login(browser, email, password).text

    for x in courseCodes:
            assignmentIDs.append(getMap(html, x, assignment))
            print("Assignment IDs for Course#%s successfully scraped." %x)
    print()

    if assignment in assignmentIDs[0]:
        try:
            os.mkdir(os.getcwd() + os.sep + "Student Submissions" + os.sep + assignment)
            print("Assignment directory not found. \nCreated in: %s" %(os.getcwd()+os.sep+"Student Submissions"))
        except FileExistsError:
            print("Assignment directory found.")
        print()

        for i in range(len(assignmentIDs)):
            print("-"*50)
            print("Downloading student java code from Course#%s" %courseCodes[i])
            print("-"*50)
            try:
            	scrape(browser, assignmentIDs[i][assignment], assignment)
            except:
            	print("Assignment not found for Course#%s" %courseCodes[i])
            print()
        print("Running programs through MOSS...\n")

        try:
            m.addFilesByWildcard(os.getcwd() + os.sep + "Student Submissions" + os.sep + assignment+os.sep+"*.java")
            url = m.send()
            print ("Report Url: " + url + "\n")
            print("Opening in browser...\n")
            webbrowser.open_new(str(url))
            print("Program successfully terminated.\nwew lad")
        except:
            print("ERROR: MOSS set up incorrectly either online or locally")

    else: print("ERROR: Assignment '%s' not found." %assignment)

if __name__ == '__main__':
    main()
