import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import json

# URLs of Amazon , Microsoft , Google
urls = [
    "https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_TPR=r86400&f_C=1586&position=1&pageNum=0"
]

#user agent
def fetch_jobs(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

#conditions to be displayed

def parse_jobs(soup):
    jobs = []
    for job in soup.find_all('li', class_='result-card'):
        job_data = {}
        job_data['Company_name'] = job.find('h4', class_='result-card__subtitle').text.strip(
        ) if job.find('h4', class_='result-card__subtitle') else None
        job_data['linkedin Job ID'] = job.find('a', href=True)['href'].split(
            '/')[-1] if job.find('a', href=True) else None
        job_data['Job title'] = job.find('h3', class_='result-card__title').text.strip(
        ) if job.find('h3', class_='result-card__title') else None
        job_data['Location'] = job.find('span', class_='job-result-card__location').text.strip(
        ) if job.find('span', class_='job-result-card__location') else None
        job_data['Posted on'] = job.find('time', class_='job-result-card__listdate').text.strip(
        ) if job.find('time', class_='job-result-card__listdate') else None
        job_data['Posted date'] = convert_date(job_data['Posted on'])
        job_data['Seniority level'] = job.find('span', class_='job-result-card__seniority-level').text.strip(
        ) if job.find('span', class_='job-result-card__seniority-level') else None
        job_data['Employment type'] = job.find('span', class_='job-result-card__employment-type').text.strip(
        ) if job.find('span', class_='job-result-card__employment-type') else None
        jobs.append(job_data)
    return jobs

#convert date
def convert_date(relative_date):
    relative_date = relative_date.lower()
    today = datetime.today()

    if 'today' in relative_date:
        return today.strftime('%d-%m-%Y')
    elif 'yesterday' in relative_date:
        return (today - timedelta(days=1)).strftime('%d-%m-%Y')
    else:
        match = re.match(r'(\d+)\s+(\w+)\s+ago', relative_date)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if 'day' in unit:
                return (today - timedelta(days=num)).strftime('%d-%m-%Y')
            elif 'week' in unit:
                return (today - timedelta(weeks=num)).strftime('%d-%m-%Y')
            elif 'month' in unit:
                return (today - timedelta(days=num*30)).strftime('%d-%m-%Y')
            elif 'year' in unit:
                return (today - timedelta(days=num*365)).strftime('%d-%m-%Y')
    return relative_date

#fetching
def main():
    all_jobs = []
    for url in urls:
        soup = fetch_jobs(url)
        jobs = parse_jobs(soup)
        all_jobs.extend(jobs)

    # Saving data to CSV
    df = pd.DataFrame(all_jobs)
    df.to_csv('linkedin_jobs.csv', index=False)

    # Saving data to JSON
    with open('linkedin_jobs.json', 'w') as json_file:
        json.dump(all_jobs, json_file, indent=4)


if __name__ == '__main__':
    main()
